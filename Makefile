.PHONY: install run test audit format lint clean docker-build docker-run help

# Variables
PYTHON := python3.11
UV := uv
PACKAGE := aws_orchestrator

help: ## Show this help message
	@echo "AWS Orchestrator - Development Commands"
	@echo "========================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies with uv
	@echo "📦 Installing dependencies with uv..."
	$(UV) sync
	@echo "✅ Dependencies installed!"

install-dev: install ## Install development dependencies
	@echo "📦 Installing dev dependencies..."
	$(UV) pip install -e ".[dev]"
	@echo "✅ Dev dependencies installed!"

run: ## Run the CLI application
	@echo "🚀 Running AWS Orchestrator..."
	$(UV) run aws-orchestrator --help

run-example: ## Run example query
	@echo "🚀 Running example query..."
	$(UV) run aws-orchestrator run "Analyze customer sentiment from Q4" --user-id demo-user

test: ## Run tests with pytest
	@echo "🧪 Running tests..."
	$(UV) run pytest -v --cov=src/$(PACKAGE) --cov-report=term-missing

test-unit: ## Run unit tests only
	@echo "🧪 Running unit tests..."
	$(UV) run pytest tests/unit/ -v

test-integration: ## Run integration tests only
	@echo "🧪 Running integration tests..."
	$(UV) run pytest tests/integration/ -v

test-coverage: ## Run tests with HTML coverage report
	@echo "🧪 Running tests with coverage report..."
	$(UV) run pytest --cov=src/$(PACKAGE) --cov-report=html --cov-report=term
	@echo "📊 Coverage report generated in htmlcov/index.html"

format: ## Format code with ruff
	@echo "🎨 Formatting code..."
	$(UV) run ruff format src/ tests/
	@echo "✅ Code formatted!"

lint: ## Lint code with ruff
	@echo "🔍 Linting code..."
	$(UV) run ruff check src/ tests/ --fix
	@echo "✅ Linting complete!"

typecheck: ## Type check with mypy
	@echo "🔍 Type checking..."
	$(UV) run mypy src/$(PACKAGE)
	@echo "✅ Type checking complete!"

security: ## Run security scan with bandit
	@echo "🔒 Running security scan..."
	$(UV) run bandit -r src/$(PACKAGE) -f json -o bandit-report.json || true
	$(UV) run bandit -r src/$(PACKAGE)
	@echo "✅ Security scan complete!"

audit: format lint typecheck security ## Run all quality checks
	@echo "✅ All quality checks passed!"

clean: ## Clean build artifacts
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf bandit-report.json
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✅ Cleaned!"

build: clean ## Build package
	@echo "📦 Building package..."
	$(UV) build
	@echo "✅ Package built!"

docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker build -t aws-orchestrator:latest .
	@echo "✅ Docker image built!"

docker-run: ## Run Docker container
	@echo "🐳 Running Docker container..."
	docker run -it --rm aws-orchestrator:latest --help

docker-test: ## Run tests in Docker
	@echo "🐳 Running tests in Docker..."
	docker run -it --rm aws-orchestrator:latest pytest

init-project: ## Initialize new orchestrator project
	@echo "🎯 Initializing new project..."
	$(UV) run aws-orchestrator init --name my-orchestrator --region us-east-1

demo: ## Run full demo
	@echo "🎬 Running full demo..."
	@echo "\n1️⃣  Checking health..."
	$(UV) run aws-orchestrator health
	@echo "\n2️⃣  Listing agents..."
	$(UV) run aws-orchestrator agents
	@echo "\n3️⃣  Processing query..."
	$(UV) run aws-orchestrator run "Analyze sales data from last quarter" --user-id demo-user

.DEFAULT_GOAL := help
