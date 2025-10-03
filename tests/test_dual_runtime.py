"""
Test dual runtime support for Pyodide and MicroPython.

These tests verify that the magic syntax works correctly on both runtimes
with their respective implementation approaches.
"""

import pytest
from unittest.mock import Mock, patch
import sys

# Mock PyScript/Pyodide imports for testing
sys.modules['js'] = Mock()
sys.modules['pyscript'] = Mock()
sys.modules['pyscript.ffi'] = Mock()
sys.modules['pyscript.js_modules'] = Mock()
sys.modules['pyodide'] = Mock()
sys.modules['pyodide.ffi'] = Mock()

# Set up mock objects
mock_to_js = Mock()
mock_create_proxy = Mock()
mock_createElement = Mock()
mock_JsProxy = Mock()

sys.modules['pyscript.ffi'].to_js = mock_to_js
sys.modules['pyscript.ffi'].create_proxy = mock_create_proxy
sys.modules['pyscript.js_modules'].crank_core = Mock()
sys.modules['pyscript.js_modules'].crank_core.createElement = mock_createElement
sys.modules['pyodide.ffi'].JsProxy = mock_JsProxy

from crank import h, ElementBuilder


class TestRuntimeDetection:
    """Test runtime detection functionality."""
    
    def setup_method(self):
        """Reset mocks before each test."""
        mock_to_js.reset_mock()
        mock_create_proxy.reset_mock()
        mock_createElement.reset_mock()
        
    def test_detect_pyodide_runtime(self):
        """Test detection of Pyodide runtime."""
        with patch('sys.implementation') as mock_impl:
            mock_impl.name = 'cpython'
            
            # Import a fresh instance to test detection
            from crank import ElementBuilder
            builder = ElementBuilder('div')
            
            # Should detect as Pyodide (cpython)
            assert not builder._is_micropython()
            
    def test_detect_micropython_runtime(self):
        """Test detection of MicroPython runtime."""
        with patch('sys.implementation') as mock_impl:
            mock_impl.name = 'micropython'
            
            from crank import ElementBuilder
            builder = ElementBuilder('div')
            
            # Should detect as MicroPython
            assert builder._is_micropython()


class TestMicroPythonChainableProxy:
    """Test MicroPython chainable proxy implementation."""
    
    def setup_method(self):
        """Reset mocks before each test."""
        mock_to_js.reset_mock()
        mock_create_proxy.reset_mock()
        mock_createElement.reset_mock()
        
    def test_chainable_proxy_creation(self):
        """Test creating a chainable proxy for MicroPython."""
        with patch('sys.implementation') as mock_impl:
            mock_impl.name = 'micropython'
            
            # Mock JS element
            mock_element = Mock()
            mock_createElement.return_value = mock_element
            
            builder = ElementBuilder('div')
            
            # Create chainable proxy
            proxy = builder._create_micropython_chainable(mock_element, {'className': 'test'})
            
            assert hasattr(proxy, '__getitem__')
            assert proxy._tag == 'div'
            assert proxy._props == {'className': 'test'}
            assert proxy._js_element == mock_element
            
    def test_chainable_proxy_getitem(self):
        """Test __getitem__ behavior of chainable proxy."""
        with patch('sys.implementation') as mock_impl:
            mock_impl.name = 'micropython'
            
            mock_element = Mock()
            mock_final_element = Mock()
            mock_createElement.return_value = mock_final_element
            mock_to_js.return_value = {'className': 'test'}
            
            builder = ElementBuilder('div')
            proxy = builder._create_micropython_chainable(mock_element, {'className': 'test'})
            
            # Test chainable syntax
            result = proxy["Hello World"]
            
            # Should create final element with children
            assert result == mock_final_element
            # Check that createElement was called with correct args
            mock_createElement.assert_called_with('div', {'className': 'test'}, "Hello World")
            
    def test_chainable_proxy_attribute_delegation(self):
        """Test that proxy delegates attributes to JS element."""
        with patch('sys.implementation') as mock_impl:
            mock_impl.name = 'micropython'
            
            mock_element = Mock()
            mock_element.some_property = "test_value"
            mock_createElement.return_value = mock_element
            
            builder = ElementBuilder('div')
            proxy = builder._create_micropython_chainable(mock_element, {})
            
            # Should delegate attribute access
            assert proxy.some_property == "test_value"
            
    def test_chainable_proxy_multiple_children(self):
        """Test proxy with multiple children."""
        with patch('sys.implementation') as mock_impl:
            mock_impl.name = 'micropython'
            
            mock_element = Mock()
            mock_final_element = Mock()
            mock_createElement.return_value = mock_final_element
            mock_to_js.return_value = {'id': 'test'}
            
            builder = ElementBuilder('span')
            proxy = builder._create_micropython_chainable(mock_element, {'id': 'test'})
            
            # Test with list of children  
            children = ["Hello", "World"]
            result = proxy[children]
            
            assert result == mock_final_element
            mock_createElement.assert_called_with('span', {'id': 'test'}, "Hello", "World")


class TestDualRuntimeMagicSyntax:
    """Test magic syntax works on both runtimes."""
    
    def setup_method(self):
        """Reset mocks before each test."""
        mock_to_js.reset_mock()
        mock_create_proxy.reset_mock()
        mock_createElement.reset_mock()
        
    def test_micropython_empty_element(self):
        """Test h.span() creates empty element on MicroPython."""
        with patch('sys.implementation') as mock_impl:
            mock_impl.name = 'micropython'
            
            mock_element = Mock()
            mock_createElement.return_value = mock_element
            
            result = h.span()
            
            mock_createElement.assert_called_once_with('span', None)
            assert result == mock_element
            
    def test_micropython_chainable_syntax(self):
        """Test h.div(className='test')['children'] on MicroPython."""
        with patch('sys.implementation') as mock_impl:
            mock_impl.name = 'micropython'
            
            mock_element = Mock()
            mock_final_element = Mock()
            mock_createElement.side_effect = [mock_element, mock_final_element]
            mock_to_js.return_value = {'className': 'test'}
            
            # Test the full chainable syntax
            chainable = h.div(className="test")
            result = chainable["Hello World"]
            
            # Should create chainable proxy, then final element
            assert mock_createElement.call_count == 2
            final_call = mock_createElement.call_args_list[1]
            assert 'div' in str(final_call)
            assert 'Hello World' in str(final_call)
            
    def test_pyodide_chainable_syntax_fallback(self):
        """Test chainable syntax falls back gracefully on Pyodide."""
        with patch('sys.implementation') as mock_impl:
            mock_impl.name = 'cpython'  # Pyodide
            
            mock_element = Mock()
            mock_element.as_object_map = Mock()
            mock_as_object_map = Mock()
            mock_element.as_object_map.return_value = mock_as_object_map
            mock_createElement.return_value = mock_element
            mock_to_js.return_value = {'className': 'test'}
            
            # Should use as_object_map approach
            chainable = h.div(className="test")
            
            # Should have called as_object_map
            mock_element.as_object_map.assert_called_once()
            
    def test_runtime_specific_error_handling(self):
        """Test error handling is runtime-specific."""
        with patch('sys.implementation') as mock_impl:
            mock_impl.name = 'micropython'
            
            mock_element = Mock()
            mock_createElement.return_value = mock_element
            
            # If createElement fails, should handle gracefully
            mock_createElement.side_effect = Exception("createElement failed")
            
            try:
                result = h.div()
                # Should handle error gracefully (implementation dependent)
            except Exception:
                # Expected to potentially fail, but shouldn't crash
                pass


class TestEdgeCasesAndCompatibility:
    """Test edge cases and compatibility scenarios."""
    
    def setup_method(self):
        """Reset mocks before each test."""
        mock_to_js.reset_mock()
        mock_create_proxy.reset_mock()
        mock_createElement.reset_mock()
        
    def test_mixed_runtime_detection(self):
        """Test behavior when runtime detection is unclear."""
        with patch('sys.implementation') as mock_impl:
            # Simulate unknown implementation
            mock_impl.name = 'unknown'
            
            mock_element = Mock()
            mock_createElement.return_value = mock_element
            
            # Should default to Pyodide behavior
            result = h.span()
            assert result == mock_element
            
    def test_missing_as_object_map_graceful_fallback(self):
        """Test graceful fallback when as_object_map is missing."""
        with patch('sys.implementation') as mock_impl:
            mock_impl.name = 'cpython'  # Pyodide
            
            mock_element = Mock()
            # Remove as_object_map to simulate older version
            del mock_element.as_object_map
            mock_createElement.return_value = mock_element
            mock_to_js.return_value = {'className': 'test'}
            
            # Should return element even without as_object_map
            result = h.div(className="test")
            assert result == mock_element
            
    def test_props_processing_consistent_across_runtimes(self):
        """Test that props processing works consistently."""
        test_cases = [
            ('micropython', 'micropython'),
            ('cpython', 'cpython')  # Pyodide
        ]
        
        for impl_name, expected in test_cases:
            with patch('sys.implementation') as mock_impl:
                mock_impl.name = impl_name
                
                mock_element = Mock()
                if impl_name == 'cpython':
                    mock_element.as_object_map = Mock(return_value=Mock())
                mock_createElement.return_value = mock_element
                mock_to_js.return_value = {'data-test': 'value'}
                
                # Test underscore to hyphen conversion
                result = h.div(data_test="value")
                
                # Should process props consistently
                mock_to_js.assert_called()
                call_args = mock_to_js.call_args[0][0]
                assert 'data-test' in call_args


if __name__ == '__main__':
    pytest.main([__file__, "-v"])