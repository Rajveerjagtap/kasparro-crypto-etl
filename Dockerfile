FROM python:3.11-slim

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/code

# Install system dependencies for asyncpg/psycopg2 and pg_isready
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY data/ ./data/
COPY entrypoint.sh .
COPY db-wait.sh .
COPY start-web.sh .
COPY start-scheduler.sh .

# Make scripts executable
RUN chmod +x /code/entrypoint.sh /code/db-wait.sh /code/start-web.sh /code/start-scheduler.sh

EXPOSE 8000

ENTRYPOINT ["/code/entrypoint.sh"]
