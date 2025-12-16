"""Pydantic schemas for API request/response validation.

Includes schemas for:
- Coin master entity (canonical asset)
- Source asset mappings
- Unified crypto data (with coin_id reference)
- API responses
"""

import uuid
from datetime import datetime
from typing import Any, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from app.db.models import DataSource, ETLStatus

T = TypeVar("T")


# =============================================================================
# COIN MASTER ENTITY SCHEMAS
# =============================================================================


class CoinSchema(BaseModel):
    """Schema for canonical Coin entity."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str = Field(..., max_length=20)
    name: str = Field(..., max_length=100)
    slug: str = Field(..., max_length=100)
    created_at: datetime
    updated_at: datetime


class CoinCreate(BaseModel):
    """Schema for creating a new Coin."""

    symbol: str = Field(..., max_length=20)
    name: str = Field(..., max_length=100)
    slug: Optional[str] = Field(None, max_length=100)


class CoinSummary(BaseModel):
    """Lightweight coin reference for API responses."""

    id: int
    symbol: str
    name: str


# =============================================================================
# SOURCE ASSET MAPPING SCHEMAS
# =============================================================================


class SourceAssetMappingSchema(BaseModel):
    """Schema for source-to-coin mappings."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    coin_id: int
    source: DataSource
    source_id: str
    source_symbol: str
    source_name: Optional[str] = None
    created_at: datetime


class SourceAssetMappingCreate(BaseModel):
    """Schema for creating a source mapping."""

    coin_id: int
    source: DataSource
    source_id: str
    source_symbol: str
    source_name: Optional[str] = None


# =============================================================================
# RAW DATA SCHEMAS
# =============================================================================


class RawDataSchema(BaseModel):
    """Schema for raw data records."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    source: DataSource
    payload: dict[str, Any]
    created_at: datetime


# =============================================================================
# UNIFIED CRYPTO DATA SCHEMAS
# =============================================================================


class UnifiedCryptoDataSchema(BaseModel):
    """Schema for normalized crypto data."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    coin_id: Optional[int] = None  # Reference to canonical Coin
    symbol: str = Field(..., max_length=20)
    price_usd: Optional[float] = None
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None
    source: DataSource
    ingested_at: datetime
    timestamp: datetime


class UnifiedCryptoDataCreate(BaseModel):
    """Schema for creating unified crypto data.

    Contains both coin_id (canonical reference) and source metadata.
    The ETL pipeline resolves source data to coin_id via AssetResolver.
    """

    # Canonical coin reference (populated by AssetResolver)
    coin_id: Optional[int] = None

    # Source-specific identifiers (used to resolve coin_id)
    source_id: Optional[str] = None  # e.g., "bitcoin" for CoinGecko
    name: Optional[str] = None  # Asset name e.g., "Bitcoin"

    # Symbol (denormalized for convenience)
    symbol: str = Field(..., max_length=20)

    # Price data
    price_usd: Optional[float] = None
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None

    # Source and timestamp
    source: DataSource
    timestamp: datetime


class UnifiedCryptoDataWithCoin(BaseModel):
    """Unified crypto data with embedded coin info for rich API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str
    price_usd: Optional[float] = None
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None
    source: DataSource
    ingested_at: datetime
    timestamp: datetime
    coin: Optional[CoinSummary] = None


class ETLJobSchema(BaseModel):
    """Schema for ETL job records."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    source: DataSource
    status: ETLStatus
    last_processed_timestamp: Optional[datetime] = None
    records_processed: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""

    items: list[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


class CryptoQueryParams(BaseModel):
    """Query parameters for crypto data endpoints."""

    symbol: Optional[str] = None
    source: Optional[DataSource] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=100)


# ============== Enhanced API Response Schemas ==============


class ResponseMetadata(BaseModel):
    """Metadata included in all API responses."""

    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    total_records: int
    api_latency_ms: float


class DataResponse(BaseModel):
    """Response schema for /data endpoint with metadata."""

    metadata: ResponseMetadata
    data: list[UnifiedCryptoDataSchema]
    pagination: dict[str, int]


class DBHealthStatus(BaseModel):
    """Database health status."""

    connected: bool
    latency_ms: float
    error: Optional[str] = None


class ETLHealthStatus(BaseModel):
    """ETL system health status."""

    last_run_source: Optional[DataSource] = None
    last_run_status: Optional[ETLStatus] = None
    last_run_at: Optional[datetime] = None
    records_processed: Optional[int] = None
    error_message: Optional[str] = None


class HealthResponse(BaseModel):
    """Response schema for /health endpoint."""

    status: str = Field(..., description="Overall system status: healthy, degraded, unhealthy")
    timestamp: datetime = Field(default_factory=lambda: datetime.now())
    database: DBHealthStatus
    etl: ETLHealthStatus
    metadata: Optional[ResponseMetadata] = None


class SymbolStats(BaseModel):
    """Statistics per symbol."""

    symbol: str
    avg_price_usd: Optional[float] = None
    min_price_usd: Optional[float] = None
    max_price_usd: Optional[float] = None
    record_count: int
    sources: list[str]


class ETLStats(BaseModel):
    """ETL job statistics."""

    total_jobs: int
    successful_jobs: int
    failed_jobs: int
    last_success_at: Optional[datetime] = None
    last_failure_at: Optional[datetime] = None
    last_job_duration_seconds: Optional[float] = None
    total_records_processed: int


class StatsResponse(BaseModel):
    """Response schema for /stats endpoint."""

    metadata: ResponseMetadata
    total_records: int
    unique_symbols: int
    sources_active: list[str]
    symbol_stats: list[SymbolStats]
    etl_stats: ETLStats
    data_freshness: Optional[datetime] = Field(
        None, description="Timestamp of most recent data"
    )
