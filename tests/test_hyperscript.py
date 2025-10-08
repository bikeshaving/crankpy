"""
Hyperscript (h function) tests - implementation agnostic
"""

def test_simple_elements():
    """Test creating simple HTML elements"""
    from crank import h
    
    div = h.div["Hello"]
    span = h.span["World"]
    p = h.p["Paragraph"]
    
    assert div is not None
    assert span is not None
    assert p is not None

def test_elements_with_attributes():
    """Test elements with attributes"""
    from crank import h
    
    div = h.div(id="test", className="container")["Content"]
    input_elem = h.input(type="text", placeholder="Enter text")
    button = h.button(disabled=True)["Click me"]
    
    assert div is not None
    assert input_elem is not None
    assert button is not None

def test_snake_case_conversion():
    """Test snake_case to kebab-case conversion"""
    from crank import h
    
    div = h.div(data_test_id="button", aria_hidden="true")["Content"]
    assert div is not None

def test_nested_elements():
    """Test nested element structures"""
    from crank import h
    
    nav = h.nav[
        h.ul[
            h.li[h.a(href="/")["Home"]],
            h.li[h.a(href="/about")["About"]],
            h.li[h.a(href="/contact")["Contact"]]
        ]
    ]
    assert nav is not None

def test_element_lists():
    """Test elements with lists of children"""
    from crank import h
    
    items = ["Item 1", "Item 2", "Item 3"]
    ul = h.ul[[h.li[item] for item in items]]
    assert ul is not None

def test_conditional_elements():
    """Test conditional element rendering"""
    from crank import h
    
    show_title = True
    content = [
        h.h1["Title"] if show_title else None,
        h.p["Always shown"]
    ]
    # Filter out None values
    filtered_content = [elem for elem in content if elem is not None]
    div = h.div[filtered_content]
    assert div is not None

def test_fragment_syntax():
    """Test Fragment creation"""
    from crank import h, Fragment
    
    fragment = h(Fragment)[
        h.div["First"],
        h.div["Second"]
    ]
    assert fragment is not None

def test_component_syntax():
    """Test calling components with h()"""
    from crank import h, component
    
    @component
    def TestComponent(ctx, props):
        name = props.get("name", "World")
        for _ in ctx:
            yield h.div[f"Hello {name}"]
    
    element = h(TestComponent, name="Test")
    assert element is not None

def test_complex_attributes():
    """Test complex attribute patterns"""
    from crank import h
    
    div = h.div(
        id="complex",
        className="container primary",
        style="color: red; background: blue;",
        data_value=42,
        aria_label="Complex element"
    )["Complex content"]
    
    assert div is not None

def test_boolean_attributes():
    """Test boolean attributes"""
    from crank import h
    
    input_elem = h.input(
        type="checkbox", 
        checked=True,
        disabled=False,
        required=True
    )
    
    assert input_elem is not None

def test_event_handlers():
    """Test event handler attributes"""
    from crank import h
    
    def handle_click():
        pass
    
    def handle_change():
        pass
    
    button = h.button(onClick=handle_click)["Click me"]
    input_elem = h.input(onChange=handle_change, type="text")
    
    assert button is not None
    assert input_elem is not None

def test_special_elements():
    """Test special HTML elements"""
    from crank import h, Portal, Raw, Text, Copy
    
    # Test special elements with magic h subscription syntax
    portal = h(Portal, root="body")[h.div["Portal content"]]
    raw = h(Raw)["<em>Raw HTML</em>"]
    text = h(Text)["Plain text"]
    copy = h(Copy, crank="some-element")
    
    assert portal is not None
    assert raw is not None
    assert text is not None
    assert copy is not None