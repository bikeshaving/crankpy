"""
Component functionality tests - implementation agnostic
"""

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
        name = props.get("name", "World")
        for _ in ctx:
            yield h.div[f"Hello {name}"]
    
    # Test actual rendering with props and verify prop handling
    renderer.render(h(PropsComponent, name="Test"), document.body)
    
    # Verify props were correctly processed and rendered
    rendered_div = document.querySelector("div")
    assert rendered_div is not None
    assert rendered_div.textContent == "Hello Test"
    
    # Test with different props to verify dynamic behavior
    renderer.render(h(PropsComponent, name="World"), document.body)
    assert rendered_div.textContent == "Hello World"

def test_component_context_only():
    """Test component with context only"""
    from crank import h, component
    
    @component  
    def ContextComponent(ctx):
        for _ in ctx:
            yield h.div["Context only"]
    
    element = h(ContextComponent)
    assert element is not None

def test_component_no_params():
    """Test component with no parameters"""
    from crank import h, component
    
    @component
    def NoParamsComponent():
        return h.div["No params"]
    
    element = h(NoParamsComponent)
    assert element is not None

def test_generator_component():
    """Test generator component"""
    from crank import h, component
    
    @component
    def GeneratorComponent(ctx):
        for props in ctx:
            count = props.get("count", 0)
            yield h.div[f"Count: {count}"]
    
    element = h(GeneratorComponent, count=5)
    assert element is not None

def test_async_generator_component():
    """Test async generator component"""
    from crank import h, component
    
    @component
    async def AsyncGeneratorComponent(ctx):
        async for props in ctx:
            value = props.get("value", "default")
            yield h.div[f"Async: {value}"]
    
    element = h(AsyncGeneratorComponent, value="test")
    assert element is not None

def test_nested_components():
    """Test nested components"""
    from crank import h, component
    
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
    
    element = h(OuterComponent, title="Test Title")
    assert element is not None

def test_component_with_children():
    """Test component that renders children"""
    from crank import h, component
    
    @component
    def WrapperComponent(ctx, props):
        for _ in ctx:
            yield h.div(className="wrapper")[
                h.h2["Wrapper"],
                props.get("children", [])
            ]
    
    element = h(WrapperComponent, children=[
        h.p["Child 1"],
        h.p["Child 2"]
    ])
    assert element is not None

def test_component_conditional_rendering():
    """Test component with conditional rendering"""
    from crank import h, component
    
    @component
    def ConditionalComponent(ctx, props):
        show = props.get("show", True)
        for _ in ctx:
            if show:
                yield h.div["Visible"]
            else:
                yield h.div["Hidden"]
    
    visible = h(ConditionalComponent, show=True)
    hidden = h(ConditionalComponent, show=False)
    assert visible is not None
    assert hidden is not None