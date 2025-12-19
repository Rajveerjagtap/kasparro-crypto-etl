"""API route definitions with enhanced endpoints."""

import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import distinct, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DataSource, ETLJob, ETLStatus, UnifiedCryptoData
from app.db.session import get_db
from app.ingestion.service import etl_service
from app.schemas.crypto import (
    DataResponse,
    DBHealthStatus,
    ETLHealthStatus,
    ETLJobSchema,
    ETLStats,
    HealthResponse,
    ResponseMetadata,
    StatsResponse,
    SymbolStats,
    UnifiedCryptoDataSchema,
)

router = APIRouter()


# ============== GET /data - Enhanced with metadata ==============


@router.get("/data", response_model=DataResponse)
async def get_data(
    symbol: Optional[str] = Query(None, description="Filter by symbol (e.g., BTC, ETH)"),
    source: Optional[DataSource] = Query(None, description="Filter by data source"),
    limit: int = Query(50, ge=1, le=500, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: AsyncSession = Depends(get_db),
) -> DataResponse:
    """
    Retrieve cryptocurrency data with pagination and filtering.
    Returns data with metadata including request_id, total_records, and api_latency_ms.
    """
    start_time = time.perf_counter()
    request_id = str(uuid.uuid4())

    # Build query
    query = select(UnifiedCryptoData)
    count_query = select(func.count()).select_from(UnifiedCryptoData)

    if symbol:
        query = query.where(UnifiedCryptoData.symbol == symbol.upper())
        count_query = count_query.where(UnifiedCryptoData.symbol == symbol.upper())

    if source:
        query = query.where(UnifiedCryptoData.source == source)
        count_query = count_query.where(UnifiedCryptoData.source == source)

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated data
    query = query.order_by(UnifiedCryptoData.timestamp.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    latency_ms = (time.perf_counter() - start_time) * 1000

    return DataResponse(
        metadata=ResponseMetadata(
            request_id=request_id,
            total_records=total,
            api_latency_ms=round(latency_ms, 2),
        ),
        data=[UnifiedCryptoDataSchema.model_validate(item) for item in items],
        pagination={
            "limit": limit,
            "offset": offset,
            "total": total,
        }
    )


# ============== GET /health - Comprehensive System Health ==============


@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """
    Comprehensive health check for DB connection and ETL status.
    """
    start_time = time.perf_counter()
    request_id = str(uuid.uuid4())

    # Check DB connection
    db_connected = False
    db_latency = 0.0
    try:
        t0 = time.perf_counter()
        await db.execute(text("SELECT 1"))
        db_latency = (time.perf_counter() - t0) * 1000
        db_connected = True
    except Exception:
        pass

    db_status = DBHealthStatus(
        connected=db_connected,
        latency_ms=round(db_latency, 2)
    )

    # Check ETL status (last run)
    last_job_query = select(ETLJob).order_by(ETLJob.started_at.desc()).limit(1)
    result = await db.execute(last_job_query)
    last_job = result.scalar_one_or_none()

    etl_status = ETLHealthStatus(
        last_run_status=last_job.status if last_job else None,
        last_run_source=last_job.source if last_job else None,
        last_run_at=last_job.completed_at if last_job else None,
        records_processed=last_job.records_processed if last_job else None,
        error_message=last_job.error_message if last_job else None,
    )

    # Determine overall status
    overall_status = "healthy"
    if not db_status.connected:
        overall_status = "unhealthy"
    elif etl_status.last_run_status == ETLStatus.FAILURE:
        overall_status = "degraded"

    latency_ms = (time.perf_counter() - start_time) * 1000

    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now(timezone.utc),
        database=db_status,
        etl=etl_status,
        metadata=ResponseMetadata(
            request_id=request_id,
            total_records=0,
            api_latency_ms=round(latency_ms, 2),
        )
    )


# ============== GET /stats - Aggregations and statistics ==============


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)) -> StatsResponse:
    """
    Get statistical summary of the crypto data.
    """
    start_time = time.perf_counter()
    request_id = str(uuid.uuid4())

    # Total records
    total_query = select(func.count()).select_from(UnifiedCryptoData)
    total = (await db.execute(total_query)).scalar() or 0

    # Unique symbols
    symbols_query = select(func.count(distinct(UnifiedCryptoData.symbol)))
    unique_symbols = (await db.execute(symbols_query)).scalar() or 0

    # Stats per symbol with sources
    stats_query = (
        select(
            UnifiedCryptoData.symbol,
            func.count(UnifiedCryptoData.id).label("count"),
            func.avg(UnifiedCryptoData.price_usd).label("avg_price"),
            func.max(UnifiedCryptoData.price_usd).label("max_price"),
            func.min(UnifiedCryptoData.price_usd).label("min_price"),
            func.array_agg(distinct(UnifiedCryptoData.source)).label("sources"),
        )
        .group_by(UnifiedCryptoData.symbol)
    )

    try:
        stats_result = (await db.execute(stats_query)).fetchall()
    except Exception:
        # SQLite doesn't support array_agg, fallback
        stats_query = (
            select(
                UnifiedCryptoData.symbol,
                func.count(UnifiedCryptoData.id).label("count"),
                func.avg(UnifiedCryptoData.price_usd).label("avg_price"),
                func.max(UnifiedCryptoData.price_usd).label("max_price"),
                func.min(UnifiedCryptoData.price_usd).label("min_price"),
            )
            .group_by(UnifiedCryptoData.symbol)
        )
        stats_result = (await db.execute(stats_query)).fetchall()

    symbol_stats = []
    for row in stats_result:
        sources = getattr(row, 'sources', None) or [s.value for s in DataSource]
        sources_list = (
            sources if isinstance(sources, list)
            else [str(s) for s in sources] if sources else []
        )
        symbol_stats.append(
            SymbolStats(
                symbol=row.symbol,
                record_count=int(row.count),
                avg_price_usd=float(row.avg_price) if row.avg_price else 0.0,
                max_price_usd=float(row.max_price) if row.max_price else 0.0,
                min_price_usd=float(row.min_price) if row.min_price else 0.0,
                sources=sources_list,
            )
        )

    # ETL job stats
    etl_jobs_query = select(ETLJob)
    etl_jobs_result = await db.execute(etl_jobs_query)
    etl_jobs = etl_jobs_result.scalars().all()

    total_jobs = len(etl_jobs)
    successful_jobs = sum(1 for j in etl_jobs if j.status == ETLStatus.SUCCESS)
    failed_jobs = sum(1 for j in etl_jobs if j.status == ETLStatus.FAILURE)
    total_records_processed = sum(j.records_processed or 0 for j in etl_jobs)

    # Get last success/failure timestamps
    success_jobs = [
        j.completed_at for j in etl_jobs
        if j.status == ETLStatus.SUCCESS and j.completed_at
    ]
    failure_jobs = [
        j.completed_at for j in etl_jobs
        if j.status == ETLStatus.FAILURE and j.completed_at
    ]
    last_success = max(success_jobs, default=None)
    last_failure = max(failure_jobs, default=None)

    # Get last job duration
    last_job = max(etl_jobs, key=lambda j: j.started_at, default=None) if etl_jobs else None
    last_job_duration = None
    if last_job and last_job.completed_at and last_job.started_at:
        last_job_duration = (last_job.completed_at - last_job.started_at).total_seconds()

    # Get data freshness
    freshness_query = select(func.max(UnifiedCryptoData.timestamp))
    data_freshness = (await db.execute(freshness_query)).scalar()

    latency_ms = (time.perf_counter() - start_time) * 1000

    return StatsResponse(
        metadata=ResponseMetadata(
            request_id=request_id,
            total_records=total,
            api_latency_ms=round(latency_ms, 2),
        ),
        total_records=total,
        unique_symbols=unique_symbols,
        sources_active=[s.value for s in DataSource],
        etl_stats=ETLStats(
            total_jobs=total_jobs,
            successful_jobs=successful_jobs,
            failed_jobs=failed_jobs,
            last_success_at=last_success,
            last_failure_at=last_failure,
            last_job_duration_seconds=last_job_duration,
            total_records_processed=total_records_processed,
        ),
        symbol_stats=symbol_stats,
        data_freshness=data_freshness,
    )


# ============== GET /metrics - Prometheus Metrics (P2.4) ==============


@router.get("/metrics")
async def get_metrics():
    """
    Expose Prometheus metrics.
    """
    from fastapi.responses import PlainTextResponse

    from app.core.middleware import metrics_collector
    content = metrics_collector.get_prometheus_output()
    return PlainTextResponse(content=content, media_type="text/plain")


# ============== GET /runs - ETL Run History with Anomaly Detection (P2.6) ==============


@router.get("/runs")
async def get_runs(
    limit: int = Query(10, ge=1, le=100, description="Number of runs to return"),
    source: Optional[DataSource] = Query(None, description="Filter by source"),
    status: Optional[ETLStatus] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Get ETL run history with anomaly detection.

    Returns recent runs with statistical analysis to identify anomalies:
    - Duration outliers (>2 standard deviations from mean)
    - Record count anomalies
    - Failure rate spikes
    """
    # Build query
    query = select(ETLJob).order_by(ETLJob.started_at.desc())

    if source:
        query = query.where(ETLJob.source == source)
    if status:
        query = query.where(ETLJob.status == status)

    query = query.limit(limit)

    result = await db.execute(query)
    jobs = list(result.scalars().all())

    if not jobs:
        return {"runs": [], "anomalies": [], "statistics": {}}

    # Calculate statistics for anomaly detection
    durations = []
    record_counts = []
    success_count = 0
    failure_count = 0

    for job in jobs:
        if job.completed_at and job.started_at:
            duration = (job.completed_at - job.started_at).total_seconds()
            durations.append(duration)
        if job.records_processed is not None:
            record_counts.append(job.records_processed)
        if job.status == ETLStatus.SUCCESS:
            success_count += 1
        elif job.status == ETLStatus.FAILURE:
            failure_count += 1

    # Calculate mean and std dev for anomaly detection
    import statistics
    anomalies = []

    if len(durations) >= 3:
        mean_duration = statistics.mean(durations)
        std_duration = statistics.stdev(durations) if len(durations) > 1 else 0

        # Check for duration anomalies (>2 std devs)
        for job in jobs:
            if job.completed_at and job.started_at:
                duration = (job.completed_at - job.started_at).total_seconds()
                if std_duration > 0 and abs(duration - mean_duration) > 2 * std_duration:
                    z_score = (duration - mean_duration) / std_duration if std_duration else 0
                    lower = mean_duration - 2 * std_duration
                    upper = mean_duration + 2 * std_duration
                    anomalies.append({
                        "job_id": job.id,
                        "type": "duration_outlier",
                        "value": duration,
                        "expected_range": f"{lower:.1f} - {upper:.1f}",
                        "z_score": z_score,
                    })

    if len(record_counts) >= 3:
        mean_records = statistics.mean(record_counts)
        std_records = statistics.stdev(record_counts) if len(record_counts) > 1 else 0

        # Check for record count anomalies
        for job in jobs:
            if job.records_processed is not None and std_records > 0:
                if abs(job.records_processed - mean_records) > 2 * std_records:
                    z_score = (job.records_processed - mean_records) / std_records
                    lower = max(0, mean_records - 2 * std_records)
                    upper = mean_records + 2 * std_records
                    anomalies.append({
                        "job_id": job.id,
                        "type": "record_count_outlier",
                        "value": job.records_processed,
                        "expected_range": f"{lower:.0f} - {upper:.0f}",
                        "z_score": z_score,
                    })

    # Check for failure rate spike
    total_jobs = success_count + failure_count
    if total_jobs > 0:
        failure_rate = failure_count / total_jobs
        if failure_rate > 0.3:  # More than 30% failures is anomalous
            anomalies.append({
                "type": "high_failure_rate",
                "value": failure_rate,
                "threshold": 0.3,
                "message": f"{failure_rate:.1%} of recent jobs failed",
            })

    return {
        "runs": [ETLJobSchema.model_validate(job) for job in jobs],
        "anomalies": anomalies,
        "statistics": {
            "total_runs": len(jobs),
            "success_count": success_count,
            "failure_count": failure_count,
            "success_rate": success_count / total_jobs if total_jobs > 0 else 0,
            "avg_duration_seconds": statistics.mean(durations) if durations else None,
            "avg_records_processed": statistics.mean(record_counts) if record_counts else None,
        },
    }


# ============== GET /runs/compare - Compare ETL Runs (P2.6) ==============


@router.get("/runs/compare")
async def compare_runs(
    run_id_1: int,
    run_id_2: int,
    db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    """
    Compare two ETL runs by ID.
    """
    query = select(ETLJob).where(ETLJob.id.in_([run_id_1, run_id_2]))
    result = await db.execute(query)
    jobs = {job.id: job for job in result.scalars().all()}

    if len(jobs) != 2:
        raise HTTPException(status_code=404, detail="One or both runs not found")

    job1 = jobs[run_id_1]
    job2 = jobs[run_id_2]

    # Calculate duration delta safely
    duration_delta = None
    if job1.completed_at and job2.completed_at:
        dur1 = (job1.completed_at - job1.started_at).total_seconds()
        dur2 = (job2.completed_at - job2.started_at).total_seconds()
        duration_delta = dur2 - dur1

    return {
        "run_1": ETLJobSchema.model_validate(job1),
        "run_2": ETLJobSchema.model_validate(job2),
        "diff": {
            "records_processed": job2.records_processed - job1.records_processed,
            "duration_delta": duration_delta
        }
    }


# ============== ETL Operations ==============


@router.post("/etl/run/{source}")
async def run_etl_for_source(
    source: DataSource,
    background_tasks: BackgroundTasks,
    sync: bool = False,
) -> dict[str, Any]:
    """
    Trigger ETL job for a specific source.
    Set sync=true to run synchronously and get immediate results.
    """
    if sync:
        try:
            job = await etl_service.run_etl_for_source(source)
            return {
                "message": f"ETL job completed for {source.value}",
                "status": "success",
                "job_id": job.id,
                "records_processed": job.records_processed,
            }
        except Exception as e:
            return {
                "message": f"ETL job failed for {source.value}",
                "status": "failed",
                "error": str(e),
            }
    else:
        background_tasks.add_task(etl_service.run_etl_for_source, source)
        return {"message": f"ETL job started for {source.value}", "status": "queued"}


@router.post("/etl/run")
async def run_all_etl(
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    """
    Trigger ETL jobs for ALL sources in the background.
    """
    background_tasks.add_task(etl_service.run_all_sources)
    return {"message": "ETL jobs started for all sources", "status": "queued"}


@router.get("/etl/jobs", response_model=list[ETLJobSchema])
async def get_etl_jobs(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
) -> list[ETLJob]:
    """
    Get history of ETL jobs.
    """
    query = select(ETLJob).order_by(ETLJob.started_at.desc()).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/sources")
async def get_sources() -> list[str]:
    """
    List available data sources.
    """
    return [s.value for s in DataSource]
