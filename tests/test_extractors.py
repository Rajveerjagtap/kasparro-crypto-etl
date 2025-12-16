"""Tests for ETL extractors."""

from datetime import datetime, timezone

from app.db.models import DataSource
from app.ingestion.extractors.coingecko import CoinGeckoExtractor
from app.ingestion.extractors.coinpaprika import CoinPaprikaExtractor
from app.ingestion.extractors.csv_extractor import CSVExtractor
from app.ingestion.transformers.schemas import RawCryptoRecord


class TestRawCryptoRecord:
    """Test data normalization validators."""

    def test_symbol_normalization(self):
        record = RawCryptoRecord(
            symbol="  btc  ",
            timestamp=datetime.now(timezone.utc),
        )
        assert record.symbol == "BTC"

    def test_price_coercion_from_string(self):
        record = RawCryptoRecord(
            symbol="ETH",
            price_usd="1234.56",
            timestamp=datetime.now(timezone.utc),
        )
        assert record.price_usd == 1234.56

    def test_price_coercion_null_values(self):
        record = RawCryptoRecord(
            symbol="ETH",
            price_usd="N/A",
            volume_24h="",
            timestamp=datetime.now(timezone.utc),
        )
        assert record.price_usd is None
        assert record.volume_24h is None

    def test_timestamp_from_iso_string(self):
        record = RawCryptoRecord(
            symbol="BTC",
            timestamp="2024-01-15T10:30:00Z",
        )
        assert record.timestamp.year == 2024
        assert record.timestamp.month == 1
        assert record.timestamp.tzinfo == timezone.utc

    def test_timestamp_from_unix(self):
        record = RawCryptoRecord(
            symbol="BTC",
            timestamp=1705315800,  # 2024-01-15 10:30:00 UTC
        )
        assert record.timestamp.year == 2024


class TestCoinPaprikaExtractor:
    """Test CoinPaprika extractor normalization."""

    def test_normalize_valid_data(self):
        extractor = CoinPaprikaExtractor()
        raw_data = [
            {
                "id": "btc-bitcoin",
                "name": "Bitcoin",
                "symbol": "BTC",
                "rank": 1,
                "quotes": {
                    "USD": {
                        "price": 45000.50,
                        "market_cap": 850000000000,
                        "volume_24h": 25000000000,
                    }
                },
                "last_updated": "2024-01-15T10:30:00Z",
            }
        ]

        normalized = extractor.normalize(raw_data)

        assert len(normalized) == 1
        assert normalized[0].symbol == "BTC"
        assert normalized[0].price_usd == 45000.50
        assert normalized[0].source == DataSource.COINPAPRIKA

    def test_normalize_missing_quotes(self):
        extractor = CoinPaprikaExtractor()
        raw_data = [
            {
                "id": "unknown-coin",
                "name": "Unknown",
                "symbol": "UNK",
                "quotes": {},
                "last_updated": "2024-01-15T10:30:00Z",
            }
        ]

        normalized = extractor.normalize(raw_data)
        assert len(normalized) == 1
        assert normalized[0].price_usd is None


class TestCoinGeckoExtractor:
    """Test CoinGecko extractor normalization."""

    def test_normalize_valid_data(self):
        extractor = CoinGeckoExtractor()
        raw_data = [
            {
                "id": "bitcoin",
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": 45000.50,
                "market_cap": 850000000000,
                "total_volume": 25000000000,
                "last_updated": "2024-01-15T10:30:00.000Z",
            }
        ]

        normalized = extractor.normalize(raw_data)

        assert len(normalized) == 1
        assert normalized[0].symbol == "BTC"
        assert normalized[0].price_usd == 45000.50
        assert normalized[0].source == DataSource.COINGECKO


class TestCSVExtractor:
    """Test CSV extractor."""

    def test_normalize_valid_data(self):
        extractor = CSVExtractor()
        raw_data = [
            {
                "symbol": "btc",
                "price_usd": "45000.50",
                "volume_24h": "25000000000",
                "timestamp": "2024-01-15",
            }
        ]

        normalized = extractor.normalize(raw_data)

        assert len(normalized) == 1
        assert normalized[0].symbol == "BTC"
        assert normalized[0].price_usd == 45000.50
        assert normalized[0].source == DataSource.CSV

    def test_normalize_with_column_mapping(self):
        extractor = CSVExtractor()
        raw_data = [
            {
                "ticker": "eth",
                "price": "2500.00",
                "vol": "10000000000",
                "date": "2024-01-15",
            }
        ]

        normalized = extractor.normalize(raw_data)

        assert len(normalized) == 1
        assert normalized[0].symbol == "ETH"
        assert normalized[0].price_usd == 2500.00
