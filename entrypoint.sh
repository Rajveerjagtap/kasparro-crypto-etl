#!/bin/bash
set -e

echo "============================================"
echo "Kasparro ETL & API Platform - Starting..."
echo "============================================"

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL environment variable is not set!"
    exit 1
fi

# Extract database connection details from DATABASE_URL
# Format: postgresql://user:password@host:port/database
if [[ $DATABASE_URL =~ postgresql://([^:]+):([^@]+)@([^:]+):([^/]+)/(.+) ]]; then
    DB_USER="${BASH_REMATCH[1]}"
    DB_PASS="${BASH_REMATCH[2]}"
    DB_HOST="${BASH_REMATCH[3]}"
    DB_PORT="${BASH_REMATCH[4]}"
    DB_NAME="${BASH_REMATCH[5]}"
else
    echo "WARNING: Could not parse DATABASE_URL, using defaults"
    DB_HOST="${DB_HOST:-db}"
    DB_PORT="${DB_PORT:-5432}"
    DB_USER="${DB_USER:-kasparro}"
fi

# Wait for database to be ready
echo "Waiting for database at $DB_HOST:$DB_PORT..."
max_attempts=30
attempt=0

while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -q 2>/dev/null; do
    attempt=$((attempt + 1))
    if [ $attempt -ge $max_attempts ]; then
        echo "ERROR: Database not ready after $max_attempts attempts"
        exit 1
    fi
    echo "Database not ready (attempt $attempt/$max_attempts), waiting..."
    sleep 2
done
echo "✓ Database is ready!"

# Run Alembic migrations
echo "Running database migrations..."
if alembic upgrade head; then
    echo "✓ Migrations complete!"
else
    echo "ERROR: Migrations failed!"
    exit 1
fi

# Determine which service to start based on command
# Render overrides CMD with dockerCommand in render.yaml
if [ $# -eq 0 ]; then
    # Default: Start web server
    echo "Starting Kasparro API server..."
    exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
else
    # Custom command (e.g., scheduler)
    echo "Starting custom command: $@"
    exec "$@"
fi
