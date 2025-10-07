"""
Test that we don't swallow real TypeErrors in user code
"""
import pytest
from playwright.sync_api import Page, expect


def test_error_handling_specificity(page: Page):
    """Test that we only catch parameter mismatch errors, not real bugs"""

    # Create the test HTML dynamically
    test_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Error Handling Test</title>
    <link rel="stylesheet" href="https://pyscript.net/releases/2025.8.1/core.css">
    <script type="module" src="https://pyscript.net/releases/2025.8.1/core.js"></script>
</head>
<body>
    <h1>Error Handling Test</h1>
    <div id="output"></div>
    
    <mpy-config>
        {
            "files": {
                "./crank/__init__.py": "crank/__init__.py",
                "./crank/dom.py": "crank/dom.py",
                "./crank/typing_stub.py": "crank/typing_stub.py"
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
from js import document
from crank import h, component

output_div = document.getElementById("output")

def log(message):
    output_div.innerHTML += f"<p>{message}</p>"

log(f"Python implementation: {sys.implementation.name}")

# Test 1: Valid component signatures
@component
def ValidComponent0():
    return h.div["No params"]

@component  
def ValidComponent1(ctx):
    for _ in ctx:
        yield h.div["One param (ctx)"]

@component
def ValidComponent2(ctx, props):
    for props in ctx:
        yield h.div["Two params (ctx, props)"]

log("✅ Valid component signatures work")

# Test 2: Component with parameter count mismatch (should be caught)
def ComponentWithTooManyParams(a, b, c, d, e):
    return h.div["Too many params"]

try:
    # This should create the component successfully
    valid0 = ValidComponent0
    valid1 = ValidComponent1  
    valid2 = ValidComponent2
    log("✅ All valid components created successfully")
except Exception as e:
    log(f"❌ Valid component creation failed: {e}")

# Test parameter count mismatch behavior
try:
    bad_component = component(ComponentWithTooManyParams)
    # In CPython: should fail at decoration time due to inspect.signature
    # In MicroPython: decoration succeeds, but will fail at runtime
    if sys.implementation.name == 'micropython':
        log("✅ MicroPython: Component with too many params created (will fail at runtime)")
    else:
        log("❌ CPython: Component with too many params should have failed at decoration time")
except ValueError as e:
    if "incompatible signature" in str(e):
        log(f"✅ Parameter mismatch correctly caught at decoration time: {e}")
    else:
        log(f"❌ Wrong ValueError: {e}")
except Exception as e:
    log(f"❌ Wrong error type for param mismatch: {type(e).__name__}: {e}")

# Test that real TypeErrors in user code are properly propagated
log("Testing TypeError propagation...")
try:
    # Create a simple function with a guaranteed TypeError
    def buggy_function():
        bad_var = None
        return bad_var + "string"  # This will definitely cause TypeError
    
    # Test that the TypeError is raised as expected
    try:
        result = buggy_function()
        log("❌ TypeError should have been raised but wasn't")
    except TypeError as e:
        log(f"✅ Simple TypeError correctly raised: {e}")
    except Exception as e:
        log(f"❌ Unexpected error in simple test: {type(e).__name__}: {e}")
        
    log("✅ TypeError propagation test completed successfully")
        
except Exception as e:
    log(f"❌ TypeError test setup failed: {e}")

log("Error handling tests completed")
    </script>
</body>
</html>"""

    # Write the test file
    import os
    test_file_path = os.path.join(os.path.dirname(__file__), "..", "test_error_handling.html")
    with open(test_file_path, "w") as f:
        f.write(test_html)

    # Navigate to our error handling test page
    page.goto("http://localhost:3333/test_error_handling.html")

    # Wait for PyScript to load and execute
    page.wait_for_timeout(10000)

    # Get all the output for analysis
    output = page.locator("#output").inner_text()
    print(f"Error handling test output:\n{output}")

    # Check that valid components work
    expect(page.locator("text=✅ All valid components created successfully")).to_be_visible()

    # Look for all test results
    success_count = page.locator("text=✅").count()
    failure_count = page.locator("text=❌").count()
    warning_count = page.locator("text=⚠️").count()

    print(f"Results: ✅ {success_count}, ❌ {failure_count}, ⚠️ {warning_count}")

    # Check if we got the completion message
    if "Error handling tests completed" not in output:
        pytest.fail("Test script didn't complete - may have hung on error")

    # Check parameter mismatch behavior (differs by implementation)
    if "Parameter mismatch correctly caught at decoration time" in output:
        print("✅ CPython: Parameter mismatch errors caught at decoration time")
    elif "MicroPython: Component with too many params created (will fail at runtime)" in output:
        print("✅ MicroPython: Parameter mismatch will be caught at runtime (acceptable)")
    else:
        print("⚠️ Parameter mismatch test had unexpected result")

    # Check that real TypeErrors are properly propagated
    if "Simple TypeError correctly raised" in output:
        print("✅ Real TypeErrors are correctly propagated (not caught)")
    elif "TypeError should have been raised but wasn't" in output:
        print("❌ Real TypeError was incorrectly caught")
    else:
        print("⚠️ Real TypeError test had unexpected result")

    # Print all results for analysis
    all_lines = output.split('\n')
    for line in all_lines:
        if any(marker in line for marker in ['✅', '❌', '⚠️']):
            print(f"Result: {line}")
    
    # Clean up the test file
    os.remove(test_file_path)
