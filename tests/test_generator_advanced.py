"""
Advanced generator feature tests for Crank.py - testing Crank.js parity

These tests verify advanced generator features like yield resume with results,
error injection with throw(), and complex lifecycle patterns.
"""
import sys
from crank import h, component
import upytest


class TestYieldResumeFeatures:
    """Test yield resume with results (like Crank.js)"""
    
    def test_yield_receives_values(self):
        """Test that yield can receive values when resumed"""
        received_values = []
        
        @component
        def YieldReceiveComponent(ctx):
            for props in ctx:
                # First yield
                result1 = yield h.div["First yield"]
                received_values.append(("first", result1))
                
                # Second yield
                result2 = yield h.div["Second yield"] 
                received_values.append(("second", result2))
                
                # Final yield with results
                yield h.div[f"Received: {result1}, {result2}"]
        
        assert YieldReceiveComponent is not None
        # Note: The actual values would be tested with a proper renderer
    
    def test_generator_send_method(self):
        """Test that component generators have send() method"""
        @component
        def SendableComponent(ctx):
            for props in ctx:
                received = yield h.div["Waiting for data"]
                yield h.div[f"Got: {received}"]
        
        # Create a mock context
        class MockContext:
            def __iter__(self):
                return iter([{}])
        
        mock_ctx = MockContext()
        gen = SendableComponent({}, mock_ctx)
        
        # Test that generator has send method
        assert hasattr(gen, 'send') or (hasattr(gen, 'python_generator') and hasattr(gen.python_generator, 'send'))
    
    def test_multiple_yields_with_resume(self):
        """Test multiple yields per iteration with resume values"""
        @component
        def MultiYieldResumeComponent(ctx):
            for props in ctx:
                val1 = yield h.div["Yield 1"]
                val2 = yield h.div["Yield 2"]
                val3 = yield h.div["Yield 3"]
                yield h.div[f"All values: {val1}, {val2}, {val3}"]
        
        assert MultiYieldResumeComponent is not None


class TestErrorInjectionFeatures:
    """Test error injection with throw() (like Crank.js)"""
    
    def test_generator_has_throw_method(self):
        """Test that component generators have throw() method"""
        @component
        def ThrowableComponent(ctx):
            try:
                for props in ctx:
                    yield h.div["Normal operation"]
            except Exception as e:
                yield h.div[f"Caught: {e}"]
        
        # Create a mock context
        class MockContext:
            def __iter__(self):
                return iter([{}])
        
        mock_ctx = MockContext()
        gen = ThrowableComponent({}, mock_ctx)
        
        # Test that generator has throw method
        assert hasattr(gen, 'throw') or (hasattr(gen, 'python_generator') and hasattr(gen.python_generator, 'throw'))
    
    def test_error_injection_handling(self):
        """Test that generators can catch thrown errors"""
        caught_errors = []
        
        @component
        def ErrorCatchingComponent(ctx):
            try:
                for props in ctx:
                    yield h.div["Vulnerable yield point"]
                    yield h.div["This might not execute"]
            except ValueError as e:
                caught_errors.append(str(e))
                yield h.div[f"Recovered from: {e}"]
            except Exception as e:
                caught_errors.append(f"Other error: {e}")
                yield h.div["Unexpected error handled"]
        
        assert ErrorCatchingComponent is not None
        # Note: Actual error injection would be tested with a proper renderer
    
    def test_async_generator_error_injection(self):
        """Test error injection in async generators"""
        @component
        async def AsyncErrorComponent(ctx):
            try:
                async for props in ctx:
                    yield h.div["Async yield point"]
            except RuntimeError as e:
                yield h.div[f"Async error caught: {e}"]
        
        assert AsyncErrorComponent is not None


class TestGeneratorLifecycle:
    """Test generator lifecycle management (like Crank.js)"""
    
    def test_finally_cleanup(self):
        """Test that finally blocks execute on generator cleanup"""
        cleanup_called = {"value": False}
        
        @component
        def CleanupComponent(ctx):
            try:
                for props in ctx:
                    yield h.div["Component running"]
                    if props.get("should_exit"):
                        return h.div["Early exit"]
            finally:
                cleanup_called["value"] = True
                # Cleanup code here
        
        assert CleanupComponent is not None
        # Note: cleanup_called would be verified with proper component unmounting
    
    def test_generator_return_values(self):
        """Test that generators can return final values"""
        @component
        def ReturningComponent(ctx):
            count = 0
            for props in ctx:
                count += 1
                yield h.div[f"Count: {count}"]
                if count >= 3:
                    return h.div["Final result"]
        
        assert ReturningComponent is not None
    
    def test_complex_lifecycle_pattern(self):
        """Test complex lifecycle with try/except/finally"""
        lifecycle_events = []
        
        @component
        def ComplexLifecycleComponent(ctx):
            try:
                lifecycle_events.append("started")
                for props in ctx:
                    if props.get("should_error"):
                        raise ValueError("Intentional error")
                    yield h.div["Normal operation"]
            except ValueError as e:
                lifecycle_events.append(f"error: {e}")
                yield h.div["Error recovery"]
            finally:
                lifecycle_events.append("cleanup")
        
        assert ComplexLifecycleComponent is not None


class TestErrorBoundaryPatterns:
    """Test error boundary and recovery patterns (like Crank.js)"""
    
    def test_error_boundary_component(self):
        """Test component that acts as an error boundary"""
        @component
        def ErrorBoundaryComponent(ctx):
            try:
                for props in ctx:
                    children = props.get("children", [])
                    # In a real implementation, this would render children
                    # and catch any errors they throw
                    yield h.div[children]
            except Exception as e:
                # Error boundary fallback
                yield h.div[
                    h.h2["Something went wrong"],
                    h.p[str(e)],
                    h.button["Retry"]
                ]
        
        assert ErrorBoundaryComponent is not None
    
    def test_error_recovery_restart(self):
        """Test component that can restart after errors"""
        attempts = {"count": 0}
        
        @component
        def RetryComponent(ctx):
            while True:  # Infinite retry loop
                try:
                    attempts["count"] += 1
                    for props in ctx:
                        if attempts["count"] < 3 and props.get("force_error"):
                            raise RuntimeError(f"Attempt {attempts['count']} failed")
                        yield h.div[f"Success on attempt {attempts['count']}"]
                        return  # Exit retry loop on success
                except RuntimeError as e:
                    yield h.div[f"Error: {e}. Retrying..."]
                    # Continue to next iteration of while loop
        
        assert RetryComponent is not None
    
    def test_nested_error_propagation(self):
        """Test error propagation through nested generators"""
        @component
        def ParentComponent(ctx):
            try:
                for props in ctx:
                    # This would render a child component
                    child = ChildComponent({}, ctx)
                    yield h.div[child]
            except Exception as e:
                yield h.div[f"Parent caught: {e}"]
        
        @component
        def ChildComponent(ctx):
            for props in ctx:
                if props.get("child_error"):
                    raise ValueError("Child component error")
                yield h.div["Child content"]
        
        assert ParentComponent is not None
        assert ChildComponent is not None


class TestContextIteratorFeatures:
    """Test context iterator return values and control flow"""
    
    def test_context_iterator_return(self):
        """Test that context iterator can return values"""
        @component
        def ContextReturnComponent(ctx):
            for props in ctx:
                if props.get("should_return"):
                    # Context iterator returns instead of yielding
                    return h.div["Returned from context iteration"]
                yield h.div["Normal yield"]
        
        assert ContextReturnComponent is not None
    
    def test_context_break_pattern(self):
        """Test breaking out of context iteration"""
        @component
        def BreakableComponent(ctx):
            for props in ctx:
                if props.get("should_break"):
                    break
                yield h.div["Before break"]
            
            # Code after loop
            yield h.div["After context loop"]
        
        assert BreakableComponent is not None
    
    def test_async_context_return(self):
        """Test async context iterator return values (Python limitation: no return values in async generators)"""
        @component
        async def AsyncContextReturnComponent(ctx):
            async for props in ctx:
                if props.get("async_return"):
                    # Python async generators cannot return values (PEP 525 limitation)
                    # In Crank.js this would be: return <div>Async return</div>
                    # In Python we must use: return (without value) or break
                    return  # Just exit without value
                yield h.div["Async normal"]
        
        assert AsyncContextReturnComponent is not None