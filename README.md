# Kasparro - Crypto Data ETL & API Platform# Kasparro - Crypto Data ETL & API Platform# Kasparro - Crypto Data ETL & API Platform



[![CI Pipeline](https://github.com/Rajveerjagtap/kasparro-crypto-etl/actions/workflows/ci.yml/badge.svg)](https://github.com/Rajveerjagtap/kasparro-crypto-etl/actions/workflows/ci.yml)

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![CI Pipeline](https://github.com/Rajveerjagtap/kasparro-crypto-etl/actions/workflows/ci.yml/badge.svg)](https://github.com/Rajveerjagtap/kasparro-crypto-etl/actions/workflows/ci.yml)A production-grade ETL and Backend system for ingesting cryptocurrency data from multiple sources (CoinPaprika, CoinGecko, CSV), normalizing it, and exposing it via a RESTful API.



A production-grade ETL and Backend system for ingesting cryptocurrency data from multiple sources (CoinPaprika, CoinGecko, CSV), normalizing it into a unified schema, and exposing it via a RESTful API.[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)



## 🚀 Live Demo[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)## 🚀 Live Demo



**🌐 Base URL:** [`https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io`](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io)



### Quick Verification (Click to Test)A production-grade ETL and Backend system for ingesting cryptocurrency data from multiple sources (CoinPaprika, CoinGecko, CSV), normalizing it into a unified schema, and exposing it via a RESTful API.**🌐 Base URL:** [`https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io`](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io)



| Endpoint | URL | Description |

|----------|-----|-------------|

| 📖 **API Docs** | [/docs](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/docs) | Interactive Swagger UI |## 🚀 Live Demo### Quick Verification (Click to Test)

| ❤️ **Health Check** | [/health](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/health) | System health status |

| 📊 **Statistics** | [/api/v1/stats](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/stats) | Data statistics & ETL status || Endpoint | URL | Description |

| 📈 **Crypto Data** | [/api/v1/data](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/data) | Retrieved cryptocurrency data |

| 🔧 **ETL Jobs** | [/api/v1/etl/jobs](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/etl/jobs) | ETL job history |**🌐 Base URL:** [`https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io`](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io)|----------|-----|-------------|

| 📉 **Metrics** | [/api/v1/metrics](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/metrics) | Prometheus metrics |

| 📖 **API Docs** | [/docs](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/docs) | Interactive Swagger UI |

---

### Quick Verification (Click to Test)| ❤️ **Health Check** | [/health](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/health) | System health status |

## ✨ Features

| 📊 **Statistics** | [/api/v1/stats](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/stats) | Data statistics & ETL status |

### Data Ingestion

- **Multi-Source Support**: CoinGecko API, CoinPaprika API, and CSV files| Endpoint | URL | Description || 📈 **Crypto Data** | [/api/v1/data](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/data) | Retrieved cryptocurrency data |

- **Unified Normalization**: All sources normalized to a canonical `UnifiedCryptoData` schema

- **Symbol Normalization**: Fuzzy matching maps aliases (e.g., "bitcoin" → "BTC")|----------|-----|-------------|| 🔧 **ETL Jobs** | [/api/v1/etl/jobs](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/etl/jobs) | ETL job history |

- **Idempotent Upserts**: `ON CONFLICT DO UPDATE` ensures no duplicate records

- **Raw Data Auditability**: Original payloads preserved in `raw_data` table| 📖 **API Docs** | [/docs](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/docs) | Interactive Swagger UI || 📉 **Metrics** | [/api/v1/metrics](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/metrics) | Prometheus metrics |



### ETL Pipeline| ❤️ **Health Check** | [/health](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/health) | System health status |

- **Scheduled Execution**: APScheduler runs ETL jobs at configurable intervals

- **Incremental Loading**: Checkpoint-based processing for efficiency| 📊 **Statistics** | [/api/v1/stats](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/stats) | Data statistics & ETL status |### Sample API Calls

- **Drift Detection**: Schema and data quality drift monitoring

- **Retry Logic**: Exponential backoff for API rate limits| 📈 **Crypto Data** | [/api/v1/data](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/data) | Retrieved cryptocurrency data |```bash



### API & Observability| 🔧 **ETL Jobs** | [/api/v1/etl/jobs](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/etl/jobs) | ETL job history |# Health check

- **RESTful API**: FastAPI with automatic OpenAPI documentation

- **Health Checks**: Deep checks on database and ETL status| 📉 **Metrics** | [/api/v1/metrics](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/metrics) | Prometheus metrics |curl https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/health

- **Prometheus Metrics**: Request counts, latency, ETL job statistics

- **Structured Logging**: JSON logs with request tracing (container-aware)



### Production Ready---# Get crypto data (with BTC filter)

- **Async-First**: Built with `asyncio`, `asyncpg`, and `httpx`

- **Validation**: Pydantic v2curl "https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/data?symbol=BTC"

- **Containerization**: Docker & Docker Compose

- **Database Migrations**: Alembic for schema versioning## ✨ Features

- **Testing**: Pytest

- **CI/CD Pipeline**: GitHub Actions with lint, test, build, and deploy stages# Trigger ETL job (sync mode)



---### Data Ingestioncurl -X POST "https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/etl/run/csv?sync=true"



## 🛠 Tech Stack- **Multi-Source Support**: CoinGecko API, CoinPaprika API, and CSV files```



| Category | Technology |- **Unified Normalization**: All sources normalized to a canonical `UnifiedCryptoData` schema

|----------|------------|

| **Language** | Python 3.11+ |- **Symbol Normalization**: Fuzzy matching maps aliases (e.g., "bitcoin" → "BTC")<img width="2816" height="1536" alt="Gemini_Generated_Image_fob8d0fob8d0fob8" src="https://github.com/user-attachments/assets/a4da84c5-1a9e-48a8-9ef4-c7cfdcb26bc1" />

| **Web Framework** | FastAPI 0.109 |

| **Database** | PostgreSQL 15 with asyncpg |- **Idempotent Upserts**: `ON CONFLICT DO UPDATE` ensures no duplicate records

| **ORM** | SQLAlchemy 2.0 (async) |

| **Validation** | Pydantic v2 |- **Raw Data Auditability**: Original payloads preserved in `raw_data` table

| **Scheduler** | APScheduler |

| **HTTP Client** | httpx (async) |

| **Containerization** | Docker & Docker Compose |

| **CI/CD** | GitHub Actions |### ETL Pipeline## Features

| **Cloud** | Azure Container Apps |

| **IaC** | Bicep |- **Scheduled Execution**: APScheduler runs ETL jobs at configurable intervals



---- **Incremental Loading**: Checkpoint-based processing for efficiency- **Multi-Source Data Ingestion**: CoinPaprika, CoinGecko APIs, and CSV files



## 📁 Project Structure- **Drift Detection**: Schema and data quality drift monitoring- **Clean Architecture**: Strict separation of concerns (Ingestion, API, Services, Schemas, Core)



```- **Retry Logic**: Exponential backoff for API rate limits- **Async-First**: Built with `asyncio` for optimized I/O operations

kasparro-crypto-etl/

├── app/- **Incremental Loading**: ETL checkpointing with idempotent upserts

│   ├── api/                    # FastAPI routes

│   │   └── routes.py           # API endpoint definitions### API & Observability- **Production Standards**: Pydantic v2 validation, SQLAlchemy Async ORM, comprehensive error handling

│   ├── core/                   # Core utilities

│   │   ├── config.py           # Pydantic settings- **RESTful API**: FastAPI with automatic OpenAPI documentation

│   │   ├── exceptions.py       # Custom exceptions

│   │   ├── logging.py          # Container-aware logging- **Health Checks**: Deep checks on database and ETL status## Tech Stack

│   │   └── middleware.py       # Request logging & metrics

│   ├── db/                     # Database layer- **Prometheus Metrics**: Request counts, latency, ETL job statistics

│   │   ├── models.py           # SQLAlchemy models

│   │   └── session.py          # Async session management- **Structured Logging**: JSON logs with request tracing (container-aware)- **Language**: Python 3.11+

│   ├── ingestion/              # ETL pipeline

│   │   ├── base.py             # BaseExtractor ABC- **Web Framework**: FastAPI

│   │   ├── drift.py            # Drift detection

│   │   ├── normalization.py    # Symbol normalizer### Production Ready- **Database**: PostgreSQL (Asyncpg)

│   │   ├── service.py          # ETL orchestration

│   │   ├── extractors/         # Source-specific extractors- **Async-First**: Built with `asyncio`, `asyncpg`, and `httpx`- **Validation**: Pydantic v2

│   │   │   ├── coingecko.py

│   │   │   ├── coinpaprika.py- **Type Safety**: Pydantic v2 validation throughout- **Containerization**: Docker & Docker Compose

│   │   │   └── csv_extractor.py

│   │   └── transformers/- **Database Migrations**: Alembic for schema versioning- **Testing**: Pytest

│   │       └── schemas.py      # Intermediate validation schemas

│   ├── schemas/                # API schemas- **CI/CD Pipeline**: GitHub Actions with lint, test, build, and deploy stages

│   │   └── crypto.py           # Request/response models

│   ├── main.py                 # FastAPI application## Project Structure

│   └── scheduler.py            # APScheduler ETL runner

├── alembic/                    # Database migrations---

│   └── versions/

│       └── 001_initial_schema.py```

├── azure/                      # Azure deployment

│   ├── main.bicep              # Infrastructure as Code## 🛠 Tech Stackkasparro/

│   └── deploy.sh               # Deployment script

├── tests/                      # Test suite (74 tests)├── app/

│   ├── conftest.py             # Pytest fixtures

│   ├── test_api.py| Category | Technology |│   ├── api/              # FastAPI endpoints

│   ├── test_extractors.py

│   ├── test_etl_service.py|----------|------------|│   ├── core/             # Config, Logging, Exceptions

│   ├── test_etl_recovery.py

│   ├── test_schema_drift.py| **Language** | Python 3.11+ |│   ├── db/               # Session manager, SQLAlchemy Models

│   └── ...

├── data/| **Web Framework** | FastAPI 0.109 |│   ├── ingestion/        # ETL logic

│   └── crypto_data.csv         # Sample CSV data

├── .github/workflows/| **Database** | PostgreSQL 15 with asyncpg |│   │   ├── extractors/   # Source-specific extractors

│   └── ci.yml                  # CI/CD pipeline

├── docker-compose.yml          # Local development| **ORM** | SQLAlchemy 2.0 (async) |│   │   └── transformers/ # Data normalization schemas

├── Dockerfile                  # Multi-stage build

├── Makefile                    # Common commands| **Validation** | Pydantic v2 |│   └── schemas/          # Pydantic models

├── requirements.txt

└── README.md| **Scheduler** | APScheduler |├── tests/                # Unit tests

```

| **HTTP Client** | httpx (async) |├── data/                 # CSV data files

---

| **Containerization** | Docker & Docker Compose |├── Dockerfile

## 🚀 Quick Start

| **CI/CD** | GitHub Actions |├── docker-compose.yml

### Prerequisites

- Python 3.11+| **Cloud** | Azure Container Apps |├── Makefile

- Docker & Docker Compose

- PostgreSQL (or use Docker)| **IaC** | Bicep |└── requirements.txt



### Setup```



1. Clone the repository:---

```bash

git clone https://github.com/Rajveerjagtap/kasparro-crypto-etl.git## Quick Start

cd kasparro-crypto-etl

```## 📁 Project Structure



2. Copy environment file:### Prerequisites

```bash

cp .env.example .env```

```

kasparro-crypto-etl/- Python 3.11+

3. Start with Docker:

```bash├── app/- Docker & Docker Compose

make docker-up

```│   ├── api/                    # FastAPI routes- PostgreSQL (or use Docker)



Or run locally:│   │   └── routes.py           # API endpoint definitions

```bash

make install│   ├── core/                   # Core utilities### Setup

make db-up

make run│   │   ├── config.py           # Pydantic settings

```

│   │   ├── exceptions.py       # Custom exceptions1. Clone the repository:

API will be available at `http://localhost:8000`

│   │   ├── logging.py          # Container-aware logging```bash

---

│   │   └── middleware.py       # Request logging & metricsgit clone https://github.com/Rajveerjagtap/kasparro-crypto-etl.git

## 📡 API Reference

│   ├── db/                     # Database layercd kasparro-crypto-etl

### Endpoints

│   │   ├── models.py           # SQLAlchemy models```

| Endpoint | Method | Description |

|----------|--------|-------------|│   │   └── session.py          # Async session management

| `/health` | GET | System health check (DB + ETL status) |

| `/api/v1/data` | GET | List crypto data with filters |│   ├── ingestion/              # ETL pipeline2. Copy environment file:

| `/api/v1/stats` | GET | Aggregated statistics |

| `/api/v1/etl/run/{source}` | POST | Trigger ETL for a source |│   │   ├── base.py             # BaseExtractor ABC```bash

| `/api/v1/etl/jobs` | GET | View ETL job history |

| `/api/v1/runs/compare` | GET | Compare two ETL runs |│   │   ├── drift.py            # Drift detectioncp .env.example .env

| `/api/v1/metrics` | GET | Prometheus metrics |

│   │   ├── normalization.py    # Symbol normalizer```

### Query Parameters for `/api/v1/data`

│   │   ├── service.py          # ETL orchestration

| Parameter | Type | Description |

|-----------|------|-------------|│   │   ├── extractors/         # Source-specific extractors3. Start with Docker:

| `symbol` | string | Filter by symbol (e.g., "BTC") |

| `source` | string | Filter by source (coingecko, coinpaprika, csv) |│   │   │   ├── coingecko.py```bash

| `limit` | int | Number of records (default: 100) |

| `offset` | int | Pagination offset (default: 0) |│   │   │   ├── coinpaprika.pymake docker-up



### Example Requests│   │   │   └── csv_extractor.py```



```bash│   │   └── transformers/

# Health check

curl http://localhost:8000/health│   │       └── schemas.py      # Intermediate validation schemasOr run locally:



# Get BTC data from CoinGecko│   ├── schemas/                # API schemas```bash

curl "http://localhost:8000/api/v1/data?symbol=BTC&source=coingecko"

│   │   └── crypto.py           # Request/response modelsmake install

# Trigger CSV ETL (synchronous)

curl -X POST "http://localhost:8000/api/v1/etl/run/csv?sync=true"│   ├── main.py                 # FastAPI applicationmake db-up



# Get statistics│   └── scheduler.py            # APScheduler ETL runnermake run

curl http://localhost:8000/api/v1/stats

```├── alembic/                    # Database migrations```



---│   └── versions/



## 🗄 Database Schema│       └── 001_initial_schema.py### API Endpoints



### Tables├── azure/                      # Azure deployment



| Table | Purpose |│   ├── main.bicep              # Infrastructure as Code| Endpoint | Method | Description |

|-------|---------|

| `raw_data` | Stores original JSON payloads for auditability |│   └── deploy.sh               # Deployment script|----------|--------|-------------|

| `unified_crypto_data` | Normalized cryptocurrency data (canonical schema) |

| `etl_jobs` | ETL job tracking with status and metrics |├── tests/                      # Test suite (74 tests)| `/health` | GET | Health check |



### Unified Crypto Data Schema│   ├── conftest.py             # Pytest fixtures| `/api/v1/data` | GET | List crypto data (with filters) |



```sql│   ├── test_api.py| `/api/v1/stats` | GET | Data statistics |

CREATE TABLE unified_crypto_data (

    id SERIAL PRIMARY KEY,│   ├── test_extractors.py| `/api/v1/etl/run/{source}` | POST | Trigger ETL for source |

    symbol VARCHAR(20) NOT NULL,

    price_usd NUMERIC(20, 8),│   ├── test_etl_service.py| `/api/v1/etl/jobs` | GET | View ETL job history |

    market_cap NUMERIC(30, 2),

    volume_24h NUMERIC(30, 2),│   ├── test_etl_recovery.py| `/api/v1/metrics` | GET | Prometheus metrics |

    source data_source_enum NOT NULL,

    timestamp TIMESTAMPTZ NOT NULL,│   ├── test_schema_drift.py

    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE (symbol, timestamp)│   └── ...### Running Tests

);

```├── data/



---│   └── crypto_data.csv         # Sample CSV data```bash



## ⏰ Scheduled ETL├── .github/workflows/make test



The scheduler service runs ETL jobs automatically:│   └── ci.yml                  # CI/CD pipeline```



```bash├── docker-compose.yml          # Local development

# Default: every hour (3600 seconds)

SCHEDULE_INTERVAL=3600├── Dockerfile                  # Multi-stage build## Database Schema



# Run scheduler locally├── Makefile                    # Common commands

python -m app.scheduler

├── requirements.txt### Tables

# Or with Docker Compose (included in `make up`)

docker compose up scheduler└── README.md

```

```- **raw_data**: Stores raw JSON blobs for auditability

### Environment Variables

- **unified_crypto_data**: Normalized cryptocurrency data

| Variable | Description | Default |

|----------|-------------|---------|---- **etl_jobs**: ETL job tracking for checkpointing

| `DATABASE_URL` | PostgreSQL connection string | Required |

| `SCHEDULE_INTERVAL` | ETL interval in seconds | `3600` |

| `LOG_LEVEL` | Logging level | `INFO` |

| `COINGECKO_KEY` | CoinGecko API key (optional) | `None` |## 🚀 Quick Start## ☁️ Cloud Deployment

| `COINPAPRIKA_KEY` | CoinPaprika API key (optional) | `None` |



---

### PrerequisitesKasparro is automatically deployed to Azure using GitHub Actions and Bicep.

## 🧪 Testing



```bash

# Run all tests (74 tests)- Python 3.11+### Infrastructure

make test

- Docker & Docker Compose- **Azure Container Apps**: Hosts the FastAPI backend and Scheduler worker.

# Run with coverage

pytest tests/ -v --cov=app- PostgreSQL (or use Docker)- **Azure Database for PostgreSQL**: Managed database service.



# Run specific test file- **Azure Container Registry**: Stores Docker images.

pytest tests/test_extractors.py -v

```### Option 1: Docker Compose (Recommended)- **Bicep**: Infrastructure as Code (IaC) for reproducible deployments.



### Test Categories



- **Unit Tests**: Extractors, models, config, schemas```bash[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FRajveerjagtap%2Fkasparro-crypto-etl%2Fmain%2Fazure%2Fmain.bicep)

- **Integration Tests**: API endpoints, database operations

- **Recovery Tests**: ETL failure injection and retry logic# Clone the repository

- **Schema Drift Tests**: Forward compatibility with API changes

git clone https://github.com/Rajveerjagtap/kasparro-crypto-etl.git### Option 1: Manual Docker Deployment

---

cd kasparro-crypto-etl

## ☁️ Cloud Deployment (Azure)

Deploy to any Docker-compatible host (AWS ECS, DigitalOcean, etc.):

### Architecture

# Create environment file

```

┌─────────────────────────────────────────────────────────────┐cat > .env << EOF```bash

│                    Azure Container Apps                      │

│  ┌─────────────────┐         ┌─────────────────┐           │DB_USER=kasparro# Build the image

│  │  Backend API    │         │   Scheduler     │           │

│  │  (FastAPI)      │         │  (APScheduler)  │           │DB_PASSWORD=kasparro_secretdocker build -t kasparro:latest .

│  └────────┬────────┘         └────────┬────────┘           │

│           │                           │                     │DB_NAME=kasparro_db

│           └───────────┬───────────────┘                     │

│                       ▼                                     │EOF# Run with your PostgreSQL connection

│           ┌─────────────────────┐                          │

│           │  PostgreSQL         │                          │# Note: DATABASE_URL must use postgresql+asyncpg:// format for SQLAlchemy async

│           │  (Flexible Server)  │                          │

│           └─────────────────────┘                          │# Start all services (PostgreSQL + Backend + Scheduler)docker run -d \

└─────────────────────────────────────────────────────────────┘

```make up  -e DATABASE_URL="postgresql+asyncpg://user:password@host:5432/database" \



### CI/CD Pipeline  -p 8000:8000 \



The GitHub Actions workflow (`.github/workflows/ci.yml`) includes:# View logs  kasparro:latest



1. **Lint & Type Check**: Ruff + MyPymake logs```

2. **Unit Tests**: Pytest with PostgreSQL service container

3. **Build Docker Image**: Multi-stage build```

4. **Integration Tests**: Docker Compose end-to-end tests

5. **Publish**: Push to GitHub Container Registry**Local Development with Docker Compose:**

6. **Deploy**: Azure Container Apps via Bicep

The API will be available at `http://localhost:8000````bash

### Manual Deployment

# Start PostgreSQL + API (uses docker-compose.yml)

```bash

# Deploy to Azure### Option 2: Local Developmentmake up

cd azure

./deploy.sh

```

```bash# View logs

---

# Install dependenciesmake logs

## 📊 Monitoring

make install

### Health Check Response

# Stop all services

```json

{# Start PostgreSQL onlymake down

  "status": "healthy",

  "database": {make db-up```

    "connected": true,

    "latency_ms": 5.2

  },

  "etl": {# Set database URLAPI will be available at `http://localhost:8000`

    "last_job_status": "success",

    "last_run": "2024-01-15T12:00:00Z",export DATABASE_URL="postgresql+asyncpg://kasparro:kasparro_secret@localhost:5433/kasparro_db"

    "record_count": 150

  }### Scheduled ETL

}

```# Run migrations



### Prometheus Metricsalembic upgrade headThe scheduler runs automatically in cloud deployment. For local testing:



```

# ETL job counts by source and status

kasparro_etl_jobs_total{source="coingecko",status="success"} 24# Start the API server```bash



# Records processedmake run# Run scheduler locally (every hour by default)

kasparro_etl_records_processed_total{source="coingecko"} 1200

```make schedule

# HTTP request latency

kasparro_http_request_duration_seconds_bucket{endpoint="/api/v1/data",le="0.5"} 100

```

---# Custom interval (30 minutes)

---

SCHEDULE_INTERVAL=1800 python -m app.scheduler

## 🤝 Contributing

## 📡 API Reference

1. Fork the repository

2. Create a feature branch (`git checkout -b feature/amazing-feature`)# Run in Docker

3. Commit changes (`git commit -m 'Add amazing feature'`)

4. Push to branch (`git push origin feature/amazing-feature`)### Endpointsmake schedule-docker

5. Open a Pull Request

```

---

| Endpoint | Method | Description |

## 📄 License

|----------|--------|-------------|### Environment Variables

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

| `/health` | GET | System health check (DB + ETL status) |

---

| `/api/v1/data` | GET | List crypto data with filters || Variable | Description | Default |

## 👤 Author

| `/api/v1/stats` | GET | Aggregated statistics ||----------|-------------|---------|

**Rajveer Jagtap**

| `/api/v1/etl/run/{source}` | POST | Trigger ETL for a source || `DATABASE_URL` | PostgreSQL connection string | Required |

- GitHub: [@Rajveerjagtap](https://github.com/Rajveerjagtap)

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
