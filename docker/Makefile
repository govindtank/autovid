# AutoVid Makefile
# Common commands for development and deployment

.PHONY: help all setup dev prod test lint clean

help: ## Show this help message
	@echo 'AutoVid Makefile Commands:'
	@echo ''
	@echo 'Usage: make [command]'
	@echo ''
	@echo 'Commands:'
	@echo '  setup     - Set up development environment (install deps)'
	@echo '  dev       - Start backend in development mode'
	@echo '  prod      - Build production Docker image'
	@echo '  docker-up - Start all services with Docker Compose'
	@echo '  docker-down - Stop all Docker containers'
	@echo '  test      - Run tests (placeholder)'
	@echo '  lint      - Lint Python code'
	@echo '  clean     - Remove generated files'

all: help

# Default target: set up development environment
setup:
	pip install -r backend/requirements.txt
	cp config/database.example.yaml config/database.yaml
	cp config/services.example.yaml config/services.yaml
	echo "✅ Setup complete! Edit config/*.yaml and then run 'make dev'"

dev: setup
	cd backend && uvicorn main:app --reload --port 8000 --host 0.0.0.0

prod:
	DOCKER_BUILDKIT=1 docker build -t autovid-api .
	docker compose up -d
	echo "✅ Production mode started with Docker Compose"

test: ## Run tests (placeholder)
	@echo "Running tests..."
	@echo "TODO: Add test suite"

lint: ## Lint Python code
	flake8 backend/ --max-line-length 120
	pydocstring backend/*.py

clean: ## Remove generated files
	rm -rf /tmp/tts_*
	rm -rf /output/*
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleaned generated files"
