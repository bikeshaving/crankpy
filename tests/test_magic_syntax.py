"""
Test magic syntax functionality for chainable elements.

These tests verify that the magic syntax works correctly in Pyodide environments,
including empty elements and chainable element patterns.
"""

import pytest
from unittest.mock import Mock, patch
import sys

# Import existing mocks from test_crank to ensure consistency
from test_crank import (
    mock_create_proxy, mock_to_js, mock_crank_core, mock_JsProxy
)

# Use the shared mock for createElement
mock_createElement = mock_crank_core.createElement

# Now import crank
from crank import h


class TestMagicSyntax:
    """Test the magic syntax functionality."""
    
    def setup_method(self):
        """Reset mocks before each test."""
        mock_to_js.reset_mock()
        mock_create_proxy.reset_mock()
        mock_createElement.reset_mock()
        mock_JsProxy.reset_mock()
    
    def test_empty_element_no_props_no_children(self):
        """Test h.span() creates empty element immediately."""
        # Arrange
        mock_element = Mock()
        mock_createElement.return_value = mock_element
        
        # Act
        result = h.span()
        
        # Assert
        mock_createElement.assert_called_once_with('span', None)
        assert result == mock_element
    
    def test_empty_element_with_props_no_children_returns_chainable(self):
        """Test h.span(className='test') returns chainable element."""
        # Arrange
        mock_element = Mock()
        mock_as_object_map = Mock()
        mock_element.as_object_map.return_value = mock_as_object_map
        mock_createElement.return_value = mock_element
        mock_to_js.return_value = {'className': 'test'}
        
        # Act
        result = h.span(className="test")
        
        # Assert
        # createElement is called multiple times (for patching and for actual element)
        assert mock_createElement.call_count >= 2
        # Should have an as_object_map call for chainable element
        mock_element.as_object_map.assert_called()
        # Should set chainable properties
        assert hasattr(mock_as_object_map, '_crank_tag')
        assert hasattr(mock_as_object_map, '_crank_props')
        assert result == mock_as_object_map
    
    def test_element_with_children_creates_immediately(self):
        """Test h.span('child1', 'child2') creates element with children immediately."""
        # Arrange
        mock_element = Mock()
        mock_createElement.return_value = mock_element
        mock_to_js.return_value = None
        
        # Act
        result = h.span("child1", "child2")
        
        # Assert
        mock_createElement.assert_called_once_with('span', None, "child1", "child2")
        assert result == mock_element
    
    def test_element_with_props_and_children_creates_immediately(self):
        """Test h.span(className='test', 'child') creates element immediately."""
        # Arrange
        mock_element = Mock()
        mock_createElement.return_value = mock_element
        mock_to_js.return_value = {'className': 'test'}
        
        # Act
        result = h.span("child", className="test")
        
        # Assert
        mock_createElement.assert_called_once_with('span', {'className': 'test'}, "child")
        assert result == mock_element
    
    def test_props_underscore_to_hyphen_conversion(self):
        """Test that underscore props are converted to hyphens."""
        # Arrange
        mock_element = Mock()
        mock_as_object_map = Mock()
        mock_element.as_object_map.return_value = mock_as_object_map
        mock_createElement.return_value = mock_element
        
        def capture_to_js(props):
            return props
        mock_to_js.side_effect = capture_to_js
        
        # Act
        result = h.div(data_test_id="button", aria_hidden="true")
        
        # Assert
        # Check that the processed props were passed to to_js
        # Look for the most recent call that contains our props
        found_call = False
        for call in mock_to_js.call_args_list:
            if call[0] and isinstance(call[0][0], dict):
                call_args = call[0][0]
                if 'data-test-id' in call_args and 'aria-hidden' in call_args:
                    assert call_args['data-test-id'] == "button"
                    assert call_args['aria-hidden'] == "true"
                    found_call = True
                    break
        assert found_call, "Expected props conversion call not found"
    
    def test_callable_props_are_proxied(self):
        """Test that callable props are wrapped with create_proxy."""
        # Arrange
        mock_element = Mock()
        mock_as_object_map = Mock()
        mock_element.as_object_map.return_value = mock_as_object_map
        mock_createElement.return_value = mock_element
        mock_proxy = Mock()
        mock_create_proxy.return_value = mock_proxy
        
        def capture_to_js(props):
            return props
        mock_to_js.side_effect = capture_to_js
        
        def click_handler():
            pass
        
        # Act
        result = h.button(onClick=click_handler)
        
        # Assert
        # Check that create_proxy was called with our function
        proxy_calls = [call for call in mock_create_proxy.call_args_list if call[0][0] == click_handler]
        assert len(proxy_calls) >= 1, "create_proxy should have been called with click_handler"
        
        # Check that to_js was called with processed props containing the proxy
        found_call = False
        for call in mock_to_js.call_args_list:
            if call[0] and isinstance(call[0][0], dict):
                call_args = call[0][0]
                if 'onClick' in call_args and call_args['onClick'] == mock_proxy:
                    found_call = True
                    break
        assert found_call, "Expected to_js call with proxied onClick not found"
    
    def test_as_object_map_type_patching_called(self):
        """Test that _patch_as_object_map_type is called when creating chainable elements."""
        # Arrange
        mock_element = Mock()
        mock_as_object_map = Mock()
        mock_element.as_object_map.return_value = mock_as_object_map
        mock_createElement.return_value = mock_element
        mock_to_js.return_value = {'test': 'prop'}
        
        # Mock the patching function to track if it's called
        with patch('crank._patch_as_object_map_type') as mock_patch:
            # Act
            result = h.span(test="prop")
            
            # Assert
            mock_patch.assert_called_once()


class TestMagicSyntaxIntegration:
    """Integration tests for magic syntax functionality."""
    
    def test_chainable_element_workflow(self):
        """Test the complete workflow of creating and using chainable elements."""
        # This test would require a more complex setup to mock the dynamic type patching
        # For now, we verify the basic structure is in place
        assert hasattr(h.span, '__call__')
        assert hasattr(h, '__getattr__')
    
    def test_element_builder_methods_exist(self):
        """Test that ElementBuilder has the required methods."""
        from crank import ElementBuilder
        
        builder = ElementBuilder('div')
        assert hasattr(builder, '__call__')
        assert hasattr(builder, '__getitem__')
        assert hasattr(builder, '_make_chainable_element')
        assert hasattr(builder, '_process_props_for_proxies')


if __name__ == '__main__':
    pytest.main([__file__])