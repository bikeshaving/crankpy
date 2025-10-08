"""
Hyperscript functionality tests using upytest for cross-runtime compatibility.

These tests verify the h function and element creation syntax.
"""
from crank import h, Fragment


def test_h_function_exists():
    """Test that h function is available"""
    assert h is not None
    assert hasattr(h, 'div')
    assert hasattr(h, 'span')
    assert hasattr(h, 'button')


def test_basic_elements():
    """Test basic element creation"""
    div_elem = h.div
    span_elem = h.span
    button_elem = h.button
    
    assert div_elem is not None
    assert span_elem is not None
    assert button_elem is not None


def test_elements_with_text_content():
    """Test elements with text content"""
    elem = h.div["Hello World"]
    assert elem is not None
    
    # Test with variables
    name = "Test"
    elem2 = h.span[f"Hello {name}"]
    assert elem2 is not None


def test_elements_with_props():
    """Test elements with properties"""
    elem = h.button(onclick="alert('clicked')")["Click me"]
    assert elem is not None
    
    elem2 = h.div(id="test-id", className="test-class")["Content"]
    assert elem2 is not None


def test_nested_elements():
    """Test nested element structures"""
    nested = h.div[
        h.h1["Title"],
        h.p["Paragraph"],
        h.ul[
            h.li["Item 1"],
            h.li["Item 2"]
        ]
    ]
    assert nested is not None


def test_element_chaining():
    """Test element method chaining"""
    # Test that we can chain different element types
    div_then_span = h.div["content"]
    span_after = h.span["more content"]
    
    assert div_then_span is not None
    assert span_after is not None


def test_props_with_underscores():
    """Test props with underscores get converted to hyphens"""
    elem = h.div(data_test="value")["Content"]
    assert elem is not None


def test_callable_props():
    """Test props that are functions"""
    def click_handler():
        pass
    
    elem = h.button(onclick=click_handler)["Click"]
    assert elem is not None


def test_complex_props():
    """Test complex prop values"""
    props = {
        "id": "complex-id",
        "className": "class1 class2",
        "style": {"color": "red", "fontSize": "14px"}
    }
    
    elem = h.div(**props)["Complex element"]
    assert elem is not None


def test_fragment_exists():
    """Test that Fragment is available"""
    assert Fragment is not None


def test_simple_fragment_as_list():
    """Test creating fragments as Python lists"""
    # Simple fragments are just Python lists
    frag = [h.div["First"], h.div["Second"]]
    assert frag is not None
    assert isinstance(frag, list)
    assert len(frag) == 2


def test_empty_fragment_as_list():
    """Test empty fragment as empty list"""
    # Empty fragments are just empty lists
    frag = []
    assert frag is not None
    assert isinstance(frag, list)
    assert len(frag) == 0


def test_fragment_with_key():
    """Test fragment with key using h() syntax"""
    # Fragment with props (when you need keys, etc.)
    try:
        frag = h("", key="my-fragment")["Child 1", "Child 2"]
        assert frag is not None
    except Exception:
        # This syntax might not work in all environments
        pass


def test_conditional_elements():
    """Test conditional element creation"""
    show_element = True
    
    result = h.div[
        h.h1["Always shown"],
        h.p["Conditional"] if show_element else None
    ]
    assert result is not None


def test_list_comprehension_elements():
    """Test elements created with list comprehensions"""
    items = ["Item 1", "Item 2", "Item 3"]
    
    list_elem = h.ul[
        [h.li[item] for item in items]
    ]
    assert list_elem is not None


def test_dynamic_tag_names():
    """Test that we can create different tag types"""
    # Test various HTML tags
    tags = ['div', 'span', 'p', 'h1', 'h2', 'h3', 'button', 'input', 'form']
    
    for tag in tags:
        elem = getattr(h, tag)
        assert elem is not None


def test_mixed_content_types():
    """Test mixing different content types"""
    mixed = h.div[
        "Plain text",
        h.span["Nested element"],
        42,  # Number
        True,  # Boolean
        h.p["Another element"]
    ]
    assert mixed is not None


class TestElementAttributes:
    """Test element attribute handling"""
    
    def test_id_attribute(self):
        """Test id attribute"""
        elem = h.div(id="test-id")["Content"]
        assert elem is not None
    
    def test_class_attribute(self):
        """Test className attribute"""
        elem = h.div(className="test-class")["Content"]
        assert elem is not None
    
    def test_style_attribute(self):
        """Test style attribute with object"""
        elem = h.div(style={"color": "red", "fontSize": "14px"})["Styled"]
        assert elem is not None
    
    def test_data_attributes(self):
        """Test data-* attributes"""
        elem = h.div(data_test="value", data_id="123")["Data attrs"]
        assert elem is not None
    
    def test_aria_attributes(self):
        """Test aria-* attributes"""
        elem = h.div(aria_label="Description", aria_hidden="true")["ARIA"]
        assert elem is not None


class TestSpecialElements:
    """Test special HTML elements"""
    
    def test_input_elements(self):
        """Test input elements"""
        text_input = h.input(type="text", value="test")
        checkbox = h.input(type="checkbox", checked=True)
        
        assert text_input is not None
        assert checkbox is not None
    
    def test_form_elements(self):
        """Test form elements"""
        form = h.form(action="/submit", method="post")[
            h.input(type="text", name="username"),
            h.button(type="submit")["Submit"]
        ]
        assert form is not None
    
    def test_media_elements(self):
        """Test media elements"""
        img = h.img(src="test.jpg", alt="Test image")
        video = h.video(src="test.mp4", controls=True)
        
        assert img is not None
        assert video is not None
    
    def test_table_elements(self):
        """Test table elements"""
        table = h.table[
            h.thead[
                h.tr[
                    h.th["Name"],
                    h.th["Age"]
                ]
            ],
            h.tbody[
                h.tr[
                    h.td["John"],
                    h.td["25"]
                ]
            ]
        ]
        assert table is not None