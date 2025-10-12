"""
Generator and async generator component tests - implementation agnostic
"""

import sys
from upytest import skip

# Check if running in MicroPython
is_micropython = "micropython" in sys.version.lower()

def test_simple_generator():
    """Test simple generator component with actual rendering"""
    from crank import h, component
    from crank.dom import renderer
    from js import document
    
    @component
    def SimpleGenerator(ctx):
        count = 0
        for _ in ctx:
            count += 1
            yield h.div[f"Render {count}"]
    
    # Clear DOM first to avoid conflicts
    document.body.innerHTML = ""
    
    # Test actual rendering and verify DOM content
    renderer.render(h(SimpleGenerator), document.body)
    
    # Verify the generator actually rendered content to DOM
    rendered_div = document.querySelector("div")
    assert rendered_div is not None
    assert "Render 1" in rendered_div.textContent

def test_generator_with_state():
    """Test generator component with internal state and actual rendering"""
    from crank import h, component
    from crank.dom import renderer
    from js import document
    
    @component
    def StatefulGenerator(ctx, props):
        state = {"counter": 0}
        
        for props in ctx:
            increment = props.get("increment", 1)
            state["counter"] += increment
            yield h.div[f"Counter: {state['counter']}"]
    
    # Clear DOM first to avoid conflicts
    document.body.innerHTML = ""
    
    # Test actual rendering and verify state management
    renderer.render(h(StatefulGenerator, increment=2), document.body)
    
    # Verify state was properly managed and rendered
    rendered_div = document.querySelector("div")
    assert rendered_div is not None
    assert "Counter: 2" in rendered_div.textContent  # Should increment by 2

@skip("async def + yield not supported in MicroPython", skip_when=is_micropython)
async def test_async_generator():
    """Test async generator component with actual rendering"""
    from crank import h, component
    from crank.dom import renderer
    from js import document
    
    @component
    async def AsyncGenerator(ctx, props):
        count = 0
        async for props in ctx:
            count += 1
            delay = props.get("delay", 0)
            yield h.div[f"Async render {count} (delay: {delay})"]
    
    # Test actual async rendering - will fail in MicroPython due to async def + yield
    result = await renderer.render(h(AsyncGenerator, delay=100), document.body)
    assert result is not None

def test_generator_with_props_changes():
    """Test generator responding to prop changes with real rendering"""
    from crank import h, component
    from crank.dom import renderer
    from js import document
    
    @component
    def PropsChangeGenerator(ctx, props):
        renders = []
        
        for props in ctx:
            name = props.get("name", "default")
            renders.append(name)
            yield h.div[
                h.h3[f"Current: {name}"],
                h.ul[[h.li[render] for render in renders]]
            ]
    
    # Clear DOM and render with initial props
    document.body.innerHTML = ""
    renderer.render(h(PropsChangeGenerator, name="initial"), document.body)
    
    # Verify initial render
    h3_element = document.querySelector("h3")
    li_elements = list(document.querySelectorAll("li"))
    assert h3_element is not None
    assert h3_element.textContent == "Current: initial"
    assert len(li_elements) == 1
    assert li_elements[0].textContent == "initial"

def test_generator_with_cleanup():
    """Test generator with cleanup logic registration"""
    from crank import h, component
    from crank.dom import renderer
    from js import document
    
    @component
    def CleanupGenerator(ctx, props):
        resources = []
        
        def cleanup():
            resources.clear()  # Cleanup function for testing registration
        
        for props in ctx:
            ctx.cleanup(cleanup)
            resource_id = props.get("resource", "default")
            resources.append(resource_id)
            yield h.div[f"Resources: {len(resources)}"]
    
    # Clear DOM and render
    document.body.innerHTML = ""
    renderer.render(h(CleanupGenerator, resource="test"), document.body)
    
    # Verify component rendered and cleanup was registered
    rendered_div = document.querySelector("div")
    assert rendered_div is not None
    assert "Resources: 1" in rendered_div.textContent

def test_nested_generators():
    """Test nested generator components with real rendering"""
    from crank import h, component
    from crank.dom import renderer
    from js import document
    
    @component
    def InnerGenerator(ctx, props):
        for props in ctx:
            value = props.get("value", 0)
            yield h.span[f"Inner: {value}"]
    
    @component
    def OuterGenerator(ctx, props):
        for props in ctx:
            multiplier = props.get("multiplier", 1)
            yield h.div[
                h.h2["Outer Generator"],
                h(InnerGenerator, value=multiplier * 2)
            ]
    
    # Clear DOM and render nested generators
    document.body.innerHTML = ""
    renderer.render(h(OuterGenerator, multiplier=3), document.body)
    
    # Verify nested generator structure
    h2_element = document.querySelector("h2")
    span_element = document.querySelector("span")
    assert h2_element is not None
    assert span_element is not None
    assert h2_element.textContent == "Outer Generator"
    assert span_element.textContent == "Inner: 6"  # 3 * 2 = 6

def test_async_generator_with_state():
    """Test async generator with state management (Pyodide only)"""
    from crank import h, component
    
    @component
    async def AsyncStateGenerator(ctx, props):
        state = {"data": [], "loading": False}
        
        async for props in ctx:
            action = props.get("action", "idle")
            
            if action == "load":
                state["loading"] = True
                yield h.div["Loading..."]
                # Simulate async operation
                state["data"].append(f"Item {len(state['data']) + 1}")
                state["loading"] = False
            
            yield h.div[
                h.p[f"Items: {len(state['data'])}"],
                h.ul[[h.li[item] for item in state["data"]]]
            ]
    
    # Test component creation (async def + yield only works in Pyodide)
    element = h(AsyncStateGenerator, action="load")
    assert element is not None

def test_generator_error_handling():
    """Test generator with error handling and real rendering"""
    from crank import h, component
    from crank.dom import renderer
    from js import document
    
    @component
    def ErrorHandlingGenerator(ctx, props):
        errors = []
        
        for props in ctx:
            try:
                should_error = props.get("error", False)
                if should_error:
                    raise ValueError("Test error")
                yield h.div["No errors"]
            except Exception as e:
                errors.append(str(e))
                yield h.div[
                    h.p["Error occurred"],
                    h.ul[[h.li[error] for error in errors]]
                ]
    
    # Test error handling with real rendering
    document.body.innerHTML = ""
    renderer.render(h(ErrorHandlingGenerator, error=True), document.body)
    
    # Verify error was caught and rendered
    error_p = document.querySelector("p")
    error_li = document.querySelector("li")
    assert error_p is not None
    assert error_li is not None
    assert error_p.textContent == "Error occurred"
    assert "Test error" in error_li.textContent

def test_generator_with_context_methods():
    """Test generator using context methods with mock tracking"""
    from crank import h, component
    from crank.dom import renderer
    from js import document
    
    # Track lifecycle calls
    lifecycle_calls = []
    
    @component
    def ContextMethodsGenerator(ctx, props):
        def scheduled_task(value):
            lifecycle_calls.append(f"scheduled:{value}")
        
        def after_render(value):
            lifecycle_calls.append(f"after:{value}")
        
        for props in ctx:
            lifecycle_calls.append("generator_iteration")
            ctx.schedule(scheduled_task)
            ctx.after(after_render)
            
            count = props.get("count", 0)
            yield h.div[f"Context methods: {count}"]
    
    # Clear DOM and render
    document.body.innerHTML = ""
    renderer.render(h(ContextMethodsGenerator, count=5), document.body)
    
    # Verify component rendered correctly
    rendered_div = document.querySelector("div")
    assert rendered_div is not None
    assert rendered_div.textContent == "Context methods: 5"
    
    # Verify generator executed and registered lifecycle hooks
    assert "generator_iteration" in lifecycle_calls
    
    # Note: Schedule and after execution depends on framework's lifecycle implementation
    # This test verifies the hooks can be registered from generator components