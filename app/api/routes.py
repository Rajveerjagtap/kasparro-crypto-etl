"""API route definitions with enhanced endpoints."""

import time
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
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
    PaginatedResponse,
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

    # Build query with filters
    query = select(UnifiedCryptoData)

    if symbol:
        query = query.where(UnifiedCryptoData.symbol == symbol.upper())
    if source:
        query = query.where(UnifiedCryptoData.source == source)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    query = query.order_by(UnifiedCryptoData.timestamp.desc()).offset(offset).limit(limit)

    result = await db.execute(query)
    items = result.scalars().all()

    # Calculate latency
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
            "returned": len(items),
            "total": total,
        },
    )


# ============== GET /health - DB connectivity and ETL status ==============


@router.get("/health", response_model=HealthResponse)
async def health_check(
    db: AsyncSession = Depends(get_db),
) -> HealthResponse:
    """
    Check system health including database connectivity and last ETL run status.
    
    Performs SELECT 1 to verify DB connection and queries ETLJob for last run info.
    """
    # Check database connectivity
    db_status = DBHealthStatus(connected=False, latency_ms=0.0)
    try:
        start_time = time.perf_counter()
        await db.execute(text("SELECT 1"))
        db_latency = (time.perf_counter() - start_time) * 1000
        db_status = DBHealthStatus(
            connected=True,
            latency_ms=round(db_latency, 2),
        )
    except Exception as e:
        db_status = DBHealthStatus(
            connected=False,
            latency_ms=0.0,
            error=str(e),
        )

    # Get last ETL job status
    etl_status = ETLHealthStatus()
    try:
        query = (
            select(ETLJob)
            .order_by(ETLJob.started_at.desc())
            .limit(1)
        )
        result = await db.execute(query)
        last_job = result.scalar_one_or_none()

        if last_job:
            etl_status = ETLHealthStatus(
                last_run_source=last_job.source,
                last_run_status=last_job.status,
                last_run_at=last_job.completed_at or last_job.started_at,
                records_processed=last_job.records_processed,
                error_message=last_job.error_message,
            )
    except Exception:
        pass

    # Determine overall status
    if db_status.connected:
        if etl_status.last_run_status == ETLStatus.FAILURE:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
    else:
        overall_status = "unhealthy"

    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now(timezone.utc),
        database=db_status,
        etl=etl_status,
    )


# ============== GET /stats - Aggregations and statistics ==============


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    db: AsyncSession = Depends(get_db),
) -> StatsResponse:
    """
    Get aggregated statistics including:
    - Total records processed
    - Average price per symbol
    - ETL job statistics
    - Last success/failure timestamps
    """
    start_time = time.perf_counter()
    request_id = str(uuid.uuid4())

    # Total records
    total_query = select(func.count()).select_from(UnifiedCryptoData)
    total_result = await db.execute(total_query)
    total_records = total_result.scalar() or 0

    # Unique symbols count
    symbols_query = select(func.count(distinct(UnifiedCryptoData.symbol)))
    symbols_result = await db.execute(symbols_query)
    unique_symbols = symbols_result.scalar() or 0

    # Active sources
    sources_query = select(distinct(UnifiedCryptoData.source))
    sources_result = await db.execute(sources_query)
    sources_active = [str(s.value) for s in sources_result.scalars().all()]

    # Symbol statistics (avg, min, max price per symbol)
    symbol_stats_query = (
        select(
            UnifiedCryptoData.symbol,
            func.avg(UnifiedCryptoData.price_usd).label("avg_price"),
            func.min(UnifiedCryptoData.price_usd).label("min_price"),
            func.max(UnifiedCryptoData.price_usd).label("max_price"),
            func.count().label("record_count"),
            func.array_agg(distinct(UnifiedCryptoData.source)).label("sources"),
        )
        .group_by(UnifiedCryptoData.symbol)
        .order_by(func.count().desc())
        .limit(50)
    )
    symbol_stats_result = await db.execute(symbol_stats_query)
    symbol_stats = []
    for row in symbol_stats_result:
        symbol_stats.append(
            SymbolStats(
                symbol=row.symbol,
                avg_price_usd=float(row.avg_price) if row.avg_price else None,
                min_price_usd=float(row.min_price) if row.min_price else None,
                max_price_usd=float(row.max_price) if row.max_price else None,
                record_count=row.record_count,
                sources=[str(s.value) for s in row.sources] if row.sources else [],
            )
        )

    # ETL job statistics
    etl_total_query = select(func.count()).select_from(ETLJob)
    etl_total_result = await db.execute(etl_total_query)
    total_jobs = etl_total_result.scalar() or 0

    etl_success_query = select(func.count()).where(ETLJob.status == ETLStatus.SUCCESS)
    etl_success_result = await db.execute(etl_success_query)
    successful_jobs = etl_success_result.scalar() or 0

    etl_failed_query = select(func.count()).where(ETLJob.status == ETLStatus.FAILURE)
    etl_failed_result = await db.execute(etl_failed_query)
    failed_jobs = etl_failed_result.scalar() or 0

    # Total records processed across all ETL jobs
    records_processed_query = select(func.sum(ETLJob.records_processed))
    records_processed_result = await db.execute(records_processed_query)
    total_records_processed = records_processed_result.scalar() or 0

    # Last success timestamp
    last_success_query = (
        select(ETLJob.completed_at)
        .where(ETLJob.status == ETLStatus.SUCCESS)
        .order_by(ETLJob.completed_at.desc())
        .limit(1)
    )
    last_success_result = await db.execute(last_success_query)
    last_success_at = last_success_result.scalar_one_or_none()

    # Last failure timestamp
    last_failure_query = (
        select(ETLJob.completed_at)
        .where(ETLJob.status == ETLStatus.FAILURE)
        .order_by(ETLJob.completed_at.desc())
        .limit(1)
    )
    last_failure_result = await db.execute(last_failure_query)
    last_failure_at = last_failure_result.scalar_one_or_none()

    # Last job duration
    last_job_query = (
        select(ETLJob)
        .where(ETLJob.completed_at.isnot(None))
        .order_by(ETLJob.completed_at.desc())
        .limit(1)
    )
    last_job_result = await db.execute(last_job_query)
    last_job = last_job_result.scalar_one_or_none()
    last_job_duration = None
    if last_job and last_job.completed_at and last_job.started_at:
        last_job_duration = (last_job.completed_at - last_job.started_at).total_seconds()

    # Data freshness (most recent timestamp)
    freshness_query = select(func.max(UnifiedCryptoData.timestamp))
    freshness_result = await db.execute(freshness_query)
    data_freshness = freshness_result.scalar_one_or_none()

    latency_ms = (time.perf_counter() - start_time) * 1000

    return StatsResponse(
        metadata=ResponseMetadata(
            request_id=request_id,
            total_records=total_records,
            api_latency_ms=round(latency_ms, 2),
        ),
        total_records=total_records,
        unique_symbols=unique_symbols,
        sources_active=sources_active,
        symbol_stats=symbol_stats,
        etl_stats=ETLStats(
            total_jobs=total_jobs,
            successful_jobs=successful_jobs,
            failed_jobs=failed_jobs,
            last_success_at=last_success_at,
            last_failure_at=last_failure_at,
            last_job_duration_seconds=last_job_duration,
            total_records_processed=total_records_processed,
        ),
        data_freshness=data_freshness,
    )


# ============== Existing endpoints (kept for backward compatibility) ==============


@router.get("/crypto", response_model=PaginatedResponse)
async def get_crypto_data(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    source: Optional[DataSource] = Query(None, description="Filter by source"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    """Retrieve paginated cryptocurrency data with optional filters."""
    query = select(UnifiedCryptoData)

    if symbol:
        query = query.where(UnifiedCryptoData.symbol == symbol.upper())
    if source:
        query = query.where(UnifiedCryptoData.source == source)
    if start_date:
        query = query.where(UnifiedCryptoData.timestamp >= start_date)
    if end_date:
        query = query.where(UnifiedCryptoData.timestamp <= end_date)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate
    offset = (page - 1) * page_size
    query = query.order_by(UnifiedCryptoData.timestamp.desc()).offset(offset).limit(page_size)

    result = await db.execute(query)
    items = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        items=[UnifiedCryptoDataSchema.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/crypto/{symbol}", response_model=list[UnifiedCryptoDataSchema])
async def get_crypto_by_symbol(
    symbol: str,
    source: Optional[DataSource] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[UnifiedCryptoDataSchema]:
    """Retrieve cryptocurrency data by symbol."""
    query = select(UnifiedCryptoData).where(
        UnifiedCryptoData.symbol == symbol.upper()
    )

    if source:
        query = query.where(UnifiedCryptoData.source == source)

    query = query.order_by(UnifiedCryptoData.timestamp.desc()).limit(limit)

    result = await db.execute(query)
    items = result.scalars().all()

    if not items:
        raise HTTPException(status_code=404, detail=f"No data found for symbol: {symbol}")

    return [UnifiedCryptoDataSchema.model_validate(item) for item in items]


@router.get("/etl/jobs", response_model=list[ETLJobSchema])
async def get_etl_jobs(
    source: Optional[DataSource] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> list[ETLJobSchema]:
    """Retrieve ETL job history."""
    query = select(ETLJob)

    if source:
        query = query.where(ETLJob.source == source)

    query = query.order_by(ETLJob.started_at.desc()).limit(limit)

    result = await db.execute(query)
    jobs = result.scalars().all()

    return [ETLJobSchema.model_validate(job) for job in jobs]


@router.post("/etl/run/{source}", response_model=ETLJobSchema)
async def trigger_etl_for_source(
    source: DataSource,
    force_full: bool = Query(False, description="Force full reload instead of incremental"),
) -> ETLJobSchema:
    """Trigger ETL pipeline for a specific source."""
    try:
        job = await etl_service.run_etl_for_source(source, force_full=force_full)
        return ETLJobSchema.model_validate(job)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/etl/run", response_model=dict)
async def trigger_etl_all(
    background_tasks: BackgroundTasks,
    sources: Optional[list[DataSource]] = Query(None, description="Specific sources to run"),
    force_full: bool = Query(False, description="Force full reload"),
) -> dict:
    """Trigger ETL pipeline for all sources (runs in background)."""
    async def run_etl():
        await etl_service.run_all_sources(sources=sources, force_full=force_full)

    background_tasks.add_task(run_etl)
    return {
        "status": "started",
        "sources": [s.value for s in (sources or list(DataSource))],
        "force_full": force_full,
    }


@router.get("/sources", response_model=list[str])
async def get_available_sources() -> list[str]:
    """List all available data sources."""
    return [source.value for source in DataSource]


# ============== GET /metrics - Prometheus-style metrics (P2.4) ==============


@router.get("/metrics", response_class=PlainTextResponse)
async def get_metrics(
    db: AsyncSession = Depends(get_db),
) -> str:
    """
    Return Prometheus-compatible metrics.
    
    Includes:
    - http_requests_total: Counter by method/status
    - etl_runs_total: Counter by source/status  
    - etl_last_duration_seconds: Gauge by source
    """
    from app.core.middleware import metrics_collector
    
    # Update ETL metrics from database
    for source in DataSource:
        # Get ETL run counts by status
        for status in ETLStatus:
            count_query = select(func.count()).where(
                ETLJob.source == source,
                ETLJob.status == status,
            )
            result = await db.execute(count_query)
            count = result.scalar() or 0
            
            # Update collector (set count, not increment)
            metrics_collector._etl_runs[(source.value, status.value)] = count
        
        # Get last duration for successful runs
        last_job_query = (
            select(ETLJob)
            .where(
                ETLJob.source == source,
                ETLJob.status == ETLStatus.SUCCESS,
                ETLJob.completed_at.isnot(None),
            )
            .order_by(ETLJob.completed_at.desc())
            .limit(1)
        )
        result = await db.execute(last_job_query)
        last_job = result.scalar_one_or_none()
        
        if last_job and last_job.completed_at and last_job.started_at:
            duration = (last_job.completed_at - last_job.started_at).total_seconds()
            metrics_collector.set_etl_duration(source.value, duration)
    
    return metrics_collector.get_prometheus_output()


# ============== GET /runs/compare - Run Comparison (P2.6) ==============


class RunComparisonResponse(BaseModel):
    """Response schema for run comparison endpoint."""
    
    source: DataSource
    run_id_current: int
    run_id_previous: int
    current_run_at: datetime
    previous_run_at: datetime
    record_count_current: int
    record_count_previous: int
    record_count_change: int
    record_count_change_percent: float
    price_volatility: Optional[float] = Field(
        None, description="Average price change % between runs"
    )
    anomaly_detected: bool = Field(
        description="True if record count changed by > 20%"
    )


@router.get("/runs/compare", response_model=RunComparisonResponse)
async def compare_runs(
    source: DataSource = Query(..., description="Data source to compare runs for"),
    db: AsyncSession = Depends(get_db),
) -> RunComparisonResponse:
    """
    Compare the last 2 successful ETL runs for a given source.
    
    Returns:
    - run_id_current vs run_id_previous
    - record_count_change (difference)
    - price_volatility (average price change % between runs)
    - anomaly_detected (true if record count changed by > 20%)
    """
    # Fetch last 2 successful runs for the source
    runs_query = (
        select(ETLJob)
        .where(
            ETLJob.source == source,
            ETLJob.status == ETLStatus.SUCCESS,
        )
        .order_by(ETLJob.completed_at.desc())
        .limit(2)
    )
    result = await db.execute(runs_query)
    runs = result.scalars().all()
    
    if len(runs) < 2:
        raise HTTPException(
            status_code=404,
            detail=f"Need at least 2 successful runs to compare. Found: {len(runs)}",
        )
    
    current_run = runs[0]
    previous_run = runs[1]
    
    # Calculate record count change
    record_count_change = current_run.records_processed - previous_run.records_processed
    
    # Calculate change percentage
    if previous_run.records_processed > 0:
        change_percent = (record_count_change / previous_run.records_processed) * 100
    else:
        change_percent = 100.0 if current_run.records_processed > 0 else 0.0
    
    # Anomaly detection: > 20% change in record count
    anomaly_detected = abs(change_percent) > 20.0
    
    # Calculate price volatility
    # Get average prices from data around each run's timestamp
    price_volatility = await _calculate_price_volatility(
        db, source, current_run, previous_run
    )
    
    return RunComparisonResponse(
        source=source,
        run_id_current=current_run.id,
        run_id_previous=previous_run.id,
        current_run_at=current_run.completed_at or current_run.started_at,
        previous_run_at=previous_run.completed_at or previous_run.started_at,
        record_count_current=current_run.records_processed,
        record_count_previous=previous_run.records_processed,
        record_count_change=record_count_change,
        record_count_change_percent=round(change_percent, 2),
        price_volatility=price_volatility,
        anomaly_detected=anomaly_detected,
    )


async def _calculate_price_volatility(
    db: AsyncSession,
    source: DataSource,
    current_run: ETLJob,
    previous_run: ETLJob,
) -> Optional[float]:
    """
    Calculate average price change percentage between two runs.
    
    Compares prices of symbols present in both runs.
    """
    if not current_run.completed_at or not previous_run.completed_at:
        return None
    
    # Get symbols and their average prices from current run period
    current_prices_query = (
        select(
            UnifiedCryptoData.symbol,
            func.avg(UnifiedCryptoData.price_usd).label("avg_price"),
        )
        .where(
            UnifiedCryptoData.source == source,
            UnifiedCryptoData.ingested_at >= previous_run.completed_at,
            UnifiedCryptoData.ingested_at <= current_run.completed_at,
        )
        .group_by(UnifiedCryptoData.symbol)
    )
    current_result = await db.execute(current_prices_query)
    current_prices = {row.symbol: row.avg_price for row in current_result}
    
    # Get prices from previous run period
    # Estimate previous period as same duration before previous_run.completed_at
    run_duration = current_run.completed_at - previous_run.completed_at
    previous_start = previous_run.completed_at - run_duration
    
    previous_prices_query = (
        select(
            UnifiedCryptoData.symbol,
            func.avg(UnifiedCryptoData.price_usd).label("avg_price"),
        )
        .where(
            UnifiedCryptoData.source == source,
            UnifiedCryptoData.ingested_at >= previous_start,
            UnifiedCryptoData.ingested_at < previous_run.completed_at,
        )
        .group_by(UnifiedCryptoData.symbol)
    )
    previous_result = await db.execute(previous_prices_query)
    previous_prices = {row.symbol: row.avg_price for row in previous_result}
    
    if not current_prices or not previous_prices:
        return None
    
    # Calculate percentage change for common symbols
    changes = []
    for symbol in current_prices:
        if symbol in previous_prices:
            current_price = current_prices[symbol]
            previous_price = previous_prices[symbol]
            
            if current_price and previous_price and previous_price > 0:
                pct_change = ((current_price - previous_price) / previous_price) * 100
                changes.append(abs(pct_change))
    
    if not changes:
        return None
    
    # Return average absolute price change
    return round(sum(changes) / len(changes), 2)
