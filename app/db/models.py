"""SQLAlchemy models for Kasparro.

Implements proper data normalization with:
- Coin: Master entity (canonical asset)
- SourceAssetMapping: Maps source-specific IDs to canonical coins
- UnifiedCryptoData: Price data referencing coin_id (not raw symbol)
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

if TYPE_CHECKING:
    pass


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class DataSource(str, enum.Enum):
    """Enumeration of supported data sources."""

    COINPAPRIKA = "coinpaprika"
    COINGECKO = "coingecko"
    CSV = "csv"


class ETLStatus(str, enum.Enum):
    """ETL job execution status."""

    SUCCESS = "success"
    FAILURE = "failure"
    RUNNING = "running"


# =============================================================================
# MASTER DATA ENTITY - Canonical Asset (Coin)
# =============================================================================


class Coin(Base):
    """
    Master entity representing a canonical cryptocurrency asset.

    This is the system-owned source of truth for asset identity.
    All price data references this entity via coin_id, not raw symbols.

    The slug field provides a unique, URL-safe identifier for the asset.

    Example:
        - id: 1, symbol: "BTC", name: "Bitcoin", slug: "bitcoin"
        - id: 2, symbol: "ETH", name: "Ethereum", slug: "ethereum"
    """

    __tablename__ = "coins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # Index defined in __table_args__
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    source_mappings: Mapped[list["SourceAssetMapping"]] = relationship(
        "SourceAssetMapping",
        back_populates="coin",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    price_data: Mapped[list["UnifiedCryptoData"]] = relationship(
        "UnifiedCryptoData",
        back_populates="coin",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_coins_symbol", "symbol"),
    )

    def __repr__(self) -> str:
        return f"<Coin(id={self.id}, symbol='{self.symbol}', name='{self.name}')>"


# =============================================================================
# SOURCE ASSET MAPPING - Links source-specific IDs to canonical Coin
# =============================================================================


class SourceAssetMapping(Base):
    """
    Maps source-specific asset identifiers to canonical Coin entity.

    This enables:
    - Different sources to use different IDs for the same asset
    - Disambiguation when symbols collide across sources
    - Tracking of source-specific metadata

    Example:
        coin_id=1 (BTC):
        - source=COINGECKO,  source_id="bitcoin",     source_symbol="btc"
        - source=COINPAPRIKA, source_id="btc-bitcoin", source_symbol="BTC"
        - source=CSV,         source_id="BTC",         source_symbol="BTC"
    """

    __tablename__ = "source_asset_mappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign key to canonical Coin
    coin_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("coins.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Source identification
    source: Mapped[DataSource] = mapped_column(
        Enum(
            DataSource,
            name="data_source_enum",
            create_type=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    source_id: Mapped[str] = mapped_column(String(100), nullable=False)
    source_symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    source_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationship back to Coin
    coin: Mapped["Coin"] = relationship("Coin", back_populates="source_mappings")

    __table_args__ = (
        # Unique constraint: one mapping per source+source_id combination
        UniqueConstraint("source", "source_id", name="uq_source_asset_mapping"),
        Index("ix_source_mapping_source_symbol", "source", "source_symbol"),
        Index("ix_source_mapping_coin_id", "coin_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<SourceAssetMapping(coin_id={self.coin_id}, "
            f"source='{self.source.value}', source_id='{self.source_id}')>"
        )


# =============================================================================
# RAW DATA - Audit trail for original payloads
# =============================================================================


class RawData(Base):
    """
    Stores raw JSON blobs from APIs/CSV for auditability.
    Preserves original data before transformation.
    """

    __tablename__ = "raw_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[DataSource] = mapped_column(
        Enum(
            DataSource,
            name="data_source_enum",
            create_type=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_raw_data_source", "source"),
        Index("ix_raw_data_created_at", "created_at"),
    )


# =============================================================================
# UNIFIED CRYPTO DATA - Normalized price data referencing Coin entity
# =============================================================================


class UnifiedCryptoData(Base):
    """
    Normalized cryptocurrency price data from all sources.

    References canonical Coin entity via coin_id for proper normalization.
    Symbol is denormalized for query convenience but coin_id is authoritative.

    Key design decisions:
    - coin_id is the PRIMARY identifier (foreign key to coins table)
    - symbol is denormalized for backward compatibility and query convenience
    - Unique constraint on (coin_id, source, timestamp) prevents duplicates
    """

    __tablename__ = "unified_crypto_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign key to canonical Coin (PRIMARY IDENTIFIER)
    coin_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("coins.id", ondelete="CASCADE"),
        nullable=True,  # Nullable for backward compatibility during migration
        index=True,
    )

    # Denormalized symbol for query convenience (NOT authoritative)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    # Price data
    price_usd: Mapped[Optional[float]] = mapped_column(Numeric(20, 8), nullable=True)
    market_cap: Mapped[Optional[float]] = mapped_column(Numeric(30, 2), nullable=True)
    volume_24h: Mapped[Optional[float]] = mapped_column(Numeric(30, 2), nullable=True)

    # Source tracking
    source: Mapped[DataSource] = mapped_column(
        Enum(
            DataSource,
            name="data_source_enum",
            create_type=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )

    # Timestamps
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Relationship to Coin
    coin: Mapped[Optional["Coin"]] = relationship(
        "Coin",
        back_populates="price_data",
    )

    __table_args__ = (
        # Primary unique constraint using coin_id (proper normalization)
        UniqueConstraint("coin_id", "source", "timestamp", name="uq_coin_source_timestamp"),
        # Legacy constraint for backward compatibility
        UniqueConstraint("symbol", "timestamp", name="uq_symbol_timestamp"),
        Index("ix_unified_coin_source", "coin_id", "source"),
        Index("ix_unified_symbol_source", "symbol", "source"),
        Index("ix_unified_timestamp", "timestamp"),
    )


class ETLJob(Base):
    """
    Tracks ETL job executions for checkpointing and incremental loading.
    """

    __tablename__ = "etl_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[DataSource] = mapped_column(
        Enum(
            DataSource, name="data_source_enum",
            create_type=False, values_callable=lambda x: [e.value for e in x]
        ),
        nullable=False,
    )
    status: Mapped[ETLStatus] = mapped_column(
        Enum(
            ETLStatus, name="etl_status_enum",
            create_type=False, values_callable=lambda x: [e.value for e in x]
        ),
        nullable=False,
    )
    last_processed_timestamp: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    records_processed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    __table_args__ = (
        Index("ix_etl_jobs_source_status", "source", "status"),
    )
