"""
Tests for MicroPython compatibility using Playwright to verify browser behavior.
"""
import os
import sys

import pytest
from playwright.sync_api import Page, expect

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_micropython_typing_imports(page: Page):
    """Test that typing imports work correctly in MicroPython"""

    # Create a test HTML file that tests typing imports
    test_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>MicroPython Typing Test</title>
    <link rel="stylesheet" href="/tests/pyscript/core.css">
    <script type="module" src="/tests/pyscript/core.js"></script>
</head>
<body>
    <div id="test-output"></div>
    
    <mpy-config>
        {
            "files": {
                "../../crank/typing_stub.py": "crank/typing_stub.py"
            }
        }
    </mpy-config>
    
    <script type="mpy">
import sys
from js import document

output_div = document.getElementById("test-output")

def log_result(message):
    output_div.innerHTML += f"<div class='result'>{message}</div>"

try:
    # Test importing our typing stub
    from crank.typing_stub import Any, Dict, List, TypeVar, Generic, TypedDict
    log_result("✅ typing_stub imports successful")
    
    # Test basic functionality - subscripting expected to fail in MicroPython
    try:
        test_dict = Dict[str, int]  # This will fail in MicroPython
        log_result("⚠️ Dict subscript works (unexpected in MicroPython)")
    except TypeError as te:
        if "isn't subscriptable" in str(te):
            log_result("✅ Dict subscript fails as expected in MicroPython")
        else:
            log_result(f"❌ Unexpected TypeError: {te}")
    
except Exception as e:
    log_result(f"❌ typing_stub test failed: {e}")
    log_result(f"Python implementation: {sys.implementation.name}")
    
# Test that we can detect MicroPython
if sys.implementation.name == 'micropython':
    log_result("✅ Running on MicroPython")
else:
    log_result(f"❌ Expected MicroPython, got {sys.implementation.name}")
    </script>
</body>
</html>
"""

    # Write the test file to test_pages directory
    test_file_path = os.path.join(os.path.dirname(__file__), "test_pages", "test_typing_micropython.html")
    with open(test_file_path, "w") as f:
        f.write(test_html)

    # Navigate to the test page via HTTP server
    page.goto("http://localhost:3333/tests/test_pages/test_typing_micropython.html")

    # Wait for PyScript to load and execute
    page.wait_for_timeout(8000)  # Increase timeout

    # Get all output for debugging
    all_output = page.locator("#test-output").inner_text()
    print(f"MicroPython typing test output:\n{all_output}")
    
    # Check for success indicators
    if "✅ typing_stub imports successful" not in all_output:
        pytest.fail(f"typing_stub imports failed. Full output: {all_output}")
    
    if "✅ Running on MicroPython" not in all_output:
        pytest.fail(f"Not running on MicroPython. Full output: {all_output}")
        
    if "✅ Dict subscript fails as expected in MicroPython" not in all_output:
        pytest.fail(f"Dict subscript behavior not as expected. Full output: {all_output}")

    # Check that we don't have actual failure messages (❌)
    if "❌" in all_output:
        pytest.fail(f"MicroPython typing test had unexpected failures. Full output: {all_output}")


def test_micropython_crank_imports(page: Page):
    """Test that Crank.py imports work in MicroPython"""

    test_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>MicroPython Crank Import Test</title>
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
from js import document

output_div = document.getElementById("test-output")
render_target = document.getElementById("render-target")

def log_result(message):
    output_div.innerHTML += f"<div class='result'>{message}</div>"

# Test each import step by step
try:
    log_result("Testing pyscript.ffi...")
    from pyscript.ffi import create_proxy, to_js
    log_result("✅ pyscript.ffi import successful")
except Exception as e:
    log_result(f"❌ pyscript.ffi import failed: {e}")

try:
    log_result("Testing pyscript.js_modules...")
    from pyscript.js_modules import crank_core
    log_result(f"✅ js_modules import successful, type: {type(crank_core)}")
except Exception as e:
    log_result(f"❌ js_modules import failed: {e}")

try:
    log_result("Testing crank import...")
    from crank import h, component
    log_result("✅ crank import successful")
    
    log_result("Testing component creation...")
    @component
    def TestComponent(ctx):
        for _ in ctx:
            yield h.div["Hello MicroPython!"]
    
    log_result("✅ component creation successful")
    
    log_result("Testing renderer import...")
    from crank.dom import renderer
    log_result("✅ renderer import successful")
    
    # Test actual rendering - this should work now after Symbol.iterator fixes
    log_result("Testing component rendering...")
    try:
        result = renderer.render(TestComponent, render_target)
        log_result("✅ rendering successful")
    except Exception as render_e:
        log_result(f"❌ rendering failed: {render_e}")
    
except Exception as e:
    log_result(f"❌ crank usage failed: {e}")
    log_result(f"Error type: {type(e).__name__}")

log_result(f"Python implementation: {sys.implementation.name}")
log_result(f"Python version: {sys.version}")
    </script>
</body>
</html>
"""

    # Write the test file to test_pages directory
    test_file_path = os.path.join(os.path.dirname(__file__), "test_pages", "test_crank_micropython.html")
    with open(test_file_path, "w") as f:
        f.write(test_html)

    # Navigate to the test page via HTTP server
    page.goto("http://localhost:3333/tests/test_pages/test_crank_micropython.html")

    # Wait for PyScript to load and execute
    page.wait_for_timeout(10000)  # Longer timeout for full Crank.py test

    # Check for success indicators
    expect(page.locator("text=✅ pyscript.ffi import successful")).to_be_visible()
    expect(page.locator("text=✅ js_modules import successful")).to_be_visible()

    # The key test - does Crank.py actually work?
    success_locator = page.locator("text=✅ rendering successful")
    if success_locator.count() == 0:
        # Get all the test output for debugging
        all_results = page.locator(".result").all_text_contents()
        pytest.fail(f"MicroPython Crank.py test failed. All results: {all_results}")

    # Main success criteria: no failures and rendering completes without error
    # Note: DOM content rendering may not be fully functional in test environment
    expect(page.locator("text=✅ rendering successful")).to_be_visible()
    
    # Ensure no critical failures occurred
    failure_locator = page.locator("text=❌ crank usage failed")
    if failure_locator.count() > 0:
        all_results = page.locator(".result").all_text_contents() 
        pytest.fail(f"MicroPython Crank.py had critical failures: {all_results}")


def test_micropython_vs_pyodide_behavior(page: Page):
    """Comparative test to see differences between MicroPython and Pyodide"""

    # This test creates both MicroPython and Pyodide versions to compare
    test_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>MicroPython vs Pyodide Comparison</title>
    <link rel="stylesheet" href="/tests/pyscript/core.css">
    <script type="module" src="/tests/pyscript/core.js"></script>
</head>
<body>
    <h2>MicroPython Results:</h2>
    <div id="mpy-output"></div>
    
    <h2>Pyodide Results:</h2>
    <div id="py-output"></div>
    
    <mpy-config>
        {
            "files": {
                "../../crank/typing_stub.py": "crank/typing_stub.py"
            }
        }
    </mpy-config>
    
    <py-config>
        {
            "files": {
                "../../crank/typing_stub.py": "crank/typing_stub.py"
            }
        }
    </py-config>
    
    <script type="mpy">
import sys
from js import document

output_div = document.getElementById("mpy-output")
output_div.innerHTML = f"<div>Implementation: {sys.implementation.name}</div>"
output_div.innerHTML += f"<div>Version: {sys.version}</div>"

# Test type subscripting
try:
    test_generic = dict[str, int]
    output_div.innerHTML += "<div>✅ dict[str, int] works</div>"
except Exception as e:
    output_div.innerHTML += f"<div>❌ dict[str, int] failed: {e}</div>"

# Test typing imports
try:
    from typing import Dict
    output_div.innerHTML += "<div>✅ typing.Dict import works</div>"
except Exception as e:
    output_div.innerHTML += f"<div>❌ typing.Dict import failed: {e}</div>"
    </script>
    
    <script type="py">
import sys
from js import document

output_div = document.getElementById("py-output")
output_div.innerHTML = f"<div>Implementation: {sys.implementation.name}</div>"
output_div.innerHTML += f"<div>Version: {sys.version}</div>"

# Test type subscripting
try:
    test_generic = dict[str, int]
    output_div.innerHTML += "<div>✅ dict[str, int] works</div>"
except Exception as e:
    output_div.innerHTML += f"<div>❌ dict[str, int] failed: {e}</div>"

# Test typing imports
try:
    from typing import Dict
    output_div.innerHTML += "<div>✅ typing.Dict import works</div>"
except Exception as e:
    output_div.innerHTML += f"<div>❌ typing.Dict import failed: {e}</div>"
    </script>
</body>
</html>
"""

    # Write the test file to test_pages directory
    test_file_path = os.path.join(os.path.dirname(__file__), "test_pages", "test_comparison.html")
    with open(test_file_path, "w") as f:
        f.write(test_html)

    # Navigate to the test page via HTTP server
    page.goto("http://localhost:3333/tests/test_pages/test_comparison.html")

    # Wait for both PyScript engines to load
    page.wait_for_timeout(15000)

    # Check that both sections have output
    expect(page.locator("#mpy-output").locator("text=Implementation:")).to_be_visible()
    expect(page.locator("#py-output").locator("text=Implementation:")).to_be_visible()

    # Get the actual differences for analysis
    mpy_content = page.locator("#mpy-output").inner_text()
    py_content = page.locator("#py-output").inner_text()

    print(f"MicroPython results:\n{mpy_content}")
    print(f"Pyodide results:\n{py_content}")

    # This test mainly captures the differences rather than asserting success


if __name__ == "__main__":
    # Allow running individual tests
    pytest.main([__file__, "-v"])
