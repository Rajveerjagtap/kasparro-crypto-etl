#!/bin/bash
# db-wait.sh - Common database initialization script
set -e

echo "Checking DATABASE_URL..."
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL environment variable is not set!"
    exit 1
fi

echo "DATABASE_URL format: ${DATABASE_URL:0:30}..."

# Extract database connection details from DATABASE_URL using Python (more reliable)
# Render provides: postgres://user:password@host:port/database or postgresql://...
eval $(python3 << 'EOF'
import os
from urllib.parse import urlparse

url = os.environ.get('DATABASE_URL', '')
# Handle both postgres:// and postgresql:// schemes
url = url.replace('postgres://', 'postgresql://')

try:
    parsed = urlparse(url)
    print(f'DB_USER="{parsed.username or "kasparro"}"')
    print(f'DB_HOST="{parsed.hostname or "localhost"}"')
    print(f'DB_PORT="{parsed.port or 5432}"')
    print(f'DB_NAME="{parsed.path.lstrip("/").split("?")[0] or "kasparro"}"')
    print('PARSE_SUCCESS="true"')
except Exception as e:
    print(f'# Parse error: {e}')
    print('PARSE_SUCCESS="false"')
EOF
)

if [ "$PARSE_SUCCESS" = "true" ]; then
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
