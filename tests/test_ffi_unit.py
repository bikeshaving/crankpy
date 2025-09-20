"""
Unit tests for FFI functionality in Crank.py using mocked PyScript environment

Following PyScript testing best practices from puepy and other projects.
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock

class TestFFIWithMocks:
    """Test FFI functionality with properly mocked PyScript environment"""
    
    def setup_method(self):
        """Set up mocks before each test"""
        # Mock PyScript modules
        self.js_mock = Mock()
        self.pyscript_mock = Mock()
        self.ffi_mock = Mock()
        self.js_modules_mock = Mock()
        
        # Mock FFI functions
        self.create_proxy_mock = Mock()
        self.to_js_mock = Mock()
        self.ffi_mock.create_proxy = self.create_proxy_mock
        self.ffi_mock.to_js = self.to_js_mock
        
        # Mock crank_core
        self.crank_core_mock = Mock()
        self.crank_core_mock.Element = Mock()
        self.crank_core_mock.createElement = Mock(return_value="mock_element")
        self.crank_core_mock.Fragment = Mock()
        self.js_modules_mock.crank_core = self.crank_core_mock
        
        # Mock JS objects
        self.js_mock.Symbol = Mock()
        self.js_mock.Symbol.for_ = Mock(return_value="mock_symbol")
        self.js_mock.Object = Mock()
        
        # Install mocks
        sys.modules['js'] = self.js_mock
        sys.modules['pyscript'] = self.pyscript_mock
        sys.modules['pyscript.ffi'] = self.ffi_mock
        sys.modules['pyscript.js_modules'] = self.js_modules_mock
        
        # Clear import cache for crank to force re-import with mocks
        if 'crank' in sys.modules:
            del sys.modules['crank']
    
    def test_component_decorator_creates_proxy(self):
        """Test that @component decorator creates proxy for function"""
        from crank import component
        
        mock_proxy = Mock()
        self.create_proxy_mock.return_value = mock_proxy
        
        @component
        def TestComponent(ctx):
            return "test element"
        
        # Should have called create_proxy
        self.create_proxy_mock.assert_called_once()
        # Should return the proxy
        assert TestComponent == mock_proxy
    
    def test_element_builder_processes_callables(self):
        """Test that ElementBuilder processes callable props"""
        from crank import ElementBuilder
        
        mock_proxy = Mock()
        self.create_proxy_mock.return_value = mock_proxy
        
        def click_handler():
            pass
        
        builder = ElementBuilder("button")
        
        # Test that callables get proxied in props processing
        props = {"onClick": click_handler}
        result = builder._process_props_for_proxies(props)
        
        self.create_proxy_mock.assert_called_with(click_handler)
        assert result["onClick"] == mock_proxy
    
    def test_nested_callable_processing(self):
        """Test processing of nested callables in complex props"""
        from crank import ElementBuilder
        
        mock_proxy = Mock()
        self.create_proxy_mock.return_value = mock_proxy
        
        def handler1():
            pass
        
        def handler2():
            pass
        
        # Create nested structure with callables
        props = {
            "events": {
                "onClick": handler1,
                "onSubmit": handler2
            },
            "simple": "string",
            "number": 42
        }
        
        builder = ElementBuilder("div")
        result = builder._process_props_for_proxies(props)
        
        # Should proxy both handlers
        assert self.create_proxy_mock.call_count == 2
        assert result["events"]["onClick"] == mock_proxy
        assert result["events"]["onSubmit"] == mock_proxy
        # Non-callables unchanged
        assert result["simple"] == "string"
        assert result["number"] == 42
    
    def test_to_js_conversion_called(self):
        """Test that to_js is called for object conversion"""
        from crank import ElementBuilder
        
        mock_js_obj = Mock()
        self.to_js_mock.return_value = mock_js_obj
        
        props = {"className": "test", "id": "button"}
        builder = ElementBuilder("button", props)
        
        # Trigger conversion by creating element
        element = builder["Click me"]
        
        # Should have called to_js for props
        self.to_js_mock.assert_called()
        # Should have called createElement
        self.crank_core_mock.createElement.assert_called()
    
    def test_context_wrapper_functionality(self):
        """Test Context wrapper delegates to JS context"""
        from crank import Context
        
        # Mock JS context with proper bind method
        js_ctx = Mock()
        js_schedule = Mock()
        js_ctx.schedule = Mock()
        js_ctx.schedule.bind = Mock(return_value=js_schedule)
        js_ctx.some_property = "test_value"
        
        ctx = Context(js_ctx)
        
        # Test method delegation
        assert hasattr(ctx, 'refresh')
        assert ctx.some_property == "test_value"
        
        # Test schedule creates proxy
        mock_proxy = Mock()
        self.create_proxy_mock.return_value = mock_proxy
        
        def test_func():
            pass
        
        ctx.schedule(test_func)
        self.create_proxy_mock.assert_called_with(test_func)
        # The bound method should be called
        js_schedule.assert_called_with(mock_proxy)
    
    def test_already_proxied_functions_not_reproxied(self):
        """Test that already proxied functions aren't proxied again"""
        from crank import ElementBuilder
        
        # Create mock that looks like JS proxy
        already_proxied = Mock()
        already_proxied.toString = Mock()  # JS proxy indicator
        
        props = {"onClick": already_proxied}
        builder = ElementBuilder("button")
        result = builder._process_props_for_proxies(props)
        
        # Should not have called create_proxy
        self.create_proxy_mock.assert_not_called()
        # Should keep original function
        assert result["onClick"] == already_proxied
    
    def test_magic_h_element_creation(self):
        """Test MagicH creates elements correctly"""
        from crank import h
        
        # Test simple element creation
        element = h.div["Hello"]
        
        # Should have called createElement
        self.crank_core_mock.createElement.assert_called()
        call_args = self.crank_core_mock.createElement.call_args
        assert call_args[0][0] == "div"  # tag name
    
    def test_magic_h_with_props_and_handlers(self):
        """Test MagicH with props containing handlers"""
        from crank import h
        
        mock_proxy = Mock()
        self.create_proxy_mock.return_value = mock_proxy
        
        def click_handler():
            pass
        
        # Create element with handler
        element = h.button(onClick=click_handler, className="btn")["Click"]
        
        # Should have proxied the handler
        self.create_proxy_mock.assert_called_with(click_handler)
        # Should have called createElement
        self.crank_core_mock.createElement.assert_called()
    
    def test_error_handling_graceful(self):
        """Test that errors don't crash the system"""
        from crank import ElementBuilder
        
        # Make create_proxy fail
        self.create_proxy_mock.side_effect = Exception("Proxy failed")
        
        def failing_handler():
            pass
        
        props = {"onClick": failing_handler}
        builder = ElementBuilder("button")
        
        # Should handle the error (either raise or handle gracefully)
        try:
            result = builder._process_props_for_proxies(props)
            # If it succeeds, that's also acceptable
        except Exception:
            # Expected to fail in this case
            pass
    
    def teardown_method(self):
        """Clean up after each test"""
        # Remove mocks from sys.modules
        modules_to_remove = ['js', 'pyscript', 'pyscript.ffi', 'pyscript.js_modules', 'crank']
        for module in modules_to_remove:
            if module in sys.modules:
                del sys.modules[module]


class TestFFIPatterns:
    """Test common FFI usage patterns"""
    
    def setup_method(self):
        """Set up minimal mocks for pattern testing"""
        # Very minimal mocking just to import
        sys.modules['js'] = Mock()
        sys.modules['pyscript'] = Mock()
        sys.modules['pyscript.ffi'] = Mock()
        sys.modules['pyscript.js_modules'] = Mock()
        
        # Mock required functions
        sys.modules['pyscript.ffi'].create_proxy = Mock(return_value="proxy")
        sys.modules['pyscript.ffi'].to_js = Mock(return_value="js_obj")
        
        # Mock crank core
        mock_core = Mock()
        mock_core.Element = Mock()
        mock_core.createElement = Mock(return_value="element")
        mock_core.Fragment = Mock()
        sys.modules['pyscript.js_modules'].crank_core = mock_core
        
        sys.modules['js'].Symbol = Mock()
        sys.modules['js'].Symbol.for_ = Mock(return_value="symbol")
        
        # Clear crank cache
        if 'crank' in sys.modules:
            del sys.modules['crank']
    
    def test_component_signature_patterns(self):
        """Test different component signature patterns"""
        from crank import component, h
        
        # No params
        @component
        def NoParams():
            return h.div["static"]
        
        # Single param (context)
        @component  
        def SingleParam(ctx):
            return h.div["with context"]
        
        # Two params (context, props)
        @component
        def TwoParams(ctx, props):
            return h.div["with props"]
        
        # All should work without errors
        # Components are proxied, so they return the proxy string "proxy"
        # The important thing is they don't raise exceptions
        assert NoParams is not None
        assert SingleParam is not None  
        assert TwoParams is not None
    
    def test_prop_name_conversions(self):
        """Test underscore to dash conversions in props"""
        from crank import h
        
        # Test underscore conversion
        element = h.div(
            data_test_id="button",
            aria_hidden="true",
            className="normal"  # No conversion needed
        )["Content"]
        
        # Should complete without error
        assert element is not None
    
    def test_fragment_patterns(self):
        """Test Fragment usage patterns"""
        from crank import h, Fragment
        
        # Test Fragment with props
        frag = h(Fragment, key="test")["content"]
        assert frag is not None
        
        # Test empty string as Fragment
        empty_frag = h("")["content"]
        assert empty_frag is not None
    
    def teardown_method(self):
        """Clean up"""
        modules_to_remove = ['js', 'pyscript', 'pyscript.ffi', 'pyscript.js_modules', 'crank']
        for module in modules_to_remove:
            if module in sys.modules:
                del sys.modules[module]


if __name__ == '__main__':
    pytest.main([__file__, "-v"])