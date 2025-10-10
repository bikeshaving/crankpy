.PHONY: test build serve clean check help

help:  ## Show this help message
	@echo "Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

test:  ## Run automated upytest with pass/fail results
	@echo "🧪 Running automated upytest in both Pyodide and MicroPython"
	@if ! curl -s http://localhost:3333/ > /dev/null 2>&1; then \
		echo "❌ Server not running. Starting server..."; \
		echo "Please run 'make serve' in another terminal, then run 'make test' again."; \
		exit 1; \
	fi
	uv run --group test python tests/test_runner.py

test-pyodide:  ## Run automated upytest for Pyodide only
	uv run --group test python tests/test_runner.py --runtime pyodide

test-micropython:  ## Run automated upytest for MicroPython only
	uv run --group test python tests/test_runner.py --runtime micropython


lint:  ## Run ruff linter and formatter
	uv run ruff check --fix .
	uv run ruff format .

typecheck:  ## Run pyright type checking
	uv run pyright crank/

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
