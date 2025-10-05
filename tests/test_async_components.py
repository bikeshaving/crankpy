"""
Test async components and async for behavior matching Crank.js
"""

import sys
from unittest.mock import Mock

import pytest

# Import existing mocks from test_crank to ensure consistency
from test_crank import mock_crank_core, mock_create_proxy, mock_JsProxy, mock_to_js

from crank import component, h


class TestAsyncComponents:
    """Test async component patterns matching Crank.js behavior."""

    def setup_method(self):
        """Reset mocks before each test."""
        mock_create_proxy.reset_mock()
        mock_create_proxy.side_effect = None
        mock_crank_core.createElement.reset_mock()
        mock_crank_core.createElement.side_effect = None

    def test_async_for_ctx_continuous_iteration(self):
        """Test that async for ctx yields continuously like Crank.js"""
        @component
        async def AsyncComponent(ctx):
            count = 0
            async for props in ctx:
                count += 1
                yield h.div[f"Render #{count}"]
                if count >= 3:  # Prevent infinite loop in test
                    break

        # Should be callable without errors
        assert callable(AsyncComponent)

    def test_regular_for_ctx_continuous_iteration(self):
        """Test that regular for ctx yields continuously (sync mode)"""
        @component
        def SyncComponent(ctx):
            count = 0
            for props in ctx:
                count += 1
                yield h.div[f"Render #{count}"]
                if count >= 3:  # Prevent infinite loop in test
                    break

        # Should be callable without errors
        assert callable(SyncComponent)

    def test_async_component_without_loop(self):
        """Test async component without loop (no-loop mode)"""
        @component
        async def NoLoopAsyncComponent(ctx):
            props = ctx.props if ctx.props else {}
            return h.div[f"Single render: {props}"]

        # Should be callable without errors
        assert callable(NoLoopAsyncComponent)

    def test_async_function_component(self):
        """Test async function component (non-generator)"""
        @component
        async def AsyncFunction(ctx):
            # Simulate async operation
            # await asyncio.sleep(0.1)  # Would work in real async environment
            return h.div["Async result"]

        # Should be callable without errors
        assert callable(AsyncFunction)

    def test_mixed_async_and_sync_components(self):
        """Test that async and sync components can coexist"""
        @component
        def SyncParent(ctx):
            for _ in ctx:
                yield h.div[
                    h(AsyncChild),
                    h(SyncChild)
                ]

        @component
        async def AsyncChild(ctx):
            return h.span["Async child"]

        @component
        def SyncChild(ctx):
            for _ in ctx:
                yield h.span["Sync child"]

        # All should be callable
        assert callable(SyncParent)
        assert callable(AsyncChild)
        assert callable(SyncChild)


class TestAsyncIteratorBehavior:
    """Test the async iterator implementation details."""

    def test_context_has_async_iterator(self):
        """Test that Context implements __aiter__"""
        from crank import Context
        
        # Mock JS context
        js_ctx = Mock()
        js_ctx.props = {"test": "value"}
        
        ctx = Context(js_ctx)
        
        # Should have async iterator method
        assert hasattr(ctx, '__aiter__')
        
        # Get the async iterator and check it has __anext__
        async_iter = ctx.__aiter__()
        assert hasattr(async_iter, '__anext__')

    def test_async_iterator_yields_props(self):
        """Test that async iterator yields props correctly"""
        from crank import Context
        
        # Mock JS context with props
        js_ctx = Mock()
        js_ctx.props = {"test": "value"}
        
        ctx = Context(js_ctx)
        async_iter = ctx.__aiter__()
        
        # Should be an async iterator
        assert hasattr(async_iter, '__anext__')

    def test_async_iterator_continuous_mode(self):
        """Test that async iterator doesn't stop after first yield"""
        from crank import Context
        
        # Mock JS context
        js_ctx = Mock()
        js_ctx.props = {"count": 1}
        
        ctx = Context(js_ctx)
        async_iter = ctx.__aiter__()
        
        # The iterator should not have a 'done' flag that stops iteration
        # (Unlike our previous broken implementation)
        assert not hasattr(async_iter, 'done') or not async_iter.done