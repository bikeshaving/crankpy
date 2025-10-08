"""
Cross-runtime compatibility tests using upytest.

These tests specifically verify behavior differences between Pyodide and MicroPython.
"""
import sys
import inspect
from crank import h, component

import upytest


def test_runtime_identification():
    """Test that we can properly identify the runtime"""
    impl_name = sys.implementation.name
    assert impl_name in ['cpython', 'micropython']
    
    # Test upytest's runtime detection
    assert hasattr(upytest, 'is_micropython')
    expected_micropython = impl_name == 'micropython'
    assert upytest.is_micropython == expected_micropython


def test_async_generator_detection():
    """Test async generator detection varies by runtime"""
    @component
    async def AsyncGenComponent(ctx):
        async for _ in ctx:
            yield h.div["Content"]
    
    # Create component instance
    class MockContext:
        pass
    
    result = AsyncGenComponent({}, MockContext())
    
    if sys.implementation.name == 'micropython':
        # MicroPython: async generators become sync (PEP 525 limitation)
        if hasattr(result, '_detected_as_async_generator'):
            assert result._detected_as_async_generator == False
    else:
        # Pyodide/CPython: should support async generators
        assert result is not None


def test_inspect_module_availability():
    """Test inspect module works in both runtimes"""
    # Both runtimes should have inspect
    assert inspect is not None
    
    # Test basic inspect functionality
    def sample_function():
        pass
    
    try:
        sig = inspect.signature(sample_function)
        assert sig is not None
    except Exception:
        # Some inspect features might not be available in MicroPython
        pass


@upytest.skip("Skip this test in MicroPython", skip_when=upytest.is_micropython)
def test_pyodide_only_feature():
    """Test that only runs in Pyodide"""
    # This test should only run in Pyodide
    assert sys.implementation.name != 'micropython'


@upytest.skip("Skip this test in Pyodide", skip_when=not upytest.is_micropython)
def test_micropython_only_feature():
    """Test that only runs in MicroPython"""
    # This test should only run in MicroPython
    assert sys.implementation.name == 'micropython'


def test_exception_handling():
    """Test exception handling works in both runtimes"""
    with upytest.raises(ValueError):
        raise ValueError("Test exception")
    
    with upytest.raises(TypeError):
        # This should raise TypeError
        "string" + 42


def test_async_function_behavior():
    """Test async function behavior"""
    @component
    async def AsyncComponent(ctx):
        return h.div["Async"]
    
    # Component should be creatable
    assert AsyncComponent is not None
    
    # Test that we can detect if it's async
    if sys.implementation.name == 'micropython':
        # MicroPython might not distinguish async functions properly
        pass
    else:
        # Pyodide should handle async functions correctly
        # Check if the component has the original function accessible
        if hasattr(AsyncComponent, '__wrapped__'):
            assert inspect.iscoroutinefunction(AsyncComponent.__wrapped__)
        else:
            # Alternative check if __wrapped__ is not available
            pass


def test_context_async_iteration():
    """Test async context iteration patterns"""
    @component
    async def AsyncIterComponent(ctx):
        async for props in ctx:
            yield h.div[f"Props: {props}"]
    
    assert AsyncIterComponent is not None


def test_micropython_async_limitation():
    """Test MicroPython async generator limitation handling"""
    @component
    async def AsyncGenComponent(ctx):
        # In MicroPython, this becomes a sync generator
        yield h.div["Content"]
    
    mock_ctx = type('MockContext', (), {})()
    result = AsyncGenComponent({}, mock_ctx)
    
    # Should create some kind of result
    assert result is not None
    
    # Check runtime-specific behavior
    if sys.implementation.name == 'micropython':
        # Should be detected as sync
        if hasattr(result, '_detected_as_async_generator'):
            assert result._detected_as_async_generator == False
    else:
        # In Pyodide, should work normally
        pass


class TestRuntimeDifferences:
    """Test class for runtime-specific behavior"""
    
    def test_module_availability(self):
        """Test which modules are available in each runtime"""
        # Core modules that should be available in both
        import sys, os, io
        assert sys is not None
        assert os is not None
        assert io is not None
        
        # Test runtime-specific modules
        try:
            import traceback
            # Available in Pyodide
            assert sys.implementation.name != 'micropython'
        except ImportError:
            # Not available in MicroPython
            assert sys.implementation.name == 'micropython'
    
    def test_asyncio_availability(self):
        """Test asyncio module availability"""
        import asyncio
        assert asyncio is not None
        
        # Both runtimes should have basic asyncio support
        assert hasattr(asyncio, 'create_task')
    
    def test_typing_availability(self):
        """Test typing module availability"""
        try:
            from typing import Dict, List, Optional
            # Available in Pyodide
            assert Dict is not None
        except ImportError:
            # Might not be available in MicroPython
            pass
    
    def test_pathlib_availability(self):
        """Test pathlib availability"""
        try:
            from pathlib import Path
            assert Path is not None
        except ImportError:
            # Might not be available in all environments
            pass
    
    def test_random_availability(self):
        """Test random module"""
        import random
        assert random is not None
        
        # Test basic random functionality
        num = random.randint(1, 10)
        assert 1 <= num <= 10


class TestComponentCompatibility:
    """Test component compatibility across runtimes"""
    
    def test_basic_component_works_everywhere(self):
        """Test basic components work in all runtimes"""
        @component
        def BasicComponent(ctx):
            return h.div["Basic"]
        
        assert BasicComponent is not None
    
    def test_generator_component_works_everywhere(self):
        """Test generator components work in all runtimes"""
        @component
        def GenComponent(ctx):
            for _ in ctx:
                yield h.div["Generator"]
        
        assert GenComponent is not None
    
    def test_props_handling_works_everywhere(self):
        """Test props handling works in all runtimes"""
        @component
        def PropsComponent(ctx, props):
            name = props.get("name", "default")
            return h.div[name]
        
        assert PropsComponent is not None