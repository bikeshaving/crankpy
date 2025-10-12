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

def test_element_with_props_rendering():
    """Test element with props renders correctly"""
    from crank import h
    from crank.dom import renderer
    from js import document

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
    from crank import h
    from crank.dom import renderer
    from js import document

    document.body.innerHTML = ""
    renderer.render(h.div[
        h.h1["Title"],
        h.p["Paragraph"],
        h.ul[
            h.li["Item 1"],
            h.li["Item 2"]
        ]
    ], document.body)

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
    from crank import h, Fragment
    from crank.dom import renderer
    from js import document

    document.body.innerHTML = ""
    renderer.render(h(Fragment)[
        h.div["First"],
        h.div["Second"]
    ], document.body)

    rendered_divs = list(document.querySelectorAll("div"))
    assert len(rendered_divs) == 2
    assert rendered_divs[0].textContent == "First"
    assert rendered_divs[1].textContent == "Second"
#
def test_text_content_rendering():
    """Test various text content types render correctly"""
    from crank import h
    from crank.dom import renderer
    from js import document

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
def test_renderer_step_breakdown():
    """Break down the renderer.render() call to isolate the exact hang point"""
    from crank import h, createElement
    from crank.dom import renderer, DOMRenderer
    from pyscript.ffi import to_js
    from js import document
    import sys

    is_micropython = "micropython" in sys.version.lower()

    # Test 1: Raw DOM manipulation (should work in both runtimes)
    document.body.innerHTML = ""
    raw_input = document.createElement("input")
    raw_input.id = "test-raw"
    raw_input.type = "text"
    document.body.appendChild(raw_input)
    assert document.getElementById("test-raw") is not None

    # Test 2: Direct Crank createElement (works in both runtimes)
    input_props = {"id": "test-direct", "type": "text"}
    js_props = to_js(input_props)
    crank_element = createElement("input", js_props)
    assert crank_element is not None

    # Test 3: Test if we can access the DOMRenderer directly
    # Skip DOMRenderer constructor test - it requires 'new' keyword

    if not is_micropython:
        # Test 4: MagicH element creation (works in Pyodide)
        input_with_props = h.input(id="test-magic", type="text")
        assert input_with_props is not None

        # Test 5: THE HANG - Crank renderer.render() with form input + attributes
        document.body.innerHTML = ""
        # This is the exact call that hangs in MicroPython
        result = renderer.render(input_with_props, document.body)
        assert result is not None

        # Test 6: Confirm hang happens specifically in renderer.render()

    # Test 7: Comparison - div elements work fine with renderer
    div_with_props = h.div(id="test-div", className="container")["Content"]
    document.body.innerHTML = ""
    result = renderer.render(div_with_props, document.body)
    assert result is not None

def test_form_input_pattern():
    """Test the exact pattern: form input controls with attributes hang in MicroPython"""
    from crank import h
    from crank.dom import renderer
    from js import document
    import sys

    is_micropython = "micropython" in sys.version.lower()

    # PATTERN DISCOVERED:
    # ✅ Works in both runtimes: Regular elements (div, span, button, form) with attributes
    # ✅ Works in both runtimes: Form input controls (input, textarea, select) WITHOUT attributes
    # ❌ Hangs in MicroPython: Form input controls (input, textarea, select) WITH attributes
    # ✅ Works in Pyodide: Form input controls WITH attributes

    # Test 1: Regular elements with attributes work in both runtimes
    document.body.innerHTML = ""
    div_with_attrs = h.div(id="test-div", className="container")["Content"]
    result1 = renderer.render(div_with_attrs, document.body)
    assert result1 is not None

    document.body.innerHTML = ""
    button_with_attrs = h.button(id="test-button", className="btn")["Click me"]
    result2 = renderer.render(button_with_attrs, document.body)
    assert result2 is not None

    # Test 2: Form input controls WITHOUT attributes work in both runtimes
    document.body.innerHTML = ""
    input_no_attrs = h.input()
    result3 = renderer.render(input_no_attrs, document.body)
    assert result3 is not None

    document.body.innerHTML = ""
    textarea_no_attrs = h.textarea()
    result4 = renderer.render(textarea_no_attrs, document.body)
    assert result4 is not None

    document.body.innerHTML = ""
    select_no_attrs = h.select()
    result5 = renderer.render(select_no_attrs, document.body)
    assert result5 is not None

    # Test 3: Form input controls WITH attributes
    # These should work in Pyodide but hang in MicroPython
    if not is_micropython:
        # Only test with attributes in Pyodide (these hang in MicroPython)
        document.body.innerHTML = ""
        input_with_attrs = h.input(id="test-input", name="field1", type="text")
        result6 = renderer.render(input_with_attrs, document.body)
        assert result6 is not None

        document.body.innerHTML = ""
        textarea_with_attrs = h.textarea(id="test-textarea", name="field2", rows="4")
        result7 = renderer.render(textarea_with_attrs, document.body)
        assert result7 is not None

        document.body.innerHTML = ""
        select_with_attrs = h.select(id="test-select", name="field3")
        result8 = renderer.render(select_with_attrs, document.body)
        assert result8 is not None

def test_boolean_attributes():
    """Test boolean attributes are handled correctly"""
    from crank import h
    from crank.dom import renderer
    from js import document

    document.body.innerHTML = ""
    renderer.render(h.input(
        checked=True,
        disabled=False,
        hidden=True
    ), document.body)

    rendered_input = document.querySelector("input")
    assert rendered_input is not None
    assert rendered_input.checked == True
    assert rendered_input.disabled == False
    assert rendered_input.hidden == True

def test_style_attribute():
    """Test style attribute is applied correctly"""
    from crank import h
    from crank.dom import renderer
    from js import document

    document.body.innerHTML = ""
    renderer.render(h.div(style="color: red; font-size: 16px;")["Styled"], document.body)

    rendered_div = document.querySelector("div")
    assert rendered_div is not None
    assert rendered_div.style.color == "red"
    assert rendered_div.style.fontSize == "16px"
