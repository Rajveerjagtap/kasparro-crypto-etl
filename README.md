# Kasparro - Crypto Data ETL & API Platform

A production-grade ETL and Backend system for ingesting cryptocurrency data from multiple sources (CoinPaprika, CoinGecko, CSV), normalizing it, and exposing it via a RESTful API.

## 🚀 Live Demo

**🌐 Base URL:** [`https://kasparro-api-im89.onrender.com`](https://kasparro-api-im89.onrender.com)

### Quick Verification (Click to Test)
| Endpoint | URL | Description |
|----------|-----|-------------|
| 📖 **API Docs** | [/docs](https://kasparro-api-im89.onrender.com/docs) | Interactive Swagger UI |
| ❤️ **Health Check** | [/health](https://kasparro-api-im89.onrender.com/health) | System health status |
| 📊 **Statistics** | [/api/v1/stats](https://kasparro-api-im89.onrender.com/api/v1/stats) | Data statistics & ETL status |
| 📈 **Crypto Data** | [/api/v1/data](https://kasparro-api-im89.onrender.com/api/v1/data) | Retrieved cryptocurrency data |
| 🔧 **ETL Jobs** | [/api/v1/etl/jobs](https://kasparro-api-im89.onrender.com/api/v1/etl/jobs) | ETL job history |
| 📉 **Metrics** | [/api/v1/metrics](https://kasparro-api-im89.onrender.com/api/v1/metrics) | Prometheus metrics |

### Sample API Calls
```bash
# Health check
curl https://kasparro-api-im89.onrender.com/health

# Get crypto data (with BTC filter)
curl "https://kasparro-api-im89.onrender.com/api/v1/data?symbol=BTC"

# Trigger ETL job (sync mode)
curl -X POST "https://kasparro-api-im89.onrender.com/api/v1/etl/run/csv?sync=true"
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
git clone https://github.com/yourusername/kasparro.git
cd kasparro
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
| `/api/v1/crypto` | GET | List crypto data (paginated) |
| `/api/v1/crypto/{symbol}` | GET | Get data by symbol |
| `/api/v1/etl/run/{source}` | POST | Trigger ETL for source |
| `/api/v1/etl/run` | POST | Trigger ETL for all sources |
| `/api/v1/etl/jobs` | GET | View ETL job history |
| `/api/v1/sources` | GET | List available sources |

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
   curl https://kasparro-api.onrender.com/health
   curl https://kasparro-api.onrender.com/data
   ```

**Services Created:**
| Service | Type | Description |
|---------|------|-------------|
| `kasparro-db` | PostgreSQL | Free tier database |
| `kasparro-api` | Web Service | Public FastAPI endpoint |
| `kasparro-scheduler` | Background Worker | Hourly ETL cron job |

### Option 2: Railway.app

Alternative deployment with simpler UI.

1. Go to [railway.app](https://railway.app)
2. **New Project** → **Deploy from GitHub repo**
3. Add **PostgreSQL** plugin
4. Set environment variable: `DATABASE_URL` (auto-populated)
5. Deploy automatically detects `railway.toml`

### Option 3: Manual Docker Deployment

Deploy to any Docker-compatible host (AWS ECS, DigitalOcean, etc.):

```bash
# Build and push image
docker build -t your-registry/kasparro:latest .
docker push your-registry/kasparro:latest

# Run with your PostgreSQL connection
docker run -d \
  -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
  -p 8000:8000 \
  your-registry/kasparro:latest
```

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
| `ENVIRONMENT` | `development` or `production` | `development` |
| `LOG_LEVEL` | Logging level | `INFO` |

## License

MIT
