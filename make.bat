.PHONY: help install run test seed backup clean logs

help:
	@echo "LabMS — Available commands:"
	@echo "  make install   → Install dependencies"
	@echo "  make run       → Start the dev server"
	@echo "  make test      → Run pytest"
	@echo "  make seed      → Seed sample data (50 patients, 200 orders)"
	@echo "  make backup    → Create a timestamped DB backup"
	@echo "  make migrate   → Run database migrations (upgrade)"
	@echo "  make logs      → Tail application log"
	@echo "  make clean     → Remove caches and .pyc files"

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
	flask db upgrade

logs:
	tail -f logs/app.log

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache 2>/dev/null || true