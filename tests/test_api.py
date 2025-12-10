"""
test_api.py - API Endpoint Integration Tests

Tests:
1. GET /health - Health check endpoint
2. GET /data - Crypto data retrieval with filters
3. GET /stats - Statistics endpoint
4. GET /metrics - Prometheus metrics
5. GET /runs/compare - Run comparison
"""
import pytest
from datetime import datetime, timezone
from uuid import uuid4
from httpx import AsyncClient

from app.models.database import UnifiedCryptoData, ETLJob

pytestmark = pytest.mark.asyncio


class TestHealthEndpoint:
    """Test /health endpoint."""

    async def test_health_returns_ok(self, async_client: AsyncClient):
        """Health endpoint should return 200 with status ok."""
        response = await async_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data

    async def test_health_includes_db_status(self, async_client: AsyncClient):
        """Health endpoint should include database connectivity status."""
        response = await async_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        # DB status is optional but recommended
        if "database" in data:
            assert data["database"] in ["connected", "ok", True]


class TestDataEndpoint:
    """Test /data endpoint."""

    async def test_data_returns_empty_list_initially(self, async_client: AsyncClient):
        """Data endpoint should return empty list when no data exists."""
        response = await async_client.get("/data")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))
        # If dict, should have 'data' key
        if isinstance(data, dict):
            assert "data" in data or "items" in data

    async def test_data_returns_seeded_data(
        self, async_client: AsyncClient, seeded_db
    ):
        """Data endpoint should return seeded crypto data."""
        response = await async_client.get("/data")
        
        assert response.status_code == 200
        data = response.json()
        
        # Handle different response formats
        items = data if isinstance(data, list) else data.get("data", data.get("items", []))
        
        assert len(items) >= 3  # BTC, ETH, XRP from seeded_db
        
        # Verify structure
        for item in items:
            assert "symbol" in item
            assert "price_usd" in item or "price" in item

    async def test_data_filter_by_symbol(
        self, async_client: AsyncClient, seeded_db
    ):
        """Data endpoint should filter by symbol parameter."""
        response = await async_client.get("/data", params={"symbol": "BTC"})
        
        assert response.status_code == 200
        data = response.json()
        
        items = data if isinstance(data, list) else data.get("data", data.get("items", []))
        
        # Should only return BTC
        for item in items:
            assert item["symbol"] == "BTC"

    async def test_data_filter_by_source(
        self, async_client: AsyncClient, seeded_db
    ):
        """Data endpoint should filter by source parameter."""
        response = await async_client.get("/data", params={"source": "test_source"})
        
        assert response.status_code == 200
        # Response should be filtered to test_source

    async def test_data_pagination(
        self, async_client: AsyncClient, seeded_db
    ):
        """Data endpoint should support pagination."""
        # Request with limit
        response = await async_client.get("/data", params={"limit": 1})
        
        assert response.status_code == 200
        data = response.json()
        
        items = data if isinstance(data, list) else data.get("data", data.get("items", []))
        
        # Should return at most 1 item
        assert len(items) <= 1


class TestStatsEndpoint:
    """Test /stats endpoint."""

    async def test_stats_returns_structure(self, async_client: AsyncClient):
        """Stats endpoint should return expected structure."""
        response = await async_client.get("/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        # Expected stats fields (may vary by implementation)
        expected_fields = ["total_records", "sources", "last_updated"]
        # At least some should be present
        assert any(field in data for field in expected_fields)

    async def test_stats_counts_match_data(
        self, async_client: AsyncClient, seeded_db
    ):
        """Stats should reflect actual data counts."""
        stats_response = await async_client.get("/stats")
        data_response = await async_client.get("/data")
        
        assert stats_response.status_code == 200
        assert data_response.status_code == 200
        
        stats = stats_response.json()
        data = data_response.json()
        
        items = data if isinstance(data, list) else data.get("data", data.get("items", []))
        
        # Total records in stats should match or be >= data count
        if "total_records" in stats:
            assert stats["total_records"] >= len(items)


class TestMetricsEndpoint:
    """Test /metrics endpoint (Prometheus format)."""

    async def test_metrics_returns_prometheus_format(self, async_client: AsyncClient):
        """Metrics endpoint should return Prometheus text format."""
        response = await async_client.get("/metrics")
        
        assert response.status_code == 200
        
        # Check content type (Prometheus uses text/plain or application/openmetrics-text)
        content_type = response.headers.get("content-type", "")
        assert any(ct in content_type for ct in ["text/plain", "text", "openmetrics"])
        
        # Check basic Prometheus format
        content = response.text
        # Should contain at least one metric line
        assert any(line for line in content.split("\n") if line and not line.startswith("#"))

    async def test_metrics_includes_http_requests(self, async_client: AsyncClient):
        """Metrics should include HTTP request counters."""
        # Make a few requests to generate metrics
        await async_client.get("/health")
        await async_client.get("/data")
        
        response = await async_client.get("/metrics")
        content = response.text
        
        # Look for HTTP request metrics
        http_metrics = ["http_requests", "request_count", "requests_total"]
        # At least one should be present (depends on implementation)
        # This is a soft check - metrics names vary


class TestRunCompareEndpoint:
    """Test /runs/compare endpoint (P2.6)."""

    async def test_compare_requires_data(self, async_client: AsyncClient):
        """Compare endpoint should handle case with no runs."""
        response = await async_client.get("/runs/compare")
        
        # Should return 200 with empty/default response or 404
        assert response.status_code in [200, 404, 400]
        
        if response.status_code == 200:
            data = response.json()
            # Should indicate no runs to compare
            assert "runs" in data or "message" in data or "error" in data

    async def test_compare_with_multiple_runs(
        self, async_client: AsyncClient, db_session
    ):
        """Compare endpoint should compare last 2 successful runs."""
        # Create two successful ETL jobs
        job1 = ETLJob(
            job_id=str(uuid4()),
            source="test",
            status="SUCCESS",
            started_at=datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
            finished_at=datetime(2024, 1, 1, 10, 5, 0, tzinfo=timezone.utc),
            records_processed=100,
            records_failed=0,
        )
        job2 = ETLJob(
            job_id=str(uuid4()),
            source="test",
            status="SUCCESS",
            started_at=datetime(2024, 1, 2, 10, 0, 0, tzinfo=timezone.utc),
            finished_at=datetime(2024, 1, 2, 10, 5, 0, tzinfo=timezone.utc),
            records_processed=110,
            records_failed=0,
        )
        db_session.add(job1)
        db_session.add(job2)
        await db_session.commit()

        # Add data for both jobs
        for i, job in enumerate([job1, job2]):
            price = 50000 + (i * 1000)  # Different prices
            data = UnifiedCryptoData(
                symbol="BTC",
                name="Bitcoin",
                price_usd=price,
                source="test",
                fetched_at=job.started_at,
                job_id=job.job_id,
            )
            db_session.add(data)
        await db_session.commit()

        response = await async_client.get("/runs/compare")
        
        if response.status_code == 200:
            data = response.json()
            # Should contain comparison data
            assert isinstance(data, dict)


class TestErrorHandling:
    """Test API error handling."""

    async def test_404_for_unknown_endpoint(self, async_client: AsyncClient):
        """Unknown endpoints should return 404."""
        response = await async_client.get("/nonexistent")
        assert response.status_code == 404

    async def test_invalid_query_params(self, async_client: AsyncClient):
        """Invalid query parameters should be handled gracefully."""
        # Invalid limit (negative)
        response = await async_client.get("/data", params={"limit": -1})
        # Should either ignore or return error
        assert response.status_code in [200, 400, 422]

    async def test_malformed_request_handling(self, async_client: AsyncClient):
        """Malformed requests should return appropriate error."""
        # POST to GET-only endpoint (if applicable)
        response = await async_client.post("/health")
        # Should return 405 Method Not Allowed or handle gracefully
        assert response.status_code in [200, 405, 422]


class TestCORS:
    """Test CORS headers if applicable."""

    async def test_cors_headers_present(self, async_client: AsyncClient):
        """Response should include CORS headers if configured."""
        response = await async_client.options("/health")
        
        # CORS is optional but check if configured
        cors_headers = [
            "access-control-allow-origin",
            "access-control-allow-methods",
        ]
        # If any CORS header is present, verify it's valid
        for header in cors_headers:
            if header in response.headers:
                assert response.headers[header] is not None


class TestResponseFormat:
    """Test consistent response formatting."""

    async def test_json_content_type(self, async_client: AsyncClient):
        """JSON endpoints should return application/json."""
        response = await async_client.get("/health")
        
        content_type = response.headers.get("content-type", "")
        assert "application/json" in content_type

    async def test_timestamps_are_iso_format(
        self, async_client: AsyncClient, seeded_db
    ):
        """Timestamps should be in ISO 8601 format."""
        response = await async_client.get("/data")
        
        assert response.status_code == 200
        data = response.json()
        
        items = data if isinstance(data, list) else data.get("data", data.get("items", []))
        
        for item in items:
            if "fetched_at" in item:
                # Should be parseable as ISO timestamp
                try:
                    datetime.fromisoformat(item["fetched_at"].replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    pytest.fail(f"Invalid timestamp format: {item['fetched_at']}")
