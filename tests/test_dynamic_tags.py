"""
Test dynamic tags with h() function
"""

def test_dynamic_string_tag():
    """Test h() with dynamic string tag variable"""
    from crank import h
    
    tag = "div"
    element = h(tag)["Dynamic tag content"]
    assert element is not None

def test_dynamic_component_variable():
    """Test h() with dynamic component variable"""
    from crank import h, Portal
    
    component = Portal
    element = h(component, root="body")["Portal content"]
    assert element is not None

def test_multiple_dynamic_cases():
    """Test various dynamic tag scenarios"""
    from crank import h, Fragment, Raw, Text
    
    # String variables
    div_tag = "div"
    span_tag = "span"
    
    # Component variables
    fragment_comp = Fragment
    raw_comp = Raw
    text_comp = Text
    
    # All should be subscriptable
    div_elem = h(div_tag, id="test")["Div content"]
    span_elem = h(span_tag, className="test")["Span content"]
    fragment_elem = h(fragment_comp)["Fragment content"]
    raw_elem = h(raw_comp)["<b>Raw content</b>"]
    text_elem = h(text_comp)["Text content"]
    
    assert div_elem is not None
    assert span_elem is not None
    assert fragment_elem is not None
    assert raw_elem is not None
    assert text_elem is not None

def test_overwrite_children_like_jsx():
    """Test that bracket syntax can overwrite children like JSX"""
    from crank import h
    
    # Like JSX: <div children="old">new content</div> - "new content" overwrites "old"
    # In PyperScript: h("div", children="old")["new content"] - "new content" should overwrite "old"
    
    element = h("div", children="old content")["new content"]
    assert element is not None
    
    # Test with components too
    tag = "span"
    element2 = h(tag, children=["old", "children"])["overwritten"]
    assert element2 is not None