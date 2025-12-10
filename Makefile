.PHONY: install run test lint docker-up docker-down clean

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --cov=app --cov-report=term-missing

lint:
	ruff check app/ tests/
	mypy app/

docker-up:
	docker-compose up -d --build

docker-down:
	docker-compose down -v

db-up:
	docker-compose up -d db

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
