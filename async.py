"""
Crank.py async module - Direct import of Crank's async utilities
"""

from js import fetch

async def _import_async():
    response = await fetch('https://cdn.jsdelivr.net/npm/@b9g/crank@latest/async.js')
    code = await response.text()
    return js.eval(f"(() => {{ {code}; return this; }})()")

_async = await _import_async()

lazy = _async.lazy
Suspense = _async.Suspense
SuspenseList = _async.SuspenseList

__all__ = ['lazy', 'Suspense', 'SuspenseList']