"""Pytest fixtures and configuration for comprehensive testing."""

import asyncio
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.db.models import Base, Coin, DataSource, UnifiedCryptoData
from app.db.session import get_db
from app.main import app

# ============== Pytest Configuration ==============


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def anyio_backend():
    """Use asyncio backend for pytest-asyncio."""
    return "asyncio"


# ============== Database URL Selection ==============


def get_test_database_url() -> str:
    """
    Get test database URL.
    Prefers PostgreSQL from environment (for CI parity), falls back to SQLite for local.
    """
    # Check for CI/integration test PostgreSQL
    pg_url = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    if pg_url:
        # Ensure it's async-compatible
        if pg_url.startswith("postgresql://"):
            pg_url = pg_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return pg_url

    # Fallback to SQLite for fast local unit tests
    return "sqlite+aiosqlite:///:memory:"


# ============== Database Fixtures ==============


@pytest_asyncio.fixture
async def test_engine():
    """Create test database engine - uses PostgreSQL in CI, SQLite locally."""
    db_url = get_test_database_url()

    # Configure engine based on database type
    if "sqlite" in db_url:
        engine = create_async_engine(
            db_url,
            echo=False,
            future=True,
        )
    else:
        # PostgreSQL settings for CI parity
        engine = create_async_engine(
            db_url,
            echo=False,
            future=True,
            pool_size=5,
            max_overflow=10,
        )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session with transaction rollback."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async with async_session() as session:
        yield session
        # Rollback any uncommitted changes
        await session.rollback()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a database session for testing with automatic cleanup.
    Alias for test_session for compatibility.
    """
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()


# ============== FastAPI Test Client Fixtures ==============


@pytest_asyncio.fixture
async def async_client(test_engine) -> AsyncGenerator[AsyncClient, None]:
    """
    Create async HTTP client for testing FastAPI endpoints.
    Overrides the database dependency to use test database.
    """
    # Create session factory for test database
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    # Override the get_db dependency
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    # Create async client
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # Clear dependency overrides
    app.dependency_overrides.clear()


@pytest.fixture
def sync_client(test_engine) -> TestClient:
    """Create synchronous test client for simple endpoint tests."""
    return TestClient(app)


# ============== Mock Data Fixtures ==============


@pytest.fixture
def sample_crypto_data() -> list[dict]:
    """Sample cryptocurrency data for testing."""
    return [
        {
            "symbol": "BTC",
            "price_usd": 45000.50,
            "market_cap": 850000000000,
            "volume_24h": 25000000000,
            "timestamp": datetime(2024, 1, 15, tzinfo=timezone.utc),
        },
        {
            "symbol": "ETH",
            "price_usd": 2500.00,
            "market_cap": 300000000000,
            "volume_24h": 15000000000,
            "timestamp": datetime(2024, 1, 15, tzinfo=timezone.utc),
        },
        {
            "symbol": "XRP",
            "price_usd": 0.55,
            "market_cap": 28000000000,
            "volume_24h": 5000000000,
            "timestamp": datetime(2024, 1, 15, tzinfo=timezone.utc),
        },
    ]


@pytest.fixture
def coingecko_api_response() -> list[dict]:
    """Mock CoinGecko API response for testing."""
    return [
        {
            "id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "current_price": 45000.50,
            "market_cap": 850000000000,
            "total_volume": 25000000000,
            "last_updated": "2024-01-15T12:00:00.000Z",
        },
        {
            "id": "ethereum",
            "symbol": "eth",
            "name": "Ethereum",
            "current_price": 2500.00,
            "market_cap": 300000000000,
            "total_volume": 15000000000,
            "last_updated": "2024-01-15T12:00:00.000Z",
        },
    ]


@pytest.fixture
def coinpaprika_api_response() -> list[dict]:
    """Mock CoinPaprika API response for testing."""
    return [
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
            "last_updated": "2024-01-15T12:00:00Z",
        },
        {
            "id": "eth-ethereum",
            "name": "Ethereum",
            "symbol": "ETH",
            "rank": 2,
            "quotes": {
                "USD": {
                    "price": 2500.00,
                    "market_cap": 300000000000,
                    "volume_24h": 15000000000,
                }
            },
            "last_updated": "2024-01-15T12:00:00Z",
        },
    ]


# ============== Temporary File Fixtures ==============


@pytest.fixture
def temp_csv_file() -> Path:
    """Create a temporary CSV file for testing."""
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".csv",
        delete=False,
    ) as f:
        f.write("ticker,price,vol,date,market_cap\n")
        f.write("BTC,45000.50,25000000000,2024-01-15,850000000000\n")
        f.write("ETH,2500.00,15000000000,2024-01-15,300000000000\n")
        f.write("XRP,0.55,5000000000,2024-01-15,28000000000\n")
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def temp_csv_with_extra_columns() -> Path:
    """Create a CSV file with unexpected extra columns for schema drift testing."""
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".csv",
        delete=False,
    ) as f:
        # Include unexpected columns: weird_col, extra_field
        f.write("ticker,price,vol,date,market_cap,weird_col,extra_field\n")
        f.write("BTC,45000.50,25000000000,2024-01-15,850000000000,unexpected_value,123\n")
        f.write("ETH,2500.00,15000000000,2024-01-15,300000000000,another_value,456\n")
        f.write("SOL,95.50,3000000000,2024-01-15,40000000000,random_data,789\n")
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def temp_csv_missing_columns() -> Path:
    """Create a CSV file with missing optional columns."""
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".csv",
        delete=False,
    ) as f:
        # Missing market_cap column
        f.write("ticker,price,vol,date\n")
        f.write("BTC,45000.50,25000000000,2024-01-15\n")
        f.write("ETH,2500.00,15000000000,2024-01-15\n")
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


# ============== ETL Service Fixtures ==============


@pytest.fixture
def mock_etl_service():
    """Create a mock ETL service for testing."""
    from app.ingestion.service import ETLService

    service = ETLService()
    return service


@pytest_asyncio.fixture
async def seeded_db(test_session: AsyncSession, sample_crypto_data: list[dict]):
    """
    Seed the test database with sample data.
    Returns the session with data already committed.
    Creates canonical Coin entities and links UnifiedCryptoData via coin_id.
    """

    # First create Coin entities
    coins = {}
    for data in sample_crypto_data:
        symbol = data["symbol"]
        if symbol not in coins:
            coin = Coin(
                symbol=symbol,
                name=symbol,  # Use symbol as name for test data
                slug=symbol.lower(),
            )
            test_session.add(coin)
            coins[symbol] = coin

    await test_session.flush()  # Get coin IDs

    # Now create UnifiedCryptoData with coin_id
    for data in sample_crypto_data:
        record = UnifiedCryptoData(
            coin_id=coins[data["symbol"]].id,
            symbol=data["symbol"],
            price_usd=data["price_usd"],
            market_cap=data["market_cap"],
            volume_24h=data["volume_24h"],
            source=DataSource.CSV,
            timestamp=data["timestamp"],
        )
        test_session.add(record)

    await test_session.commit()

    yield test_session
