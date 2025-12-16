"""Tests for ETL Scheduler."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.scheduler import ETLScheduler

pytestmark = pytest.mark.asyncio

class TestETLScheduler:
    """Test ETL Scheduler functionality."""

    async def test_run_etl_job_calls_service(self):
        """Verify that run_etl_job calls the ETL service."""
        scheduler = ETLScheduler()

        # Mock etl_service in app.scheduler
        with patch("app.scheduler.etl_service") as mock_service:
            mock_service.run_all_sources = AsyncMock(return_value={})

            await scheduler.run_etl_job()

            mock_service.run_all_sources.assert_called_once_with(parallel=True)

    async def test_scheduler_initialization(self):
        """Test scheduler initialization."""
        with patch.dict("os.environ", {"ETL_INTERVAL_HOURS": "2"}):
            scheduler = ETLScheduler()
            assert scheduler.interval_seconds == 7200
            assert scheduler.scheduler is not None

    async def test_start_adds_job(self):
        """Verify that start adds a cron job."""
        scheduler = ETLScheduler()
        scheduler.scheduler = MagicMock()
        scheduler.run_etl_job = AsyncMock()

        # We mock asyncio.sleep to raise CancelledError to exit the infinite loop in start()
        with patch("asyncio.sleep", side_effect=asyncio.CancelledError):
            try:
                await scheduler.start()
            except asyncio.CancelledError:
                pass

        # Verify add_job was called
        assert scheduler.scheduler.add_job.called
        _, kwargs = scheduler.scheduler.add_job.call_args
        assert kwargs['id'] == 'etl_main_job'

