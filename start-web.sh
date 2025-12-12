#!/bin/bash
# start-web.sh - Startup script for Render web service
set -e

echo "============================================"
echo "Kasparro API - Starting Web Service"
echo "============================================"

# Convert Render's postgres:// URL to postgresql+asyncpg:// for SQLAlchemy
if [[ "$DATABASE_URL" == postgres://* ]]; then
    export DATABASE_URL="${DATABASE_URL/postgres:\/\//postgresql+asyncpg:\/\/}"
    echo "✓ Converted DATABASE_URL to asyncpg format"
elif [[ "$DATABASE_URL" == postgresql://* ]] && [[ "$DATABASE_URL" != *"+asyncpg"* ]]; then
    export DATABASE_URL="${DATABASE_URL/postgresql:\/\//postgresql+asyncpg:\/\/}"
    echo "✓ Converted DATABASE_URL to asyncpg format"
fi

# Source the common database setup
source /code/db-wait.sh

# Start the web server
echo "Starting FastAPI server on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
