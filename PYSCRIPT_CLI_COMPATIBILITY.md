# PyScript CLI + Crankpy Compatibility Research

## PyScript CLI Overview

The PyScript CLI is a command-line tool that simplifies creating and serving PyScript applications. It provides:

### Installation
```bash
pip install pyscript
# or
uv add pyscript
```

### Main Commands
- **`pyscript create <project-name>`** - Create new PyScript project with interactive setup
- **`pyscript create --wrap <script.py>`** - Wrap existing Python script in PyScript HTML
- **`pyscript run <path> --port <port>`** - Serve PyScript application locally

### Key Features
- Generates `pyscript.toml` configuration files
- Creates HTML templates pre-configured with PyScript
- Supports JavaScript module integration via `js_modules` configuration
- Interactive project setup with metadata collection

## PyScript Configuration (`pyscript.toml`)

PyScript uses TOML or JSON configuration files with these key sections:

### JavaScript Modules
```toml
[js_modules.main]
"https://cdn.jsdelivr.net/npm/@b9g/crank@0.7.1/+esm" = "crank_core"
"https://cdn.jsdelivr.net/npm/some-lib" = "some_lib"
```

### File Fetching
```toml
[[fetch]]
files = ["../crank/__init__.py", "../crank/dom.py"]
to_folder = "crank"
```

### Project Metadata
```toml
[project]
name = "My PyScript App"
description = "A PyScript application"
version = "1.0.0"
author = "Your Name"
email = "your.email@example.com"
```

## Crankpy Compatibility

### ✅ What Works
1. **JavaScript Module Integration** - Crank.js can be loaded via `js_modules.main`
2. **File Fetching** - Crankpy source files can be fetched using `[[fetch]]` configuration
3. **Standard PyScript Features** - All standard PyScript functionality works with crankpy
4. **Component System** - Crankpy components work within PyScript CLI projects

### 🔧 Configuration Required
To use crankpy with PyScript CLI projects, you need:

1. **Add Crank.js to js_modules**:
   ```toml
   [js_modules.main]
   "https://cdn.jsdelivr.net/npm/@b9g/crank@0.7.1/+esm" = "crank_core"
   ```

2. **Fetch crankpy source files**:
   ```toml
   [[fetch]]
   files = ["../crank/__init__.py", "../crank/dom.py", "../crank/html.py", "../crank/async.py"]
   to_folder = "crank"
   ```

3. **Use standard crankpy imports**:
   ```python
   from pyscript.js_modules import crank_core
   from crank import h, component
   from crank.dom import renderer
   ```

### 📁 Test Project Structure
```
test_pyscript_cli/
├── pyscript.toml     # PyScript configuration
├── main.py           # Python application code
└── index.html        # HTML template
```

### 🚀 Running the Test
```bash
# Start the compatibility test server
make serve-pyscript-cli-test

# Visit http://localhost:3334 to see crankpy working with PyScript CLI
```

## Recommendations

1. **Use PyScript CLI** for quick prototyping and development of crankpy applications
2. **Manual Configuration** required - PyScript CLI doesn't auto-detect crankpy dependencies
3. **File Organization** - Keep crankpy source files accessible for the `[[fetch]]` configuration
4. **Development Workflow** - Use `pyscript run` for local development, standard build tools for production

## Limitations

1. **No Auto-Detection** - PyScript CLI doesn't automatically configure crankpy dependencies
2. **Manual Setup** - Requires manual `pyscript.toml` configuration for each project
3. **Path Dependencies** - Fetched files need correct relative paths to crankpy source

## Conclusion

✅ **Crankpy is compatible with PyScript CLI** with proper configuration. The integration requires manual setup of `js_modules` and file fetching, but once configured, crankpy components work seamlessly within PyScript CLI projects.

The test project at `test_pyscript_cli/` demonstrates a working integration with:
- Component creation and rendering
- Event handling and state management  
- Proper PyScript CLI project structure
- JavaScript module integration