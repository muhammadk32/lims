.PHONY: help install install-dev run test seed backup migrate logs clean
.PHONY: docker-build docker-up docker-down docker-logs docker-shell

help:
    @echo "LabMS — Available commands:"
    @echo "  make install         Install dev dependencies"
    @echo "  make run             Start the dev server (port 5000)"
    @echo "  make test            Run pytest"
    @echo "  make seed            Seed sample data"
    @echo "  make backup          Create a timestamped DB backup"
    @echo "  make migrate         Run database migrations (upgrade)"
    @echo "  make logs            Tail application log"
    @echo "  make clean           Remove caches and .pyc files"
    @echo ""
    @echo "  make docker-build    Build the Docker image"
    @echo "  make docker-up       Start the container (port 8000)"
    @echo "  make docker-down     Stop the container"
    @echo "  make docker-logs     Tail container logs"
    @echo "  make docker-shell    Open a shell inside the container"

install:
    pip install -r requirements.txt

run:
    python app.py

test:
    pytest

seed:
    python -m scripts.seed_data --patients 50 --orders 200

backup:
    python -m scripts.backup

migrate:
    flask --app app db upgrade

logs:
    tail -f logs/app.log

clean:
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    rm -rf .pytest_cache 2>/dev/null || true

docker-build:
    docker compose build

docker-up:
    docker compose up -d

docker-down:
    docker compose down

docker-logs:
    docker compose logs -f

docker-shell:
    docker compose exec web /bin/bash