.PHONY: test test-unit test-integration test-main build serve clean help

help:  ## Show this help message
	@echo "Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

test:  ## Run all tests (unit + integration)
	uv run python -m pytest -v

test-unit:  ## Run unit tests only
	uv run python -m pytest tests/test_crank.py -v

test-integration:  ## Run Playwright integration tests
	uv run python -m pytest tests/test_integration.py -v

test-main:  ## Run main test suite (alias for test-unit)
	uv run python -m pytest tests/test_crank.py -v

lint:  ## Run ruff linter
	uv run ruff check .

lint-fix:  ## Run ruff linter and fix issues
	uv run ruff check --fix .

format:  ## Format code with ruff
	uv run ruff format .

typecheck:  ## Run pyright type checking
	uv run pyright crank/

typecheck-tests:  ## Run type checking on type-only tests
	uv run pyright tests/test_types.py

typecheck-all:  ## Run all type checking (core + tests)
	$(MAKE) typecheck
	$(MAKE) typecheck-tests

check:  ## Run all checks (lint + typecheck)
	$(MAKE) lint
	$(MAKE) typecheck

serve:  ## Start local server on port 3333
	python3 -m http.server 3333

build:  ## Build package for distribution
	uv run python -m build

clean:  ## Clean build artifacts
	rm -rf dist/ build/ *.egg-info/ .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete


dev-install:  ## Install in development mode with dev dependencies
	uv sync --extra dev