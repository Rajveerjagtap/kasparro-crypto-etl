# Kasparro - Crypto Data ETL & API Platform

[![CI Pipeline](https://github.com/Rajveerjagtap/kasparro-crypto-etl/actions/workflows/ci.yml/badge.svg)](https://github.com/Rajveerjagtap/kasparro-crypto-etl/actions/workflows/ci.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-grade ETL and Backend system for ingesting cryptocurrency data from multiple sources (CoinPaprika, CoinGecko, CSV), normalizing it into a unified schema, and exposing it via a RESTful API.

## 🚀 Live Demo

**🌐 Base URL:** [`https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io`](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io)

### Quick Verification (Click to Test)

| Endpoint | URL | Description |
|----------|-----|-------------|
| 📖 **API Docs** | [/docs](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/docs) | Interactive Swagger UI |
| ❤️ **Health Check** | [/health](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/health) | System health status |
| 📊 **Statistics** | [/api/v1/stats](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/stats) | Data statistics & ETL status |
| 📈 **Crypto Data** | [/api/v1/data](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/data) | Retrieved cryptocurrency data |
| 🔧 **ETL Jobs** | [/api/v1/etl/jobs](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/etl/jobs) | ETL job history |
| 📉 **Metrics** | [/api/v1/metrics](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/metrics) | Prometheus metrics |

### Sample API Calls

```bash
# Health check
curl https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/health

# Get crypto data (with BTC filter)
curl "https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/data?symbol=BTC"

# Trigger ETL job (sync mode)
curl -X POST "https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/etl/run/csv?sync=true"
```

---

## ✨ Features

### Data Ingestion
- **Multi-Source Support**: CoinGecko API, CoinPaprika API, and CSV files
- **Unified Normalization**: All sources normalized to a canonical `UnifiedCryptoData` schema
- **Symbol Normalization**: Fuzzy matching maps aliases (e.g., "bitcoin" → "BTC")
- **Idempotent Upserts**: `ON CONFLICT DO UPDATE` ensures no duplicate records
- **Raw Data Auditability**: Original payloads preserved in `raw_data` table

### ETL Pipeline
- **Scheduled Execution**: APScheduler runs ETL jobs at configurable intervals
- **Incremental Loading**: Checkpoint-based processing for efficiency
- **Drift Detection**: Schema and data quality drift monitoring
- **Retry Logic**: Exponential backoff for API rate limits

### API & Observability
- **RESTful API**: FastAPI with automatic OpenAPI documentation
- **Health Checks**: Deep checks on database and ETL status
- **Prometheus Metrics**: Request counts, latency, ETL job statistics
- **Structured Logging**: JSON logs with request tracing (container-aware)

### Production Ready
- **Async-First**: Built with `asyncio`, `asyncpg`, and `httpx`
- **Validation**: Pydantic v2
- **Containerization**: Docker & Docker Compose
- **Database Migrations**: Alembic for schema versioning
- **Testing**: Pytest with 74 tests
- **CI/CD Pipeline**: GitHub Actions with lint, test, build, and deploy stages

---

## 🛠 Tech Stack

| Category | Technology |
|----------|------------|
| **Language** | Python 3.11+ |
| **Web Framework** | FastAPI 0.109 |
| **Database** | PostgreSQL 15 with asyncpg |
| **ORM** | SQLAlchemy 2.0 (async) |
| **Validation** | Pydantic v2 |
| **Scheduler** | APScheduler |
| **HTTP Client** | httpx (async) |
| **Containerization** | Docker & Docker Compose |
| **CI/CD** | GitHub Actions |
| **Cloud** | Azure Container Apps |
| **IaC** | Bicep |

---

## 📁 Project Structure

```
kasparro-crypto-etl/
├── app/
│   ├── api/                    # FastAPI routes
│   │   └── routes.py           # API endpoint definitions
│   ├── core/                   # Core utilities
│   │   ├── config.py           # Pydantic settings
│   │   ├── exceptions.py       # Custom exceptions
│   │   ├── logging.py          # Container-aware logging
│   │   └── middleware.py       # Request logging & metrics
│   ├── db/                     # Database layer
│   │   ├── models.py           # SQLAlchemy models
│   │   └── session.py          # Async session management
│   ├── ingestion/              # ETL pipeline
│   │   ├── base.py             # BaseExtractor ABC
│   │   ├── drift.py            # Drift detection
│   │   ├── normalization.py    # Symbol normalizer
│   │   ├── service.py          # ETL orchestration
│   │   ├── extractors/         # Source-specific extractors
│   │   │   ├── coingecko.py
│   │   │   ├── coinpaprika.py
│   │   │   └── csv_extractor.py
│   │   └── transformers/
│   │       └── schemas.py      # Intermediate validation schemas
│   ├── schemas/                # API schemas
│   │   └── crypto.py           # Request/response models
│   ├── main.py                 # FastAPI application
│   └── scheduler.py            # APScheduler ETL runner
├── alembic/                    # Database migrations
│   └── versions/
│       └── 001_initial_schema.py
├── azure/                      # Azure deployment
│   ├── main.bicep              # Infrastructure as Code
│   └── deploy.sh               # Deployment script
├── tests/                      # Test suite (74 tests)
│   ├── conftest.py             # Pytest fixtures
│   ├── test_api.py
│   ├── test_extractors.py
│   ├── test_etl_service.py
│   ├── test_etl_recovery.py
│   ├── test_schema_drift.py
│   └── ...
├── data/
│   └── crypto_data.csv         # Sample CSV data
├── .github/workflows/
│   └── ci.yml                  # CI/CD pipeline
├── docker-compose.yml          # Local development
├── Dockerfile                  # Multi-stage build
├── Makefile                    # Common commands
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL (or use Docker)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Rajveerjagtap/kasparro-crypto-etl.git
cd kasparro-crypto-etl
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Start with Docker:
```bash
make docker-up
```

Or run locally:
```bash
make install
make db-up
make run
```

API will be available at `http://localhost:8000`

---

## 📡 API Reference

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System health check (DB + ETL status) |
| `/api/v1/data` | GET | List crypto data with filters |
| `/api/v1/stats` | GET | Aggregated statistics |
| `/api/v1/etl/run/{source}` | POST | Trigger ETL for a source |
| `/api/v1/etl/jobs` | GET | View ETL job history |
| `/api/v1/runs/compare` | GET | Compare two ETL runs |
| `/api/v1/metrics` | GET | Prometheus metrics |

### Query Parameters for `/api/v1/data`

| Parameter | Type | Description |
|-----------|------|-------------|
| `symbol` | string | Filter by symbol (e.g., "BTC") |
| `source` | string | Filter by source (coingecko, coinpaprika, csv) |
| `limit` | int | Number of records (default: 100) |
| `offset` | int | Pagination offset (default: 0) |

### Example Requests

```bash
# Health check
curl http://localhost:8000/health

# Get BTC data from CoinGecko
curl "http://localhost:8000/api/v1/data?symbol=BTC&source=coingecko"

# Trigger CSV ETL (synchronous)
curl -X POST "http://localhost:8000/api/v1/etl/run/csv?sync=true"

# Get statistics
curl http://localhost:8000/api/v1/stats
```

---

## 🗄 Database Schema

### Tables

| Table | Purpose |
|-------|---------|
| `raw_data` | Stores original JSON payloads for auditability |
| `unified_crypto_data` | Normalized cryptocurrency data (canonical schema) |
| `etl_jobs` | ETL job tracking with status and metrics |

### Unified Crypto Data Schema

```sql
CREATE TABLE unified_crypto_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    price_usd NUMERIC(20, 8),
    market_cap NUMERIC(30, 2),
    volume_24h NUMERIC(30, 2),
    source data_source_enum NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (symbol, timestamp)
);
```

---

## ⏰ Scheduled ETL

The scheduler service runs ETL jobs automatically:

```bash
# Default: every hour (3600 seconds)
SCHEDULE_INTERVAL=3600

# Run scheduler locally
python -m app.scheduler

# Or with Docker Compose (included in `make up`)
docker compose up scheduler
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SCHEDULE_INTERVAL` | ETL interval in seconds | `3600` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `COINGECKO_KEY` | CoinGecko API key (optional) | `None` |
| `COINPAPRIKA_KEY` | CoinPaprika API key (optional) | `None` |

---

## 🧪 Testing

```bash
# Run all tests (74 tests)
make test

# Run with coverage
pytest tests/ -v --cov=app

# Run specific test file
pytest tests/test_extractors.py -v
```

### Test Categories
- **Unit Tests**: Extractors, models, config, schemas
- **Integration Tests**: API endpoints, database operations
- **Recovery Tests**: ETL failure injection and retry logic
- **Schema Drift Tests**: Forward compatibility with API changes

---

## ☁️ Cloud Deployment (Azure)

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Azure Container Apps                      │
│  ┌─────────────────┐          ┌─────────────────┐          │
│  │   Backend API   │          │    Scheduler    │          │
│  │    (FastAPI)    │          │  (APScheduler)  │          │
│  └────────┬────────┘          └────────┬────────┘          │
│           │                             │                    │
│           └───────────┬─────────────────┘                    │
│                       ▼                                      │
│           ┌─────────────────────┐                           │
│           │     PostgreSQL      │                           │
│           │ (Flexible Server)   │                           │
│           └─────────────────────┘                           │
└─────────────────────────────────────────────────────────────┘
```

### CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) includes:

1. **Lint & Type Check**: Ruff + MyPy
2. **Unit Tests**: Pytest with PostgreSQL service container
3. **Build Docker Image**: Multi-stage build
4. **Integration Tests**: Docker Compose end-to-end tests
5. **Publish**: Push to GitHub Container Registry
6. **Deploy**: Azure Container Apps via Bicep

### Manual Deployment

```bash
# Deploy to Azure
cd azure
./deploy.sh
```

---

## 📊 Monitoring

### Health Check Response

```json
{
  "status": "healthy",
  "database": {
    "connected": true,
    "latency_ms": 5.2
  },
  "etl": {
    "last_job_status": "success",
    "last_run": "2024-01-15T12:00:00Z",
    "record_count": 150
  }
}
```

### Prometheus Metrics

```
# ETL job counts by source and status
kasparro_etl_jobs_total{source="coingecko",status="success"} 24

# Records processed
kasparro_etl_records_processed_total{source="coingecko"} 1200

# HTTP request latency
kasparro_http_request_duration_seconds_bucket{endpoint="/api/v1/data",le="0.5"} 100
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Rajveer Jagtap**
- GitHub: [@Rajveerjagtap](https://github.com/Rajveerjagtap)
