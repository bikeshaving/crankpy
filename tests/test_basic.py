"""
Basic unit tests for Crank.py core functionality
"""

import pytest
import sys
import os

# Add the project root to the path so we can import crank
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_imports():
    """Test that we can import the basic crank modules"""
    from crank import h, component, createElement
    from crank.dom import renderer
    
    assert callable(h)
    assert callable(component)
    assert callable(createElement)
    assert renderer is not None

def test_h_function_with_strings():
    """Test the h function with string tags"""
    from crank import h
    
    # Test basic element creation
    result = h("div", {}, "Hello")
    
    # Since this creates Crank elements, we can't easily test the internals
    # without the full PyScript environment, but we can test it doesn't crash
    assert result is not None

def test_h_function_with_props():
    """Test the h function with props"""
    from crank import h
    
    props = {"className": "test", "id": "myid"}
    result = h("div", props, "Content")
    
    assert result is not None

def test_h_function_with_children():
    """Test the h function with multiple children"""
    from crank import h
    
    result = h("div", {},
        h("h1", {}, "Title"),
        h("p", {}, "Paragraph")
    )
    
    assert result is not None

def test_component_decorator():
    """Test the component decorator"""
    from crank import component
    
    @component
    def TestComponent(ctx):
        return "test"
    
    # The decorator should return a proxied function
    assert TestComponent is not None
    assert callable(TestComponent)

def test_component_decorator_with_generator():
    """Test the component decorator with generator function"""
    from crank import component
    
    @component
    def GeneratorComponent(ctx):
        for _ in ctx:
            yield "test"
    
    assert GeneratorComponent is not None
    assert callable(GeneratorComponent)