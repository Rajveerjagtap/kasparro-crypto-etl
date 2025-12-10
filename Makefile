.PHONY: up down logs test install run lint docker-up docker-down clean shell migrate

# ============== Docker Orchestration (P0.3) ==============

up:
	docker-compose up --build -d
	@echo "✓ Kasparro is running at http://localhost:8000"
	@echo "✓ API docs at http://localhost:8000/docs"

down:
	docker-compose down

logs:
	docker-compose logs -f

test:
	docker-compose run --rm backend pytest tests/ -v

shell:
	docker-compose exec backend /bin/bash

migrate:
	docker-compose exec backend alembic upgrade head

# ============== Local Development ==============

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

lint:
	ruff check app/ tests/
	mypy app/

# ============== Legacy Docker Commands ==============

docker-up:
	docker-compose up -d --build

docker-down:
	docker-compose down -v

db-up:
	docker-compose up -d db

# ============== Scheduler (Cloud ETL) ==============

schedule:
	python -m app.scheduler

schedule-docker:
	docker-compose run --rm backend python -m app.scheduler

# ============== Cleanup ==============

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	docker-compose down -v --remove-orphans 2>/dev/null || true
