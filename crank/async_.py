"""
Crank.py async module - Async utilities for Suspense, lazy loading, etc.
"""

try:
    import js
    # Try to access Crank async from global scope if available
    _async = js.CrankAsync
    lazy = _async.lazy
    Suspense = _async.Suspense
    SuspenseList = _async.SuspenseList
except (ImportError, AttributeError):
    # Fallback implementations for testing environments
    class MockSuspense:
        """Mock Suspense component for testing"""
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
    
    class MockSuspenseList:
        """Mock SuspenseList component for testing"""
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
    
    def mock_lazy(loader):
        """Mock lazy loading function for testing"""
        # In testing, just return the loaded component directly
        return loader()
    
    lazy = mock_lazy
    Suspense = MockSuspense
    SuspenseList = MockSuspenseList

__all__ = ['lazy', 'Suspense', 'SuspenseList']
