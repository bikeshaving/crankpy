"""
Crank.py async module - Direct import of Crank's async utilities
"""

import js

# Access Crank async from global scope
_async = js.CrankAsync

lazy = _async.lazy
Suspense = _async.Suspense
SuspenseList = _async.SuspenseList

__all__ = ['lazy', 'Suspense', 'SuspenseList']