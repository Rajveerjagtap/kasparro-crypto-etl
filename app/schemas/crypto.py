"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.db.models import DataSource, ETLStatus


class RawDataSchema(BaseModel):
    """Schema for raw data records."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    source: DataSource
    payload: dict[str, Any]
    created_at: datetime


class UnifiedCryptoDataSchema(BaseModel):
    """Schema for normalized crypto data."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str = Field(..., max_length=20)
    price_usd: Optional[float] = None
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None
    source: DataSource
    ingested_at: datetime
    timestamp: datetime


class UnifiedCryptoDataCreate(BaseModel):
    """Schema for creating unified crypto data."""

    symbol: str = Field(..., max_length=20)
    price_usd: Optional[float] = None
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None
    source: DataSource
    timestamp: datetime


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
