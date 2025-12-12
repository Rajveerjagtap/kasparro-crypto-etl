#!/bin/bash
# start-scheduler.sh - Startup script for Render background worker
set -e

echo "============================================"
echo "Kasparro Scheduler - Starting ETL Worker"
echo "============================================"

# Source the common database setup
source /code/db-wait.sh

# Start the scheduler
echo "Starting ETL scheduler (interval: ${SCHEDULE_INTERVAL:-3600}s)..."
exec python -m app.scheduler
