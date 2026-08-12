"""Tests for the jsx t-string template tag."""


def test_simple_element():
    from crank import El
    from crank.template import jsx

    el = jsx(t"<div>Hello</div>")
    assert isinstance(el, El)
    assert el.tag == "div"
    assert el.children == ["Hello"]


def test_element_with_string_props():
    from crank.template import jsx

    el = jsx(t'<div id="app" class="container">Content</div>')
    assert el.props == {"id": "app", "class": "container"}
    assert el.children == ["Content"]


def test_prop_expression():
    from crank.template import jsx

    handler = lambda ev: None  # noqa: E731
    el = jsx(t"<button onclick={handler} disabled={True}>Go</button>")
    assert el.props["onclick"] is handler
    assert el.props["disabled"] is True


def test_boolean_prop():
    from crank.template import jsx

    el = jsx(t"<input checked />")
    assert el.tag == "input"
    assert el.props == {"checked": True}


def test_child_expression():
    from crank.template import jsx

    name = "World"
    el = jsx(t"<div>Hello, {name}!</div>")
    assert el.children == ["Hello, ", "World", "!"]


def test_child_conversion_and_format():
    from crank.template import jsx

    count = 3.14159
    el = jsx(t"<span>{count:.2f}</span>")
    assert el.children == ["3.14"]


def test_interpolated_prop_string():
    from crank.template import jsx

    theme = "dark"
    el = jsx(t'<div class="btn {theme}">x</div>')
    assert el.props == {"class": "btn dark"}


def test_nested_elements():
    from crank.template import jsx

    el = jsx(t"<ul><li>One</li><li>Two</li></ul>")
    assert el.tag == "ul"
    assert len(el.children) == 2
    assert el.children[0].tag == "li"
    assert el.children[0].children == ["One"]
    assert el.children[1].children == ["Two"]


def test_fragment():
    from crank import Fragment
    from crank.template import jsx

    el = jsx(t"<div>a</div><div>b</div>")
    assert el.tag is Fragment or el.tag == Fragment
    assert len(el.children) == 2


def test_self_closing():
    from crank.template import jsx

    el = jsx(t'<img src="x.png" />')
    assert el.tag == "img"
    assert el.props == {"src": "x.png"}
    assert el.children == []


def test_component_tag():
    from crank import component, h
    from crank.template import jsx

    @component
    def Greeting(ctx, props):
        return h.div[f"Hello, {props.get('name', 'World')}"]

    el = jsx(t'<{Greeting} name="Test" />')
    assert el.tag is Greeting
    assert el.props == {"name": "Test"}

    el2 = jsx(t"<{Greeting}>child<//>")
    assert el2.tag is Greeting
    assert el2.children == ["child"]


def test_spread_props():
    from crank.template import jsx

    extra = {"id": "spread", "title": "hi"}
    el = jsx(t'<div class="base" ...{extra}>x</div>')
    assert el.props == {"class": "base", "id": "spread", "title": "hi"}


def test_comment():
    from crank.template import jsx

    el = jsx(t"<div><!-- ignored -->text</div>")
    assert el.children == ["text"]


def test_whitespace_handling():
    from crank.template import jsx

    el = jsx(t"""
        <div>
            <span>a</span>
            <span>b</span>
        </div>
    """)
    assert el.tag == "div"
    assert len(el.children) == 2


def test_unmatched_closing_tag_error():
    from crank.template import jsx

    try:
        jsx(t"<div>text</span>")
    except SyntaxError as e:
        assert "div" in str(e) and "span" in str(e)
    else:
        raise AssertionError("expected SyntaxError")


def test_render_to_dom():
    from js import document

    from crank.dom import renderer
    from crank.template import jsx

    name = "Crank"
    document.body.innerHTML = ""
    renderer.render(
        jsx(t'<div id="jsx-root"><h1>Hello, {name}</h1></div>'), document.body
    )
    root = document.getElementById("jsx-root")
    assert root is not None
    assert document.querySelector("h1").textContent == "Hello, Crank"


def test_render_component_with_state():
    from js import document

    from crank import component
    from crank.dom import renderer
    from crank.template import jsx

    @component
    def Counter(ctx):
        count = 42
        for _ in ctx:
            yield jsx(t"<p>Count: {count}</p>")

    document.body.innerHTML = ""
    renderer.render(jsx(t"<div><{Counter} /></div>"), document.body)
    assert document.querySelector("p").textContent == "Count: 42"


def test_html_alias():
    from crank.template import html, jsx

    assert html is jsx
    el = html(t"<div>aliased</div>")
    assert el.tag == "div"
    assert el.children == ["aliased"]


def test_parse_cache_reuse():
    from crank.template import jsx

    def make(n):
        return jsx(t"<div>{n}</div>")

    a = make(1)
    b = make(2)
    assert a.children == [1]
    assert b.children == [2]
