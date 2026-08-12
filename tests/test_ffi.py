"""FFI edge-case tests.

These tests exercise the boundary between the pure Python element tree
and the JavaScript runtime: value conversion, callable proxying, element
reuse, and structures that cross the FFI in unusual shapes. Each test
must pass on Pyodide and on MicroPython.

Each test renders into its own container element. Crank keeps
reconciliation state per root, so tests must not share a root while
they wipe the DOM by hand.
"""


def make_root():
    from js import document

    root = document.createElement("div")
    document.body.appendChild(root)
    return root


def test_unicode_text_and_props():
    """Unicode text survives the FFI in children and in props"""
    from crank import h
    from crank.dom import renderer

    root = make_root()
    renderer.render(h.div(title="日本語のタイトル")["Emoji: 🚀🐍 — Ünïcödé"], root)
    div = root.querySelector("div")
    assert div.textContent == "Emoji: 🚀🐍 — Ünïcödé"
    assert div.getAttribute("title") == "日本語のタイトル"


def test_special_characters_as_text():
    """Angle brackets, quotes, and ampersands render as text, not markup"""
    from crank import h
    from crank.dom import renderer

    root = make_root()
    renderer.render(h.div["<script>\"&'</script>"], root)
    div = root.querySelector("div")
    assert div.textContent == "<script>\"&'</script>", div.textContent
    # Pyodide 314 returns a JsNull proxy for a querySelector miss, not
    # None, so test by truthiness rather than identity
    assert not div.querySelector("script"), div.innerHTML


def test_numeric_children():
    """Numbers of different shapes render as text"""
    from crank import h
    from crank.dom import renderer

    root = make_root()
    renderer.render(
        h.div[
            h.span[0],
            h.span[-1],
            h.span[3.5],
            h.span[10**12],
        ],
        root,
    )
    texts = [s.textContent for s in root.querySelectorAll("span")]
    assert texts == ["0", "-1", "3.5", "1000000000000"], texts


def test_falsy_children_are_skipped():
    """None, True, and False render nothing. Zero renders as text."""
    from crank import h
    from crank.dom import renderer

    root = make_root()
    renderer.render(h.div[None, True, False, 0, ""], root)
    div = root.querySelector("div")
    assert div.textContent == "0", div.textContent


def test_nested_list_children():
    """Nested Python lists cross the FFI as nested arrays"""
    from crank import h
    from crank.dom import renderer

    root = make_root()
    renderer.render(h.ul[[[h.li["a"], h.li["b"]], [h.li["c"]]]], root)
    items = list(root.querySelectorAll("li"))
    assert [li.textContent for li in items] == ["a", "b", "c"]


def test_tuple_children():
    """A tuple of children behaves like a list"""
    from crank import h
    from crank.dom import renderer

    root = make_root()
    renderer.render(h.div[("first", " ", "second")], root)
    text = root.querySelector("div").textContent
    assert text == "first second", text


def test_deep_nesting():
    """A 50-level tree transforms and renders without stack problems"""
    from crank import h
    from crank.dom import renderer

    el = h.span["core"]
    for _ in range(50):
        el = h.div[el]

    root = make_root()
    renderer.render(el, root)
    count = len(list(root.querySelectorAll("div")))
    assert count == 50, count
    assert root.querySelector("span").textContent == "core"


def test_shared_subtree():
    """The same El node used twice renders as two elements"""
    from crank import h
    from crank.dom import renderer

    shared = h.span["shared"]
    root = make_root()
    renderer.render(h.div[shared, shared], root)
    spans = list(root.querySelectorAll("span"))
    assert len(spans) == 2
    assert spans[0].textContent == "shared"
    assert spans[1].textContent == "shared"


def test_el_reuse_across_renders():
    """The same El tree renders correctly more than one time"""
    from crank import h
    from crank.dom import renderer

    el = h.p["reusable"]
    root1 = make_root()
    renderer.render(el, root1)
    assert root1.querySelector("p").textContent == "reusable"
    root2 = make_root()
    renderer.render(el, root2)
    assert root2.querySelector("p").textContent == "reusable"


def test_style_object_prop():
    """A dict style prop crosses the FFI as a plain object"""
    from crank import h
    from crank.dom import renderer

    root = make_root()
    renderer.render(
        h.div(style={"color": "red", "backgroundColor": "blue"})["styled"], root
    )
    div = root.querySelector("div")
    assert div.style.color == "red"
    assert div.style.backgroundColor == "blue"


def test_scalar_props_round_trip():
    """Scalar props reach the component unchanged"""
    from crank import component, h
    from crank.dom import renderer

    received = {}

    @component
    def Probe(ctx, props):
        received.update(props)
        return h.div["done"]

    root = make_root()
    renderer.render(h(Probe, text="hello", count=42, ratio=0.5, flag=True), root)
    assert root.querySelector("div").textContent == "done"
    assert received["text"] == "hello"
    assert received["count"] == 42
    assert received["ratio"] == 0.5
    assert received["flag"] is True


def test_element_as_prop():
    """An El passed as a prop transforms and renders inside a component"""
    from crank import component, h
    from crank.dom import renderer

    @component
    def Layout(ctx, props):
        return h.div(className="layout")[props.get("header"), props.get("body")]

    root = make_root()
    renderer.render(h(Layout, header=h.h1["Title"], body=h.p["Body"]), root)
    assert root.querySelector("h1").textContent == "Title"
    assert root.querySelector("p").textContent == "Body"


def test_list_of_elements_as_prop():
    """A list of El nodes passed as one prop renders inside a component"""
    from crank import component, h
    from crank.dom import renderer

    @component
    def List(ctx, props):
        return h.ul[props.get("items")]

    root = make_root()
    renderer.render(h(List, items=[h.li["one"], h.li["two"], h.li["three"]]), root)
    items = list(root.querySelectorAll("li"))
    assert [li.textContent for li in items] == ["one", "two", "three"]


def test_handler_closure_state():
    """A handler closure mutates state, and refresh re-renders"""
    from js import Event

    from crank import component, h
    from crank.dom import renderer

    @component
    def Counter(ctx):
        count = 0

        @ctx.refresh
        def increment():
            nonlocal count
            count += 1

        for _ in ctx:
            yield h.button(onclick=increment)[f"count:{count}"]

    root = make_root()
    renderer.render(h(Counter), root)
    button = root.querySelector("button")
    assert button.textContent == "count:0"
    button.dispatchEvent(Event.new("click"))
    button.dispatchEvent(Event.new("click"))
    assert root.querySelector("button").textContent == "count:2"


def test_bound_method_handler():
    """A bound method works as an event handler across the FFI"""
    from js import Event

    from crank import h
    from crank.dom import renderer

    class Recorder:
        def __init__(self):
            self.calls = []

        def handle(self, event):
            self.calls.append(event.type)

    recorder = Recorder()
    root = make_root()
    renderer.render(h.button(onclick=recorder.handle)["Go"], root)
    root.querySelector("button").dispatchEvent(Event.new("click"))
    assert recorder.calls == ["click"]


def test_callable_object_handler():
    """An object with __call__ works as an event handler across the FFI"""
    from js import Event

    from crank import h
    from crank.dom import renderer

    class Handler:
        def __init__(self):
            self.calls = 0

        def __call__(self, event):
            self.calls += 1

    handler = Handler()
    root = make_root()
    renderer.render(h.button(onclick=handler)["Go"], root)
    root.querySelector("button").dispatchEvent(Event.new("click"))
    assert handler.calls == 1


def test_event_object_access():
    """Handlers can read properties of the JavaScript event object"""
    from js import Event

    from crank import h
    from crank.dom import renderer

    seen = {}

    def handle(event):
        seen["type"] = event.type
        seen["tag"] = event.target.tagName.lower()

    root = make_root()
    renderer.render(h.button(onclick=handle)["x"], root)
    root.querySelector("button").dispatchEvent(Event.new("click"))
    assert seen["type"] == "click"
    assert seen["tag"] == "button"


def test_same_handler_on_two_elements():
    """One function proxied for two elements fires for both"""
    from js import Event

    from crank import h
    from crank.dom import renderer

    calls = []

    def handle(event):
        calls.append(event.target.id)

    root = make_root()
    renderer.render(
        h.div[
            h.button(onclick=handle, id="ffi-btn-a")["A"],
            h.button(onclick=handle, id="ffi-btn-b")["B"],
        ],
        root,
    )
    for button in root.querySelectorAll("button"):
        button.dispatchEvent(Event.new("click"))
    assert calls == ["ffi-btn-a", "ffi-btn-b"]


def test_portal_root_js_node():
    """A real DOM node crosses the FFI as the Portal root prop"""
    from crank import Portal, h
    from crank.dom import renderer

    root = make_root()
    target = make_root()
    renderer.render(
        h.div[
            "main",
            h(Portal, root=target)[h.p["teleported"]],
        ],
        root,
    )
    assert target.querySelector("p").textContent == "teleported"


def test_component_returning_scalars():
    """Components can return a string or a number"""
    from crank import component, h
    from crank.dom import renderer

    @component
    def Text():
        return "just text"

    @component
    def Number():
        return 42

    root = make_root()
    renderer.render(h.div[h(Text), " / ", h(Number)], root)
    assert root.querySelector("div").textContent == "just text / 42"


def test_component_yielding_list():
    """A generator component can yield a list of elements"""
    from crank import component, h
    from crank.dom import renderer

    @component
    def Pair(ctx):
        for _ in ctx:
            yield [h.span["a"], h.span["b"]]

    root = make_root()
    renderer.render(h.div[h(Pair)], root)
    spans = list(root.querySelectorAll("span"))
    assert [s.textContent for s in spans] == ["a", "b"]


def test_prop_namespace_spread():
    """A prop:name key in a spread dict passes through verbatim"""
    from crank import h
    from crank.dom import renderer

    root = make_root()
    renderer.render(h.div(**{"prop:innerHTML": "<b>bold</b>"}), root)
    assert root.querySelector("div b").textContent == "bold"


def test_prop_namespace_double_underscore():
    """prop__name converts to prop:name for keyword arguments"""
    from crank import h
    from crank.dom import renderer

    root = make_root()
    renderer.render(h.div(prop__innerHTML="<i>italic</i>"), root)
    assert root.querySelector("div i").textContent == "italic"


def test_attr_namespace():
    """attr:name sets attributes directly, in both spellings"""
    from crank import h
    from crank.dom import renderer

    root = make_root()
    renderer.render(
        h.div(attr__data_thing="via-kwarg", **{"attr:class": "via-spread"})["x"],
        root,
    )
    div = root.querySelector("div")
    assert div.getAttribute("data-thing") == "via-kwarg"
    assert div.getAttribute("class") == "via-spread"


def test_bare_builder_as_child():
    """A builder with no children renders as an empty element"""
    from crank import h
    from crank.dom import renderer

    root = make_root()
    renderer.render(h.div[h.br, "after break"], root)
    div = root.querySelector("div")
    assert div.querySelector("br") is not None, div.innerHTML
    assert div.textContent == "after break", div.textContent
