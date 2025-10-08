"""
Async functionality tests - implementation agnostic
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

def test_async_component_pattern():
    """Test async component pattern"""
    from crank import h, component
    from crank.async_ import Suspense
    
    @component
    async def AsyncComponent(ctx):
        async for _ in ctx:
            yield h.div["Async content"]
    
    wrapper = h(Suspense, fallback=h.div["Loading..."], children=[
        h(AsyncComponent)
    ])
    assert wrapper is not None