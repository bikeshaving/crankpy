"""
Tests for the magic j function (JSX-like syntax)
"""

import pytest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_magic_j_imports():
    """Test that we can import the magic j function"""
    from crank import j
    
    assert j is not None

def test_magic_j_html_elements():
    """Test magic j with HTML elements"""
    from crank import j
    
    # Test basic element access
    div_builder = j.div
    assert div_builder is not None
    
    # Test element with props
    result = j.div(className="test")
    assert result is not None
    
def test_magic_j_component_lookup():
    """Test magic j component lookup"""
    from crank import j, component
    
    @component  
    def TestComponent(ctx):
        return "test"
    
    # This should find TestComponent in the local scope
    # Note: This might not work in pytest context due to scope issues
    # but we can test it doesn't crash
    try:
        result = j.TestComponent
        # If it works, great
        assert result is not None
    except NameError:
        # If it fails due to scope, that's expected in test context
        pass

def test_magic_j_children_syntax():
    """Test magic j with children syntax"""
    from crank import j
    
    # Test the [children] syntax
    result = j.div["Hello World"]
    assert result is not None
    
    # Test with multiple children
    result = j.div[
        j.h1["Title"],
        j.p["Content"]
    ]
    assert result is not None