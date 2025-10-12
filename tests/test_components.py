"""
Component functionality tests - implementation agnostic
"""

import sys
from upytest import skip

# Check if running in MicroPython
is_micropython = "micropython" in sys.version.lower()

def test_simple_component():
    """Test basic component functionality with actual rendering"""
    from crank import h, component
    from crank.dom import renderer
    from js import document
    
    @component
    def SimpleComponent(ctx):
        for _ in ctx:
            yield h.div["Simple component"]
    
    # Test actual rendering
    result = renderer.render(h(SimpleComponent), document.body)
    assert result is not None

def test_component_with_props():
    """Test component with props and actual rendering"""
    from crank import h, component
    from crank.dom import renderer
    from js import document
    
    @component
    def PropsComponent(ctx, props):
        # Generator components should receive new props on each iteration
        for props in ctx:  # This should receive updated props
            name = props.get("name", "World")
            yield h.div[f"Hello {name}"]
    
    # Clear DOM first to avoid conflicts
    document.body.innerHTML = ""
    
    # Test actual rendering with props and verify prop handling
    renderer.render(h(PropsComponent, name="Test"), document.body)
    
    # Verify props were correctly processed and rendered
    rendered_div = document.querySelector("div")
    assert rendered_div is not None
    assert rendered_div.textContent == "Hello Test"
    
    # Test with different props to verify dynamic behavior
    renderer.render(h(PropsComponent, name="World"), document.body)
    
    # Verify props update correctly
    updated_div = document.querySelector("div")
    assert updated_div is not None
    assert updated_div.textContent == "Hello World"

def test_component_context_only():
    """Test component with context only"""
    from crank import h, component
    from crank.dom import renderer
    from js import document
    
    @component  
    def ContextComponent(ctx):
        for _ in ctx:
            yield h.div["Context only"]
    
    # Clear DOM and render
    document.body.innerHTML = ""
    renderer.render(h(ContextComponent), document.body)
    
    # Verify component rendered correctly
    rendered_div = document.querySelector("div")
    assert rendered_div is not None
    assert rendered_div.textContent == "Context only"

def test_component_no_params():
    """Test component with no parameters"""
    from crank import h, component
    from crank.dom import renderer
    from js import document
    
    @component
    def NoParamsComponent():
        return h.div["No params"]
    
    # Clear DOM and render
    document.body.innerHTML = ""
    renderer.render(h(NoParamsComponent), document.body)
    
    # Verify component rendered correctly
    rendered_div = document.querySelector("div")
    assert rendered_div is not None
    assert rendered_div.textContent == "No params"

def test_generator_component():
    """Test generator component"""
    from crank import h, component
    from crank.dom import renderer
    from js import document
    
    @component
    def GeneratorComponent(ctx):
        for props in ctx:
            count = props.get("count", 0)
            yield h.div[f"Count: {count}"]
    
    # Clear DOM and render
    document.body.innerHTML = ""
    renderer.render(h(GeneratorComponent, count=5), document.body)
    
    # Verify generator component rendered with props
    rendered_div = document.querySelector("div")
    assert rendered_div is not None
    assert rendered_div.textContent == "Count: 5"

@skip("async def + yield not supported in MicroPython", skip_when=is_micropython)
def test_async_generator_component():
    """Test async generator component creation (Pyodide only)"""
    from crank import h, component
    
    @component
    async def AsyncGeneratorComponent(ctx):
        async for props in ctx:
            value = props.get("value", "default")
            yield h.div[f"Async: {value}"]
    
    # Test component creation (async def + yield only works in Pyodide)
    element = h(AsyncGeneratorComponent, value="test")
    assert element is not None

def test_nested_components():
    """Test nested components with real rendering"""
    from crank import h, component
    from crank.dom import renderer
    from js import document
    
    @component
    def InnerComponent(ctx, props):
        text = props.get("text", "inner")
        for _ in ctx:
            yield h.span[text]
    
    @component
    def OuterComponent(ctx, props):
        title = props.get("title", "outer")
        for _ in ctx:
            yield h.div[
                h.h1[title],
                h(InnerComponent, text="nested")
            ]
    
    # Clear DOM and render nested components
    document.body.innerHTML = ""
    renderer.render(h(OuterComponent, title="Test Title"), document.body)
    
    # Verify nested structure rendered correctly
    rendered_h1 = document.querySelector("h1")
    rendered_span = document.querySelector("span")
    assert rendered_h1 is not None
    assert rendered_span is not None
    assert rendered_h1.textContent == "Test Title"
    assert rendered_span.textContent == "nested"

def test_component_with_children():
    """Test component that renders children with real rendering"""
    from crank import h, component
    from crank.dom import renderer
    from js import document
    
    @component
    def WrapperComponent(ctx, props):
        for _ in ctx:
            yield h.div(className="wrapper")[
                h.h2["Wrapper"],
                props.get("children", [])
            ]
    
    # Clear DOM and render component with children
    document.body.innerHTML = ""
    renderer.render(h(WrapperComponent, children=[
        h.p["Child 1"],
        h.p["Child 2"]
    ]), document.body)
    
    # Verify wrapper and children rendered correctly
    wrapper_div = document.querySelector("div.wrapper")
    wrapper_h2 = document.querySelector("h2")
    child_paragraphs = list(document.querySelectorAll("p"))
    
    assert wrapper_div is not None
    assert wrapper_h2 is not None
    assert wrapper_h2.textContent == "Wrapper"
    assert len(child_paragraphs) == 2
    assert child_paragraphs[0].textContent == "Child 1"
    assert child_paragraphs[1].textContent == "Child 2"

def test_component_conditional_rendering():
    """Test component with conditional rendering"""
    from crank import h, component
    from crank.dom import renderer
    from js import document
    
    @component
    def ConditionalComponent(ctx, props):
        for props in ctx:  # Re-enable context iteration with our fix
            show = props.get("show", True)
            if show:
                yield h.div["Visible"]
            else:
                yield h.div["Hidden"]
    
    # Test visible condition
    document.body.innerHTML = ""
    renderer.render(h(ConditionalComponent, show=True), document.body)
    visible_div = document.querySelector("div")
    assert visible_div is not None
    assert visible_div.textContent == "Visible"
    
    # Test hidden condition  
    document.body.innerHTML = ""
    renderer.render(h(ConditionalComponent, show=False), document.body)
    hidden_div = document.querySelector("div")
    assert hidden_div is not None
    assert hidden_div.textContent == "Hidden"