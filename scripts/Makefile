.PHONY: help install test test-cov lint format clean run docker-build docker-run

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install flake8 black bandit safety

test: ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing

test-fast: ## Run fast tests only
	pytest tests/ -v -m "not slow"

test-backend: ## Run backend tests only
	pytest tests/unit/test_app.py tests/unit/test_utils.py -v

lint: ## Run linting
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format: ## Format code
	black . --line-length 127

security: ## Run security checks
	bandit -r . -f txt
	safety check

clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf uploads/*

run: ## Run the application
	python app.py

run-dev: ## Run the application in development mode
	FLASK_ENV=development python app.py

docker-build: ## Build Docker image
	docker build -t turtle-species-id:latest .

docker-run: ## Run Docker container
	docker run -p 8080:8080 --env-file .env turtle-species-id:latest

docker-test: ## Test Docker container
	docker run --rm -p 8080:8080 --env-file .env turtle-species-id:latest &
	sleep 10
	curl -f http://localhost:8080/health
	docker stop $$(docker ps -q --filter ancestor=turtle-species-id:latest)

ci: ## Run CI pipeline locally
	make install-dev
	make lint
	make security
	make test-cov
	make docker-build

all: clean install-dev lint security test-cov ## Run all checks
