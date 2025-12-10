"""Tests for ETL service."""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.db.models import DataSource, ETLStatus
from app.ingestion.service import ETLService
from app.schemas.crypto import UnifiedCryptoDataCreate


class TestETLService:
    """Test ETL service orchestration."""

    def test_get_extractor_returns_correct_type(self):
        service = ETLService()

        from app.ingestion.extractors.coinpaprika import CoinPaprikaExtractor
        from app.ingestion.extractors.coingecko import CoinGeckoExtractor
        from app.ingestion.extractors.csv_extractor import CSVExtractor

        assert isinstance(service.get_extractor(DataSource.COINPAPRIKA), CoinPaprikaExtractor)
        assert isinstance(service.get_extractor(DataSource.COINGECKO), CoinGeckoExtractor)
        assert isinstance(service.get_extractor(DataSource.CSV), CSVExtractor)

    def test_get_extractor_caches_instance(self):
        service = ETLService()

        ext1 = service.get_extractor(DataSource.CSV)
        ext2 = service.get_extractor(DataSource.CSV)

        assert ext1 is ext2

    def test_get_extractor_invalid_source(self):
        service = ETLService()
        service.EXTRACTORS = {}  # Clear extractors

        with pytest.raises(ValueError, match="No extractor registered"):
            service.get_extractor(DataSource.CSV)
