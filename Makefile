# Makefile for Agno-AGI Marketing Automation System

.PHONY: help install format lint test run demo clean setup-dev

# Default target
help: ## Show this help
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	pip install -r requirements.txt

setup-dev: ## Setup development environment
	python -m venv venv
	source venv/bin/activate && pip install -r requirements.txt
	@echo "✅ Development environment setup complete!"
	@echo "Activate with: source venv/bin/activate"
	@echo "To enable pre-commit hooks (optional), run: make install-hooks"

install-hooks: ## Install pre-commit hooks (optional)
	source venv/bin/activate && pre-commit install
	@echo "✅ Pre-commit hooks installed (will run on git commit)"

format: ## Format code with black, isort, and autoflake
	black --line-length=100 src/ config/ main.py
	isort --profile=black --line-length=100 src/ config/ main.py
	autoflake --remove-all-unused-imports --remove-unused-variables --in-place --recursive src/ config/ main.py
	@echo "✅ Code formatted successfully!"

lint: ## Run linting with flake8
	flake8 --max-line-length=100 --extend-ignore=E203,W503,E501,F401,F841 src/ config/ main.py

typecheck: ## Run type checking with mypy
	mypy src/ config/ main.py --ignore-missing-imports --no-strict-optional

security: ## Run security checks with bandit
	bandit -r src/ config/ main.py -f json || true

check: format lint ## Run all code quality checks
	@echo "✅ All checks completed!"

test: ## Run tests (placeholder)
	@echo "Tests not yet implemented"

run: ## Run the main application
	python main.py

demo: ## Run the demo
	python src/demo.py

simple-demo: ## Run the simple demo
	python src/simple_demo.py

clean: ## Clean up temporary files and cache
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@echo "✅ Cleaned up temporary files!"

precommit: ## Run pre-commit hooks manually on all files
	pre-commit run --all-files

git-setup: ## Setup Git repository (without auto-hooks)
	git init
	@echo "✅ Git repository initialized!"
	@echo "To install pre-commit hooks, run: make install-hooks"

# Development shortcuts
dev: setup-dev ## Alias for setup-dev

# Quick quality check before committing (manual)
pre-commit-check: format lint ## Quick check before committing
	@echo "✅ Ready for commit!"
