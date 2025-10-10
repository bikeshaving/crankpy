"""
Basic Crank.py tests - testing actual rendering behavior
"""

def test_basic_element_rendering():
    """Test basic element renders correctly to DOM"""
    from crank import h
    from crank.dom import renderer
    from js import document

    document.body.innerHTML = ""
    renderer.render(h.div["Hello World"], document.body)

    rendered_div = document.querySelector("div")
    assert rendered_div is not None
    assert rendered_div.textContent == "Hello World"

#def test_element_with_props_rendering():
#    """Test element with props renders correctly"""
#    from crank import h
#    from crank.dom import renderer
#    from js import document
#
#    document.body.innerHTML = ""
#    renderer.render(h.div(id="test", className="container")["Content"], document.body)
#
#    rendered_div = document.querySelector("div")
#    assert rendered_div is not None
#    assert rendered_div.textContent == "Content"
#    assert rendered_div.id == "test"
#    assert rendered_div.className == "container"
#
#def test_nested_element_rendering():
#    """Test nested elements render correctly"""
#    from crank import h
#    from crank.dom import renderer
#    from js import document
#
#    document.body.innerHTML = ""
#    renderer.render(h.div[
#        h.h1["Title"],
#        h.p["Paragraph"],
#        h.ul[
#            h.li["Item 1"],
#            h.li["Item 2"]
#        ]
#    ], document.body)
#
#    rendered_h1 = document.querySelector("h1")
#    rendered_p = document.querySelector("p")
#    rendered_lis = list(document.querySelectorAll("li"))
#
#    assert rendered_h1 is not None
#    assert rendered_h1.textContent == "Title"
#    assert rendered_p is not None
#    assert rendered_p.textContent == "Paragraph"
#    assert len(rendered_lis) == 2
#    assert rendered_lis[0].textContent == "Item 1"
#    assert rendered_lis[1].textContent == "Item 2"
#
#def test_fragment_rendering():
#    """Test fragment renders children correctly"""
#    from crank import h, Fragment
#    from crank.dom import renderer
#    from js import document
#
#    document.body.innerHTML = ""
#    renderer.render(h(Fragment)[
#        h.div["First"],
#        h.div["Second"]
#    ], document.body)
#
#    rendered_divs = list(document.querySelectorAll("div"))
#    assert len(rendered_divs) == 2
#    assert rendered_divs[0].textContent == "First"
#    assert rendered_divs[1].textContent == "Second"
#
#def test_text_content_rendering():
#    """Test various text content types render correctly"""
#    from crank import h
#    from crank.dom import renderer
#    from js import document
#
#    # Test string content
#    document.body.innerHTML = ""
#    renderer.render(h.span["String content"], document.body)
#    span1 = document.querySelector("span")
#    assert span1.textContent == "String content"
#
#    # Test number content
#    document.body.innerHTML = ""
#    renderer.render(h.span[42], document.body)
#    span2 = document.querySelector("span")
#    assert span2.textContent == "42"
#
#    # Test empty content
#    document.body.innerHTML = ""
#    renderer.render(h.span[""], document.body)
#    span3 = document.querySelector("span")
#    assert span3.textContent == ""
#
#def test_multiple_attributes():
#    """Test element with multiple attributes"""
#    from crank import h
#    from crank.dom import renderer
#    from js import document
#
#    document.body.innerHTML = ""
#    renderer.render(h.input(
#        type="text",
#        placeholder="Enter text",
#        value="default",
#        disabled=True,
#        data_testid="input-field"
#    ), document.body)
#
#    rendered_input = document.querySelector("input")
#    assert rendered_input is not None
#    assert rendered_input.type == "text"
#    assert rendered_input.placeholder == "Enter text"
#    assert rendered_input.value == "default"
#    assert rendered_input.disabled == True
#    assert rendered_input.getAttribute("data-testid") == "input-field"
#
#def test_boolean_attributes():
#    """Test boolean attributes are handled correctly"""
#    from crank import h
#    from crank.dom import renderer
#    from js import document
#
#    document.body.innerHTML = ""
#    renderer.render(h.input(
#        checked=True,
#        disabled=False,
#        hidden=True
#    ), document.body)
#
#    rendered_input = document.querySelector("input")
#    assert rendered_input is not None
#    assert rendered_input.checked == True
#    assert rendered_input.disabled == False
#    assert rendered_input.hidden == True
#
#def test_style_attribute():
#    """Test style attribute is applied correctly"""
#    from crank import h
#    from crank.dom import renderer
#    from js import document
#
#    document.body.innerHTML = ""
#    renderer.render(h.div(style="color: red; font-size: 16px;")["Styled"], document.body)
#
#    rendered_div = document.querySelector("div")
#    assert rendered_div is not None
#    assert rendered_div.style.color == "red"
#    assert rendered_div.style.fontSize == "16px"
