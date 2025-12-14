"""
scheduler.py - Robust ETL Scheduler using APScheduler

Implements scheduled ETL jobs for cryptocurrency data ingestion.
Uses APScheduler for robust cron-style scheduling and execution.

Usage:
    python -m app.scheduler
"""
import asyncio
import os
import signal
import logging
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

from app.ingestion.service import etl_service
from app.db.models import DataSource, ETLStatus

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s"}',
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)
logger = logging.getLogger("kasparro.scheduler")

class ETLScheduler:
    """
    Robust ETL Scheduler using APScheduler.
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        # Support both seconds (SCHEDULE_INTERVAL) and hours (ETL_INTERVAL_HOURS)
        self.interval_seconds = int(os.getenv("SCHEDULE_INTERVAL", "3600"))
        if "ETL_INTERVAL_HOURS" in os.environ:
            self.interval_seconds = int(os.getenv("ETL_INTERVAL_HOURS")) * 3600

    async def run_etl_job(self):
        """
        Execute a complete ETL cycle for all sources.
        """
        logger.info("Starting scheduled ETL job...")
        start_time = datetime.now(timezone.utc)
        
        try:
            # Run ETL for all sources in parallel
            results = await etl_service.run_all_sources(parallel=True)
            
            # Count successes
            success_count = 0
            for job in results.values():
                logger.info(f"Job source: {job.source}, status: {job.status} (type: {type(job.status)}), expected: {ETLStatus.SUCCESS}")
                if job.status == ETLStatus.SUCCESS or str(job.status) == ETLStatus.SUCCESS.value:
                    success_count += 1
            
            # Log summary
            logger.info(f"ETL Job Completed. Success: {success_count}/{len(results)}")
            
        except Exception as e:
            logger.error(f"Critical error in ETL job: {str(e)}", exc_info=True)
        finally:
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info(f"ETL cycle finished in {duration:.2f}s")

    def job_listener(self, event):
        """
        Listener for job events (success/failure).
        """
        if event.exception:
            logger.error(f"Job {event.job_id} failed: {event.exception}")
        else:
            logger.info(f"Job {event.job_id} executed successfully")

    async def start(self):
        """
        Start the scheduler and block until interrupted.
        """
        logger.info(f"Initializing Scheduler (Interval: {self.interval_seconds} seconds)")
        
        # Add the ETL job
        # Use IntervalTrigger for robust periodic scheduling
        from apscheduler.triggers.interval import IntervalTrigger
        trigger = IntervalTrigger(seconds=self.interval_seconds)

        self.scheduler.add_job(
            self.run_etl_job, 
            trigger=trigger, 
            id="etl_main_job",
            replace_existing=True
        )
        
        # Add listener
        self.scheduler.add_listener(self.job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        
        # Start scheduler
        self.scheduler.start()
        logger.info(f"Scheduler started. Next run at: {self.scheduler.get_job('etl_main_job').next_run_time}")

        # Keep alive
        try:
            # Run once on startup for immediate feedback in dev/prod
            logger.info("Triggering initial startup run...")
            await self.run_etl_job()
            
            # Wait forever
            while True:
                await asyncio.sleep(1000)
        except (KeyboardInterrupt, asyncio.CancelledError):
            logger.info("Stopping scheduler...")
            self.scheduler.shutdown()

if __name__ == "__main__":
    scheduler = ETLScheduler()
    try:
        asyncio.run(scheduler.start())
    except (KeyboardInterrupt, SystemExit):
        pass
