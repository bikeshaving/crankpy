"""Crank.py async module - Suspense and lazy loading utilities."""

from pyscript.js_modules import crank_async

from . import js_component

# js_component keeps the component functions on the JavaScript side, which
# the MicroPython FFI would otherwise break. See crank/__init__.py.
Suspense = js_component(crank_async, "Suspense")
SuspenseList = js_component(crank_async, "SuspenseList")
lazy = crank_async.lazy

__all__ = ["Suspense", "SuspenseList", "lazy"]
