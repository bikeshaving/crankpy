"""
Basic Crank.py tests - implementation agnostic
"""

def test_h_import():
    """Test that h function can be imported"""
    from crank import h
    assert h is not None

def test_component_import():
    """Test that component decorator can be imported"""
    from crank import component
    assert component is not None

def test_element_creation():
    """Test basic element creation"""
    from crank import h
    element = h.div["Hello World"]
    assert element is not None

def test_element_with_props():
    """Test element creation with props"""
    from crank import h
    element = h.div(id="test", className="container")["Content"]
    assert element is not None

def test_component_creation():
    """Test component creation"""
    from crank import h, component
    
    @component
    def SimpleComponent(ctx):
        for _ in ctx:
            yield h.div["Simple component"]
    
    assert callable(SimpleComponent)

def test_component_with_props():
    """Test component with props"""
    from crank import h, component
    
    @component  
    def PropsComponent(ctx, props):
        name = props.get("name", "World")
        for _ in ctx:
            yield h.div[f"Hello {name}"]
    
    assert callable(PropsComponent)

def test_nested_elements():
    """Test nested element creation"""
    from crank import h
    element = h.div[
        h.h1["Title"],
        h.p["Paragraph"],
        h.ul[
            h.li["Item 1"],
            h.li["Item 2"]
        ]
    ]
    assert element is not None

def test_fragment_creation():
    """Test fragment creation"""
    from crank import h, Fragment
    fragment = h(Fragment)[
        h.div["First"],
        h.div["Second"]
    ]
    assert fragment is not None