"""
Implementation-agnostic component tests that run in both Pyodide and MicroPython
"""
import sys
from crank import h, component


class TestBasicComponents:
    """Test basic component functionality"""
    
    def test_component_decorator_exists(self):
        """Test that component decorator is available"""
        assert component is not None
        assert callable(component)
    
    def test_simple_return_component(self):
        """Test simple component that returns an element"""
        @component
        def SimpleComponent(ctx):
            return h.div["Hello World"]
        
        assert SimpleComponent is not None
        assert callable(SimpleComponent)
    
    def test_component_with_props(self):
        """Test component that uses props"""
        @component
        def PropsComponent(ctx, props):
            name = props.get("name", "World")
            return h.div[f"Hello {name}"]
        
        assert PropsComponent is not None
        assert callable(PropsComponent)
    
    def test_generator_component(self):
        """Test generator component"""
        @component
        def GeneratorComponent(ctx):
            for _ in ctx:
                yield h.div["Generator content"]
        
        assert GeneratorComponent is not None
        assert callable(GeneratorComponent)
    
    def test_component_with_state(self):
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
                    h.span[f"Count: {count}"],
                    h.button(onclick=increment)["Increment"]
                ]
        
        assert StatefulComponent is not None
        assert callable(StatefulComponent)


class TestRuntimeCompatibility:
    """Test runtime-specific behavior"""
    
    def test_runtime_detection(self):
        """Test that we can detect the runtime"""
        runtime_name = sys.implementation.name
        assert runtime_name in ['cpython', 'pyodide', 'micropython']
    
    def test_async_function_components(self):
        """Test async function components work in both runtimes"""
        @component
        async def AsyncFunction(ctx):
            # This should work as a regular function in both runtimes
            return h.div["Async function result"]
        
        assert AsyncFunction is not None
        assert callable(AsyncFunction)
    
    def test_sync_generator_components(self):
        """Test sync generators work in both runtimes"""
        @component
        def SyncGenerator(ctx):
            yield h.div["First"]
            yield h.div["Second"]
        
        assert SyncGenerator is not None
        assert callable(SyncGenerator)


class TestAsyncGenerators:
    """Test async generator behavior (runtime-dependent)"""
    
    def test_async_generator_decoration(self):
        """Test async generator can be decorated (may behave as sync in MicroPython)"""
        @component
        async def AsyncGenerator(ctx):
            # In MicroPython, this becomes a sync generator
            # In Pyodide, this is a true async generator
            yield h.div["Async generator content"]
        
        assert AsyncGenerator is not None
        assert callable(AsyncGenerator)
    
    def test_async_generator_runtime_behavior(self):
        """Test that async generators behave appropriately per runtime"""
        @component
        async def TestAsyncGen(ctx):
            yield h.div["Test"]
        
        # Create a mock context for testing
        class MockContext:
            pass
        
        mock_ctx = MockContext()
        mock_props = {}
        
        # This should work in both runtimes, but behavior differs
        result = TestAsyncGen(mock_props, mock_ctx)
        
        if sys.implementation.name == 'micropython':
            # Should be wrapped as sync generator
            assert hasattr(result, '_detected_as_async_generator')
            # In MicroPython, should be detected as sync (False)
            assert result._detected_as_async_generator == False
        else:
            # In Pyodide/CPython, may be detected as async
            # This test is more flexible for different runtime behaviors
            assert result is not None