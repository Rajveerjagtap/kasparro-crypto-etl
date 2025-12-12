#!/bin/bash
# start-web.sh - Startup script for Render web service
set -e

echo "============================================"
echo "Kasparro API - Starting Web Service"
echo "============================================"

# Source the common database setup
source /code/db-wait.sh

# Start the web server
echo "Starting FastAPI server on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
