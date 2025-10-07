.PHONY: test build serve clean check help

help:  ## Show this help message
	@echo "Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

test:  ## Run all tests
	uv run python -m pytest -v

lint:  ## Run ruff linter and formatter
	uv run ruff check --fix .
	uv run ruff format .

typecheck:  ## Run pyright type checking
	uv run pyright crank/ tests/test_types.py

check:  ## Run all checks (lint + typecheck)
	$(MAKE) lint
	$(MAKE) typecheck

serve:  ## Start local server on port 3333
	python3 -m http.server 3333

build:  ## Build package for distribution
	uv build

clean:  ## Clean build artifacts
	rm -rf dist/ build/ *.egg-info/ .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

install:  ## Install in development mode with dev dependencies
	uv sync --extra dev
