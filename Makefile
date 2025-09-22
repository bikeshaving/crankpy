.PHONY: test test-unit test-integration test-main build serve-examples serve-test-server serve-pyscript-cli-test clean help

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

serve-test-server:  ## Start test server for integration tests (http://localhost:3333)
	python -m http.server 3333

serve-pyscript-cli-test:  ## Start server for PyScript CLI compatibility test (http://localhost:3334)
	@echo "Starting PyScript CLI compatibility test at http://localhost:3334"
	@echo "Testing crankpy integration with PyScript CLI configuration"
	cd test_pyscript_cli && python -m http.server 3334

build:  ## Build package for distribution
	uv run python -m build

serve-examples:  ## Start local server for examples (http://localhost:3333/examples/)
	@echo "Starting server at http://localhost:3333"
	@echo "Examples available at http://localhost:3333/examples/"
	python -m http.server 3333

clean:  ## Clean build artifacts
	rm -rf dist/ build/ *.egg-info/ .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

publish:  ## Build and publish to PyPI (requires TWINE_PASSWORD)
	$(MAKE) clean
	$(MAKE) build
	uv run twine upload dist/*

dev-install:  ## Install in development mode with dev dependencies
	uv sync --extra dev