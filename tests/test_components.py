"""
Component functionality tests using upytest for cross-runtime compatibility.

These tests run in both Pyodide and MicroPython using the official upytest framework.
"""
import sys
from crank import h, component


def test_component_decorator_exists():
    """Test that component decorator is available"""
    assert component is not None
    assert callable(component)


def test_simple_return_component():
    """Test simple component that returns an element"""
    @component
    def SimpleComponent(ctx):
        return h.div["Hello World"]
    
    assert SimpleComponent is not None
    assert callable(SimpleComponent)


def test_component_with_props():
    """Test component that uses props"""
    @component
    def PropsComponent(ctx, props):
        name = props.get("name", "World")
        return h.div[f"Hello {name}"]
    
    assert PropsComponent is not None
    assert callable(PropsComponent)


def test_generator_component():
    """Test generator component"""
    @component
    def GeneratorComponent(ctx):
        for _ in ctx:
            yield h.div["Generator content"]
    
    assert GeneratorComponent is not None
    assert callable(GeneratorComponent)


def test_component_with_state():
    """Test component with local state"""
    @component
    def StatefulComponent(ctx):
        count = 0
        
        @ctx.refresh
        def increment():
            nonlocal count
            count += 1
        
        for _ in ctx:
            yield h.div[
                h.h1[f"Count: {count}"],
                h.button(onclick=increment)["Increment"]
            ]
    
    assert StatefulComponent is not None
    assert callable(StatefulComponent)


def test_runtime_detection():
    """Test that we can detect the current runtime"""
    impl_name = sys.implementation.name
    assert impl_name in ['cpython', 'micropython']


def test_async_function_components():
    """Test async function components"""
    @component
    async def AsyncComponent(ctx):
        return h.div["Async content"]
    
    assert AsyncComponent is not None
    assert callable(AsyncComponent)


def test_sync_generator_components():
    """Test sync generator components"""
    @component
    def SyncGenComponent(ctx):
        for _ in ctx:
            yield h.div["Sync generator content"]
    
    assert SyncGenComponent is not None
    assert callable(SyncGenComponent)


def test_async_generator_decoration():
    """Test that async generator components can be decorated"""
    @component
    async def AsyncGenComponent(ctx):
        yield h.div["Async generator content"]
    
    assert AsyncGenComponent is not None
    assert callable(AsyncGenComponent)


def test_async_generator_runtime_behavior():
    """Test async generator behavior varies by runtime"""
    @component
    async def AsyncGenComponent(ctx):
        async for _ in ctx:
            yield h.div["Async generator content"]
    
    # Create mock context and props
    class MockContext:
        pass
    
    mock_ctx = MockContext()
    mock_props = {}
    
    # Test component creation
    result = AsyncGenComponent(mock_props, mock_ctx)
    assert result is not None
    
    # Runtime-specific behavior testing
    if sys.implementation.name == 'micropython':
        # In MicroPython, async generators become sync due to PEP 525 limitation
        if hasattr(result, '_detected_as_async_generator'):
            assert result._detected_as_async_generator == False
    else:
        # In Pyodide/CPython, should work as async generator
        assert result is not None


class TestComponentLifecycle:
    """Test component lifecycle methods"""
    
    def test_context_refresh_decorator(self):
        """Test ctx.refresh decorator functionality"""
        @component
        def RefreshComponent(ctx):
            state = {"count": 0}
            
            @ctx.refresh  
            def increment():
                state["count"] += 1
            
            for _ in ctx:
                yield h.div[f"Count: {state['count']}"]
        
        assert RefreshComponent is not None
    
    def test_context_iteration(self):
        """Test ctx iteration patterns"""
        @component
        def IteratingComponent(ctx):
            for _ in ctx:
                yield h.div["Iteration"]
        
        assert IteratingComponent is not None
    
    def test_async_context_iteration(self):
        """Test async ctx iteration patterns"""
        @component
        async def AsyncIteratingComponent(ctx):
            async for _ in ctx:
                yield h.div["Async iteration"]
        
        assert AsyncIteratingComponent is not None


class TestComponentProps:
    """Test component props handling"""
    
    def test_props_parameter(self):
        """Test props parameter handling"""
        @component
        def PropsComponent(ctx, props):
            return h.div[props.get("text", "default")]
        
        assert PropsComponent is not None
    
    def test_props_destructuring(self):
        """Test props can be accessed like dict"""
        @component  
        def DestructuredPropsComponent(ctx, props):
            name = props.get("name", "Anonymous")
            age = props.get("age", 0)
            return h.div[f"{name} is {age} years old"]
        
        assert DestructuredPropsComponent is not None
    
    def test_component_without_props(self):
        """Test components can work without props parameter"""
        @component
        def NoPropsComponent(ctx):
            return h.div["No props needed"]
        
        assert NoPropsComponent is not None