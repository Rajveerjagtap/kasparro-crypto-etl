# Kasparro - Crypto Data ETL & API Platform

A production-grade ETL and Backend system for ingesting cryptocurrency data from multiple sources (CoinPaprika, CoinGecko, CSV), normalizing it, and exposing it via a RESTful API.

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

<img width="2816" height="1536" alt="Gemini_Generated_Image_fob8d0fob8d0fob8" src="https://github.com/user-attachments/assets/a4da84c5-1a9e-48a8-9ef4-c7cfdcb26bc1" />



## Features

- **Multi-Source Data Ingestion**: CoinPaprika, CoinGecko APIs, and CSV files
- **Clean Architecture**: Strict separation of concerns (Ingestion, API, Services, Schemas, Core)
- **Async-First**: Built with `asyncio` for optimized I/O operations
- **Incremental Loading**: ETL checkpointing with idempotent upserts
- **Production Standards**: Pydantic v2 validation, SQLAlchemy Async ORM, comprehensive error handling

## Tech Stack

- **Language**: Python 3.11+
- **Web Framework**: FastAPI
- **Database**: PostgreSQL (Asyncpg)
- **Validation**: Pydantic v2
- **Containerization**: Docker & Docker Compose
- **Testing**: Pytest

## Project Structure

```
kasparro/
├── app/
│   ├── api/              # FastAPI endpoints
│   ├── core/             # Config, Logging, Exceptions
│   ├── db/               # Session manager, SQLAlchemy Models
│   ├── ingestion/        # ETL logic
│   │   ├── extractors/   # Source-specific extractors
│   │   └── transformers/ # Data normalization schemas
│   └── schemas/          # Pydantic models
├── tests/                # Unit tests
├── data/                 # CSV data files
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── requirements.txt
```

## Quick Start

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

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/v1/data` | GET | List crypto data (with filters) |
| `/api/v1/stats` | GET | Data statistics |
| `/api/v1/etl/run/{source}` | POST | Trigger ETL for source |
| `/api/v1/etl/jobs` | GET | View ETL job history |
| `/api/v1/metrics` | GET | Prometheus metrics |

### Running Tests

```bash
make test
```

## Database Schema

### Tables

- **raw_data**: Stores raw JSON blobs for auditability
- **unified_crypto_data**: Normalized cryptocurrency data
- **etl_jobs**: ETL job tracking for checkpointing

## ☁️ Cloud Deployment

Kasparro is designed for **free-tier cloud deployment** with a public API endpoint and scheduled ETL.

### Option 1: Render.com (Recommended)

The easiest way to deploy with automatic infrastructure setup.

**Prerequisites:**
- GitHub account
- Render.com account (free)

**Steps:**

1. **Push to GitHub:**
   ```bash
   git add -A
   git commit -m "Deploy to cloud"
   git push origin main
   ```

2. **Deploy to Render:**
   - Go to [render.com](https://render.com) and sign up
   - Click **New** → **Blueprint**
   - Connect your GitHub repository
   - Render auto-detects `render.yaml` and creates:
     - ✅ PostgreSQL database (free tier)
     - ✅ Web service (public API at `https://kasparro-api.onrender.com`)
     - ✅ Background worker (scheduled ETL every hour)

3. **Verify deployment:**
   ```bash
   curl https://kasparro-api-im89.onrender.com/health
   curl https://kasparro-api-im89.onrender.com/api/v1/data
   ```

**Services Created:**
| Service | Type | Description |
|---------|------|-------------|
| `kasparro-db` | PostgreSQL | Free tier database |
| `kasparro-api` | Web Service | Public FastAPI endpoint |
| `kasparro-scheduler` | Background Worker | Hourly ETL cron job |

### Option 2: Manual Docker Deployment

Deploy to any Docker-compatible host (AWS ECS, DigitalOcean, etc.):

```bash
# Build the image
docker build -t kasparro:latest .

# Run with your PostgreSQL connection
# Note: DATABASE_URL must use postgresql+asyncpg:// format for SQLAlchemy async
docker run -d \
  -e DATABASE_URL="postgresql+asyncpg://user:password@host:5432/database" \
  -p 8000:8000 \
  kasparro:latest
```

**Local Development with Docker Compose:**
```bash
# Start PostgreSQL + API (uses docker-compose.yml)
make up

# View logs
make logs

# Stop all services
make down
```

API will be available at `http://localhost:8000`

### Scheduled ETL

The scheduler runs automatically in cloud deployment. For local testing:

```bash
# Run scheduler locally (every hour by default)
make schedule

# Custom interval (30 minutes)
SCHEDULE_INTERVAL=1800 python -m app.scheduler

# Run in Docker
make schedule-docker
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SCHEDULE_INTERVAL` | ETL interval in seconds | `3600` (1 hour) |
| `LOG_LEVEL` | Logging level | `INFO` |

## Deployment Verification

To verify the deployment status and ETL execution:

### 1. Check Deployment Status
Visit the [Render Dashboard](https://dashboard.render.com) to view the status of your services.
- **Web Service**: Should be "Live"
- **Worker Service**: Should be "Live"

### 2. Verify ETL Execution Logs
Access the logs for the `kasparro-scheduler` worker service:
```bash
# Example log output indicating successful ETL run
INFO:kasparro.scheduler:Scheduler started - running ETL every 3600 seconds
INFO:kasparro.scheduler:Starting scheduled ETL job...
INFO:kasparro.ingestion.service:Starting ETL for source: coingecko
INFO:kasparro.ingestion.service:coingecko: ETL completed, 50 records processed
INFO:kasparro.ingestion.service:Starting ETL for source: coinpaprika
INFO:kasparro.ingestion.service:coinpaprika: ETL completed, 50 records processed
INFO:kasparro.scheduler:Scheduled ETL job completed successfully
```

### 3. Verify Metrics
Check the `/metrics` endpoint for Prometheus metrics:
```bash
curl https://kasparro-api-im89.onrender.com/api/v1/metrics
# Expected output includes:
# kasparro_etl_jobs_total{source="coingecko",status="success"} 12.0
# kasparro_etl_records_processed_total{source="coingecko"} 600.0
```

### 4. Verify Data Freshness
Query the stats endpoint to see the latest ingestion timestamps:
```bash
curl https://kasparro-api-im89.onrender.com/api/v1/stats
```
Response should show recent `last_processed` timestamps.

## ☁️ Azure Deployment

This project is automatically deployed to Azure using GitHub Actions and Bicep.

### Infrastructure
- **Azure Container Apps**: Hosts the FastAPI backend and Scheduler worker.
- **Azure Database for PostgreSQL**: Managed database service.
- **Azure Container Registry**: Stores Docker images.
- **Bicep**: Infrastructure as Code (IaC) for reproducible deployments.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FRajveerjagtap%2Fkasparro-crypto-etl%2Fmain%2Fazure%2Fmain.bicep)

## License

MIT
