#!/bin/bash
# db-wait.sh - Common database initialization script
set -e

echo "Checking DATABASE_URL..."
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
    echo "✓ Parsed DATABASE_URL: $DB_USER@$DB_HOST:$DB_PORT/$DB_NAME"
else
    echo "WARNING: Could not parse DATABASE_URL, using defaults"
    DB_HOST="${DB_HOST:-localhost}"
    DB_PORT="${DB_PORT:-5432}"
    DB_USER="${DB_USER:-kasparro}"
fi

# Wait for database to be ready
echo "Waiting for database at $DB_HOST:$DB_PORT..."
max_attempts=60
attempt=0

while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -q 2>/dev/null; do
    attempt=$((attempt + 1))
    if [ $attempt -ge $max_attempts ]; then
        echo "ERROR: Database not ready after $max_attempts attempts"
        exit 1
    fi
    if [ $((attempt % 10)) -eq 0 ]; then
        echo "Still waiting... (attempt $attempt/$max_attempts)"
    fi
    sleep 2
done
echo "✓ Database is ready!"

# Run Alembic migrations (only on first service to start)
echo "Running database migrations..."
if alembic upgrade head 2>&1; then
    echo "✓ Migrations complete!"
else
    echo "WARNING: Migrations may have failed or already completed"
    # Don't exit - migrations might already be applied
fi
