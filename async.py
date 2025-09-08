"""
Crank.py async module

Direct import of Crank's async module from JavaScript.
Exposes the exact same API: lazy, Suspense, SuspenseList, etc.
"""

from js import fetch
import js

# Import Crank's async module directly
async def _import_async():
    response = await fetch('https://cdn.jsdelivr.net/npm/@b9g/crank@latest/async.js')
    async_code = await response.text()
    return js.eval(f"(async () => {{ {async_code}; return this; }})()")

# Get the module
_async_module = await _import_async()

# Re-export exact Crank API
lazy = _async_module.lazy
Suspense = _async_module.Suspense
SuspenseList = _async_module.SuspenseList

__all__ = ['lazy', 'Suspense', 'SuspenseList']