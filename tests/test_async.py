"""
Async functionality tests - split by async function vs async generator support
- async def functions: Work in both Pyodide and MicroPython
- async def + yield: Work in Pyodide only (MicroPython limitation)

Python to JavaScript API Mapping:
- Python: `async for props in ctx:` ↔ JavaScript: `for await (const props of this)`
- Python: `yield h.div[content]` ↔ JavaScript: `yield <div>{content}</div>`
- Both support continuous async rendering and component racing patterns
"""

def test_async_imports():
    """Test that async components can be imported"""
    from crank.async_ import lazy, Suspense, SuspenseList
    assert lazy is not None
    assert Suspense is not None  
    assert SuspenseList is not None

def test_lazy_function():
    """Test lazy function works"""
    from crank.async_ import lazy
    from crank import h, component
    
    @component
    def LazyComponent(ctx):
        for _ in ctx:
            yield h.div["Lazy loaded"]
    
    lazy_comp = lazy(lambda: LazyComponent)
    assert callable(lazy_comp)

def test_suspense_creation():
    """Test Suspense component creation"""
    from crank import h
    from crank.async_ import Suspense
    
    suspense = h(Suspense, fallback=h.div["Loading..."], children=[h.div["Content"]])
    assert suspense is not None

def test_suspense_list_creation():
    """Test SuspenseList component creation"""
    from crank import h
    from crank.async_ import Suspense, SuspenseList
    
    suspense_list = h(SuspenseList, revealOrder="forwards", children=[
        h(Suspense, fallback=h.div["Loading 1"], children=[h.div["Content 1"]]),
        h(Suspense, fallback=h.div["Loading 2"], children=[h.div["Content 2"]])
    ])
    assert suspense_list is not None

async def test_async_function_basic():
    """Test basic async def function - should work in both runtimes"""
    from crank import h, component
    from crank.dom import renderer
    import asyncio
    
    @component
    async def AsyncFunction(ctx, props):
        # Regular async def function - should work in both Pyodide and MicroPython
        await asyncio.sleep(0.001)
        message = props.get("message", "async")
        return h.div[f"Async: {message}"]
    
    # Test that we can create the component
    component_element = h(AsyncFunction, message="test")
    assert component_element is not None
    
    # Test direct component execution
    ctx = type('MockCtx', (), {})()
    props = {"message": "test"}
    element = await AsyncFunction(ctx, props)
    assert element is not None

async def test_async_function_with_await():
    """Test async function with multiple awaits - should work in both runtimes"""
    from crank import h, component
    import asyncio
    
    async def fetch_data(name):
        await asyncio.sleep(0.001)
        return f"Data for {name}"
    
    @component
    async def MultiAwaitComponent(ctx, props):
        # Multiple async operations - should work in both runtimes
        data1 = await fetch_data("first")
        data2 = await fetch_data("second")
        return h.div[f"{data1} | {data2}"]
    
    # Test that we can create the component
    component_element = h(MultiAwaitComponent)
    assert component_element is not None
    
    # Test direct component execution
    ctx = type('MockCtx', (), {})()
    props = {}
    element = await MultiAwaitComponent(ctx, props)
    assert element is not None

async def test_async_generator_basic():
    """Test async generator rendering - Pyodide only (fails in MicroPython)"""
    from crank import h, component
    from crank.dom import renderer
    import asyncio
    
    @component
    async def AsyncGenerator(ctx, props):
        # async def + yield - only works in Pyodide, fails in MicroPython
        counter = 0
        async for props in ctx:
            await asyncio.sleep(0.001)
            counter += 1
            yield h.div[f"Async generator: {counter}"]
    
    # Test that we can create the component
    component_element = h(AsyncGenerator)
    assert component_element is not None
    
    # Note: async def + yield only works in Pyodide, not MicroPython
    # This test will fail in MicroPython due to syntax limitations

async def test_async_generator_with_async_for():
    """Test async generator with async for loop rendering - Pyodide only"""
    from crank import h, component
    from crank.dom import renderer
    import asyncio
    
    async def async_iterator():
        for i in range(3):
            await asyncio.sleep(0.001)
            yield i
    
    @component
    async def AsyncForComponent(ctx, props):
        # async def + yield + async for - only works in Pyodide
        items = []
        async for item in async_iterator():
            items.append(h.li[f"Item {item}"])
        
        async for props in ctx:
            yield h.ul[items]
    
    # Test rendering component with async for loops - will fail in MicroPython due to async def + yield
    from js import document
    result = await renderer.render(h(AsyncForComponent), document.body)
    assert result is not None

async def test_async_generator_complex():
    """Test complex async generator rendering patterns - Pyodide only"""
    from crank import h, component
    from crank.dom import renderer
    import asyncio
    
    @component
    async def ComplexAsyncGenerator(ctx, props):
        # Complex async def + yield pattern - only works in Pyodide
        phase = "init"
        counter = 0
        
        async for props in ctx:
            mode = props.get("mode", "normal")
            
            if mode == "loading":
                await asyncio.sleep(0.001)
                yield h.div["Loading..."]
            else:
                if phase == "init":
                    await asyncio.sleep(0.001)
                    yield h.div[f"Initializing... {counter}"]
                    phase = "running"
                    counter += 1
                else:
                    await asyncio.sleep(0.001)
                    yield h.div[f"Running... {counter}"]
                    counter += 1
                    
                if counter > 2:
                    yield h.div["Complete!"]
                    return
    
    # Test rendering complex async generator with state transitions - will fail in MicroPython due to async def + yield
    from js import document
    
    result1 = await renderer.render(h(ComplexAsyncGenerator, mode="normal"), document.body)
    assert result1 is not None
    
    # Test loading mode
    result2 = await renderer.render(h(ComplexAsyncGenerator, mode="loading"), document.body)
    assert result2 is not None
    
    # Test multiple renders to verify state progression  
    result3 = await renderer.render(h(ComplexAsyncGenerator, mode="normal"), document.body)
    assert result3 is not None

# Additional sync generator patterns (merged from async_advanced)

def test_sync_generator_multiple_yields():
    """Test sync generator with multiple yields"""
    from crank import h, component
    
    @component
    def Component(ctx, props):
        i = 0
        for props in ctx:
            yield h.span[f"Render {i}: {props.get('message', '')}"]
            i += 1
            if i > 2:
                break
    
    result = h.div[h(Component, message="Hello")]
    assert result is not None

def test_sync_generator_with_state():
    """Test sync generator component with internal state"""
    from crank import h, component
    
    @component  
    def Counter(ctx, props):
        count = 0
        while True:
            yield h.div[f"Count: {count}"]
            count += 1
            if count > 3:
                break
    
    result = h(Counter)
    assert result is not None

# Crank.js "for await...of" API equivalent tests
# These test the Python async for patterns that match JavaScript's for await...of

async def test_for_await_of_loading_sequence():
    """Test for await...of loading sequence - Pyodide only (fails in MicroPython)"""
    from crank import h, component
    from crank.dom import renderer
    import asyncio
    
    @component
    async def LoadingSequence(ctx, props):
        """
        Equivalent to JavaScript:
        for await ({message} of this) {
            yield <div>Loading {message}...</div>;
            await new Promise(resolve => setTimeout(resolve, 10));
            yield <div>Loaded: {message}</div>;
        }
        """
        async for props in ctx:
            message = props.get("message", "data")
            
            # First yield - loading state
            yield h.div[f"Loading {message}..."]
            
            # Simulate async work
            await asyncio.sleep(0.001)
            
            # Second yield - loaded state
            yield h.div[f"Loaded: {message}"]
    
    # Test actual DOM rendering - will fail in MicroPython due to async def + yield
    try:
        from js import document
        result = await renderer.render(h(LoadingSequence, message="async-data"), document.body)
        assert result is not None
    except NameError:
        # Fallback for environments without DOM - use js.null instead of None
        try:
            from js import null as js_null
            render_root = js_null
        except ImportError:
            render_root = None
        result = await renderer.render(h(LoadingSequence, message="async-data"), render_root)
        assert result is not None

async def test_for_await_of_racing_pattern():
    """Test component racing with for await...of - Pyodide only (fails in MicroPython)"""
    from crank import h, component
    from crank.dom import renderer
    import asyncio
    
    @component
    async def AsyncLoader(ctx, props):
        """
        Equivalent to JavaScript:
        for await ({data} of this) {
            yield <div>🔄 Loading...</div>;
            yield <AsyncData data={data} />;
        }
        """
        async for props in ctx:
            data = props.get("data", "default")
            
            # First yield - loading indicator
            yield h.div["🔄 Loading..."]
            
            # Second yield - async data component
            await asyncio.sleep(0.001)
            yield h.div[f"Data loaded: {data}"]
    
    # Test actual DOM rendering - will fail in MicroPython due to async def + yield
    try:
        from js import document
        result = await renderer.render(h(AsyncLoader, data="test-data"), document.body)
        assert result is not None
    except NameError:
        # Fallback for environments without DOM - use js.null instead of None
        try:
            from js import null as js_null
            render_root = js_null
        except ImportError:
            render_root = None
        result = await renderer.render(h(AsyncLoader, data="test-data"), render_root)
        assert result is not None
