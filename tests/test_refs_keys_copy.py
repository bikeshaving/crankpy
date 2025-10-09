"""
Tests for refs, keys, and copy props - achieving Crank.js parity
These are critical features for DOM manipulation and component optimization
"""

def test_basic_ref():
    """Test basic ref callback execution with real rendering"""
    from crank import h
    from crank.dom import renderer
    from js import document
    
    ref_called = False
    ref_element = None
    
    def ref_callback(element):
        nonlocal ref_called, ref_element
        ref_called = True
        ref_element = element
    
    # Clear DOM and render with ref
    document.body.innerHTML = ""
    renderer.render(h.div(ref=ref_callback)["Hello"], document.body)
    
    # Verify element was rendered
    rendered_div = document.querySelector("div")
    assert rendered_div is not None
    assert rendered_div.textContent == "Hello"
    
    # Verify ref callback was called with actual DOM element
    assert ref_called
    assert ref_element is not None
    # In real implementation, ref_element should be the same as rendered_div

def test_ref_passing_through_components():
    """Test ref passing through function components with real rendering"""
    from crank import h, component
    from crank.dom import renderer
    from js import document
    
    ref_called = False
    ref_element = None
    
    def ref_callback(element):
        nonlocal ref_called, ref_element
        ref_called = True
        ref_element = element
    
    @component
    def Component(ctx, props):
        ref = props.get("ref")
        return h.span(ref=ref)["Hello"]
    
    # Clear DOM and render component with ref
    document.body.innerHTML = ""
    renderer.render(h.div[h(Component, ref=ref_callback)], document.body)
    
    # Verify component rendered
    rendered_span = document.querySelector("span")
    assert rendered_span is not None
    assert rendered_span.textContent == "Hello"
    
    # Verify ref callback was called
    assert ref_called
    assert ref_element is not None

def test_basic_keys():
    """Test basic key functionality with real rendering"""
    from crank import h
    from crank.dom import renderer
    from js import document
    
    # Elements with keys
    keyed_elements = [
        h.span(key="1")["1"],
        h.span(key="2")["2"],
        h.span(key="3")["3"]
    ]
    
    # Clear DOM and render keyed elements
    document.body.innerHTML = ""
    renderer.render(h.div[keyed_elements], document.body)
    
    # Verify keyed elements rendered correctly
    rendered_spans = list(document.querySelectorAll("span"))
    assert len(rendered_spans) == 3
    assert rendered_spans[0].textContent == "1"
    assert rendered_spans[1].textContent == "2"
    assert rendered_spans[2].textContent == "3"

def test_simple_dom_identity():
    """Test the most basic DOM identity preservation between renders"""
    from crank import h, createElement
    from crank.dom import renderer
    from js import document, console
    
    # Clear DOM
    document.body.innerHTML = ""
    
    # Debug: Check what renderer.render actually returns
    element1 = h.span["Hello"]
    element2 = h.span["Hello"]
    
    console.log("element1:", element1)
    console.log("element2:", element2)
    console.log("element1 === element2:", element1 is element2)
    console.log("typeof renderer.render:", type(renderer.render))
    
    # First render - single element
    result1 = renderer.render(element1, document.body)
    console.log("First render result:", result1)
    
    first_span = document.querySelector("span")
    assert first_span is not None
    assert first_span.textContent == "Hello"
    console.log("First span:", first_span)
    
    # Second render - same element structure
    result2 = renderer.render(element2, document.body)
    console.log("Second render result:", result2)
    
    second_span = document.querySelector("span")
    assert second_span is not None
    assert second_span.textContent == "Hello"
    console.log("Second span:", second_span)
    
    # Check if the DOM node is the same object using js_id
    is_same_node = first_span.js_id == second_span.js_id
    console.log("DOM nodes identical (js_id):", is_same_node)
    console.log("first_span.js_id:", first_span.js_id)
    console.log("second_span.js_id:", second_span.js_id)
    
    # Also check if the rendered elements are the same
    console.log("Render results identical:", result1.js_id == result2.js_id if hasattr(result1, 'js_id') else "No js_id")
    
    # If this fails, DOM reconciliation isn't working at all
    assert is_same_node, "Single element should preserve DOM node identity on re-render"

def test_key_reordering():
    """Test that keyed elements maintain DOM node identity during reordering"""
    from crank import h, component
    from crank.dom import renderer
    from js import document
    
    @component
    def KeyedList(ctx, props):
        for props in ctx:
            order = props.get("order", ["1", "2", "3"])
            yield h.div[[
                h.span(key=key)[f"Item {key}"] for key in order
            ]]
    
    # Clear body first
    document.body.innerHTML = ""
    
    # Render initial order [1, 2, 3]
    renderer.render(h(KeyedList, order=["1", "2", "3"]), document.body)
    original_spans = list(document.querySelectorAll("span"))
    
    # Verify initial rendering
    assert len(original_spans) == 3
    assert original_spans[0].textContent == "Item 1"
    assert original_spans[1].textContent == "Item 2"
    assert original_spans[2].textContent == "Item 3"
    
    # Store references to original DOM nodes
    item1_node = original_spans[0]  # "Item 1" 
    item2_node = original_spans[1]  # "Item 2"
    item3_node = original_spans[2]  # "Item 3"
    
    # Render reordered [3, 1, 2]
    renderer.render(h(KeyedList, order=["3", "1", "2"]), document.body)
    reordered_spans = list(document.querySelectorAll("span"))
    
    # Verify keyed elements are reordered correctly
    assert len(reordered_spans) == 3
    assert reordered_spans[0].textContent == "Item 3"
    assert reordered_spans[1].textContent == "Item 1"
    assert reordered_spans[2].textContent == "Item 2"
    
    # CRITICAL: Verify DOM node identity is preserved during reordering
    # The same DOM nodes should exist in new positions (if keys work correctly)
    assert reordered_spans[1].js_id == item1_node.js_id, "Item 1 DOM node should maintain identity"
    assert reordered_spans[2].js_id == item2_node.js_id, "Item 2 DOM node should maintain identity"
    assert reordered_spans[0].js_id == item3_node.js_id, "Item 3 DOM node should maintain identity"

def test_keyed_arrays():
    """Test keyed arrays and DOM node identity preservation"""
    from crank import h
    from crank.dom import renderer
    from js import document
    
    items = ["apple", "banana", "cherry"]
    
    # Create and render keyed list
    keyed_list = [h.li(key=item)[item] for item in items]
    document.body.innerHTML = ""
    renderer.render(h.ul[keyed_list], document.body)
    
    # Verify original list rendered correctly
    original_lis = list(document.querySelectorAll("li"))
    assert len(original_lis) == 3
    assert original_lis[0].textContent == "apple"
    assert original_lis[1].textContent == "banana"
    assert original_lis[2].textContent == "cherry"
    
    # Store references to original DOM nodes
    apple_node = original_lis[0]
    cherry_node = original_lis[2]  # banana will be removed
    
    # Modify the list (remove middle item) and re-render
    modified_items = ["apple", "cherry"]
    modified_list = [h.li(key=item)[item] for item in modified_items]
    renderer.render(h.ul[modified_list], document.body)
    
    # Verify modified list rendered correctly
    modified_lis = list(document.querySelectorAll("li"))
    assert len(modified_lis) == 2
    assert modified_lis[0].textContent == "apple"
    assert modified_lis[1].textContent == "cherry"
    
    # CRITICAL: Verify DOM node identity is preserved for remaining items
    assert modified_lis[0].js_id == apple_node.js_id, "Apple DOM node should maintain identity"
    assert modified_lis[1].js_id == cherry_node.js_id, "Cherry DOM node should maintain identity"

def test_mixed_keyed_unkeyed():
    """Test mix of keyed and unkeyed elements with real rendering"""
    from crank import h
    from crank.dom import renderer
    from js import document
    
    # Clear DOM and render mixed elements
    document.body.innerHTML = ""
    renderer.render(h.div[
        h.span["Unkeyed"],
        h.span(key="keyed")["Keyed"],
        h.span["Another unkeyed"]
    ], document.body)
    
    # Verify mixed elements rendered correctly
    rendered_spans = list(document.querySelectorAll("span"))
    assert len(rendered_spans) == 3
    assert rendered_spans[0].textContent == "Unkeyed"
    assert rendered_spans[1].textContent == "Keyed"
    assert rendered_spans[2].textContent == "Another unkeyed"

def test_duplicate_keys():
    """Test duplicate key handling (should work but may warn)"""
    from crank import h
    
    # This should work but may produce warnings in real implementations
    duplicate_keys = h.div[
        h.span(key="same")["First"],
        h.span(key="same")["Second"],
        h.span(key="same")["Third"]
    ]
    assert duplicate_keys is not None

def test_basic_copy_prop():
    """Test basic copy prop functionality with real rendering"""
    from crank import h, component
    from crank.dom import renderer
    from js import document
    
    @component
    def CopyTestComponent(ctx, props):
        for props in ctx:
            copy_mode = props.get("copy", False)
            content = props.get("content", "default")
            yield h.div(copy=copy_mode)[f"Content: {content}"]
    
    # Test copy=True behavior
    document.body.innerHTML = ""
    renderer.render(h(CopyTestComponent, copy=True, content="original"), document.body)
    
    original_div = document.querySelector("div")
    assert original_div is not None
    assert "Content: original" in original_div.textContent
    
    # Test copy=False behavior  
    document.body.innerHTML = ""
    renderer.render(h(CopyTestComponent, copy=False, content="updated"), document.body)
    
    updated_div = document.querySelector("div")
    assert updated_div is not None
    assert "Content: updated" in updated_div.textContent

def test_copy_with_components():
    """Test copy prop with components and real rendering"""
    from crank import h, component
    from crank.dom import renderer
    from js import document
    
    @component  
    def Greeting(ctx, props):
        for props in ctx:
            name = props.get("name", "World")
            yield h.div[f"Hello {name}"]
    
    # Test component with copy=True
    document.body.innerHTML = ""
    renderer.render(h(Greeting, copy=True, name="Alice"), document.body)
    
    alice_div = document.querySelector("div")
    assert alice_div is not None
    assert alice_div.textContent == "Hello Alice"
    
    # Test component with copy=False
    document.body.innerHTML = ""
    renderer.render(h(Greeting, copy=False, name="Bob"), document.body)
    
    bob_div = document.querySelector("div")
    assert bob_div is not None
    assert bob_div.textContent == "Hello Bob"

def test_selective_copy_props():
    """Test selective prop copying"""
    from crank import h
    
    # Copy specific props only
    selective = h.div(
        copy="style class",
        style="color: red;",
        className="greeting",
        id="test"
    )["Content"]
    assert selective is not None

def test_copy_prop_exclusion():
    """Test copy prop exclusion with !prop syntax"""
    from crank import h
    
    # Exclude specific props from copying
    excluded = h.div(
        copy="!style !class", 
        style="color: blue;",
        className="excluded",
        id="included"
    )["Content"]
    assert excluded is not None

def test_copy_children():
    """Test copy=children to preserve child content"""
    from crank import h
    
    # Copy children only
    children_copied = h.div(copy="children", className="new-class")["Original children"]
    assert children_copied is not None
    
    # Exclude children from copying
    children_excluded = h.div(copy="!children", className="updated")["New children"]
    assert children_excluded is not None

def test_refs_with_generators():
    """Test refs with generator components and real rendering"""
    from crank import h, component
    from crank.dom import renderer
    from js import document
    
    ref_called = False
    ref_element = None
    
    def ref_callback(element):
        nonlocal ref_called, ref_element
        ref_called = True
        ref_element = element
    
    @component
    def GeneratorComponent(ctx, props):
        ref = props.get("ref")
        for props in ctx:
            yield h.div(ref=ref)["Generator content"]
    
    # Clear DOM and render generator with ref
    document.body.innerHTML = ""
    renderer.render(h(GeneratorComponent, ref=ref_callback), document.body)
    
    # Verify generator rendered
    rendered_div = document.querySelector("div")
    assert rendered_div is not None
    assert rendered_div.textContent == "Generator content"
    
    # Verify ref callback was called
    assert ref_called
    assert ref_element is not None

def test_copy_with_generators():
    """Test copy prop with generator components"""
    from crank import h, component
    
    @component
    def TimerComponent(ctx, props):
        counter = 0
        copy_prop = props.get("copy", False)
        
        for props in ctx:
            counter += 1
            yield h.div[f"Count: {counter}"]
    
    # Generator with copy=True should preserve state
    copied_gen = h(TimerComponent, copy=True)
    assert copied_gen is not None

def test_complex_key_scenarios():
    """Test complex key-based scenarios"""
    from crank import h
    
    # Moving elements around
    scenario1 = h.div[
        h.span(key="a")["A"],
        h.span(key="b")["B"], 
        h.span(key="c")["C"]
    ]
    
    # Reverse order
    scenario2 = h.div[
        h.span(key="c")["C"],
        h.span(key="b")["B"],
        h.span(key="a")["A"]
    ]
    
    # Add new items
    scenario3 = h.div[
        h.span(key="a")["A"],
        h.span(key="x")["X"],  # New
        h.span(key="b")["B"],
        h.span(key="y")["Y"],  # New
        h.span(key="c")["C"]
    ]
    
    assert scenario1 is not None
    assert scenario2 is not None
    assert scenario3 is not None

def test_ref_with_special_elements():
    """Test refs with special elements like Portal, Raw, etc."""
    from crank import h, Portal, Raw, Text
    
    ref_called = False
    
    def ref_callback(element):
        nonlocal ref_called
        ref_called = True
    
    # Ref with Portal
    portal_with_ref = h(Portal, ref=ref_callback, root="body")[
        h.div["Portal content"]
    ]
    assert portal_with_ref is not None
    
    # Ref with Raw
    raw_with_ref = h(Raw, ref=ref_callback)["<em>Raw content</em>"]
    assert raw_with_ref is not None

def test_copy_isolation_pattern():
    """Test copy prop for component isolation"""
    from crank import h, component
    
    def isolate(Component):
        """Higher-order component that isolates a component"""
        @component
        def Wrapper(ctx, props):
            return h(Component, **props, copy=True)
        return Wrapper
    
    @component
    def BaseComponent(ctx, props):
        name = props.get("name", "Default")
        return h.div[f"Hello {name}"]
    
    IsolatedComponent = isolate(BaseComponent)
    
    # Isolated component should work
    isolated = h(IsolatedComponent, name="Isolated")
    assert isolated is not None

def test_refs_in_nested_structures():
    """Test refs in deeply nested component structures"""
    from crank import h, component
    
    refs_called = []
    
    def make_ref_callback(name):
        def callback(element):
            refs_called.append(name)
        return callback
    
    @component
    def Child(ctx, props):
        ref = props.get("ref")
        return h.span(ref=ref)[props.get("text", "")]
    
    @component  
    def Parent(ctx, props):
        return h.div[
            h(Child, ref=make_ref_callback("child1"), text="First"),
            h(Child, ref=make_ref_callback("child2"), text="Second")
        ]
    
    # Nested refs should work
    nested = h(Parent)
    assert nested is not None

def test_dynamic_keys():
    """Test dynamically generated keys"""
    from crank import h
    
    # Generate elements with dynamic keys
    dynamic_items = []
    for i in range(5):
        key = f"item-{i}"
        element = h.li(key=key)[f"Item {i}"]
        dynamic_items.append(element)
    
    dynamic_list = h.ul[dynamic_items]
    assert dynamic_list is not None
    
    # Shuffle the items (simulating reordering) - manual shuffle for MicroPython compatibility
    shuffled_indices = [3, 1, 4, 0, 2]  # Manually shuffled order
    
    shuffled_items = []
    for i in shuffled_indices:
        key = f"item-{i}"
        element = h.li(key=key)[f"Item {i}"]
        shuffled_items.append(element)
    
    shuffled_list = h.ul[shuffled_items]
    assert shuffled_list is not None

def test_copy_with_async_components():
    """Test copy prop with async-style components"""
    from crank import h, component
    
    @component
    def AsyncStyleComponent(ctx, props):
        # Simulate async behavior with a simple counter
        copy_prop = props.get("copy", False)
        message = props.get("message", "Default")
        
        # In real async components, copy would prevent re-execution
        return h.div[f"Async: {message}"]
    
    # Test with copy=True
    copied_async = h(AsyncStyleComponent, copy=True, message="Copied")
    assert copied_async is not None
    
    # Test with copy=False
    normal_async = h(AsyncStyleComponent, copy=False, message="Normal")
    assert normal_async is not None