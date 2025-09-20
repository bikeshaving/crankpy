# Contributing to Crank.py

Thank you for your interest in contributing to Crank.py! This project aims to provide a 1:1 Python mapping of the Crank JavaScript framework.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/bikeshaving/crankpy.git crankpy
   cd crankpy
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

## Running Tests

```bash
# Run all tests
python -m pytest test_crank.py -v

# Run specific test
python -m pytest test_crank.py::test_create_element -v

# Run basic functionality test
python test_crank.py
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
4. Run the test suite: `python -m pytest test_crank.py`
5. Update documentation as needed
6. Submit a pull request with a clear description

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