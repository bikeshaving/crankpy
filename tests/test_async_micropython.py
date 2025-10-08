"""
Tests for async generator component support in MicroPython.
"""
import os
import sys

import pytest
from playwright.sync_api import Page, expect

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_async_generator_micropython(page: Page):
    """Test that async generator components work in MicroPython"""

    # Create a test HTML file that tests async generator components
    test_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>MicroPython Async Generator Test</title>
    <link rel="stylesheet" href="/tests/pyscript/core.css">
    <script type="module" src="/tests/pyscript/core.js"></script>
</head>
<body>
    <div id="test-output"></div>
    <div id="render-target"></div>
    
    <mpy-config>
        {
            "files": {
                "../../crank/__init__.py": "crank/__init__.py",
                "../../crank/dom.py": "crank/dom.py",
                "../../crank/typing_stub.py": "crank/typing_stub.py"
            },
            "js_modules": {
                "main": {
                    "https://esm.run/@b9g/crank@0.7.1/crank.js": "crank_core",
                    "https://esm.run/@b9g/crank@0.7.1/dom.js": "crank_dom"
                }
            }
        }
    </mpy-config>
    
    <script type="mpy">
import sys
import asyncio
from js import document

output_div = document.getElementById("test-output")
render_target = document.getElementById("render-target")

def log_result(message):
    output_div.innerHTML += f"<div class='result'>{message}</div>"

async def main():
    try:
        log_result("Testing MicroPython async generator components...")
        
        from crank import h, component
        from crank.dom import renderer
        
        # Test async generator component
        @component
        async def AsyncCounter(ctx):
            count = 0
            
            @ctx.refresh
            def increment():
                nonlocal count
                count += 1
            
            async for _ in ctx:  # This should use Symbol.asyncIterator
                yield h.div[
                    h.h1[f"Async Count: {count}"],
                    h.button(onclick=increment)["Increment"]
                ]
        
        log_result("✅ Async component creation successful")
        
        # Test MicroPython async generator behavior
        log_result("\\n--- Testing MicroPython Async Generators ---")
        
        @component
        def sync_comp(ctx):
            yield "sync"
        
        @component  
        async def async_comp(ctx):
            # Note: In MicroPython, this behaves like a sync generator
            # due to lack of async generator support (PEP 525)
            yield "async"
        
        class MockContext:
            pass
        
        mock_ctx = MockContext()
        mock_props = {}
        
        for name, comp in [("sync_comp", sync_comp), ("async_comp", async_comp)]:
            log_result(f"{name}:")
            try:
                result = comp(mock_props, mock_ctx)
                
                if hasattr(result, '_detected_as_async_generator'):
                    detected = result._detected_as_async_generator
                    log_result(f"  Detected as async: {detected}")
                    
                    # In MicroPython, both should be False due to async generator limitation
                    if detected == False:
                        log_result(f"  ✅ Correctly detected as sync (MicroPython limitation)")
                    else:
                        log_result(f"  ⚠️  Unexpected async detection")
                else:
                    log_result(f"  No detection attribute")
                    
            except Exception as e:
                log_result(f"  ❌ Error: {e}")
        
        log_result("--- Async Generator Test Complete ---\\n")
        
        # Test rendering
        try:
            log_result("Starting async rendering...")
            result = renderer.render(h(AsyncCounter), render_target)
            log_result("✅ Async rendering successful")
        except Exception as render_e:
            log_result(f"❌ Async rendering failed: {render_e}")
            log_result(f"Error type: {type(render_e).__name__}")
            import traceback
            log_result(f"Traceback: {traceback.format_exc()}")
        
    except Exception as e:
        log_result(f"❌ Async test failed: {e}")
        log_result(f"Error type: {type(e).__name__}")
        import traceback
        log_result(f"Traceback: {traceback.format_exc()}")

    log_result(f"Python implementation: {sys.implementation.name}")

# Run the async test
asyncio.create_task(main())
    </script>
</body>
</html>
"""

    # Write the test file to test_pages directory
    test_file_path = os.path.join(os.path.dirname(__file__), "test_pages", "test_async_micropython.html")
    with open(test_file_path, "w") as f:
        f.write(test_html)

    # Navigate to the test page via HTTP server
    page.goto("http://localhost:3333/tests/test_pages/test_async_micropython.html")

    # Wait for PyScript to load and execute
    page.wait_for_timeout(10000)  # Longer timeout for async operations

    # Get all output for debugging
    all_output = page.locator("#test-output").inner_text()
    print(f"MicroPython async test output:\n{all_output}")
    
    # Check if MicroPython implementation is working correctly
    if "MicroPython limitation" in all_output:
        print("✅ MicroPython async generator limitation properly handled")
    
    # Check for success indicators
    if "✅ Async component creation successful" not in all_output:
        pytest.fail(f"Async component creation failed. Full output: {all_output}")
    
    # For async components, rendering might not complete immediately
    # Check that rendering at least started
    if "Starting async rendering..." not in all_output:
        pytest.fail(f"Async rendering did not start. Full output: {all_output}")
    
    if "Python implementation: micropython" not in all_output:
        pytest.fail(f"Not running on MicroPython. Full output: {all_output}")
        
    # Check that we don't have actual failure messages (❌)
    if "❌" in all_output:
        pytest.fail(f"Test contains failure indicators. Full output: {all_output}")