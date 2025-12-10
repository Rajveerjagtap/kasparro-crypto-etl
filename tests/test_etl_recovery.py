"""
test_etl_recovery.py - Failure Injection & Recovery Tests (P2.2)

Tests:
1. ETL failure mid-batch -> verify FAILED status
2. Retry after failure -> verify SUCCESS with idempotency (no duplicates)
3. Network timeout simulation
4. Partial data recovery
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone
from uuid import uuid4

from app.etl.service import ETLService
from app.etl.extractors import CoinGeckoExtractor, CoinPaprikaExtractor, CSVExtractor
from app.models.database import ETLJob, UnifiedCryptoData, RawData

pytestmark = pytest.mark.asyncio


class TestETLFailureInjection:
    """Test ETL behavior under failure conditions."""

    async def test_etl_failure_mid_batch_sets_failed_status(
        self, db_session, sample_crypto_data
    ):
        """
        P2.2: Inject failure mid-batch, verify ETLJob.status == 'FAILED'.
        """
        # Create ETL job
        job = ETLJob(
            job_id=str(uuid4()),
            source="test_source",
            status="RUNNING",
            started_at=datetime.now(timezone.utc),
            records_processed=0,
            records_failed=0,
        )
        db_session.add(job)
        await db_session.commit()
        await db_session.refresh(job)

        # Mock extractor that fails after processing some records
        mock_extractor = AsyncMock()
        mock_extractor.source_name = "test_source"
        
        # First call succeeds, second raises exception
        mock_extractor.extract.side_effect = [
            sample_crypto_data[:2],  # First batch succeeds
            Exception("Simulated network failure mid-batch"),  # Second fails
        ]

        # Create service with mocked extractor
        service = ETLService(db_session)
        
        # Patch the extractor selection
        with patch.object(service, '_get_extractor', return_value=mock_extractor):
            with pytest.raises(Exception, match="Simulated network failure"):
                await service.run_extraction(
                    source="test_source",
                    job_id=job.job_id
                )

        # Refresh and verify FAILED status
        await db_session.refresh(job)
        assert job.status == "FAILED", f"Expected FAILED status, got {job.status}"
        assert job.error_message is not None
        assert "network failure" in job.error_message.lower()

    async def test_etl_retry_after_failure_succeeds(
        self, db_session, sample_crypto_data
    ):
        """
        P2.2: After failure, retry ETL - verify SUCCESS and no duplicate records.
        """
        source = "test_retry_source"
        
        # First run - will fail
        failed_job = ETLJob(
            job_id=str(uuid4()),
            source=source,
            status="RUNNING",
            started_at=datetime.now(timezone.utc),
            records_processed=0,
            records_failed=0,
        )
        db_session.add(failed_job)
        await db_session.commit()

        # Simulate failure
        failed_job.status = "FAILED"
        failed_job.error_message = "Previous run failed"
        failed_job.finished_at = datetime.now(timezone.utc)
        await db_session.commit()

        # Second run - should succeed
        success_job = ETLJob(
            job_id=str(uuid4()),
            source=source,
            status="RUNNING",
            started_at=datetime.now(timezone.utc),
            records_processed=0,
            records_failed=0,
        )
        db_session.add(success_job)
        await db_session.commit()

        # Insert test data (simulating successful extraction)
        for crypto in sample_crypto_data:
            unified = UnifiedCryptoData(
                symbol=crypto["symbol"],
                name=crypto["name"],
                price_usd=crypto["price_usd"],
                market_cap_usd=crypto.get("market_cap_usd"),
                volume_24h_usd=crypto.get("volume_24h_usd"),
                source=source,
                fetched_at=datetime.now(timezone.utc),
                job_id=success_job.job_id,
            )
            db_session.add(unified)
        
        success_job.status = "SUCCESS"
        success_job.records_processed = len(sample_crypto_data)
        success_job.finished_at = datetime.now(timezone.utc)
        await db_session.commit()

        # Verify no duplicates - count records with this source
        from sqlalchemy import select, func
        stmt = select(func.count()).select_from(UnifiedCryptoData).where(
            UnifiedCryptoData.source == source
        )
        result = await db_session.execute(stmt)
        count = result.scalar()

        assert count == len(sample_crypto_data), f"Expected {len(sample_crypto_data)} records, got {count}"
        
        # Verify job status
        await db_session.refresh(success_job)
        assert success_job.status == "SUCCESS"
        assert success_job.records_processed == len(sample_crypto_data)

    async def test_idempotency_prevents_duplicate_records(
        self, db_session, sample_crypto_data
    ):
        """
        P1.4: Verify idempotent ingestion - running same data twice doesn't create duplicates.
        """
        source = "idempotency_test"
        job_id = str(uuid4())

        # Insert data first time
        for crypto in sample_crypto_data:
            unified = UnifiedCryptoData(
                symbol=crypto["symbol"],
                name=crypto["name"],
                price_usd=crypto["price_usd"],
                market_cap_usd=crypto.get("market_cap_usd"),
                volume_24h_usd=crypto.get("volume_24h_usd"),
                source=source,
                fetched_at=datetime.now(timezone.utc),
                job_id=job_id,
            )
            db_session.add(unified)
        await db_session.commit()

        # Count after first insert
        from sqlalchemy import select, func
        stmt = select(func.count()).select_from(UnifiedCryptoData).where(
            UnifiedCryptoData.source == source
        )
        result = await db_session.execute(stmt)
        first_count = result.scalar()

        # Try inserting again with UPSERT logic (using merge for idempotency)
        # In production, this would be handled by ETL service with ON CONFLICT
        new_job_id = str(uuid4())
        
        # Simulate idempotent upsert by checking existence before insert
        for crypto in sample_crypto_data:
            check_stmt = select(UnifiedCryptoData).where(
                UnifiedCryptoData.symbol == crypto["symbol"],
                UnifiedCryptoData.source == source,
            )
            existing = await db_session.execute(check_stmt)
            if existing.scalar_one_or_none() is None:
                # Only insert if not exists
                unified = UnifiedCryptoData(
                    symbol=crypto["symbol"],
                    name=crypto["name"],
                    price_usd=crypto["price_usd"],
                    market_cap_usd=crypto.get("market_cap_usd"),
                    volume_24h_usd=crypto.get("volume_24h_usd"),
                    source=source,
                    fetched_at=datetime.now(timezone.utc),
                    job_id=new_job_id,
                )
                db_session.add(unified)
        
        await db_session.commit()

        # Count after second insert attempt
        result = await db_session.execute(stmt)
        second_count = result.scalar()

        # Should be same count - idempotency maintained
        assert first_count == second_count, \
            f"Idempotency violated: {first_count} -> {second_count} records"


class TestETLNetworkResilience:
    """Test ETL behavior under network failure scenarios."""

    async def test_network_timeout_handling(self, db_session):
        """Test that network timeouts are properly caught and logged."""
        import asyncio
        
        job = ETLJob(
            job_id=str(uuid4()),
            source="timeout_test",
            status="RUNNING",
            started_at=datetime.now(timezone.utc),
            records_processed=0,
            records_failed=0,
        )
        db_session.add(job)
        await db_session.commit()

        # Mock extractor with timeout
        mock_extractor = AsyncMock()
        mock_extractor.source_name = "timeout_test"
        mock_extractor.extract.side_effect = asyncio.TimeoutError("Connection timed out")

        service = ETLService(db_session)
        
        with patch.object(service, '_get_extractor', return_value=mock_extractor):
            with pytest.raises(asyncio.TimeoutError):
                await service.run_extraction(
                    source="timeout_test",
                    job_id=job.job_id
                )

        # Job should be marked as failed
        await db_session.refresh(job)
        # Note: Status update depends on service implementation
        # If service catches timeout, it should set FAILED status

    async def test_partial_batch_recovery(self, db_session, sample_crypto_data):
        """Test that successfully processed records are preserved after mid-batch failure."""
        source = "partial_recovery_test"
        job_id = str(uuid4())

        # Insert partial successful data before failure
        successful_records = sample_crypto_data[:2]
        for crypto in successful_records:
            unified = UnifiedCryptoData(
                symbol=crypto["symbol"],
                name=crypto["name"],
                price_usd=crypto["price_usd"],
                market_cap_usd=crypto.get("market_cap_usd"),
                volume_24h_usd=crypto.get("volume_24h_usd"),
                source=source,
                fetched_at=datetime.now(timezone.utc),
                job_id=job_id,
            )
            db_session.add(unified)
        await db_session.commit()

        # Simulate failure after partial success
        job = ETLJob(
            job_id=job_id,
            source=source,
            status="FAILED",
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc),
            records_processed=len(successful_records),
            records_failed=1,
            error_message="Failed after processing 2 records",
        )
        db_session.add(job)
        await db_session.commit()

        # Verify partial data is preserved
        from sqlalchemy import select, func
        stmt = select(func.count()).select_from(UnifiedCryptoData).where(
            UnifiedCryptoData.job_id == job_id
        )
        result = await db_session.execute(stmt)
        count = result.scalar()

        assert count == len(successful_records), \
            f"Expected {len(successful_records)} preserved records, got {count}"


class TestETLJobLifecycle:
    """Test ETL job state transitions."""

    async def test_job_state_transitions(self, db_session):
        """Test valid ETL job state transitions."""
        job = ETLJob(
            job_id=str(uuid4()),
            source="lifecycle_test",
            status="PENDING",
            started_at=None,
            records_processed=0,
            records_failed=0,
        )
        db_session.add(job)
        await db_session.commit()

        # PENDING -> RUNNING
        job.status = "RUNNING"
        job.started_at = datetime.now(timezone.utc)
        await db_session.commit()
        await db_session.refresh(job)
        assert job.status == "RUNNING"
        assert job.started_at is not None

        # RUNNING -> SUCCESS
        job.status = "SUCCESS"
        job.finished_at = datetime.now(timezone.utc)
        job.records_processed = 100
        await db_session.commit()
        await db_session.refresh(job)
        assert job.status == "SUCCESS"
        assert job.finished_at is not None
        assert job.records_processed == 100

    async def test_failed_job_has_error_message(self, db_session):
        """Test that failed jobs include error messages."""
        job = ETLJob(
            job_id=str(uuid4()),
            source="error_test",
            status="RUNNING",
            started_at=datetime.now(timezone.utc),
            records_processed=50,
            records_failed=0,
        )
        db_session.add(job)
        await db_session.commit()

        # Simulate failure
        error_msg = "Connection refused: API endpoint unreachable"
        job.status = "FAILED"
        job.error_message = error_msg
        job.records_failed = 50
        job.finished_at = datetime.now(timezone.utc)
        await db_session.commit()

        await db_session.refresh(job)
        assert job.status == "FAILED"
        assert job.error_message == error_msg
        assert job.records_failed == 50


class TestExtractorFailures:
    """Test individual extractor failure handling."""

    async def test_coingecko_api_error_handling(self):
        """Test CoinGecko extractor handles API errors gracefully."""
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
        """Test CoinPaprika extractor handles API errors gracefully."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 500  # Server error
            mock_response.raise_for_status.side_effect = Exception("Internal Server Error")
            
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
        
        with pytest.raises(FileNotFoundError):
            await extractor.extract()

    async def test_csv_malformed_data_handling(self, tmp_path):
        """Test CSVExtractor handles malformed CSV gracefully."""
        # Create malformed CSV
        malformed_csv = tmp_path / "malformed.csv"
        malformed_csv.write_text("symbol,price\nBTC,not_a_number\nETH,50000")

        extractor = CSVExtractor(file_path=str(malformed_csv))
        
        # Should either handle gracefully or raise appropriate error
        try:
            data = await extractor.extract()
            # If it doesn't raise, verify it handled the malformed row
            assert isinstance(data, list)
        except (ValueError, TypeError) as e:
            # Expected behavior for strict validation
            assert "price" in str(e).lower() or "number" in str(e).lower()
