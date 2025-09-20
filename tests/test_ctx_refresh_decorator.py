"""
Browser tests for @ctx.refresh decorator functionality
"""

import pytest
from playwright.sync_api import Page, expect
import time
from pathlib import Path

BASE_URL = "http://localhost:8888"

def test_ctx_refresh_decorator(page: Page, serve_inline_html):
    """Test @ctx.refresh decorator works correctly"""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Context Refresh Decorator Test</title>
    <link rel="stylesheet" href="https://pyscript.net/releases/2025.8.1/core.css">
    <script type="module" src="https://pyscript.net/releases/2025.8.1/core.js"></script>
</head>
<body>
    <py-config>
        {
            "files": {
                "../crank/__init__.py": "crank/__init__.py",
                "../crank/dom.py": "crank/dom.py"
            },
            "js_modules": {
                "main": {
                    "https://cdn.jsdelivr.net/npm/@b9g/crank@latest/crank.js": "crank_core",
                    "https://cdn.jsdelivr.net/npm/@b9g/crank@latest/dom.js": "crank_dom"
                }
            }
        }
    </py-config>
    
    <py-script>
from crank import h, component
from crank.dom import renderer
from js import document

@component
def DecoratorTest(ctx):
    count = 0
    text = ""
    
    @ctx.refresh
    def increment():
        nonlocal count
        count += 1
    
    @ctx.refresh
    def decrement():
        nonlocal count
        count -= 1
    
    @ctx.refresh
    def update_text(event):
        nonlocal text
        text = event.target.value
    
    for _ in ctx:
        yield h.div[
            h.p(id="count")[f"Count: {count}"],
            h.button(onClick=increment, id="inc")["Increment"],
            h.button(onClick=decrement, id="dec")["Decrement"],
            h.input(type="text", onInput=update_text, value=text, id="text-input"),
            h.p(id="text-display")[f"Text: {text}"]
        ]

renderer.render(h(DecoratorTest), document.body)
    </py-script>
</body>
</html>"""
    
    url = serve_inline_html("test_ctx_refresh_decorator.html", html_content)
    page.goto(url)
    
    # Test increment
    page.wait_for_selector("#count", timeout=15000)
    expect(page.locator("#count")).to_contain_text("Count: 0")
    
    page.click("#inc")
    page.wait_for_timeout(100)
    expect(page.locator("#count")).to_contain_text("Count: 1")
    
    page.click("#inc")
    page.wait_for_timeout(100)
    expect(page.locator("#count")).to_contain_text("Count: 2")
    
    # Test decrement
    page.click("#dec")
    page.wait_for_timeout(100)
    expect(page.locator("#count")).to_contain_text("Count: 1")
    
    # Test text input
    page.fill("#text-input", "Hello Decorator")
    page.wait_for_timeout(100)
    expect(page.locator("#text-display")).to_contain_text("Text: Hello Decorator")

def test_ctx_refresh_mixed_usage(page: Page, serve_inline_html):
    """Test mixing @ctx.refresh decorator with direct ctx.refresh() calls"""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Mixed Refresh Usage Test</title>
    <link rel="stylesheet" href="https://pyscript.net/releases/2025.8.1/core.css">
    <script type="module" src="https://pyscript.net/releases/2025.8.1/core.js"></script>
</head>
<body>
    <py-config>
        {
            "files": {
                "../crank/__init__.py": "crank/__init__.py",
                "../crank/dom.py": "crank/dom.py"
            },
            "js_modules": {
                "main": {
                    "https://cdn.jsdelivr.net/npm/@b9g/crank@latest/crank.js": "crank_core",
                    "https://cdn.jsdelivr.net/npm/@b9g/crank@latest/dom.js": "crank_dom"
                }
            }
        }
    </py-config>
    
    <py-script>
from crank import h, component
from crank.dom import renderer
from js import document

@component
def MixedUsageTest(ctx):
    decorator_count = 0
    direct_count = 0
    
    # Using decorator
    @ctx.refresh
    def increment_decorator():
        nonlocal decorator_count
        decorator_count += 1
    
    # Using direct call
    def increment_direct():
        nonlocal direct_count
        direct_count += 1
        ctx.refresh()  # Direct call
    
    for _ in ctx:
        yield h.div[
            h.p(id="decorator-count")[f"Decorator count: {decorator_count}"],
            h.p(id="direct-count")[f"Direct count: {direct_count}"],
            h.button(onClick=increment_decorator, id="dec-btn")["Increment (decorator)"],
            h.button(onClick=increment_direct, id="dir-btn")["Increment (direct)"]
        ]

renderer.render(h(MixedUsageTest), document.body)
    </py-script>
</body>
</html>"""
    
    url = serve_inline_html("test_mixed_refresh.html", html_content)
    page.goto(url)
    
    # Test decorator version
    page.wait_for_selector("#decorator-count", timeout=15000)
    expect(page.locator("#decorator-count")).to_contain_text("Decorator count: 0")
    
    page.click("#dec-btn")
    page.wait_for_timeout(100)
    expect(page.locator("#decorator-count")).to_contain_text("Decorator count: 1")
    
    # Test direct version
    expect(page.locator("#direct-count")).to_contain_text("Direct count: 0")
    
    page.click("#dir-btn")
    page.wait_for_timeout(100)
    expect(page.locator("#direct-count")).to_contain_text("Direct count: 1")

@pytest.fixture
def serve_inline_html(http_server):
    """Fixture to create temporary HTML files for testing"""
    created_files = []
    
    def _create_html(filename: str, content: str):
        # Create in examples directory
        filepath = Path(__file__).parent.parent / "examples" / filename
        filepath.write_text(content)
        created_files.append(filepath)
        return f"{BASE_URL}/examples/{filename}"
    
    yield _create_html
    
    # Cleanup
    for filepath in created_files:
        if filepath.exists():
            filepath.unlink()

@pytest.fixture(scope="session")
def http_server():
    """Use the same http_server fixture"""
    import socket
    import subprocess
    import time
    
    # Find an available port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        port = s.getsockname()[1]
    
    global BASE_URL
    BASE_URL = f"http://localhost:{port}"
    
    # Start server in project root
    project_root = Path(__file__).parent.parent
    server = subprocess.Popen(
        ["python3", "-m", "http.server", str(port)],
        cwd=project_root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Wait for server to start
    time.sleep(1)
    
    yield port
    
    # Cleanup
    server.terminate()
    server.wait()