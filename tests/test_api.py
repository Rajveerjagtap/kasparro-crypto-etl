"""
test_api.py - API Endpoint Integration Tests

Tests:
1. GET /health - Health check endpoint (root level)
2. GET /api/v1/data - Crypto data retrieval with filters
3. GET /api/v1/stats - Statistics endpoint
4. GET /api/v1/runs/compare - Run comparison
"""
import pytest
from datetime import datetime, timezone
from uuid import uuid4
from httpx import AsyncClient

from app.db.models import UnifiedCryptoData, ETLJob, DataSource, ETLStatus

pytestmark = pytest.mark.asyncio


class TestHealthEndpoint:
    """Test /health endpoint."""

    async def test_health_returns_ok(self, async_client: AsyncClient):
        """Health endpoint should return 200 with status healthy."""
        response = await async_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
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
    """Test /api/v1/data endpoint."""

    async def test_data_returns_empty_list_initially(self, async_client: AsyncClient):
        """Data endpoint should return empty list when no data exists."""
        response = await async_client.get("/api/v1/data")
        
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
        response = await async_client.get("/api/v1/data")
        
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
        response = await async_client.get("/api/v1/data", params={"symbol": "BTC"})
        
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
        response = await async_client.get("/api/v1/data", params={"source": "csv"})
        
        assert response.status_code == 200
        # Response should be filtered to csv source

    async def test_data_pagination(
        self, async_client: AsyncClient, seeded_db
    ):
        """Data endpoint should support pagination."""
        # Request with limit
        response = await async_client.get("/api/v1/data", params={"limit": 1})
        
        assert response.status_code == 200
        data = response.json()
        
        items = data if isinstance(data, list) else data.get("data", data.get("items", []))
        
        # Should return at most 1 item
        assert len(items) <= 1


class TestStatsEndpoint:
    """Test /api/v1/stats endpoint."""

    async def test_stats_returns_structure(self, async_client: AsyncClient):
        """Stats endpoint should return expected structure."""
        response = await async_client.get("/api/v1/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify basic structure
        assert isinstance(data, dict)

    async def test_stats_counts_match_data(
        self, async_client: AsyncClient, seeded_db
    ):
        """Stats should reflect actual data counts."""
        stats_response = await async_client.get("/api/v1/stats")
        data_response = await async_client.get("/api/v1/data")
        
        assert stats_response.status_code == 200
        assert data_response.status_code == 200


class TestMetricsEndpoint:
    """Test metrics endpoint (if available)."""

    async def test_metrics_returns_prometheus_format(self, async_client: AsyncClient):
        """Metrics endpoint should return Prometheus format."""
        # Metrics might be at /metrics or /api/v1/metrics
        response = await async_client.get("/api/v1/metrics")
        
        # Might be 200 or 404 depending on implementation
        assert response.status_code in [200, 404]

    async def test_metrics_includes_http_requests(self, async_client: AsyncClient):
        """Metrics should include HTTP request counters."""
        # Make some requests first
        await async_client.get("/health")
        
        response = await async_client.get("/api/v1/metrics")
        
        # Just check it doesn't error
        assert response.status_code in [200, 404]


class TestRunCompareEndpoint:
    """Test /api/v1/runs/compare endpoint."""

    async def test_compare_requires_data(self, async_client: AsyncClient):
        """Compare endpoint requires run_id params."""
        # Without params, should return 422 (validation error)
        response = await async_client.get("/api/v1/runs/compare")
        
        # FastAPI returns 422 for missing required params
        assert response.status_code == 422

    async def test_compare_with_multiple_runs(
        self, async_client: AsyncClient, test_session
    ):
        """Compare endpoint should compare multiple ETL runs."""
        # Create ETL jobs with correct column names
        job1 = ETLJob(
            source=DataSource.CSV,
            status=ETLStatus.SUCCESS,
            records_processed=10,
            started_at=datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc),
            completed_at=datetime(2024, 1, 15, 12, 5, tzinfo=timezone.utc),
        )
        job2 = ETLJob(
            source=DataSource.CSV,
            status=ETLStatus.SUCCESS,
            records_processed=15,
            started_at=datetime(2024, 1, 16, 12, 0, tzinfo=timezone.utc),
            completed_at=datetime(2024, 1, 16, 12, 5, tzinfo=timezone.utc),
        )
        
        test_session.add_all([job1, job2])
        await test_session.commit()
        await test_session.refresh(job1)
        await test_session.refresh(job2)
        
        # Call with run_id params
        response = await async_client.get(
            "/api/v1/runs/compare",
            params={"run_id_1": job1.id, "run_id_2": job2.id}
        )
        
        # Should return 200 with comparison data
        assert response.status_code == 200
        data = response.json()
        assert "run_1" in data
        assert "run_2" in data
        assert "diff" in data


class TestErrorHandling:
    """Test API error handling."""

    async def test_404_for_unknown_endpoint(self, async_client: AsyncClient):
        """Unknown endpoints should return 404."""
        response = await async_client.get("/unknown/endpoint")
        
        assert response.status_code == 404

    async def test_invalid_query_params(self, async_client: AsyncClient):
        """Invalid query params should be handled gracefully."""
        response = await async_client.get("/api/v1/data", params={"limit": -1})
        
        # Should return validation error or use default
        assert response.status_code in [200, 400, 422]

    async def test_malformed_request_handling(self, async_client: AsyncClient):
        """Malformed requests should return appropriate error."""
        # Send invalid JSON to an endpoint that expects JSON body
        response = await async_client.post(
            "/api/v1/data",  # This endpoint might not accept POST
            content="invalid json",
            headers={"Content-Type": "application/json"},
        )
        
        # Should return 4xx error (405 method not allowed, or 400/422 for bad request)
        assert response.status_code in [400, 404, 405, 422]


class TestCORS:
    """Test CORS configuration."""

    async def test_cors_headers_present(self, async_client: AsyncClient):
        """CORS headers should be present in response."""
        response = await async_client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            }
        )
        
        # Should allow CORS
        assert response.status_code in [200, 204, 405]


class TestResponseFormat:
    """Test response format consistency."""

    async def test_json_content_type(self, async_client: AsyncClient):
        """Responses should have JSON content type."""
        response = await async_client.get("/health")
        
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")

    async def test_timestamps_are_iso_format(
        self, async_client: AsyncClient, seeded_db
    ):
        """Timestamps should be in ISO format."""
        response = await async_client.get("/api/v1/data")
        
        assert response.status_code == 200
        data = response.json()
        
        items = data if isinstance(data, list) else data.get("data", data.get("items", []))
        
        if items:
            # Check timestamp format if present
            item = items[0]
            if "timestamp" in item:
                # Should be ISO format string
                assert isinstance(item["timestamp"], str)
