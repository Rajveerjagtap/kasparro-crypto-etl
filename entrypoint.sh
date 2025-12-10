#!/bin/bash
set -e

echo "============================================"
echo "Kasparro ETL & API Platform - Starting..."
echo "============================================"

# Wait for database to be ready
echo "Waiting for database..."
while ! pg_isready -h "${DB_HOST:-db}" -p "${DB_PORT:-5432}" -U "${DB_USER:-kasparro}" -q; do
    echo "Database not ready, waiting..."
    sleep 2
done
echo "Database is ready!"

# Run Alembic migrations
echo "Running database migrations..."
alembic upgrade head
echo "Migrations complete!"

# Start the application
echo "Starting Kasparro API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
