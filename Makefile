.PHONY: help install dev clean docker-up docker-down test health-check

# Default target
help:
	@echo "Multi-Agent Data Analysis Assistant - Makefile Commands"
	@echo ""
	@echo "  install       Install Python dependencies"
	@echo "  dev           Start development server"
	@echo "  clean         Clean up generated files"
	@echo "  docker-up     Start Docker services"
	@echo "  docker-down   Stop Docker services"
	@echo "  test          Run tests"
	@echo "  health-check  Run health check script"

# Install dependencies
install:
	pip install -r requirements.txt

# Install development dependencies
install-dev:
	pip install -r requirements.txt
	pre-commit install

# Start development server
dev:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Clean up generated files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true

# Start Docker services
docker-up:
	cd infrastructure/docker && docker-compose up -d

# Stop Docker services
docker-down:
	cd infrastructure/docker && docker-compose down

# View Docker logs
docker-logs:
	cd infrastructure/docker && docker-compose logs -f

# Run tests
test:
	cd backend && pytest tests/ -v --cov=app --cov-report=term-missing

# Run health check
health-check:
	python infrastructure/scripts/health_check.py

# Format code
format:
	black backend/ --line-length 88
	isort backend/ --profile black

# Lint code
lint:
	flake8 backend/
	mypy backend/

# Create data directories
create-dirs:
	mkdir -p data/postgres data/redis data/rabbitmq data/minio data/prometheus data/grafana data/logs

# Setup environment file
setup-env:
	cp .env.example .env
	@echo "Created .env file. Please edit it with your configuration."