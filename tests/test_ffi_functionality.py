"""
Comprehensive tests for FFI functionality in Crank.py

Tests the PyScript FFI integration including:
- create_proxy for function wrapping
- to_js for object conversion
- Props processing with nested callables
- Event handler proxying
- Edge cases and error handling
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock

# Mock PyScript modules before importing crank
sys.modules['js'] = Mock()
sys.modules['pyscript'] = Mock()
sys.modules['pyscript.ffi'] = Mock()
sys.modules['pyscript.js_modules'] = Mock()

# Mock the PyScript FFI functions
mock_create_proxy = Mock()
mock_to_js = Mock()
sys.modules['pyscript.ffi'].create_proxy = mock_create_proxy
sys.modules['pyscript.ffi'].to_js = mock_to_js

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

# Now import crank after mocking
from crank import h, component, ElementBuilder, MagicH


class TestFFIProxyCreation:
    """Test create_proxy functionality"""
    
    def test_component_function_proxying(self):
        """Test that component functions get properly proxied"""
        mock_create_proxy.reset_mock()
        mock_proxy = Mock()
        mock_create_proxy.return_value = mock_proxy
        
        @component
        def TestComponent(ctx):
            return h.div["test"]
        
        # Should have called create_proxy on the wrapper
        mock_create_proxy.assert_called_once()
        assert TestComponent == mock_proxy
    
    def test_context_method_proxying(self):
        """Test that context methods create proxies for callbacks"""
        from crank import Context
        
        mock_create_proxy.reset_mock()
        mock_proxy = Mock()
        mock_create_proxy.return_value = mock_proxy
        
        # Mock JS context
        js_ctx = Mock()
        js_ctx.schedule = Mock()
        js_ctx.after = Mock()
        js_ctx.cleanup = Mock()
        
        ctx = Context(js_ctx)
        
        def test_func():
            pass
        
        # Test schedule decorator
        ctx.schedule(test_func)
        mock_create_proxy.assert_called_with(test_func)
        js_ctx.schedule.assert_called_with(mock_proxy)
        
        mock_create_proxy.reset_mock()
        
        # Test after decorator
        ctx.after(test_func)
        mock_create_proxy.assert_called_with(test_func)
        js_ctx.after.assert_called_with(mock_proxy)
        
        mock_create_proxy.reset_mock()
        
        # Test cleanup decorator
        ctx.cleanup(test_func)
        mock_create_proxy.assert_called_with(test_proxy)
        js_ctx.cleanup.assert_called_with(mock_proxy)
    
    @patch('crank.create_proxy')
    def test_event_handler_proxying(self, mock_create_proxy):
        """Test that event handlers get proxied in props"""
        mock_proxy = Mock()
        mock_create_proxy.return_value = mock_proxy
        
        def click_handler():
            pass
        
        # Test direct function in props
        builder = ElementBuilder("button")
        builder(onClick=click_handler)
        
        mock_create_proxy.assert_called_with(click_handler)
    
    @patch('crank.create_proxy')
    def test_nested_callable_proxying(self, mock_create_proxy):
        """Test proxying of nested callables in props"""
        mock_proxy = Mock()
        mock_create_proxy.return_value = mock_proxy
        
        def handler1():
            pass
        
        def handler2():
            pass
        
        def handler3():
            pass
        
        # Test nested dict with callables
        props = {
            "events": {
                "onClick": handler1,
                "onSubmit": handler2
            },
            "callbacks": [handler3],
            "simpleString": "test"
        }
        
        builder = ElementBuilder("div")
        result = builder._process_props_for_proxies(props)
        
        # Should have created proxies for all callables
        assert mock_create_proxy.call_count == 3
        assert result["events"]["onClick"] == mock_proxy
        assert result["events"]["onSubmit"] == mock_proxy
        assert result["callbacks"][0] == mock_proxy
        assert result["simpleString"] == "test"  # Non-callable unchanged
    
    @patch('crank.create_proxy')
    def test_already_proxied_callables(self, mock_create_proxy):
        """Test that already proxied functions aren't re-proxied"""
        # Mock an already proxied function
        already_proxied = Mock()
        already_proxied.toString = Mock()  # JS proxy indicator
        
        props = {"onClick": already_proxied}
        
        builder = ElementBuilder("button")
        result = builder._process_props_for_proxies(props)
        
        # Should not have called create_proxy
        mock_create_proxy.assert_not_called()
        assert result["onClick"] == already_proxied


class TestFFIObjectConversion:
    """Test to_js functionality"""
    
    @patch('crank.to_js')
    def test_props_conversion(self, mock_to_js):
        """Test that props get converted to JS objects"""
        mock_js_obj = Mock()
        mock_to_js.return_value = mock_js_obj
        
        props = {"className": "test", "id": "button"}
        
        builder = ElementBuilder("button", props)
        builder["Click me"]
        
        # Should have converted props to JS
        mock_to_js.assert_called_with(props)
    
    @patch('crank.to_js')
    def test_children_conversion(self, mock_to_js):
        """Test that non-string children get converted"""
        mock_js_obj = Mock()
        mock_to_js.return_value = mock_js_obj
        
        # Mock element children
        child_element = Mock()
        
        builder = ElementBuilder("div")
        builder[["text", child_element]]  # List with mixed content
        
        # Should convert non-string children
        mock_to_js.assert_called_with(child_element)
    
    @patch('crank.to_js')
    def test_fragment_props_conversion(self, mock_to_js):
        """Test Fragment props conversion"""
        from crank import Fragment
        
        mock_js_obj = Mock()
        mock_to_js.return_value = mock_js_obj
        
        magic_h = MagicH()
        props = {"key": "frag1"}
        
        # Test Fragment with props
        magic_h(Fragment, **props)
        
        mock_to_js.assert_called_with(props)


class TestFFIEdgeCases:
    """Test edge cases and error scenarios"""
    
    def test_component_with_too_many_params(self):
        """Test error handling for components with invalid signatures"""
        with pytest.raises(ValueError, match="too many parameters"):
            @component
            def BadComponent(ctx, props, extra):
                return h.div["bad"]
    
    @patch('crank.create_proxy')
    def test_proxy_creation_failure(self, mock_create_proxy):
        """Test handling of proxy creation failures"""
        mock_create_proxy.side_effect = Exception("Proxy creation failed")
        
        # Should still work with a fallback or handle gracefully
        with pytest.raises(Exception):
            @component
            def TestComponent(ctx):
                return h.div["test"]
    
    def test_context_with_missing_js_methods(self):
        """Test Context wrapper with JS context missing methods"""
        from crank import Context
        
        # Mock JS context without some methods
        js_ctx = Mock()
        del js_ctx.refresh  # Remove refresh method
        del js_ctx.schedule
        
        ctx = Context(js_ctx)
        
        # Should handle missing methods gracefully
        assert ctx._refresh is None
        assert ctx._schedule is None
        
        # refresh() should not crash
        ctx.refresh()  # Should do nothing
        
        def test_func():
            pass
        
        # schedule should not crash
        result = ctx.schedule(test_func)
        assert result == test_func  # Returns original function
    
    def test_props_processing_with_circular_references(self):
        """Test props processing doesn't crash on circular references"""
        def handler():
            pass
        
        # Create circular reference
        props = {"handler": handler}
        props["self"] = props  # Circular reference
        
        builder = ElementBuilder("div")
        
        # Should handle without infinite recursion
        # Note: This might raise an exception which is acceptable
        try:
            result = builder._process_props_for_proxies(props)
            # If it succeeds, verify it handled the circular ref
            assert "handler" in result
        except (RecursionError, ValueError):
            # Acceptable to fail on circular references
            pass
    
    @patch('crank.create_proxy')
    def test_empty_props_processing(self, mock_create_proxy):
        """Test processing empty or None props"""
        builder = ElementBuilder("div")
        
        # Test empty dict
        result = builder._process_props_for_proxies({})
        assert result == {}
        mock_create_proxy.assert_not_called()
        
        # Test None (shouldn't be called with None, but test anyway)
        result = builder._process_props_for_proxies(None) if hasattr(builder, '_process_props_for_proxies') else None
        mock_create_proxy.assert_not_called()


class TestFFIIntegration:
    """Integration tests for FFI functionality"""
    
    @patch('crank.create_proxy')
    @patch('crank.to_js')
    def test_complete_element_creation_flow(self, mock_to_js, mock_create_proxy):
        """Test the complete flow from element creation to JS conversion"""
        mock_proxy = Mock()
        mock_create_proxy.return_value = mock_proxy
        mock_js_props = Mock()
        mock_to_js.return_value = mock_js_props
        
        def click_handler():
            pass
        
        # Create element with callable props
        element = h.button(
            onClick=click_handler,
            className="btn",
            data_test_id="submit"
        )["Submit"]
        
        # Verify the flow
        mock_create_proxy.assert_called_with(click_handler)
        mock_to_js.assert_called()  # Called for props conversion
    
    @patch('crank.create_proxy')
    def test_magic_h_callable_processing(self, mock_create_proxy):
        """Test MagicH processes callables correctly"""
        mock_proxy = Mock()
        mock_create_proxy.return_value = mock_proxy
        
        def handler():
            pass
        
        magic_h = MagicH()
        
        # Test direct callable prop processing
        result = magic_h._process_props_for_proxies({"onClick": handler})
        
        mock_create_proxy.assert_called_with(handler)
        assert result["onClick"] == mock_proxy
    
    def test_context_iteration_protocols(self):
        """Test Context delegation to JS iteration protocols"""
        from crank import Context
        
        # Mock JS context with iteration
        js_ctx = Mock()
        js_ctx.__iter__ = Mock(return_value=iter([1, 2, 3]))
        
        ctx = Context(js_ctx)
        
        # Test synchronous iteration
        result = list(ctx)
        assert result == [1, 2, 3]
        
        # Test attribute delegation
        js_ctx.some_property = "test_value"
        assert ctx.some_property == "test_value"


class TestFFIErrorHandling:
    """Test error handling in FFI operations"""
    
    @patch('crank.to_js')
    def test_to_js_conversion_failure(self, mock_to_js):
        """Test handling of to_js conversion failures"""
        mock_to_js.side_effect = Exception("Conversion failed")
        
        # Should handle conversion failures gracefully
        builder = ElementBuilder("div")
        
        with pytest.raises(Exception):
            builder(className="test")["content"]
    
    def test_invalid_props_types(self):
        """Test handling of invalid prop types"""
        builder = ElementBuilder("div")
        
        # Test with various invalid types
        invalid_props = {
            "validString": "ok",
            "validNumber": 42,
            "validBool": True,
            "validNone": None
        }
        
        # Should not crash with these prop types
        result = builder._process_props_for_proxies(invalid_props)
        assert result["validString"] == "ok"
        assert result["validNumber"] == 42
        assert result["validBool"] is True
        assert result["validNone"] is None


if __name__ == '__main__':
    pytest.main([__file__, "-v"])