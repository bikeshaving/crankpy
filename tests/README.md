# Crank.py Test Suite

This directory contains the **upytest-based test suite** for Crank.py. These tests run directly in browser environments using PyScript's official testing framework.

## 🎯 **Testing Philosophy**

Crank.py is designed for **PyScript environments** (Pyodide and MicroPython), so we test in the **actual deployment environments** rather than mocking or using CPython locally.

## 🧪 Test Structure

### Test Files

- **`test_components.py`** - Component functionality tests
  - Basic component creation and decoration
  - Props handling and state management  
  - Lifecycle methods and context iteration
  - Async/sync generator compatibility

- **`test_hyperscript.py`** - Hyperscript syntax tests
  - Element creation and attributes
  - Fragment handling (Python lists)
  - Complex props and nested structures
  - Special HTML elements (forms, media, tables)

- **`test_cross_runtime.py`** - Cross-runtime compatibility tests
  - Runtime detection and identification
  - MicroPython vs Pyodide behavior differences
  - Module availability testing
  - Conditional test skipping

- **`conftest.py`** - Global setup and teardown
  - Test environment initialization
  - Runtime-specific configuration
  - Import verification

## 🚀 Running Tests

### Browser Test Runners

**Pyodide Runner:**
```
http://localhost:3333/test_upytest_runner.html
```

**MicroPython Runner:**
```
http://localhost:3333/test_upytest_runner_micropython.html
```

### Playwright Integration Tests

```bash
# Run all upytest integration tests
uv run python -m pytest test_upytest_integration.py -v

# Run specific runtime tests
uv run python -m pytest test_upytest_integration.py::TestUpytestPyodideIntegration -v
uv run python -m pytest test_upytest_integration.py::TestUpytestMicroPythonIntegration -v
```

## 📊 Test Results

### Expected Results

**Pyodide:**
- ✅ 57+ tests passed
- ⏭️ 1 test skipped (MicroPython-only)
- 🧪 Full async generator support

**MicroPython:**
- ✅ 58+ tests passed  
- ⏭️ 1 test skipped (Pyodide-only)
- 🧪 Proper async generator limitation handling

## 🔧 upytest Features Used

### Test Discovery
- Automatic discovery of `test_*` functions
- Support for `Test*` classes with `test_*` methods
- File-based test organization

### Skip Decorators
```python
import upytest

@upytest.skip("Skip in MicroPython", skip_when=upytest.is_micropython)
def test_pyodide_only_feature():
    pass

@upytest.skip("Skip in Pyodide", skip_when=not upytest.is_micropython)  
def test_micropython_only_feature():
    pass
```

### Exception Testing
```python
def test_exceptions():
    with upytest.raises(ValueError):
        raise ValueError("Expected error")
```

### Setup/Teardown
```python
# conftest.py
def setup():
    """Called before each test"""
    pass

def teardown():
    """Called after each test"""
    pass
```

## 🏗️ Architecture

### Cross-Runtime Compatibility

The test suite is designed to work identically in both runtimes:

1. **Runtime Detection**: Uses `sys.implementation.name` and `upytest.is_micropython`
2. **Conditional Testing**: Tests adapt behavior based on runtime capabilities
3. **Graceful Degradation**: MicroPython limitations are handled transparently
4. **Consistent API**: Same test code runs in both environments

### Test Categories

1. **Unit Tests**: Individual function/component testing
2. **Integration Tests**: Component + hyperscript interaction
3. **Compatibility Tests**: Cross-runtime behavior verification
4. **Feature Tests**: Specific Crank.py feature validation

## 🔍 Debugging

### Viewing Test Output

The browser test runners provide detailed output including:
- Test execution progress (dots, F, S)
- Failure tracebacks
- Runtime information
- Timing data
- Colored status indicators

### Common Issues

**Import Errors:**
- Verify all Crank.py files are properly configured in HTML
- Check file paths in py-config/mpy-config

**Timeout Issues:**
- MicroPython tests may take longer than Pyodide
- Increase Playwright timeout if needed

**Runtime Differences:**
- Some tests may behave differently between runtimes
- Use conditional logic for runtime-specific expectations

## 📈 Migration from Custom Tests

This upytest suite replaces our previous custom implementation because:

1. **Official Support**: Maintained by PyScript team
2. **Cross-Runtime**: Works in both Pyodide and MicroPython  
3. **Full pytest Compatibility**: Familiar syntax and features
4. **Professional Output**: Proper test reporting and formatting
5. **Exception Handling**: Robust error handling across runtimes

The migration provides a more maintainable and feature-complete testing solution while ensuring compatibility with both Python runtimes supported by PyScript.