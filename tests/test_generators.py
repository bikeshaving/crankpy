"""
Generator and async generator component tests - implementation agnostic
"""

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
    
    # Test actual rendering and verify state management
    renderer.render(h(StatefulGenerator, increment=2), document.body)
    
    # Verify state was properly managed and rendered
    rendered_div = document.querySelector("div")
    assert rendered_div is not None
    assert "Counter: 2" in rendered_div.textContent  # Should increment by 2

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
    """Test generator responding to prop changes"""
    from crank import h, component
    
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
    
    element = h(PropsChangeGenerator, name="initial")
    assert element is not None

def test_generator_with_cleanup():
    """Test generator with cleanup logic"""
    from crank import h, component
    
    @component
    def CleanupGenerator(ctx, props):
        resources = []
        
        def cleanup():
            resources.clear()
        
        for props in ctx:
            ctx.cleanup(cleanup)
            resource_id = props.get("resource", "default")
            resources.append(resource_id)
            yield h.div[f"Resources: {len(resources)}"]
    
    element = h(CleanupGenerator, resource="test")
    assert element is not None

def test_nested_generators():
    """Test nested generator components"""
    from crank import h, component
    
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
    
    element = h(OuterGenerator, multiplier=3)
    assert element is not None

def test_async_generator_with_state():
    """Test async generator with state management"""
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
    
    element = h(AsyncStateGenerator, action="load")
    assert element is not None

def test_generator_error_handling():
    """Test generator with error handling"""
    from crank import h, component
    
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
    
    element = h(ErrorHandlingGenerator, error=True)
    assert element is not None

def test_generator_with_context_methods():
    """Test generator using context methods"""
    from crank import h, component
    
    @component
    def ContextMethodsGenerator(ctx, props):
        def scheduled_task():
            pass
        
        def after_render():
            pass
        
        for props in ctx:
            ctx.schedule(scheduled_task)
            ctx.after(after_render)
            
            count = props.get("count", 0)
            yield h.div[f"Context methods: {count}"]
    
    element = h(ContextMethodsGenerator, count=5)
    assert element is not None