# Kasparro - Crypto Data ETL & API Platform# Kasparro - Crypto Data ETL & API Platform# Kasparro - Crypto Data ETL & API Platform# Kasparro - Crypto Data ETL & API Platform# Kasparro - Crypto Data ETL & API Platform



[![CI Pipeline](https://github.com/Rajveerjagtap/kasparro-crypto-etl/actions/workflows/ci.yml/badge.svg)](https://github.com/Rajveerjagtap/kasparro-crypto-etl/actions/workflows/ci.yml)

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![CI Pipeline](https://github.com/Rajveerjagtap/kasparro-crypto-etl/actions/workflows/ci.yml/badge.svg)](https://github.com/Rajveerjagtap/kasparro-crypto-etl/actions/workflows/ci.yml)



A production-grade ETL and Backend system for ingesting cryptocurrency data from multiple sources (CoinPaprika, CoinGecko, CSV), normalizing it via **canonical entity resolution**, and exposing it via a RESTful API.[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)



## 🚀 Live Demo[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![CI Pipeline](https://github.com/Rajveerjagtap/kasparro-crypto-etl/actions/workflows/ci.yml/badge.svg)](https://github.com/Rajveerjagtap/kasparro-crypto-etl/actions/workflows/ci.yml)



**🌐 Base URL:** [`https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io`](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io)



### Quick Verification (Click to Test)A production-grade ETL and Backend system for ingesting cryptocurrency data from multiple sources (CoinPaprika, CoinGecko, CSV), normalizing it via **canonical entity resolution**, and exposing it via a RESTful API.[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)



| Endpoint | URL | Description |

|----------|-----|-------------|

| 📖 **API Docs** | [/docs](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/docs) | Interactive Swagger UI |## 🚀 Live Demo[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![CI Pipeline](https://github.com/Rajveerjagtap/kasparro-crypto-etl/actions/workflows/ci.yml/badge.svg)](https://github.com/Rajveerjagtap/kasparro-crypto-etl/actions/workflows/ci.yml)A production-grade ETL and Backend system for ingesting cryptocurrency data from multiple sources (CoinPaprika, CoinGecko, CSV), normalizing it, and exposing it via a RESTful API.

| ❤️ **Health Check** | [/health](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/health) | System health status |

| 📊 **Statistics** | [/api/v1/stats](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/stats) | Data statistics & ETL status |

| 📈 **Crypto Data** | [/api/v1/data](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/data) | Retrieved cryptocurrency data |

| 🔧 **ETL Jobs** | [/api/v1/etl/jobs](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/etl/jobs) | ETL job history |**🌐 Base URL:** [`https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io`](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io)

| 📉 **Metrics** | [/api/v1/metrics](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/metrics) | Prometheus metrics |



---

### Quick Verification (Click to Test)A production-grade ETL and Backend system for ingesting cryptocurrency data from multiple sources (CoinPaprika, CoinGecko, CSV), normalizing it into a unified schema, and exposing it via a RESTful API.[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)

## ✨ Features



### Proper Entity Normalization (Asset Resolution)

| Endpoint | URL | Description |

- **Canonical Coin Entity**: System-owned `Coin` master table with unique `coin_id`

- **Source Asset Mapping**: Links source-specific IDs (CoinGecko `bitcoin`, CoinPaprika `btc-bitcoin`) to canonical coins|----------|-----|-------------|

- **Asset Resolver**: Intelligently maps incoming data to correct coin entity, handling symbol collisions

- **Aggregation by Entity**: Data is keyed by `(coin_id, timestamp)` not raw symbols - enabling proper deduplication| 📖 **API Docs** | [/docs](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/docs) | Interactive Swagger UI |## 🚀 Live Demo[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)## 🚀 Live Demo



### Data Ingestion| ❤️ **Health Check** | [/health](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/health) | System health status |



- **Multi-Source Support**: CoinGecko API, CoinPaprika API, and CSV files| 📊 **Statistics** | [/api/v1/stats](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/stats) | Data statistics & ETL status |

- **Unified Normalization**: All sources normalized via `AssetResolver` to canonical entities

- **Idempotent Upserts**: `ON CONFLICT DO UPDATE` on `(coin_id, timestamp)` ensures no duplicates| 📈 **Crypto Data** | [/api/v1/data](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/data) | Retrieved cryptocurrency data |

- **Raw Data Auditability**: Original payloads preserved in `raw_data` table

| 🔧 **ETL Jobs** | [/api/v1/etl/jobs](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/etl/jobs) | ETL job history |**🌐 Base URL:** [`https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io`](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io)

### ETL Pipeline

| 📉 **Metrics** | [/api/v1/metrics](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/metrics) | Prometheus metrics |

- **Scheduled Execution**: APScheduler runs ETL jobs at configurable intervals

- **Incremental Loading**: Checkpoint-based processing for efficiency

- **Drift Detection**: Schema and data quality drift monitoring

- **Retry Logic**: Exponential backoff for API rate limits---



### API & Observability### Quick Verification (Click to Test)A production-grade ETL and Backend system for ingesting cryptocurrency data from multiple sources (CoinPaprika, CoinGecko, CSV), normalizing it into a unified schema, and exposing it via a RESTful API.**🌐 Base URL:** [`https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io`](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io)



- **RESTful API**: FastAPI with automatic OpenAPI documentation## ✨ Features

- **Health Checks**: Deep checks on database and ETL status

- **Prometheus Metrics**: Request counts, latency, ETL job statistics

- **Structured Logging**: JSON logs with request tracing

### Proper Entity Normalization (Asset Resolution)

### Production Ready

| Endpoint | URL | Description |

- **Async-First**: Built with `asyncio`, `asyncpg`, and `httpx`

- **Validation**: Pydantic v2 for schema validation- **Canonical Coin Entity**: System-owned `Coin` master table with unique `coin_id`

- **Containerization**: Docker & Docker Compose

- **CI/CD**: GitHub Actions with automated testing- **Source Asset Mapping**: Links source-specific IDs (CoinGecko `bitcoin`, CoinPaprika `btc-bitcoin`) to canonical coins|----------|-----|-------------|



---- **Asset Resolver**: Intelligently maps incoming data to correct coin entity, handling symbol collisions



## 🏗️ Architecture- **Aggregation by Entity**: Data is keyed by `(coin_id, timestamp)` not raw symbols - enabling proper deduplication| 📖 **API Docs** | [/docs](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/docs) | Interactive Swagger UI |## 🚀 Live Demo### Quick Verification (Click to Test)



### Entity-Relationship Model



```### Data Ingestion| ❤️ **Health Check** | [/health](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/health) | System health status |

┌──────────────────────────────────────────────────────────────────────┐

│                        DATA NORMALIZATION FLOW                        │

├──────────────────────────────────────────────────────────────────────┤

│                                                                       │- **Multi-Source Support**: CoinGecko API, CoinPaprika API, and CSV files| 📊 **Statistics** | [/api/v1/stats](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/stats) | Data statistics & ETL status || Endpoint | URL | Description |

│   Source APIs                    Canonical Entity                     │

│   ──────────                     ────────────────                     │- **Unified Normalization**: All sources normalized via `AssetResolver` to canonical entities

│                                                                       │

│   CoinGecko ─────┐                                                    │- **Idempotent Upserts**: `ON CONFLICT DO UPDATE` on `(coin_id, timestamp)` ensures no duplicates| 📈 **Crypto Data** | [/api/v1/data](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/data) | Retrieved cryptocurrency data |

│   {"id": "bitcoin",              ┌─────────────────┐                  │

│    "symbol": "btc"}─────────────►│  Coin (id=1)    │                  │- **Raw Data Auditability**: Original payloads preserved in `raw_data` table

│                     │            │  symbol: "BTC"  │                  │

│   CoinPaprika ──────┤            │  name: "Bitcoin"│                  │| 🔧 **ETL Jobs** | [/api/v1/etl/jobs](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/etl/jobs) | ETL job history |**🌐 Base URL:** [`https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io`](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io)|----------|-----|-------------|

│   {"id": "btc-bitcoin",          │  slug: "bitcoin"│                  │

│    "symbol": "BTC"}─────────────►└────────┬────────┘                  │### ETL Pipeline

│                     │                     │                           │

│   CSV ──────────────┘                     │                           │| 📉 **Metrics** | [/api/v1/metrics](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/metrics) | Prometheus metrics |

│   {"ticker": "BTC"}─────────────►         ▼                           │

│                                  ┌─────────────────────┐              │- **Scheduled Execution**: APScheduler runs ETL jobs at configurable intervals

│                                  │ UnifiedCryptoData   │              │

│                                  │ coin_id: 1          │              │- **Incremental Loading**: Checkpoint-based processing for efficiency| 📖 **API Docs** | [/docs](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/docs) | Interactive Swagger UI |

│                                  │ price_usd: 45000    │              │

│                                  │ timestamp: 2024-...  │              │- **Drift Detection**: Schema and data quality drift monitoring

│                                  └─────────────────────┘              │

│                                                                       │- **Retry Logic**: Exponential backoff for API rate limits---

└──────────────────────────────────────────────────────────────────────┘

```



### Database Schema### API & Observability### Quick Verification (Click to Test)| ❤️ **Health Check** | [/health](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/health) | System health status |



```sql

-- Canonical asset master entity

CREATE TABLE coins (- **RESTful API**: FastAPI with automatic OpenAPI documentation## ✨ Features

    id SERIAL PRIMARY KEY,

    symbol VARCHAR(20) NOT NULL,       -- e.g., "BTC"- **Health Checks**: Deep checks on database and ETL status

    name VARCHAR(100) NOT NULL,        -- e.g., "Bitcoin"

    slug VARCHAR(100) NOT NULL UNIQUE, -- e.g., "bitcoin"- **Prometheus Metrics**: Request counts, latency, ETL job statistics| 📊 **Statistics** | [/api/v1/stats](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/stats) | Data statistics & ETL status |

    created_at TIMESTAMPTZ NOT NULL,

    updated_at TIMESTAMPTZ NOT NULL- **Structured Logging**: JSON logs with request tracing

);

### Data Ingestion

-- Maps source-specific IDs to canonical coins

CREATE TABLE source_asset_mappings (### Production Ready

    id SERIAL PRIMARY KEY,

    coin_id INTEGER REFERENCES coins(id),- **Multi-Source Support**: CoinGecko API, CoinPaprika API, and CSV files| Endpoint | URL | Description || 📈 **Crypto Data** | [/api/v1/data](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/data) | Retrieved cryptocurrency data |

    source data_source_enum NOT NULL,   -- 'coingecko', 'coinpaprika', 'csv'

    source_id VARCHAR(100) NOT NULL,    -- e.g., "bitcoin", "btc-bitcoin"- **Async-First**: Built with `asyncio`, `asyncpg`, and `httpx`

    source_symbol VARCHAR(20) NOT NULL, -- e.g., "btc", "BTC"

    UNIQUE(source, source_id)- **Validation**: Pydantic v2 for schema validation- **Unified Normalization**: All sources normalized to a canonical `UnifiedCryptoData` schema

);

- **Containerization**: Docker & Docker Compose

-- Normalized price data keyed by coin_id

CREATE TABLE unified_crypto_data (- **CI/CD**: GitHub Actions with automated testing- **Symbol Normalization**: Fuzzy matching maps aliases (e.g., "bitcoin" → "BTC")|----------|-----|-------------|| 🔧 **ETL Jobs** | [/api/v1/etl/jobs](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/etl/jobs) | ETL job history |

    id SERIAL PRIMARY KEY,

    coin_id INTEGER REFERENCES coins(id),

    symbol VARCHAR(20) NOT NULL,        -- Denormalized for convenience

    price_usd DECIMAL,---- **Idempotent Upserts**: `ON CONFLICT DO UPDATE` ensures no duplicate records

    market_cap DECIMAL,

    volume_24h DECIMAL,

    source data_source_enum NOT NULL,

    timestamp TIMESTAMPTZ NOT NULL,## 🏗️ Architecture- **Raw Data Auditability**: Original payloads preserved in `raw_data` table| 📖 **API Docs** | [/docs](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/docs) | Interactive Swagger UI || 📉 **Metrics** | [/api/v1/metrics](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/metrics) | Prometheus metrics |

    ingested_at TIMESTAMPTZ NOT NULL,

    UNIQUE(coin_id, timestamp)          -- Proper normalization!

);

```### Entity-Relationship Model



### Project Structure



``````### ETL Pipeline| ❤️ **Health Check** | [/health](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/health) | System health status |

kasparro-crypto-etl/

├── app/┌──────────────────────────────────────────────────────────────────────┐

│   ├── api/                    # FastAPI routes

│   │   └── routes.py│                        DATA NORMALIZATION FLOW                        │- **Scheduled Execution**: APScheduler runs ETL jobs at configurable intervals

│   ├── core/                   # Config, logging, middleware

│   │   ├── config.py├──────────────────────────────────────────────────────────────────────┤

│   │   └── exceptions.py

│   ├── db/                     # Database models & session│                                                                       │- **Incremental Loading**: Checkpoint-based processing for efficiency| 📊 **Statistics** | [/api/v1/stats](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/stats) | Data statistics & ETL status |### Sample API Calls

│   │   ├── models.py           # Coin, SourceAssetMapping, UnifiedCryptoData

│   │   └── session.py│   Source APIs                    Canonical Entity                     │

│   ├── ingestion/              # ETL components

│   │   ├── asset_resolver.py   # Canonical entity resolution│   ──────────                     ────────────────                     │- **Drift Detection**: Schema and data quality drift monitoring

│   │   ├── service.py          # ETL orchestration

│   │   ├── extractors/         # Source-specific extractors│                                                                       │

│   │   │   ├── coingecko.py

│   │   │   ├── coinpaprika.py│   CoinGecko ─────┐                                                    │- **Retry Logic**: Exponential backoff for API rate limits| 📈 **Crypto Data** | [/api/v1/data](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/data) | Retrieved cryptocurrency data |```bash

│   │   │   └── csv_extractor.py

│   │   └── transformers/       # Data validation schemas│   {"id": "bitcoin",              ┌─────────────────┐                  │

│   ├── schemas/                # Pydantic API schemas

│   ├── main.py                 # FastAPI application│    "symbol": "btc"}─────────────►│  Coin (id=1)    │                  │

│   └── scheduler.py            # APScheduler setup

├── alembic/                    # Database migrations│                     │            │  symbol: "BTC"  │                  │

│   └── versions/

│       ├── 001_initial_schema.py│   CoinPaprika ──────┤            │  name: "Bitcoin"│                  │### API & Observability| 🔧 **ETL Jobs** | [/api/v1/etl/jobs](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/etl/jobs) | ETL job history |# Health check

│       └── 002_add_coin_master.py

├── tests/                      # Comprehensive test suite│   {"id": "btc-bitcoin",          │  slug: "bitcoin"│                  │

├── docker-compose.yml

├── Dockerfile│    "symbol": "BTC"}─────────────►└────────┬────────┘                  │- **RESTful API**: FastAPI with automatic OpenAPI documentation

└── requirements.txt

```│                     │                     │                           │



---│   CSV ──────────────┘                     │                           │- **Health Checks**: Deep checks on database and ETL status| 📉 **Metrics** | [/api/v1/metrics](https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/metrics) | Prometheus metrics |curl https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/health



## 🔧 Installation & Setup│   {"ticker": "BTC"}─────────────►         ▼                           │



### Prerequisites│                                  ┌─────────────────────┐              │- **Prometheus Metrics**: Request counts, latency, ETL job statistics



- Python 3.11+│                                  │ UnifiedCryptoData   │              │

- PostgreSQL 15+ (or Docker)

- Docker & Docker Compose (optional)│                                  │ coin_id: 1          │              │- **Structured Logging**: JSON logs with request tracing (container-aware)



### Option 1: Docker Compose (Recommended)│                                  │ price_usd: 45000    │              │



```bash│                                  │ timestamp: 2024-...  │              │

# Clone the repository

git clone https://github.com/Rajveerjagtap/kasparro-crypto-etl.git│                                  └─────────────────────┘              │

cd kasparro-crypto-etl

│                                                                       │### Production Ready---# Get crypto data (with BTC filter)

# Start all services

docker-compose up -d└──────────────────────────────────────────────────────────────────────┘



# Apply database migrations```- **Async-First**: Built with `asyncio`, `asyncpg`, and `httpx`

docker-compose exec backend alembic upgrade head



# Access the API

open http://localhost:8000/docs### Database Schema- **Validation**: Pydantic v2curl "https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/data?symbol=BTC"

```



### Option 2: Local Development

```sql- **Containerization**: Docker & Docker Compose

```bash

# Clone and setup virtual environment-- Canonical asset master entity

git clone https://github.com/Rajveerjagtap/kasparro-crypto-etl.git

cd kasparro-crypto-etlCREATE TABLE coins (- **Database Migrations**: Alembic for schema versioning## ✨ Features

python -m venv venv

source venv/bin/activate    id SERIAL PRIMARY KEY,



# Install dependencies    symbol VARCHAR(20) NOT NULL,       -- e.g., "BTC"- **Testing**: Pytest

pip install -r requirements.txt

    name VARCHAR(100) NOT NULL,        -- e.g., "Bitcoin"

# Set environment variables

cp .env.example .env    slug VARCHAR(100) NOT NULL UNIQUE, -- e.g., "bitcoin"- **CI/CD Pipeline**: GitHub Actions with lint, test, build, and deploy stages# Trigger ETL job (sync mode)

# Edit .env with your database credentials

    created_at TIMESTAMPTZ NOT NULL,

# Run database migrations

alembic upgrade head    updated_at TIMESTAMPTZ NOT NULL



# Start the server);

uvicorn app.main:app --reload

```---### Data Ingestioncurl -X POST "https://kasparro-backend.thankfulwave-f9a1a1b4.eastus2.azurecontainerapps.io/api/v1/etl/run/csv?sync=true"



### Environment Variables-- Maps source-specific IDs to canonical coins



| Variable | Default | Description |CREATE TABLE source_asset_mappings (

|----------|---------|-------------|

| `DATABASE_URL` | `postgresql+asyncpg://user:pass@localhost/kasparro` | Database connection string |    id SERIAL PRIMARY KEY,

| `COINGECKO_API_KEY` | - | Optional: CoinGecko Pro API key |

| `COINPAPRIKA_API_KEY` | - | Optional: CoinPaprika API key |    coin_id INTEGER REFERENCES coins(id),## 🛠 Tech Stack- **Multi-Source Support**: CoinGecko API, CoinPaprika API, and CSV files```

| `ETL_SCHEDULE_MINUTES` | `15` | ETL run interval |

| `LOG_LEVEL` | `INFO` | Logging verbosity |    source data_source_enum NOT NULL,   -- 'coingecko', 'coinpaprika', 'csv'



---    source_id VARCHAR(100) NOT NULL,    -- e.g., "bitcoin", "btc-bitcoin"



## 📡 API Reference    source_symbol VARCHAR(20) NOT NULL, -- e.g., "btc", "BTC"



### Endpoints    UNIQUE(source, source_id)| Category | Technology |- **Unified Normalization**: All sources normalized to a canonical `UnifiedCryptoData` schema



| Method | Endpoint | Description |);

|--------|----------|-------------|

| GET | `/health` | System health check ||----------|------------|

| GET | `/api/v1/data` | Get cryptocurrency data |

| GET | `/api/v1/data?symbol=BTC` | Filter by symbol |-- Normalized price data keyed by coin_id

| GET | `/api/v1/data?source=coingecko` | Filter by source |

| GET | `/api/v1/stats` | Aggregated statistics |CREATE TABLE unified_crypto_data (| **Language** | Python 3.11+ |- **Symbol Normalization**: Fuzzy matching maps aliases (e.g., "bitcoin" → "BTC")<img width="2816" height="1536" alt="Gemini_Generated_Image_fob8d0fob8d0fob8" src="https://github.com/user-attachments/assets/a4da84c5-1a9e-48a8-9ef4-c7cfdcb26bc1" />

| GET | `/api/v1/etl/jobs` | ETL job history |

| POST | `/api/v1/etl/trigger` | Manual ETL trigger |    id SERIAL PRIMARY KEY,

| GET | `/api/v1/metrics` | Prometheus metrics |

    coin_id INTEGER REFERENCES coins(id),| **Web Framework** | FastAPI 0.109 |

### Example Responses

    symbol VARCHAR(20) NOT NULL,        -- Denormalized for convenience

#### Health Check

```json    price_usd DECIMAL,| **Database** | PostgreSQL 15 with asyncpg |- **Idempotent Upserts**: `ON CONFLICT DO UPDATE` ensures no duplicate records

{

  "status": "healthy",    market_cap DECIMAL,

  "timestamp": "2024-12-16T10:30:00Z",

  "database": {    volume_24h DECIMAL,| **ORM** | SQLAlchemy 2.0 (async) |

    "connected": true,

    "latency_ms": 2.5    source data_source_enum NOT NULL,

  },

  "etl": {    timestamp TIMESTAMPTZ NOT NULL,| **Validation** | Pydantic v2 |- **Raw Data Auditability**: Original payloads preserved in `raw_data` table

    "last_run_status": "success",

    "last_run_at": "2024-12-16T10:15:00Z",    ingested_at TIMESTAMPTZ NOT NULL,

    "records_processed": 500

  }    UNIQUE(coin_id, timestamp)          -- Proper normalization!| **Scheduler** | APScheduler |

}

```);



#### Data Response```| **HTTP Client** | httpx (async) |

```json

{

  "metadata": {

    "request_id": "550e8400-e29b-41d4-a716-446655440000",### Project Structure| **Containerization** | Docker & Docker Compose |

    "total_records": 1250,

    "api_latency_ms": 12.5

  },

  "data": [```| **CI/CD** | GitHub Actions |### ETL Pipeline## Features

    {

      "id": 1,kasparro-crypto-etl/

      "coin_id": 1,

      "symbol": "BTC",├── app/| **Cloud** | Azure Container Apps |

      "price_usd": 45000.50,

      "market_cap": 850000000000,│   ├── api/                    # FastAPI routes

      "volume_24h": 25000000000,

      "source": "coingecko",│   │   └── routes.py| **IaC** | Bicep |- **Scheduled Execution**: APScheduler runs ETL jobs at configurable intervals

      "timestamp": "2024-12-16T10:00:00Z"

    }│   ├── core/                   # Config, logging, middleware

  ],

  "pagination": {│   │   ├── config.py

    "limit": 50,

    "offset": 0,│   │   └── exceptions.py

    "total": 1250

  }│   ├── db/                     # Database models & session---- **Incremental Loading**: Checkpoint-based processing for efficiency- **Multi-Source Data Ingestion**: CoinPaprika, CoinGecko APIs, and CSV files

}

```│   │   ├── models.py           # Coin, SourceAssetMapping, UnifiedCryptoData



---│   │   └── session.py



## 🧪 Testing│   ├── ingestion/              # ETL components



```bash│   │   ├── asset_resolver.py   # Canonical entity resolution## 📁 Project Structure- **Drift Detection**: Schema and data quality drift monitoring- **Clean Architecture**: Strict separation of concerns (Ingestion, API, Services, Schemas, Core)

# Run all tests

pytest tests/ -v│   │   ├── service.py          # ETL orchestration



# Run with coverage│   │   ├── extractors/         # Source-specific extractors

pytest tests/ --cov=app --cov-report=html

│   │   │   ├── coingecko.py

# Run specific test module

pytest tests/test_models.py -v│   │   │   ├── coinpaprika.py```- **Retry Logic**: Exponential backoff for API rate limits- **Async-First**: Built with `asyncio` for optimized I/O operations

```

│   │   │   └── csv_extractor.py

### Test Coverage

│   │   └── transformers/       # Data validation schemaskasparro-crypto-etl/

- Model structure tests (Coin, SourceAssetMapping, UnifiedCryptoData)

- Extractor normalization tests│   ├── schemas/                # Pydantic API schemas

- API endpoint tests

- ETL recovery and resilience tests│   ├── main.py                 # FastAPI application├── app/- **Incremental Loading**: ETL checkpointing with idempotent upserts

- Schema drift handling tests

│   └── scheduler.py            # APScheduler setup

---

├── alembic/                    # Database migrations│   ├── api/                    # FastAPI routes

## 🐳 Docker

│   └── versions/

### Build Image

│       ├── 001_initial_schema.py│   │   └── routes.py           # API endpoint definitions### API & Observability- **Production Standards**: Pydantic v2 validation, SQLAlchemy Async ORM, comprehensive error handling

```bash

docker build -t kasparro-backend .│       └── 002_add_coin_master.py

```

├── tests/                      # Comprehensive test suite│   ├── core/                   # Core utilities

### Run Container

├── docker-compose.yml

```bash

docker run -p 8000:8000 \├── Dockerfile│   │   ├── config.py           # Pydantic settings- **RESTful API**: FastAPI with automatic OpenAPI documentation

  -e DATABASE_URL="postgresql+asyncpg://user:pass@host/db" \

  kasparro-backend└── requirements.txt

```

```│   │   ├── exceptions.py       # Custom exceptions

### Docker Compose Services



```yaml

services:---│   │   ├── logging.py          # Container-aware logging- **Health Checks**: Deep checks on database and ETL status## Tech Stack

  backend:

    build: .

    ports:

      - "8000:8000"## 🔧 Installation & Setup│   │   └── middleware.py       # Request logging & metrics

    depends_on:

      - db



  db:### Prerequisites│   ├── db/                     # Database layer- **Prometheus Metrics**: Request counts, latency, ETL job statistics

    image: postgres:15-alpine

    environment:

      POSTGRES_USER: kasparro

      POSTGRES_PASSWORD: kasparro- Python 3.11+│   │   ├── models.py           # SQLAlchemy models

      POSTGRES_DB: kasparro

```- PostgreSQL 15+ (or Docker)



---- Docker & Docker Compose (optional)│   │   └── session.py          # Async session management- **Structured Logging**: JSON logs with request tracing (container-aware)- **Language**: Python 3.11+



## ☁️ Azure Deployment



The application is deployed on Azure Container Apps with:### Option 1: Docker Compose (Recommended)│   ├── ingestion/              # ETL pipeline



- **Container App**: Auto-scaling backend

- **Azure PostgreSQL**: Managed database

- **GitHub Actions**: CI/CD pipeline```bash│   │   ├── base.py             # BaseExtractor ABC- **Web Framework**: FastAPI



### Deployment Script# Clone the repository



```bashgit clone https://github.com/Rajveerjagtap/kasparro-crypto-etl.git│   │   ├── drift.py            # Drift detection

# Deploy to Azure

./azure/deploy.shcd kasparro-crypto-etl

```

│   │   ├── normalization.py    # Symbol normalizer### Production Ready- **Database**: PostgreSQL (Asyncpg)

---

# Start all services

## 📊 Metrics & Monitoring

docker-compose up -d│   │   ├── service.py          # ETL orchestration

### Prometheus Metrics



| Metric | Type | Description |

|--------|------|-------------|# Apply database migrations│   │   ├── extractors/         # Source-specific extractors- **Async-First**: Built with `asyncio`, `asyncpg`, and `httpx`- **Validation**: Pydantic v2

| `http_requests_total` | Counter | Total HTTP requests |

| `http_request_duration_seconds` | Histogram | Request latency |docker-compose exec backend alembic upgrade head

| `etl_runs_total` | Counter | ETL job executions |

| `etl_duration_seconds` | Gauge | ETL job duration |│   │   │   ├── coingecko.py

| `etl_records_processed` | Gauge | Records per ETL run |

# Access the API

### Health Check Deep Dive

open http://localhost:8000/docs│   │   │   ├── coinpaprika.py- **Type Safety**: Pydantic v2 validation throughout- **Containerization**: Docker & Docker Compose

- Database connectivity and latency

- Last ETL job status and timing```

- Overall system health status

│   │   │   └── csv_extractor.py

---

### Option 2: Local Development

## 🤝 Contributing

│   │   └── transformers/- **Database Migrations**: Alembic for schema versioning- **Testing**: Pytest

1. Fork the repository

2. Create a feature branch (`git checkout -b feature/amazing-feature`)```bash

3. Commit your changes (`git commit -m 'Add amazing feature'`)

4. Push to the branch (`git push origin feature/amazing-feature`)# Clone and setup virtual environment│   │       └── schemas.py      # Intermediate validation schemas

5. Open a Pull Request

git clone https://github.com/Rajveerjagtap/kasparro-crypto-etl.git

---

cd kasparro-crypto-etl│   ├── schemas/                # API schemas- **CI/CD Pipeline**: GitHub Actions with lint, test, build, and deploy stages

## 📄 License

python -m venv venv

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

source venv/bin/activate│   │   └── crypto.py           # Request/response models

---



## 🙏 Acknowledgments

# Install dependencies│   ├── main.py                 # FastAPI application## Project Structure

- [CoinGecko API](https://www.coingecko.com/en/api)

- [CoinPaprika API](https://api.coinpaprika.com)pip install -r requirements.txt

- [FastAPI](https://fastapi.tiangolo.com/)

- [SQLAlchemy](https://www.sqlalchemy.org/)│   └── scheduler.py            # APScheduler ETL runner


# Set environment variables

cp .env.example .env├── alembic/                    # Database migrations---

# Edit .env with your database credentials

│   └── versions/

# Run database migrations

alembic upgrade head│       └── 001_initial_schema.py```



# Start the server├── azure/                      # Azure deployment

uvicorn app.main:app --reload

```│   ├── main.bicep              # Infrastructure as Code## 🛠 Tech Stackkasparro/



### Environment Variables│   └── deploy.sh               # Deployment script



| Variable | Default | Description |├── tests/                      # Test suite (74 tests)├── app/

|----------|---------|-------------|

| `DATABASE_URL` | `postgresql+asyncpg://user:pass@localhost/kasparro` | Database connection string |│   ├── conftest.py             # Pytest fixtures

| `COINGECKO_API_KEY` | - | Optional: CoinGecko Pro API key |

| `COINPAPRIKA_API_KEY` | - | Optional: CoinPaprika API key |│   ├── test_api.py| Category | Technology |│   ├── api/              # FastAPI endpoints

| `ETL_SCHEDULE_MINUTES` | `15` | ETL run interval |

| `LOG_LEVEL` | `INFO` | Logging verbosity |│   ├── test_extractors.py



---│   ├── test_etl_service.py|----------|------------|│   ├── core/             # Config, Logging, Exceptions



## 📡 API Reference│   ├── test_etl_recovery.py



### Endpoints│   ├── test_schema_drift.py| **Language** | Python 3.11+ |│   ├── db/               # Session manager, SQLAlchemy Models



| Method | Endpoint | Description |│   └── ...

|--------|----------|-------------|

| GET | `/health` | System health check |├── data/| **Web Framework** | FastAPI 0.109 |│   ├── ingestion/        # ETL logic

| GET | `/api/v1/data` | Get cryptocurrency data |

| GET | `/api/v1/data?symbol=BTC` | Filter by symbol |│   └── crypto_data.csv         # Sample CSV data

| GET | `/api/v1/data?source=coingecko` | Filter by source |

| GET | `/api/v1/stats` | Aggregated statistics |├── .github/workflows/| **Database** | PostgreSQL 15 with asyncpg |│   │   ├── extractors/   # Source-specific extractors

| GET | `/api/v1/etl/jobs` | ETL job history |

| POST | `/api/v1/etl/trigger` | Manual ETL trigger |│   └── ci.yml                  # CI/CD pipeline

| GET | `/api/v1/metrics` | Prometheus metrics |

├── docker-compose.yml          # Local development| **ORM** | SQLAlchemy 2.0 (async) |│   │   └── transformers/ # Data normalization schemas

### Example Responses

├── Dockerfile                  # Multi-stage build

#### Health Check

```json├── Makefile                    # Common commands| **Validation** | Pydantic v2 |│   └── schemas/          # Pydantic models

{

  "status": "healthy",├── requirements.txt

  "timestamp": "2024-12-16T10:30:00Z",

  "database": {└── README.md| **Scheduler** | APScheduler |├── tests/                # Unit tests

    "connected": true,

    "latency_ms": 2.5```

  },

  "etl": {| **HTTP Client** | httpx (async) |├── data/                 # CSV data files

    "last_run_status": "success",

    "last_run_at": "2024-12-16T10:15:00Z",---

    "records_processed": 500

  }| **Containerization** | Docker & Docker Compose |├── Dockerfile

}

```## 🚀 Quick Start



#### Data Response| **CI/CD** | GitHub Actions |├── docker-compose.yml

```json

{### Prerequisites

  "metadata": {

    "request_id": "550e8400-e29b-41d4-a716-446655440000",- Python 3.11+| **Cloud** | Azure Container Apps |├── Makefile

    "total_records": 1250,

    "api_latency_ms": 12.5- Docker & Docker Compose

  },

  "data": [- PostgreSQL (or use Docker)| **IaC** | Bicep |└── requirements.txt

    {

      "id": 1,

      "coin_id": 1,

      "symbol": "BTC",### Setup```

      "price_usd": 45000.50,

      "market_cap": 850000000000,

      "volume_24h": 25000000000,

      "source": "coingecko",1. Clone the repository:---

      "timestamp": "2024-12-16T10:00:00Z"

    }```bash

  ],

  "pagination": {git clone https://github.com/Rajveerjagtap/kasparro-crypto-etl.git## Quick Start

    "limit": 50,

    "offset": 0,cd kasparro-crypto-etl

    "total": 1250

  }```## 📁 Project Structure

}

```



---2. Copy environment file:### Prerequisites



## 🧪 Testing```bash



```bashcp .env.example .env```

# Run all tests

pytest tests/ -v```



# Run with coveragekasparro-crypto-etl/- Python 3.11+

pytest tests/ --cov=app --cov-report=html

3. Start with Docker:

# Run specific test module

pytest tests/test_models.py -v```bash├── app/- Docker & Docker Compose

```

make docker-up

### Test Coverage

```│   ├── api/                    # FastAPI routes- PostgreSQL (or use Docker)

- Model structure tests (Coin, SourceAssetMapping, UnifiedCryptoData)

- Extractor normalization tests

- API endpoint tests

- ETL recovery and resilience testsOr run locally:│   │   └── routes.py           # API endpoint definitions

- Schema drift handling tests

```bash

---

make install│   ├── core/                   # Core utilities### Setup

## 🐳 Docker

make db-up

### Build Image

make run│   │   ├── config.py           # Pydantic settings

```bash

docker build -t kasparro-backend .```

```

│   │   ├── exceptions.py       # Custom exceptions1. Clone the repository:

### Run Container

API will be available at `http://localhost:8000`

```bash

docker run -p 8000:8000 \│   │   ├── logging.py          # Container-aware logging```bash

  -e DATABASE_URL="postgresql+asyncpg://user:pass@host/db" \

  kasparro-backend---

```

│   │   └── middleware.py       # Request logging & metricsgit clone https://github.com/Rajveerjagtap/kasparro-crypto-etl.git

### Docker Compose Services

## 📡 API Reference

```yaml

services:│   ├── db/                     # Database layercd kasparro-crypto-etl

  backend:

    build: .### Endpoints

    ports:

      - "8000:8000"│   │   ├── models.py           # SQLAlchemy models```

    depends_on:

      - db| Endpoint | Method | Description |



  db:|----------|--------|-------------|│   │   └── session.py          # Async session management

    image: postgres:15-alpine

    environment:| `/health` | GET | System health check (DB + ETL status) |

      POSTGRES_USER: kasparro

      POSTGRES_PASSWORD: kasparro| `/api/v1/data` | GET | List crypto data with filters |│   ├── ingestion/              # ETL pipeline2. Copy environment file:

      POSTGRES_DB: kasparro

```| `/api/v1/stats` | GET | Aggregated statistics |



---| `/api/v1/etl/run/{source}` | POST | Trigger ETL for a source |│   │   ├── base.py             # BaseExtractor ABC```bash



## ☁️ Azure Deployment| `/api/v1/etl/jobs` | GET | View ETL job history |



The application is deployed on Azure Container Apps with:| `/api/v1/runs/compare` | GET | Compare two ETL runs |│   │   ├── drift.py            # Drift detectioncp .env.example .env



- **Container App**: Auto-scaling backend| `/api/v1/metrics` | GET | Prometheus metrics |

- **Azure PostgreSQL**: Managed database

- **GitHub Actions**: CI/CD pipeline│   │   ├── normalization.py    # Symbol normalizer```



### Deployment Script### Query Parameters for `/api/v1/data`



```bash│   │   ├── service.py          # ETL orchestration

# Deploy to Azure

./azure/deploy.sh| Parameter | Type | Description |

```

|-----------|------|-------------|│   │   ├── extractors/         # Source-specific extractors3. Start with Docker:

---

| `symbol` | string | Filter by symbol (e.g., "BTC") |

## 📊 Metrics & Monitoring

| `source` | string | Filter by source (coingecko, coinpaprika, csv) |│   │   │   ├── coingecko.py```bash

### Prometheus Metrics

| `limit` | int | Number of records (default: 100) |

| Metric | Type | Description |

|--------|------|-------------|| `offset` | int | Pagination offset (default: 0) |│   │   │   ├── coinpaprika.pymake docker-up

| `http_requests_total` | Counter | Total HTTP requests |

| `http_request_duration_seconds` | Histogram | Request latency |

| `etl_runs_total` | Counter | ETL job executions |

| `etl_duration_seconds` | Gauge | ETL job duration |### Example Requests│   │   │   └── csv_extractor.py```

| `etl_records_processed` | Gauge | Records per ETL run |



### Health Check Deep Dive

```bash│   │   └── transformers/

- Database connectivity and latency

- Last ETL job status and timing# Health check

- Overall system health status

curl http://localhost:8000/health│   │       └── schemas.py      # Intermediate validation schemasOr run locally:

---



## 🤝 Contributing

# Get BTC data from CoinGecko│   ├── schemas/                # API schemas```bash

1. Fork the repository

2. Create a feature branch (`git checkout -b feature/amazing-feature`)curl "http://localhost:8000/api/v1/data?symbol=BTC&source=coingecko"

3. Commit your changes (`git commit -m 'Add amazing feature'`)

4. Push to the branch (`git push origin feature/amazing-feature`)│   │   └── crypto.py           # Request/response modelsmake install

5. Open a Pull Request

# Trigger CSV ETL (synchronous)

---

curl -X POST "http://localhost:8000/api/v1/etl/run/csv?sync=true"│   ├── main.py                 # FastAPI applicationmake db-up

## 📄 License



This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

# Get statistics│   └── scheduler.py            # APScheduler ETL runnermake run

---

curl http://localhost:8000/api/v1/stats

## 🙏 Acknowledgments

```├── alembic/                    # Database migrations```

- [CoinGecko API](https://www.coingecko.com/en/api)

- [CoinPaprika API](https://api.coinpaprika.com)

- [FastAPI](https://fastapi.tiangolo.com/)

- [SQLAlchemy](https://www.sqlalchemy.org/)---│   └── versions/




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
