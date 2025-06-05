.PHONY: help install test test-coverage lint format run docker-build docker-run clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	pip install -r requirements.txt
	pip install pytest pytest-cov pytest-flask flake8 black isort

test: ## Run tests
	pytest tests/ -v

test-coverage: ## Run tests with coverage report
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term

lint: ## Run linters
	flake8 app.py aws_integration.py tests/
	black --check .
	isort --check-only .

format: ## Format code
	black .
	isort .

run: ## Run the Flask application
	python3 app.py

docker-build: ## Build Docker image
	docker build -t gvisit:latest .

docker-run: ## Run Docker container
	docker-compose up

docker-test: ## Run tests in Docker
	docker-compose run --rm web pytest tests/ -v

clean: ## Clean up cache and temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov .pytest_cache
	rm -rf journal_entries.json

security-check: ## Run security checks
	bandit -r app.py aws_integration.py
	safety check

terraform-plan: ## Run terraform plan
	terraform init
	terraform plan

terraform-apply: ## Apply terraform changes
	terraform init
	terraform apply

git-push: ## Commit and push changes
	git add .
	git commit -m "Update: $(shell date +%Y-%m-%d)"
	git push origin main 