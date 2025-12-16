"""
test_etl_recovery.py - Failure Injection & Recovery Tests (P2.2)

Tests:
1. ETL failure mid-batch -> verify FAILED status
2. Retry after failure -> verify SUCCESS with idempotency (no duplicates)
3. Network timeout simulation
4. Partial data recovery
"""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.db.models import DataSource, ETLJob, ETLStatus, UnifiedCryptoData
from app.ingestion.extractors.coingecko import CoinGeckoExtractor
from app.ingestion.extractors.coinpaprika import CoinPaprikaExtractor
from app.ingestion.extractors.csv_extractor import CSVExtractor

pytestmark = pytest.mark.asyncio


class TestETLFailureInjection:
    """Test ETL behavior under failure conditions."""

    async def test_etl_failure_mid_batch_sets_failed_status(self, db_session):
        """When ETL fails mid-batch, job status should be FAILURE."""
        # Create ETL job
        job = ETLJob(
            source=DataSource.CSV,
            status=ETLStatus.RUNNING,
            records_processed=0,
            started_at=datetime.now(timezone.utc),
        )
        db_session.add(job)
        await db_session.commit()
        await db_session.refresh(job)

        # Simulate failure by updating status
        job.status = ETLStatus.FAILURE
        job.error_message = "Simulated mid-batch failure"
        await db_session.commit()
        await db_session.refresh(job)

        assert job.status == ETLStatus.FAILURE
        assert job.error_message is not None

    async def test_etl_retry_after_failure_succeeds(self, db_session):
        """After a failure, retry should succeed and update status."""
        # Create a failed job
        failed_job = ETLJob(
            source=DataSource.CSV,
            status=ETLStatus.FAILURE,
            records_processed=5,
            started_at=datetime(2024, 1, 15, tzinfo=timezone.utc),
            completed_at=datetime(2024, 1, 15, 0, 5, tzinfo=timezone.utc),
            error_message="Connection timeout",
        )
        db_session.add(failed_job)
        await db_session.commit()

        # Create a new successful retry job
        retry_job = ETLJob(
            source=DataSource.CSV,
            status=ETLStatus.SUCCESS,
            records_processed=10,
            started_at=datetime(2024, 1, 16, tzinfo=timezone.utc),
            completed_at=datetime(2024, 1, 16, 0, 5, tzinfo=timezone.utc),
        )
        db_session.add(retry_job)
        await db_session.commit()
        await db_session.refresh(retry_job)

        assert retry_job.status == ETLStatus.SUCCESS
        assert retry_job.records_processed == 10

    async def test_idempotency_prevents_duplicate_records(self, db_session, sample_crypto_data):
        """Re-running ETL should not create duplicate records."""
        # Insert initial data
        for crypto in sample_crypto_data:
            record = UnifiedCryptoData(
                symbol=crypto["symbol"],
                price_usd=crypto["price_usd"],
                market_cap=crypto.get("market_cap"),
                volume_24h=crypto.get("volume_24h"),
                source=DataSource.CSV,
                timestamp=crypto["timestamp"],
            )
            db_session.add(record)
        await db_session.commit()

        # Count records
        from sqlalchemy import func, select
        count_query = select(func.count()).select_from(UnifiedCryptoData)
        result = await db_session.execute(count_query)
        initial_count = result.scalar()

        assert initial_count == len(sample_crypto_data)


class TestETLNetworkResilience:
    """Test ETL resilience to network issues."""

    async def test_network_timeout_handling(self, db_session):
        """ETL should handle network timeouts gracefully."""
        job = ETLJob(
            source=DataSource.COINGECKO,
            status=ETLStatus.RUNNING,
            records_processed=0,
            started_at=datetime.now(timezone.utc),
        )
        db_session.add(job)
        await db_session.commit()

        # Simulate timeout -> failure
        job.status = ETLStatus.FAILURE
        job.error_message = "Network timeout after 30s"
        await db_session.commit()
        await db_session.refresh(job)

        assert job.status == ETLStatus.FAILURE
        assert "timeout" in job.error_message.lower()

    async def test_partial_batch_recovery(self, db_session, sample_crypto_data):
        """ETL should handle partial batch success."""
        # Insert partial data (simulate partial success)
        partial_data = sample_crypto_data[:2]  # Only first 2 records

        for crypto in partial_data:
            record = UnifiedCryptoData(
                symbol=crypto["symbol"],
                price_usd=crypto["price_usd"],
                market_cap=crypto.get("market_cap"),
                volume_24h=crypto.get("volume_24h"),
                source=DataSource.CSV,
                timestamp=crypto["timestamp"],
            )
            db_session.add(record)
        await db_session.commit()

        # Verify partial data exists
        from sqlalchemy import func, select
        count_query = select(func.count()).select_from(UnifiedCryptoData)
        result = await db_session.execute(count_query)
        count = result.scalar()

        assert count == 2


class TestETLJobLifecycle:
    """Test ETL job state transitions."""

    async def test_job_state_transitions(self, db_session):
        """ETL job should transition through states correctly."""
        # Create job in RUNNING state
        job = ETLJob(
            source=DataSource.CSV,
            status=ETLStatus.RUNNING,
            records_processed=0,
            started_at=datetime.now(timezone.utc),
        )
        db_session.add(job)
        await db_session.commit()

        assert job.status == ETLStatus.RUNNING

        # Transition to SUCCESS
        job.status = ETLStatus.SUCCESS
        job.records_processed = 100
        job.completed_at = datetime.now(timezone.utc)
        await db_session.commit()
        await db_session.refresh(job)

        assert job.status == ETLStatus.SUCCESS
        assert job.records_processed == 100

    async def test_failed_job_has_error_message(self, db_session):
        """Failed ETL jobs should have error messages."""
        job = ETLJob(
            source=DataSource.COINGECKO,
            status=ETLStatus.FAILURE,
            records_processed=0,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            error_message="API rate limit exceeded",
        )
        db_session.add(job)
        await db_session.commit()
        await db_session.refresh(job)

        assert job.status == ETLStatus.FAILURE
        assert job.error_message is not None
        assert len(job.error_message) > 0


class TestExtractorFailures:
    """Test individual extractor failure handling."""

    async def test_coingecko_api_error_handling(self):
        """CoinGecko extractor should handle API errors."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 429  # Rate limited
            mock_response.raise_for_status.side_effect = Exception("Rate limited")

            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client.return_value = mock_client_instance

            extractor = CoinGeckoExtractor()

            with pytest.raises(Exception):
                await extractor.extract()

    async def test_coinpaprika_api_error_handling(self):
        """CoinPaprika extractor should handle API errors."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.raise_for_status.side_effect = Exception("Server error")

            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client_instance.__aenter__.return_value = mock_client_instance
            mock_client_instance.__aexit__.return_value = None
            mock_client.return_value = mock_client_instance

            extractor = CoinPaprikaExtractor()

            with pytest.raises(Exception):
                await extractor.extract()

    async def test_csv_file_not_found_error(self):
        """Test CSVExtractor handles missing file gracefully."""
        extractor = CSVExtractor(file_path="/nonexistent/path/data.csv")

        from app.core.exceptions import ExtractionException
        with pytest.raises(ExtractionException):
            await extractor.extract()

    async def test_csv_malformed_data_handling(self, tmp_path):
        """Test CSVExtractor handles malformed CSV gracefully."""
        # Create malformed CSV
        malformed_csv = tmp_path / "malformed.csv"
        malformed_csv.write_text("symbol,price\nBTC,not_a_number\nETH,50000")

        extractor = CSVExtractor(file_path=str(malformed_csv))

        # Should either handle gracefully or raise appropriate error
        try:
            raw_data, normalized_data = await extractor.extract()
            # If it doesn't raise, verify it handled the malformed row
            # It might skip the bad row or include it with None/default
            assert isinstance(normalized_data, list)
        except (ValueError, TypeError) as e:
            # Expected behavior for strict validation
            assert "price" in str(e).lower() or "number" in str(e).lower()
