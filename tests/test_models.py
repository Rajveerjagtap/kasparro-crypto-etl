"""Tests for database models."""

import pytest
from datetime import datetime, timezone

from app.db.models import (
    Base,
    DataSource,
    ETLJob,
    ETLStatus,
    RawData,
    UnifiedCryptoData,
)


class TestDataSourceEnum:
    """Test DataSource enumeration."""

    def test_datasource_values(self):
        assert DataSource.COINPAPRIKA.value == "coinpaprika"
        assert DataSource.COINGECKO.value == "coingecko"
        assert DataSource.CSV.value == "csv"


class TestETLStatusEnum:
    """Test ETLStatus enumeration."""

    def test_etlstatus_values(self):
        assert ETLStatus.SUCCESS.value == "success"
        assert ETLStatus.FAILURE.value == "failure"
        assert ETLStatus.RUNNING.value == "running"


class TestRawDataModel:
    """Test RawData model structure."""

    def test_tablename(self):
        assert RawData.__tablename__ == "raw_data"

    def test_columns_exist(self):
        columns = {c.name for c in RawData.__table__.columns}
        expected = {"id", "source", "payload", "created_at"}
        assert expected == columns


class TestUnifiedCryptoDataModel:
    """Test UnifiedCryptoData model structure."""

    def test_tablename(self):
        assert UnifiedCryptoData.__tablename__ == "unified_crypto_data"

    def test_columns_exist(self):
        columns = {c.name for c in UnifiedCryptoData.__table__.columns}
        expected = {
            "id", "symbol", "price_usd", "market_cap",
            "volume_24h", "source", "ingested_at", "timestamp"
        }
        assert expected == columns


class TestETLJobModel:
    """Test ETLJob model structure."""

    def test_tablename(self):
        assert ETLJob.__tablename__ == "etl_jobs"

    def test_columns_exist(self):
        columns = {c.name for c in ETLJob.__table__.columns}
        expected = {
            "id", "source", "status", "last_processed_timestamp",
            "records_processed", "started_at", "completed_at", "error_message"
        }
        assert expected == columns
