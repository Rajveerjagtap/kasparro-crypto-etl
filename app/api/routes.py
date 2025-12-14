"""API route definitions with enhanced endpoints."""

import time
import uuid
from datetime import datetime, timezone
from typing import Optional

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
        last_run_timestamp=last_job.completed_at if last_job else None,
        active_jobs=0  # Placeholder, would need query for RUNNING jobs
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
        symbol_stats.append(
            SymbolStats(
                symbol=row.symbol,
                record_count=row.count,
                avg_price_usd=float(row.avg_price) if row.avg_price else 0.0,
                max_price_usd=float(row.max_price) if row.max_price else 0.0,
                min_price_usd=float(row.min_price) if row.min_price else 0.0,
                sources=sources if isinstance(sources, list) else [str(s) for s in sources] if sources else [],
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
    last_success = max((j.completed_at for j in etl_jobs if j.status == ETLStatus.SUCCESS and j.completed_at), default=None)
    last_failure = max((j.completed_at for j in etl_jobs if j.status == ETLStatus.FAILURE and j.completed_at), default=None)

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


# ============== GET /metrics - Prometheus Metrics (P2.5) ==============


@router.get("/metrics")
async def get_metrics():
    """
    Expose Prometheus metrics.
    """
    from fastapi.responses import PlainTextResponse

    from app.core.middleware import metrics_collector
    return PlainTextResponse(content=metrics_collector.get_prometheus_output(), media_type="text/plain")


# ============== GET /runs/compare - Compare ETL Runs (P2.6) ==============


@router.get("/runs/compare")
async def compare_runs(
    run_id_1: int,
    run_id_2: int,
    db: AsyncSession = Depends(get_db)
):
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

    return {
        "run_1": ETLJobSchema.model_validate(job1),
        "run_2": ETLJobSchema.model_validate(job2),
        "diff": {
            "records_processed": job2.records_processed - job1.records_processed,
            "duration_delta": (job2.completed_at - job2.started_at).total_seconds() - (job1.completed_at - job1.started_at).total_seconds() if job1.completed_at and job2.completed_at else None
        }
    }


# ============== ETL Operations ==============


@router.post("/etl/run/{source}")
async def run_etl_for_source(
    source: DataSource,
    background_tasks: BackgroundTasks,
    sync: bool = False,
):
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
):
    """
    Trigger ETL jobs for ALL sources in the background.
    """
    background_tasks.add_task(etl_service.run_all_sources)
    return {"message": "ETL jobs started for all sources", "status": "queued"}


@router.get("/etl/jobs", response_model=list[ETLJobSchema])
async def get_etl_jobs(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """
    Get history of ETL jobs.
    """
    query = select(ETLJob).order_by(ETLJob.started_at.desc()).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/sources")
async def get_sources():
    """
    List available data sources.
    """
    return [s.value for s in DataSource]
