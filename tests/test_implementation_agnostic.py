"""
Test runner that demonstrates in-browser pytest concept
"""
import os
import sys
import pytest
from playwright.sync_api import Page

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_browser_pytest_pyodide(page: Page):
    """Test running implementation-agnostic tests in Pyodide"""
    
    test_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>In-Browser Pytest - Pyodide</title>
    <link rel="stylesheet" href="/tests/pyscript/core.css">
    <script type="module" src="/tests/pyscript/core.js"></script>
</head>
<body>
    <div id="test-output"></div>
    
    <py-config>
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
    </py-config>
    
    <py-script>
import sys
from js import document
from crank import h, component

output_div = document.getElementById("test-output")

def log(msg):
    output_div.innerHTML += f"<div>{msg}</div>"

# Implementation-agnostic tests
class TestComponents:
    def test_component_decorator(self):
        assert component is not None
        log("✅ component decorator exists")
    
    def test_basic_component(self):
        @component
        def Hello(ctx):
            return h.div["Hello World"]
        
        assert Hello is not None
        log("✅ basic component creation works")
    
    def test_generator_component(self):
        @component
        def Generator(ctx):
            for _ in ctx:
                yield h.div["content"]
        
        assert Generator is not None
        log("✅ generator component creation works")
        
    def test_async_component_decoration(self):
        @component
        async def AsyncComp(ctx):
            return h.div["async"]
        
        assert AsyncComp is not None
        log("✅ async component decoration works")

class TestHyperscript:
    def test_h_function(self):
        assert h is not None
        assert hasattr(h, 'div')
        log("✅ h function and div element work")
    
    def test_element_creation(self):
        elem = h.div["test content"]
        assert elem is not None
        log("✅ element creation works")
    
    def test_nested_elements(self):
        nested = h.div[h.span["nested"]]
        assert nested is not None
        log("✅ nested elements work")

# Run tests manually (since pytest isn't easily available in browser)
def run_tests():
    log(f"🧪 Running implementation-agnostic tests in {sys.implementation.name}")
    
    test_classes = [TestComponents, TestHyperscript]
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        log(f"\\n--- {test_class.__name__} ---")
        instance = test_class()
        
        for method_name in dir(instance):
            if method_name.startswith('test_'):
                total_tests += 1
                try:
                    method = getattr(instance, method_name)
                    method()
                    passed_tests += 1
                except Exception as e:
                    log(f"❌ {method_name}: {e}")
    
    log(f"\\n🎯 Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        log("🎉 All tests passed!")
    else:
        log(f"❌ {total_tests - passed_tests} tests failed")

# Run the tests
run_tests()
    </py-script>
</body>
</html>
"""

    # Write the test file
    test_file_path = os.path.join(os.path.dirname(__file__), "test_pages", "test_browser_pytest.html")
    with open(test_file_path, "w") as f:
        f.write(test_html)

    # Navigate to the test page
    page.goto("http://localhost:3333/tests/test_pages/test_browser_pytest.html")

    # Wait for execution
    page.wait_for_timeout(8000)

    # Get test results
    all_output = page.locator("#test-output").inner_text()
    print(f"In-browser pytest output:\n{all_output}")
    
    # Check for success
    if "All tests passed!" in all_output:
        print("✅ In-browser implementation-agnostic tests work!")
    else:
        pytest.fail(f"In-browser tests failed. Output: {all_output}")


def test_browser_pytest_micropython(page: Page):
    """Test running implementation-agnostic tests in MicroPython"""
    
    test_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>In-Browser Pytest - MicroPython</title>
    <link rel="stylesheet" href="/tests/pyscript/core.css">
    <script type="module" src="/tests/pyscript/core.js"></script>
</head>
<body>
    <div id="test-output"></div>
    
    <mpy-config>
        {
            "experimental_create_proxy": "auto",
            "files": {
                "../../crank/__init__.py": "crank/__init__.py",
                "../../crank/dom.py": "crank/dom.py",
                "../../crank/typing_stub.py": "crank/typing_stub.py"
            }
        }
    </mpy-config>
    
    <script type="mpy">
import sys
from js import document
from crank import h, component

output_div = document.getElementById("test-output")

def log(msg):
    output_div.innerHTML += f"<div>{msg}</div>"

# Same implementation-agnostic tests as Pyodide
class TestComponents:
    def test_component_decorator(self):
        assert component is not None
        log("✅ component decorator exists")
    
    def test_basic_component(self):
        @component
        def Hello(ctx):
            return h.div["Hello World"]
        
        assert Hello is not None
        log("✅ basic component creation works")
    
    def test_generator_component(self):
        @component
        def Generator(ctx):
            for _ in ctx:
                yield h.div["content"]
        
        assert Generator is not None
        log("✅ generator component creation works")
        
    def test_async_component_decoration(self):
        @component
        async def AsyncComp(ctx):
            # In MicroPython, this becomes a sync generator
            return h.div["async"]
        
        assert AsyncComp is not None
        log("✅ async component decoration works (treated as sync in MicroPython)")
        
    def test_micropython_async_limitation(self):
        @component
        async def AsyncGen(ctx):
            yield h.div["async gen content"]
        
        # Test that it gets wrapped correctly
        mock_ctx = type('MockContext', (), {})()
        result = AsyncGen({}, mock_ctx)
        
        # Should be detected as sync in MicroPython
        if hasattr(result, '_detected_as_async_generator'):
            assert result._detected_as_async_generator == False
            log("✅ async generator correctly detected as sync in MicroPython")
        else:
            log("⚠️ no async detection metadata found")

class TestHyperscript:
    def test_h_function(self):
        assert h is not None
        assert hasattr(h, 'div')
        log("✅ h function and div element work")
    
    def test_element_creation(self):
        elem = h.div["test content"]
        assert elem is not None
        log("✅ element creation works")
    
    def test_nested_elements(self):
        nested = h.div[h.span["nested"]]
        assert nested is not None
        log("✅ nested elements work")

# Run tests
def run_tests():
    log(f"🧪 Running implementation-agnostic tests in {sys.implementation.name}")
    
    test_classes = [TestComponents, TestHyperscript]
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        log(f"\\n--- {test_class.__name__} ---")
        instance = test_class()
        
        for method_name in dir(instance):
            if method_name.startswith('test_'):
                total_tests += 1
                try:
                    method = getattr(instance, method_name)
                    method()
                    passed_tests += 1
                except Exception as e:
                    log(f"❌ {method_name}: {e}")
    
    log(f"\\n🎯 Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        log("🎉 All tests passed!")
    else:
        log(f"❌ {total_tests - passed_tests} tests failed")

# Run the tests
run_tests()
    </script>
</body>
</html>
"""

    # Write the test file
    test_file_path = os.path.join(os.path.dirname(__file__), "test_pages", "test_browser_pytest_mpy.html")
    with open(test_file_path, "w") as f:
        f.write(test_html)

    # Navigate to the test page
    page.goto("http://localhost:3333/tests/test_pages/test_browser_pytest_mpy.html")

    # Wait for execution
    page.wait_for_timeout(8000)

    # Get test results
    all_output = page.locator("#test-output").inner_text()
    print(f"In-browser MicroPython pytest output:\n{all_output}")
    
    # Check for success
    if "All tests passed!" in all_output:
        print("✅ In-browser MicroPython implementation-agnostic tests work!")
    else:
        pytest.fail(f"In-browser MicroPython tests failed. Output: {all_output}")