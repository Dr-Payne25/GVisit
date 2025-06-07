.PHONY: help install test lint format security docker-build docker-run docker-stop clean setup-ci run dev

# Default target
help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make test        - Run tests with coverage"
	@echo "  make lint        - Run code quality checks"
	@echo "  make format      - Format code with black and isort"
	@echo "  make security    - Run security scans"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run  - Run Docker container"
	@echo "  make docker-stop - Stop Docker container"
	@echo "  make clean       - Clean up temporary files"
	@echo "  make setup-ci    - Install all CI/CD tools"
	@echo "  make run         - Run the application locally"
	@echo "  make dev         - Run in development mode"

# Install dependencies
install:
	pip install -r requirements.txt

# Install CI/CD tools
setup-ci:
	pip install black flake8 isort mypy bandit safety pytest pytest-cov pytest-flask

# Run tests
test:
	pytest tests/ -v --cov=. --cov-report=xml --cov-report=html --cov-report=term

# Run specific test file
test-file:
	pytest $(FILE) -v

# Run linting
lint:
	@echo "Running Black formatter check..."
	black . --check --diff
	@echo "\nRunning isort import checker..."
	isort . --check-only --diff
	@echo "\nRunning Flake8 linter..."
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	@echo "\nRunning Bandit security linter..."
	bandit -r . -f json -o bandit-report.json || true

# Format code
format:
	@echo "Formatting code with Black..."
	black .
	@echo "\nSorting imports with isort..."
	isort .

# Run security scans
security:
	@echo "Running Bandit security scan..."
	bandit -r . -ll
	@echo "\nChecking dependencies with Safety..."
	safety check --json --output safety-report.json || true

# Docker commands
docker-build:
	docker build -t gvisit:latest .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Clean up
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name ".coverage" -delete
	find . -type d -name "htmlcov" -delete
	rm -f .coverage coverage.xml
	rm -f bandit-report.json safety-report.json

# Run the application
run:
	python3 app.py

# Run in development mode
dev:
	FLASK_ENV=development python3 app.py

# Database management
backup-journal:
	cp journal_entries.json journal_entries_backup_$(shell date +%Y%m%d_%H%M%S).json
	@echo "Journal backed up successfully"

# Git shortcuts
push:
	git add -A && git commit -m "$(MSG)" && git push origin main

# AWS deployment (requires AWS CLI configured)
deploy-aws:
	@echo "Deploying to AWS..."
	cd terraform && terraform apply -auto-approve 