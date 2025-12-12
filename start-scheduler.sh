#!/bin/bash
# start-scheduler.sh - Startup script for Render background worker
set -e

echo "============================================"
echo "Kasparro Scheduler - Starting ETL Worker"
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

# Start the scheduler
echo "Starting ETL scheduler (interval: ${SCHEDULE_INTERVAL:-3600}s)..."
exec python -m app.scheduler
