"""
scheduler.py - Cloud-based Scheduled ETL Runner

Implements scheduled ETL jobs for cryptocurrency data ingestion.
Runs continuously in production, executing ETL jobs on a configurable schedule.

Usage:
    python -m app.scheduler           # Run scheduler (default: hourly)
    SCHEDULE_INTERVAL=1800 python -m app.scheduler  # Run every 30 minutes
"""
import asyncio
import os
import sys
import signal
import logging
from datetime import datetime, timezone
from typing import Optional

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s"}',
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)
logger = logging.getLogger("kasparro.scheduler")


class ETLScheduler:
    """
    Async ETL Scheduler for cloud deployment.
    
    Runs ETL jobs on a configurable interval using asyncio.
    Designed for deployment as a background worker on Render, Railway, etc.
    """
    
    def __init__(self, interval_seconds: int = 3600):
        """
        Initialize scheduler.
        
        Args:
            interval_seconds: Time between ETL runs (default: 3600 = 1 hour)
        """
        self.interval = interval_seconds
        self.running = False
        self.current_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
    async def run_etl_job(self) -> dict:
        """
        Execute a complete ETL cycle for all sources.
        
        Returns:
            dict: Summary of ETL job results
        """
        from app.db.session import async_session_maker
        from app.etl.service import ETLService
        
        results = {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "sources": {},
            "status": "success",
        }
        
        sources = ["coingecko", "coinpaprika"]
        
        async with async_session_maker() as session:
            service = ETLService(session)
            
            for source in sources:
                try:
                    logger.info(f"Starting ETL for source: {source}")
                    job_result = await service.run_full_etl(source=source)
                    results["sources"][source] = {
                        "status": "success",
                        "job_id": job_result.get("job_id"),
                        "records_processed": job_result.get("records_processed", 0),
                    }
                    logger.info(
                        f"ETL completed for {source}: "
                        f"{job_result.get('records_processed', 0)} records"
                    )
                except Exception as e:
                    logger.error(f"ETL failed for {source}: {str(e)}")
                    results["sources"][source] = {
                        "status": "failed",
                        "error": str(e),
                    }
                    results["status"] = "partial_failure"
        
        results["finished_at"] = datetime.now(timezone.utc).isoformat()
        return results
    
    async def _scheduler_loop(self):
        """Main scheduler loop."""
        logger.info(
            f"Scheduler started - running ETL every {self.interval} seconds "
            f"({self.interval / 3600:.1f} hours)"
        )
        
        # Run immediately on startup
        try:
            logger.info("Running initial ETL on startup...")
            result = await self.run_etl_job()
            logger.info(f"Initial ETL complete: {result['status']}")
        except Exception as e:
            logger.error(f"Initial ETL failed: {e}")
        
        # Then run on schedule
        while self.running:
            try:
                # Wait for interval or shutdown signal
                try:
                    await asyncio.wait_for(
                        self._shutdown_event.wait(),
                        timeout=self.interval
                    )
                    # If we get here, shutdown was requested
                    break
                except asyncio.TimeoutError:
                    # Timeout means interval elapsed, run ETL
                    pass
                
                if not self.running:
                    break
                    
                logger.info("Scheduled ETL run starting...")
                result = await self.run_etl_job()
                logger.info(f"Scheduled ETL complete: {result['status']}")
                
            except asyncio.CancelledError:
                logger.info("Scheduler loop cancelled")
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                # Continue running despite errors
                await asyncio.sleep(60)  # Brief pause before retry
        
        logger.info("Scheduler loop ended")
    
    async def start(self):
        """Start the scheduler."""
        if self.running:
            logger.warning("Scheduler already running")
            return
            
        self.running = True
        self._shutdown_event.clear()
        self.current_task = asyncio.create_task(self._scheduler_loop())
        logger.info("Scheduler started")
    
    async def stop(self):
        """Stop the scheduler gracefully."""
        if not self.running:
            return
            
        logger.info("Stopping scheduler...")
        self.running = False
        self._shutdown_event.set()
        
        if self.current_task:
            self.current_task.cancel()
            try:
                await self.current_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Scheduler stopped")
    
    async def run_forever(self):
        """Run scheduler until interrupted."""
        await self.start()
        
        # Wait for shutdown signal
        try:
            await self._shutdown_event.wait()
        except asyncio.CancelledError:
            pass
        finally:
            await self.stop()


async def main():
    """Main entry point for the scheduler."""
    # Get interval from environment (default: 1 hour)
    interval = int(os.getenv("SCHEDULE_INTERVAL", "3600"))
    
    scheduler = ETLScheduler(interval_seconds=interval)
    
    # Setup signal handlers for graceful shutdown
    loop = asyncio.get_running_loop()
    
    def signal_handler():
        logger.info("Received shutdown signal")
        scheduler._shutdown_event.set()
    
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler)
    
    logger.info("=" * 60)
    logger.info("Kasparro ETL Scheduler")
    logger.info(f"Schedule Interval: {interval} seconds ({interval/3600:.1f} hours)")
    logger.info("=" * 60)
    
    await scheduler.run_forever()
    
    logger.info("Scheduler shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
