"""SQLAlchemy models for Kasparro."""

import enum
from datetime import datetime
from typing import Any

from sqlalchemy import (
    DateTime,
    Enum,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.types import JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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


class RawData(Base):
    """
    Stores raw JSON blobs from APIs/CSV for auditability.
    Preserves original data before transformation.
    """

    __tablename__ = "raw_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[DataSource] = mapped_column(
        Enum(DataSource, name="data_source_enum", create_type=False, values_callable=lambda x: [e.value for e in x]),
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


class UnifiedCryptoData(Base):
    """
    Normalized cryptocurrency data from all sources.
    Single schema for unified querying.
    """

    __tablename__ = "unified_crypto_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    price_usd: Mapped[float] = mapped_column(Numeric(20, 8), nullable=True)
    market_cap: Mapped[float] = mapped_column(Numeric(30, 2), nullable=True)
    volume_24h: Mapped[float] = mapped_column(Numeric(30, 2), nullable=True)
    source: Mapped[DataSource] = mapped_column(
        Enum(DataSource, name="data_source_enum", create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("symbol", "timestamp", name="uq_symbol_timestamp"),
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
        Enum(DataSource, name="data_source_enum", create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    status: Mapped[ETLStatus] = mapped_column(
        Enum(ETLStatus, name="etl_status_enum", create_type=False, values_callable=lambda x: [e.value for e in x]),
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
