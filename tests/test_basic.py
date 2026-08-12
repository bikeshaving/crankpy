"""
Basic Crank.py tests - testing actual rendering behavior
"""


def test_basic_element_rendering():
    """Test basic element renders correctly to DOM"""
    from js import document

    from crank import h
    from crank.dom import renderer

    document.body.innerHTML = ""
    renderer.render(h.div["Hello World"], document.body)

    rendered_div = document.querySelector("div")
    assert rendered_div is not None
    assert rendered_div.textContent == "Hello World"


def test_element_with_props_rendering():
    """Test element with props renders correctly"""
    from js import document

    from crank import h
    from crank.dom import renderer

    document.body.innerHTML = ""
    renderer.render(h.div(id="test", className="container")["Content"], document.body)

    rendered_div = document.querySelector("div")
    assert rendered_div is not None
    assert rendered_div.textContent == "Content"
    assert rendered_div.id == "test"
    assert rendered_div.className == "container"


#
def test_nested_element_rendering():
    """Test nested elements render correctly"""
    from js import document

    from crank import h
    from crank.dom import renderer

    document.body.innerHTML = ""
    renderer.render(
        h.div[h.h1["Title"], h.p["Paragraph"], h.ul[h.li["Item 1"], h.li["Item 2"]]],
        document.body,
    )

    rendered_h1 = document.querySelector("h1")
    rendered_p = document.querySelector("p")
    rendered_lis = list(document.querySelectorAll("li"))

    assert rendered_h1 is not None
    assert rendered_h1.textContent == "Title"
    assert rendered_p is not None
    assert rendered_p.textContent == "Paragraph"
    assert len(rendered_lis) == 2
    assert rendered_lis[0].textContent == "Item 1"
    assert rendered_lis[1].textContent == "Item 2"


#
def test_fragment_rendering():
    """Test fragment renders children correctly"""
    from js import document

    from crank import Fragment, h
    from crank.dom import renderer

    document.body.innerHTML = ""
    renderer.render(h(Fragment)[h.div["First"], h.div["Second"]], document.body)

    rendered_divs = list(document.querySelectorAll("div"))
    assert len(rendered_divs) == 2
    assert rendered_divs[0].textContent == "First"
    assert rendered_divs[1].textContent == "Second"


#
def test_text_content_rendering():
    """Test various text content types render correctly"""
    from js import document

    from crank import h
    from crank.dom import renderer

    # Test string content
    document.body.innerHTML = ""
    renderer.render(h.span["String content"], document.body)
    span1 = document.querySelector("span")
    assert span1.textContent == "String content"

    # Test number content
    document.body.innerHTML = ""
    renderer.render(h.span[42], document.body)
    span2 = document.querySelector("span")
    assert span2.textContent == "42"

    # Test empty content
    document.body.innerHTML = ""
    renderer.render(h.span[""], document.body)
    span3 = document.querySelector("span")
    assert span3.textContent == ""


def test_form_controls_with_attributes():
    """Test form controls with attributes render on both runtimes"""
    from js import document

    from crank import h
    from crank.dom import renderer

    document.body.innerHTML = ""
    renderer.render(h.input(id="test-input", name="field1", type="text"), document.body)
    rendered_input = document.getElementById("test-input")
    assert rendered_input is not None
    assert rendered_input.name == "field1"
    assert rendered_input.type == "text"

    document.body.innerHTML = ""
    renderer.render(
        h.textarea(id="test-textarea", name="field2", rows="4"), document.body
    )
    rendered_textarea = document.getElementById("test-textarea")
    assert rendered_textarea is not None
    assert rendered_textarea.name == "field2"

    document.body.innerHTML = ""
    renderer.render(h.select(id="test-select", name="field3"), document.body)
    rendered_select = document.getElementById("test-select")
    assert rendered_select is not None
    assert rendered_select.name == "field3"


def test_form_controls_without_attributes():
    """Test bare form controls render on both runtimes"""
    from js import document

    from crank import h
    from crank.dom import renderer

    for tag in ("input", "textarea", "select"):
        document.body.innerHTML = ""
        renderer.render(h[tag](), document.body)
        assert document.querySelector(tag) is not None


def test_boolean_attributes():
    """Test boolean attributes are handled correctly"""
    from js import document

    from crank import h
    from crank.dom import renderer

    document.body.innerHTML = ""
    renderer.render(h.input(checked=True, disabled=False, hidden=True), document.body)

    rendered_input = document.querySelector("input")
    assert rendered_input is not None
    assert rendered_input.checked == True
    assert rendered_input.disabled == False
    assert rendered_input.hidden == True


def test_style_attribute():
    """Test style attribute is applied correctly"""
    from js import document

    from crank import h
    from crank.dom import renderer

    document.body.innerHTML = ""
    renderer.render(
        h.div(style="color: red; font-size: 16px;")["Styled"], document.body
    )

    rendered_div = document.querySelector("div")
    assert rendered_div is not None
    assert rendered_div.style.color == "red"
    assert rendered_div.style.fontSize == "16px"
