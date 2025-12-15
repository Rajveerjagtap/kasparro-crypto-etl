# Kasparro - Crypto Data ETL & API Platform# Kasparro - Crypto Data ETL & API Platform



[![CI Pipeline](https://github.com/Rajveerjagtap/kasparro-crypto-etl/actions/workflows/ci.yml/badge.svg)](https://github.com/Rajveerjagtap/kasparro-crypto-etl/actions/workflows/ci.yml)A production-grade ETL and Backend system for ingesting cryptocurrency data from multiple sources (CoinPaprika, CoinGecko, CSV), normalizing it, and exposing it via a RESTful API.

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)## 🚀 Live Demo



A production-grade ETL and Backend system for ingesting cryptocurrency data from multiple sources (CoinPaprika, CoinGecko, CSV), normalizing it into a unified schema, and exposing it via a RESTful API.**🌐 Base URL:** [`https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io`](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io)



## 🚀 Live Demo### Quick Verification (Click to Test)

| Endpoint | URL | Description |

**🌐 Base URL:** [`https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io`](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io)|----------|-----|-------------|

| 📖 **API Docs** | [/docs](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/docs) | Interactive Swagger UI |

### Quick Verification (Click to Test)| ❤️ **Health Check** | [/health](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/health) | System health status |

| 📊 **Statistics** | [/api/v1/stats](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/stats) | Data statistics & ETL status |

| Endpoint | URL | Description || 📈 **Crypto Data** | [/api/v1/data](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/data) | Retrieved cryptocurrency data |

|----------|-----|-------------|| 🔧 **ETL Jobs** | [/api/v1/etl/jobs](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/etl/jobs) | ETL job history |

| 📖 **API Docs** | [/docs](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/docs) | Interactive Swagger UI || 📉 **Metrics** | [/api/v1/metrics](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/metrics) | Prometheus metrics |

| ❤️ **Health Check** | [/health](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/health) | System health status |

| 📊 **Statistics** | [/api/v1/stats](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/stats) | Data statistics & ETL status |### Sample API Calls

| 📈 **Crypto Data** | [/api/v1/data](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/data) | Retrieved cryptocurrency data |```bash

| 🔧 **ETL Jobs** | [/api/v1/etl/jobs](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/etl/jobs) | ETL job history |# Health check

| 📉 **Metrics** | [/api/v1/metrics](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/metrics) | Prometheus metrics |curl https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/health



---# Get crypto data (with BTC filter)

curl "https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/data?symbol=BTC"

## ✨ Features

# Trigger ETL job (sync mode)

### Data Ingestioncurl -X POST "https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/etl/run/csv?sync=true"

- **Multi-Source Support**: CoinGecko API, CoinPaprika API, and CSV files```

- **Unified Normalization**: All sources normalized to a canonical `UnifiedCryptoData` schema

- **Symbol Normalization**: Fuzzy matching maps aliases (e.g., "bitcoin" → "BTC")<img width="2816" height="1536" alt="Gemini_Generated_Image_fob8d0fob8d0fob8" src="https://github.com/user-attachments/assets/a4da84c5-1a9e-48a8-9ef4-c7cfdcb26bc1" />

- **Idempotent Upserts**: `ON CONFLICT DO UPDATE` ensures no duplicate records

- **Raw Data Auditability**: Original payloads preserved in `raw_data` table



### ETL Pipeline## Features

- **Scheduled Execution**: APScheduler runs ETL jobs at configurable intervals

- **Incremental Loading**: Checkpoint-based processing for efficiency- **Multi-Source Data Ingestion**: CoinPaprika, CoinGecko APIs, and CSV files

- **Drift Detection**: Schema and data quality drift monitoring- **Clean Architecture**: Strict separation of concerns (Ingestion, API, Services, Schemas, Core)

- **Retry Logic**: Exponential backoff for API rate limits- **Async-First**: Built with `asyncio` for optimized I/O operations

- **Incremental Loading**: ETL checkpointing with idempotent upserts

### API & Observability- **Production Standards**: Pydantic v2 validation, SQLAlchemy Async ORM, comprehensive error handling

- **RESTful API**: FastAPI with automatic OpenAPI documentation

- **Health Checks**: Deep checks on database and ETL status## Tech Stack

- **Prometheus Metrics**: Request counts, latency, ETL job statistics

- **Structured Logging**: JSON logs with request tracing (container-aware)- **Language**: Python 3.11+

- **Web Framework**: FastAPI

### Production Ready- **Database**: PostgreSQL (Asyncpg)

- **Async-First**: Built with `asyncio`, `asyncpg`, and `httpx`- **Validation**: Pydantic v2

- **Type Safety**: Pydantic v2 validation throughout- **Containerization**: Docker & Docker Compose

- **Database Migrations**: Alembic for schema versioning- **Testing**: Pytest

- **CI/CD Pipeline**: GitHub Actions with lint, test, build, and deploy stages

## Project Structure

---

```

## 🛠 Tech Stackkasparro/

├── app/

| Category | Technology |│   ├── api/              # FastAPI endpoints

|----------|------------|│   ├── core/             # Config, Logging, Exceptions

| **Language** | Python 3.11+ |│   ├── db/               # Session manager, SQLAlchemy Models

| **Web Framework** | FastAPI 0.109 |│   ├── ingestion/        # ETL logic

| **Database** | PostgreSQL 15 with asyncpg |│   │   ├── extractors/   # Source-specific extractors

| **ORM** | SQLAlchemy 2.0 (async) |│   │   └── transformers/ # Data normalization schemas

| **Validation** | Pydantic v2 |│   └── schemas/          # Pydantic models

| **Scheduler** | APScheduler |├── tests/                # Unit tests

| **HTTP Client** | httpx (async) |├── data/                 # CSV data files

| **Containerization** | Docker & Docker Compose |├── Dockerfile

| **CI/CD** | GitHub Actions |├── docker-compose.yml

| **Cloud** | Azure Container Apps |├── Makefile

| **IaC** | Bicep |└── requirements.txt

```

---

## Quick Start

## 📁 Project Structure

### Prerequisites

```

kasparro-crypto-etl/- Python 3.11+

├── app/- Docker & Docker Compose

│   ├── api/                    # FastAPI routes- PostgreSQL (or use Docker)

│   │   └── routes.py           # API endpoint definitions

│   ├── core/                   # Core utilities### Setup

│   │   ├── config.py           # Pydantic settings

│   │   ├── exceptions.py       # Custom exceptions1. Clone the repository:

│   │   ├── logging.py          # Container-aware logging```bash

│   │   └── middleware.py       # Request logging & metricsgit clone https://github.com/Rajveerjagtap/kasparro-crypto-etl.git

│   ├── db/                     # Database layercd kasparro-crypto-etl

│   │   ├── models.py           # SQLAlchemy models```

│   │   └── session.py          # Async session management

│   ├── ingestion/              # ETL pipeline2. Copy environment file:

│   │   ├── base.py             # BaseExtractor ABC```bash

│   │   ├── drift.py            # Drift detectioncp .env.example .env

│   │   ├── normalization.py    # Symbol normalizer```

│   │   ├── service.py          # ETL orchestration

│   │   ├── extractors/         # Source-specific extractors3. Start with Docker:

│   │   │   ├── coingecko.py```bash

│   │   │   ├── coinpaprika.pymake docker-up

│   │   │   └── csv_extractor.py```

│   │   └── transformers/

│   │       └── schemas.py      # Intermediate validation schemasOr run locally:

│   ├── schemas/                # API schemas```bash

│   │   └── crypto.py           # Request/response modelsmake install

│   ├── main.py                 # FastAPI applicationmake db-up

│   └── scheduler.py            # APScheduler ETL runnermake run

├── alembic/                    # Database migrations```

│   └── versions/

│       └── 001_initial_schema.py### API Endpoints

├── azure/                      # Azure deployment

│   ├── main.bicep              # Infrastructure as Code| Endpoint | Method | Description |

│   └── deploy.sh               # Deployment script|----------|--------|-------------|

├── tests/                      # Test suite (74 tests)| `/health` | GET | Health check |

│   ├── conftest.py             # Pytest fixtures| `/api/v1/data` | GET | List crypto data (with filters) |

│   ├── test_api.py| `/api/v1/stats` | GET | Data statistics |

│   ├── test_extractors.py| `/api/v1/etl/run/{source}` | POST | Trigger ETL for source |

│   ├── test_etl_service.py| `/api/v1/etl/jobs` | GET | View ETL job history |

│   ├── test_etl_recovery.py| `/api/v1/metrics` | GET | Prometheus metrics |

│   ├── test_schema_drift.py

│   └── ...### Running Tests

├── data/

│   └── crypto_data.csv         # Sample CSV data```bash

├── .github/workflows/make test

│   └── ci.yml                  # CI/CD pipeline```

├── docker-compose.yml          # Local development

├── Dockerfile                  # Multi-stage build## Database Schema

├── Makefile                    # Common commands

├── requirements.txt### Tables

└── README.md

```- **raw_data**: Stores raw JSON blobs for auditability

- **unified_crypto_data**: Normalized cryptocurrency data

---- **etl_jobs**: ETL job tracking for checkpointing



## 🚀 Quick Start## ☁️ Cloud Deployment



### PrerequisitesKasparro is automatically deployed to Azure using GitHub Actions and Bicep.



- Python 3.11+### Infrastructure

- Docker & Docker Compose- **Azure Container Apps**: Hosts the FastAPI backend and Scheduler worker.

- PostgreSQL (or use Docker)- **Azure Database for PostgreSQL**: Managed database service.

- **Azure Container Registry**: Stores Docker images.

### Option 1: Docker Compose (Recommended)- **Bicep**: Infrastructure as Code (IaC) for reproducible deployments.



```bash[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FRajveerjagtap%2Fkasparro-crypto-etl%2Fmain%2Fazure%2Fmain.bicep)

# Clone the repository

git clone https://github.com/Rajveerjagtap/kasparro-crypto-etl.git### Option 1: Manual Docker Deployment

cd kasparro-crypto-etl

Deploy to any Docker-compatible host (AWS ECS, DigitalOcean, etc.):

# Create environment file

cat > .env << EOF```bash

DB_USER=kasparro# Build the image

DB_PASSWORD=kasparro_secretdocker build -t kasparro:latest .

DB_NAME=kasparro_db

EOF# Run with your PostgreSQL connection

# Note: DATABASE_URL must use postgresql+asyncpg:// format for SQLAlchemy async

# Start all services (PostgreSQL + Backend + Scheduler)docker run -d \

make up  -e DATABASE_URL="postgresql+asyncpg://user:password@host:5432/database" \

  -p 8000:8000 \

# View logs  kasparro:latest

make logs```

```

**Local Development with Docker Compose:**

The API will be available at `http://localhost:8000````bash

# Start PostgreSQL + API (uses docker-compose.yml)

### Option 2: Local Developmentmake up



```bash# View logs

# Install dependenciesmake logs

make install

# Stop all services

# Start PostgreSQL onlymake down

make db-up```



# Set database URLAPI will be available at `http://localhost:8000`

export DATABASE_URL="postgresql+asyncpg://kasparro:kasparro_secret@localhost:5433/kasparro_db"

### Scheduled ETL

# Run migrations

alembic upgrade headThe scheduler runs automatically in cloud deployment. For local testing:



# Start the API server```bash

make run# Run scheduler locally (every hour by default)

```make schedule



---# Custom interval (30 minutes)

SCHEDULE_INTERVAL=1800 python -m app.scheduler

## 📡 API Reference

# Run in Docker

### Endpointsmake schedule-docker

```

| Endpoint | Method | Description |

|----------|--------|-------------|### Environment Variables

| `/health` | GET | System health check (DB + ETL status) |

| `/api/v1/data` | GET | List crypto data with filters || Variable | Description | Default |

| `/api/v1/stats` | GET | Aggregated statistics ||----------|-------------|---------|

| `/api/v1/etl/run/{source}` | POST | Trigger ETL for a source || `DATABASE_URL` | PostgreSQL connection string | Required |

| `/api/v1/etl/jobs` | GET | View ETL job history || `SCHEDULE_INTERVAL` | ETL interval in seconds | `3600` (1 hour) |

| `/api/v1/runs/compare` | GET | Compare two ETL runs || `LOG_LEVEL` | Logging level | `INFO` |

| `/api/v1/metrics` | GET | Prometheus metrics |

## Deployment Verification

### Query Parameters for `/api/v1/data`

To verify the deployment status and ETL execution:

| Parameter | Type | Description |

|-----------|------|-------------|### 1. Check Deployment Status

| `symbol` | string | Filter by symbol (e.g., "BTC") |Visit the [Azure Portal](https://portal.azure.com) to view the status of your services.

| `source` | string | Filter by source (coingecko, coinpaprika, csv) |- **Container App**: Should be "Running"

| `limit` | int | Number of records (default: 100) |

| `offset` | int | Pagination offset (default: 0) |### 2. Verify ETL Execution Logs

Access the logs for the container app in Azure Portal:

### Example Requests```bash

# Example log output indicating successful ETL run

```bashINFO:kasparro.scheduler:Scheduler started - running ETL every 3600 seconds

# Health checkINFO:kasparro.scheduler:Starting scheduled ETL job...

curl http://localhost:8000/healthINFO:kasparro.ingestion.service:Starting ETL for source: coingecko

INFO:kasparro.ingestion.service:coingecko: ETL completed, 50 records processed

# Get BTC data from CoinGeckoINFO:kasparro.ingestion.service:Starting ETL for source: coinpaprika

curl "http://localhost:8000/api/v1/data?symbol=BTC&source=coingecko"INFO:kasparro.ingestion.service:coinpaprika: ETL completed, 50 records processed

INFO:kasparro.scheduler:Scheduled ETL job completed successfully

# Trigger CSV ETL (synchronous)```

curl -X POST "http://localhost:8000/api/v1/etl/run/csv?sync=true"

### 3. Verify Metrics

# Get statisticsCheck the `/metrics` endpoint for Prometheus metrics:

curl http://localhost:8000/api/v1/stats```bash

```curl https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/metrics

# Expected output includes:

---# kasparro_etl_jobs_total{source="coingecko",status="success"} 12.0

# kasparro_etl_records_processed_total{source="coingecko"} 600.0

## 🗄 Database Schema```



### Tables### 4. Verify Data Freshness

Query the stats endpoint to see the latest ingestion timestamps:

| Table | Purpose |```bash

|-------|---------|curl https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/stats

| `raw_data` | Stores original JSON payloads for auditability |```

| `unified_crypto_data` | Normalized cryptocurrency data (canonical schema) |Response should show recent `last_processed` timestamps.

| `etl_jobs` | ETL job tracking with status and metrics |

## License

### Unified Crypto Data Schema

MIT

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
│  ┌─────────────────┐         ┌─────────────────┐           │
│  │  Backend API    │         │   Scheduler     │           │
│  │  (FastAPI)      │         │  (APScheduler)  │           │
│  └────────┬────────┘         └────────┬────────┘           │
│           │                           │                     │
│           └───────────┬───────────────┘                     │
│                       ▼                                     │
│           ┌─────────────────────┐                          │
│           │  PostgreSQL         │                          │
│           │  (Flexible Server)  │                          │
│           └─────────────────────┘                          │
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
