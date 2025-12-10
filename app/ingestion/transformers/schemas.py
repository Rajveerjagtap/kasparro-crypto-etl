"""Pydantic schemas for data normalization and validation."""

from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class RawCryptoRecord(BaseModel):
    """Intermediate schema for validating raw crypto data before normalization."""

    symbol: str
    price_usd: Optional[float] = None
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None
    timestamp: datetime

    @field_validator("symbol", mode="before")
    @classmethod
    def normalize_symbol(cls, v: Any) -> str:
        """Standardize symbol to uppercase, strip whitespace."""
        if isinstance(v, str):
            return v.strip().upper()
        return str(v).upper()

    @field_validator("price_usd", "market_cap", "volume_24h", mode="before")
    @classmethod
    def coerce_to_float(cls, v: Any) -> Optional[float]:
        """Convert string/int values to float, handle nulls."""
        if v is None or v == "" or v == "N/A":
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None

    @field_validator("timestamp", mode="before")
    @classmethod
    def normalize_timestamp(cls, v: Any) -> datetime:
        """Convert various timestamp formats to UTC datetime."""
        if isinstance(v, datetime):
            if v.tzinfo is None:
                return v.replace(tzinfo=timezone.utc)
            return v.astimezone(timezone.utc)

        if isinstance(v, str):
            # Handle common ISO formats
            formats = [
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
            ]
            for fmt in formats:
                try:
                    dt = datetime.strptime(v, fmt)
                    return dt.replace(tzinfo=timezone.utc)
                except ValueError:
                    continue

        if isinstance(v, (int, float)):
            # Unix timestamp
            return datetime.fromtimestamp(v, tz=timezone.utc)

        raise ValueError(f"Unable to parse timestamp: {v}")


class CoinPaprikaResponse(BaseModel):
    """Schema for CoinPaprika API response validation."""

    id: str
    name: str
    symbol: str
    rank: Optional[int] = None
    quotes: dict[str, Any] = Field(default_factory=dict)
    last_updated: Optional[str] = None


class CoinGeckoResponse(BaseModel):
    """Schema for CoinGecko API response validation."""

    id: str
    symbol: str
    name: Optional[str] = None
    current_price: Optional[float] = None
    market_cap: Optional[float] = None
    total_volume: Optional[float] = None
    last_updated: Optional[str] = None
