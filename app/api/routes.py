"""API route definitions."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DataSource, ETLJob, UnifiedCryptoData
from app.db.session import get_db
from app.ingestion.service import etl_service
from app.schemas.crypto import (
    ETLJobSchema,
    PaginatedResponse,
    UnifiedCryptoDataSchema,
)

router = APIRouter()


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
