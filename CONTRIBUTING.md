# Contributing to Crank.py

Thank you for your interest in contributing to Crank.py! This project aims to provide a 1:1 Python mapping of the Crank JavaScript framework.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/bikeshaving/crankpy.git crankpy
   cd crankpy
   ```

2. Install [uv](https://docs.astral.sh/uv/) if you haven't already:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. Install dependencies and set up development environment:
   ```bash
   make install
   ```

## Development Commands

Use the Makefile for all development tasks:

```bash
# Install dependencies
make install

# Run all tests (144+ comprehensive tests)
make test

# Run only unit tests
make test-unit

# Run integration tests (Playwright browser tests)
make test-integration

# Code quality checks
make lint          # Run ruff linter
make lint-fix      # Fix linting issues
make format        # Format code
make typecheck     # Run pyright type checking
make check         # Run both lint + typecheck

# Development server
make serve         # Start server on port 3333

# Build and clean
make build         # Build package
make clean         # Clean build artifacts

# Help
make help          # Show all available commands
```

## Code Style

This project follows Python best practices:

- Use type hints for all public APIs
- Follow PEP 8 for code style
- Write docstrings for all public functions and classes
- Maintain 1:1 correspondence with Crank JavaScript APIs

## Maintaining 1:1 Mappings

When contributing, ensure Python APIs map directly to JavaScript Crank:

| JavaScript | Python |
|------------|--------|
| `function Component()` | `@component def component()` |
| `async function Component()` | `@async_component async def component()` |
| `function* Component()` | `@generator_component def component()` |
| `async function* Component()` | `@async_generator_component async def component()` |

## Adding New Features

1. Check if the feature exists in JavaScript Crank
2. Implement the Python equivalent maintaining the same API surface
3. Add comprehensive tests
4. Update documentation and examples
5. Ensure PyScript compatibility

## Documentation

- Update README.md for user-facing changes
- Add examples to examples.py for new features
- Include docstrings with examples for new APIs

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes with tests
4. Run quality checks: `make check`
5. Run the test suite: `make test`
6. Update documentation as needed
7. Submit a pull request with a clear description

## Release Process

Releases are automated:
1. Update version in `pyproject.toml`
2. Create a Git tag: `git tag v0.x.x`
3. Push tag: `git push origin v0.x.x`
4. GitHub Actions will build and publish to PyPI

## Questions?

- Open an issue for bugs or feature requests
- Reference the main Crank repository for JavaScript API questions
- Check existing issues and discussions