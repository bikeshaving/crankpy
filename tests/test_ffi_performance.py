"""
Performance and stress tests for FFI functionality

Tests performance characteristics and edge cases:
- Large number of proxies
- Deep nesting scenarios
- Performance benchmarks
- Memory usage patterns
"""

import pytest
import time
import sys
from unittest.mock import Mock, patch
from crank import h, component, ElementBuilder, MagicH


class TestFFIPerformance:
    """Test FFI performance characteristics"""
    
    @patch('crank.create_proxy')
    def test_many_proxies_creation(self, mock_create_proxy):
        """Test creating many proxies doesn't degrade performance"""
        mock_proxy = Mock()
        mock_create_proxy.return_value = mock_proxy
        
        # Create many handlers
        handlers = []
        for i in range(1000):
            def handler(i=i):  # Capture i in closure
                return f"handler_{i}"
            handlers.append(handler)
        
        start_time = time.time()
        
        # Process all handlers through FFI
        builder = ElementBuilder("div")
        props = {f"handler_{i}": handlers[i] for i in range(1000)}
        result = builder._process_props_for_proxies(props)
        
        end_time = time.time()
        
        # Should complete in reasonable time (< 1 second)
        assert end_time - start_time < 1.0
        assert mock_create_proxy.call_count == 1000
        assert len(result) == 1000
    
    @patch('crank.create_proxy')
    def test_deep_nesting_performance(self, mock_create_proxy):
        """Test deep nesting doesn't cause exponential slowdown"""
        mock_proxy = Mock()
        mock_create_proxy.return_value = mock_proxy
        
        def create_handler():
            return lambda: "test"
        
        # Create deeply nested structure
        props = {"handler": create_handler()}
        current = props
        
        # Create 100 levels of nesting
        for i in range(100):
            current["nested"] = {"handler": create_handler()}
            current = current["nested"]
        
        start_time = time.time()
        
        builder = ElementBuilder("div")
        result = builder._process_props_for_proxies(props)
        
        end_time = time.time()
        
        # Should complete in reasonable time
        assert end_time - start_time < 1.0
        # Should have created proxies for all handlers
        assert mock_create_proxy.call_count == 101  # 1 + 100 nested
    
    def test_repeated_proxy_checks(self):
        """Test performance of repeated proxy checks"""
        # Mock already proxied function
        already_proxied = Mock()
        already_proxied.toString = Mock()  # JS proxy indicator
        
        props = {"handler": already_proxied}
        
        builder = ElementBuilder("div")
        
        start_time = time.time()
        
        # Process same props many times
        for _ in range(1000):
            result = builder._process_props_for_proxies(props)
        
        end_time = time.time()
        
        # Should be fast since no proxy creation needed
        assert end_time - start_time < 0.5
    
    @patch('crank.to_js')
    def test_large_object_conversion(self, mock_to_js):
        """Test performance of converting large objects"""
        mock_js_obj = Mock()
        mock_to_js.return_value = mock_js_obj
        
        # Create large props object
        large_props = {}
        for i in range(1000):
            large_props[f"prop_{i}"] = f"value_{i}"
        
        start_time = time.time()
        
        builder = ElementBuilder("div", large_props)
        builder["content"]
        
        end_time = time.time()
        
        # Should complete in reasonable time
        assert end_time - start_time < 1.0
        mock_to_js.assert_called()


class TestFFIStressTests:
    """Stress tests for FFI functionality"""
    
    @patch('crank.create_proxy')
    def test_component_creation_stress(self, mock_create_proxy):
        """Test creating many components with FFI"""
        mock_proxy = Mock()
        mock_create_proxy.return_value = mock_proxy
        
        components = []
        
        start_time = time.time()
        
        # Create 100 components
        for i in range(100):
            @component
            def TestComponent(ctx, name=f"component_{i}"):
                return h.div[name]
            
            components.append(TestComponent)
        
        end_time = time.time()
        
        # Should complete quickly
        assert end_time - start_time < 2.0
        assert mock_create_proxy.call_count == 100
        assert len(components) == 100
    
    def test_context_method_stress(self):
        """Test Context methods under stress"""
        from crank import Context
        
        # Mock JS context
        js_ctx = Mock()
        js_ctx.refresh = Mock()
        js_ctx.schedule = Mock()
        js_ctx.after = Mock()
        js_ctx.cleanup = Mock()
        
        ctx = Context(js_ctx)
        
        # Create many functions to register
        functions = [lambda i=i: f"func_{i}" for i in range(100)]
        
        start_time = time.time()
        
        # Register all functions
        for func in functions:
            ctx.schedule(func)
            ctx.after(func)
            ctx.cleanup(func)
        
        end_time = time.time()
        
        # Should complete quickly
        assert end_time - start_time < 1.0
        assert js_ctx.schedule.call_count == 100
        assert js_ctx.after.call_count == 100
        assert js_ctx.cleanup.call_count == 100
    
    @patch('crank.create_proxy')
    def test_magic_h_stress(self, mock_create_proxy):
        """Test MagicH under stress conditions"""
        mock_proxy = Mock()
        mock_create_proxy.return_value = mock_proxy
        
        magic_h = MagicH()
        handlers = [lambda i=i: f"handler_{i}" for i in range(50)]
        
        start_time = time.time()
        
        # Create many elements with handlers
        elements = []
        for i in range(50):
            element = magic_h.div(
                onClick=handlers[i],
                onMouseOver=handlers[i],
                id=f"element_{i}"
            )[f"Element {i}"]
            elements.append(element)
        
        end_time = time.time()
        
        # Should complete in reasonable time
        assert end_time - start_time < 2.0
        assert len(elements) == 50
        # Each element has 2 handlers = 100 total
        assert mock_create_proxy.call_count == 100


class TestFFIEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_empty_iterations(self):
        """Test handling of empty iterations"""
        from crank import Context
        
        js_ctx = Mock()
        js_ctx.__iter__ = Mock(return_value=iter([]))  # Empty iterator
        
        ctx = Context(js_ctx)
        
        # Should handle empty iteration gracefully
        result = list(ctx)
        assert result == []
    
    def test_very_long_prop_names(self):
        """Test handling of very long property names"""
        builder = ElementBuilder("div")
        
        # Create prop with very long name
        long_name = "a" * 1000
        props = {long_name: "value"}
        
        # Should not crash
        result = builder._process_props_for_proxies(props)
        assert result[long_name] == "value"
    
    def test_unicode_in_props(self):
        """Test handling of Unicode in props"""
        builder = ElementBuilder("div")
        
        unicode_props = {
            "emoji": "🚀🎉",
            "chinese": "你好世界",
            "arabic": "مرحبا بالعالم",
            "handler_émoji": lambda: "🎯"
        }
        
        # Should handle Unicode correctly
        result = builder._process_props_for_proxies(unicode_props)
        assert result["emoji"] == "🚀🎉"
        assert result["chinese"] == "你好世界"
        assert result["arabic"] == "مرحبا بالعالم"
    
    def test_numeric_prop_names(self):
        """Test handling of numeric property names"""
        builder = ElementBuilder("div")
        
        # Props with numeric names (converted to strings)
        numeric_props = {
            123: "numeric key",
            "456": "string numeric key",
            "handler_789": lambda: "numeric handler"
        }
        
        # Should handle without crashing
        result = builder._process_props_for_proxies(numeric_props)
        assert len(result) == 3
    
    @patch('crank.create_proxy')
    def test_none_values_in_nested_structures(self, mock_create_proxy):
        """Test None values in complex nested structures"""
        mock_proxy = Mock()
        mock_create_proxy.return_value = mock_proxy
        
        props = {
            "nested": {
                "value": None,
                "handler": lambda: "test",
                "deep": {
                    "nullValue": None,
                    "anotherHandler": lambda: "deep"
                }
            },
            "listWithNones": [None, lambda: "list", None],
            "topLevel": None
        }
        
        builder = ElementBuilder("div")
        result = builder._process_props_for_proxies(props)
        
        # Should handle None values gracefully
        assert result["nested"]["value"] is None
        assert result["nested"]["deep"]["nullValue"] is None
        assert result["listWithNones"][0] is None
        assert result["listWithNones"][2] is None
        assert result["topLevel"] is None
        
        # Should still proxy the handlers
        mock_create_proxy.assert_any_call(props["nested"]["handler"])
        mock_create_proxy.assert_any_call(props["nested"]["deep"]["anotherHandler"])
        mock_create_proxy.assert_any_call(props["listWithNones"][1])


class TestFFIMemoryUsage:
    """Test memory usage patterns"""
    
    def test_proxy_reference_cleanup(self):
        """Test that proxy references don't cause memory leaks"""
        # This is more of a conceptual test since we can't easily
        # measure memory in unit tests, but we can test patterns
        
        from crank import Context
        
        js_ctx = Mock()
        js_ctx.schedule = Mock()
        
        ctx = Context(js_ctx)
        
        # Create and register many functions
        for i in range(100):
            def temp_func(i=i):
                return f"temp_{i}"
            
            ctx.schedule(temp_func)
            # temp_func should be eligible for garbage collection
            # after this iteration (if not held by proxy)
        
        # All functions should have been registered
        assert js_ctx.schedule.call_count == 100
    
    @patch('crank.create_proxy')
    def test_repeated_element_creation(self, mock_create_proxy):
        """Test memory behavior with repeated element creation"""
        mock_proxy = Mock()
        mock_create_proxy.return_value = mock_proxy
        
        handler = lambda: "test"
        
        # Create many elements with same handler
        for i in range(100):
            h.button(onClick=handler, id=f"btn_{i}")["Button"]
        
        # Handler should be proxied many times (no caching)
        assert mock_create_proxy.call_count == 100
    
    def test_large_component_trees(self):
        """Test behavior with large component trees"""
        @component
        def LeafComponent(ctx, props):
            return h.div[props.get("content", "leaf")]
        
        @component  
        def BranchComponent(ctx, props):
            depth = props.get("depth", 0)
            if depth <= 0:
                return h(LeafComponent, content=f"leaf_{depth}")
            
            return h.div[
                h(BranchComponent, depth=depth-1),
                h(BranchComponent, depth=depth-1)
            ]
        
        # Create deep tree (2^5 = 32 leaf nodes)
        tree = h(BranchComponent, depth=5)
        
        # Should create without issues
        assert tree is not None


if __name__ == '__main__':
    pytest.main([__file__, "-v"])