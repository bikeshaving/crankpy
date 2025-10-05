"""
Shared mock setup for tests that need to mock PyScript/Pyodide modules
"""

import sys
from unittest.mock import Mock

# Mock PyScript modules before importing crank
sys.modules['js'] = Mock()
sys.modules['pyscript'] = Mock()
sys.modules['pyscript.ffi'] = Mock()
sys.modules['pyscript.js_modules'] = Mock()
sys.modules['pyodide'] = Mock()
sys.modules['pyodide.ffi'] = Mock()

# Mock the PyScript FFI functions
mock_create_proxy = Mock()
mock_to_js = Mock()
mock_JsProxy = Mock()
sys.modules['pyscript.ffi'].create_proxy = mock_create_proxy
sys.modules['pyscript.ffi'].to_js = mock_to_js
sys.modules['pyodide.ffi'].JsProxy = mock_JsProxy

# Mock crank_core
mock_crank_core = Mock()
mock_crank_core.Element = Mock()
mock_crank_core.createElement = Mock()
mock_crank_core.Fragment = Mock()
sys.modules['pyscript.js_modules'].crank_core = mock_crank_core

# Mock JS objects
sys.modules['js'].Symbol = Mock()
sys.modules['js'].Symbol.for_ = Mock(return_value="mock_symbol")
sys.modules['js'].Object = Mock()
sys.modules['js'].document = Mock()

# Mock crank.dom
sys.modules['crank.dom'] = Mock()
mock_renderer = Mock()
sys.modules['crank.dom'].renderer = mock_renderer

# Export the mocks for use in tests
__all__ = [
    'mock_create_proxy',
    'mock_to_js', 
    'mock_JsProxy',
    'mock_crank_core',
    'mock_renderer'
]