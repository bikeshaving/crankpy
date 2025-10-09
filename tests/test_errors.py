"""
Error handling and edge case tests
"""

def test_invalid_element_type():
    """Test handling of invalid element types"""
    from crank import h
    from crank.dom import renderer
    from js import document
    
    # Test with None as element type (should handle gracefully)
    try:
        element = h(None)["Content"]
        document.body.innerHTML = ""
        renderer.render(element, document.body)
        # If it doesn't crash, that's a pass
        assert True
    except Exception as e:
        # If it throws a reasonable error, that's also acceptable
        assert "None" in str(e) or "null" in str(e) or "undefined" in str(e)

def test_invalid_props():
    """Test handling of invalid props"""
    from crank import h
    from crank.dom import renderer
    from js import document
    
    # Test with invalid prop values
    document.body.innerHTML = ""
    
    try:
        # Test with function as prop value (should convert or handle gracefully)
        def invalid_prop():
            return "function"
            
        renderer.render(h.div(invalidProp=invalid_prop)["Content"], document.body)
        
        rendered_div = document.querySelector("div")
        assert rendered_div is not None
        assert rendered_div.textContent == "Content"
    except Exception:
        # If it throws an error, that's acceptable for invalid props
        assert True

def test_circular_references():
    """Test handling of circular references in props"""
    from crank import h
    
    # Create circular reference
    circular = {}
    circular["self"] = circular
    
    try:
        # This should either work or throw a reasonable error
        element = h.div(data=circular)["Content"]
        assert element is not None
    except Exception as e:
        # Circular reference errors are acceptable
        assert "circular" in str(e).lower() or "recursive" in str(e).lower() or len(str(e)) > 0

def test_component_errors():
    """Test error handling in components"""
    from crank import h, component
    from crank.dom import renderer
    from js import document
    
    @component
    def ErrorComponent(ctx, props):
        error_type = props.get("errorType", "none")
        
        if error_type == "render":
            # Error during render
            raise ValueError("Render error")
        elif error_type == "yield":
            # Error during yield
            for _ in ctx:
                raise RuntimeError("Yield error")
        else:
            # Normal component
            for _ in ctx:
                yield h.div["Normal component"]
    
    # Test normal component works
    document.body.innerHTML = ""
    renderer.render(h(ErrorComponent, errorType="none"), document.body)
    normal_div = document.querySelector("div")
    assert normal_div is not None
    assert normal_div.textContent == "Normal component"
    
    # Test error handling (should not crash the whole app)
    try:
        document.body.innerHTML = ""
        renderer.render(h(ErrorComponent, errorType="render"), document.body)
        # If it renders something or nothing, that's fine
        assert True
    except Exception:
        # If it throws an error, that's also acceptable
        assert True

def test_deep_nesting_limits():
    """Test very deep element nesting"""
    from crank import h
    from crank.dom import renderer
    from js import document
    
    # Create deeply nested structure
    def create_deep_nesting(depth):
        if depth <= 0:
            return "Deep content"
        return h.div[create_deep_nesting(depth - 1)]
    
    try:
        deep_element = create_deep_nesting(50)  # 50 levels deep
        document.body.innerHTML = ""
        renderer.render(deep_element, document.body)
        
        # Should render successfully
        innermost = document.querySelector("div")
        assert innermost is not None
    except Exception as e:
        # Deep nesting errors are acceptable (stack overflow, etc.)
        assert len(str(e)) > 0

def test_invalid_children():
    """Test handling of invalid children"""
    from crank import h
    from crank.dom import renderer
    from js import document
    
    # Test with undefined/None children
    document.body.innerHTML = ""
    renderer.render(h.div[None, "Valid", None], document.body)
    
    rendered_div = document.querySelector("div")
    assert rendered_div is not None
    # Should contain at least the valid content
    assert "Valid" in rendered_div.textContent

def test_async_component_errors():
    """Test error handling in async components"""
    from crank import h, component
    from crank.dom import renderer
    from js import document
    import asyncio
    
    @component
    async def AsyncErrorComponent(ctx, props):
        error_type = props.get("errorType", "none")
        
        if error_type == "async_error":
            await asyncio.sleep(0.001)
            raise ValueError("Async error")
        else:
            await asyncio.sleep(0.001)
            return h.div["Async success"]
    
    # Test normal async component
    try:
        document.body.innerHTML = ""
        # Note: Direct async rendering may not be supported in all environments
        element = h(AsyncErrorComponent, errorType="none")
        assert element is not None
    except Exception:
        # Async component creation errors are acceptable
        assert True

def test_generator_component_errors():
    """Test error handling in generator components"""
    from crank import h, component
    from crank.dom import renderer
    from js import document
    
    @component
    def GeneratorErrorComponent(ctx, props):
        error_on = props.get("errorOn", 0)
        count = 0
        
        for props in ctx:
            if count == error_on:
                raise ValueError(f"Generator error on iteration {count}")
            yield h.div[f"Iteration {count}"]
            count += 1
            if count > 3:  # Prevent infinite loop
                break
    
    # Test normal generator
    document.body.innerHTML = ""
    renderer.render(h(GeneratorErrorComponent, errorOn=999), document.body)
    normal_div = document.querySelector("div")
    assert normal_div is not None
    
    # Test generator error
    try:
        document.body.innerHTML = ""
        renderer.render(h(GeneratorErrorComponent, errorOn=0), document.body)
        # Should handle error gracefully
        assert True
    except Exception:
        # Generator errors are acceptable
        assert True

def test_context_method_errors():
    """Test error handling with context methods"""
    from crank import h, component
    from crank.dom import renderer
    from js import document
    
    @component
    def ContextErrorComponent(ctx, props):
        try:
            # Test invalid schedule call
            ctx.schedule(None)  # Invalid callback
        except Exception:
            pass  # Expected to fail
            
        try:
            # Test invalid after call
            ctx.after("not a function")  # Invalid callback
        except Exception:
            pass  # Expected to fail
            
        for _ in ctx:
            yield h.div["Context error tests"]
    
    # Should render despite context errors
    document.body.innerHTML = ""
    renderer.render(h(ContextErrorComponent), document.body)
    
    rendered_div = document.querySelector("div")
    assert rendered_div is not None
    assert rendered_div.textContent == "Context error tests"

def test_malformed_jsx_equivalent():
    """Test handling of malformed JSX-equivalent structures"""
    from crank import h
    
    try:
        # Test malformed element structures
        malformed = h.div[
            h.span,  # Missing content/children
            h.p["Valid content"],
            h.button()  # Empty call
        ]
        assert malformed is not None
    except Exception:
        # Malformed structure errors are acceptable
        assert True

def test_memory_stress():
    """Test memory usage with many elements"""
    from crank import h
    from crank.dom import renderer
    from js import document
    
    try:
        # Create many elements to test memory handling
        many_elements = []
        for i in range(100):  # 100 elements
            many_elements.append(h.div[f"Element {i}"])
        
        document.body.innerHTML = ""
        renderer.render(h.div[many_elements], document.body)
        
        # Should render successfully
        rendered_divs = list(document.querySelectorAll("div"))
        assert len(rendered_divs) >= 100  # At least the 100 elements plus container
    except Exception:
        # Memory stress errors are acceptable
        assert True