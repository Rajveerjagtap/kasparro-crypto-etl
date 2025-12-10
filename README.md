# Kasparro - Crypto Data ETL & API Platform

A production-grade ETL and Backend system for ingesting cryptocurrency data from multiple sources (CoinPaprika, CoinGecko, CSV), normalizing it, and exposing it via a RESTful API.

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

## License

MIT
