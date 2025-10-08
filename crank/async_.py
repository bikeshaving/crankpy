"""
Crank.py async module - Async utilities for Suspense, lazy loading, etc.
"""
from pyscript.js_modules import crank_async

# Export async utilities
lazy = crank_async.lazy
Suspense = crank_async.Suspense
SuspenseList = crank_async.SuspenseList

__all__ = ['lazy', 'Suspense', 'SuspenseList']
