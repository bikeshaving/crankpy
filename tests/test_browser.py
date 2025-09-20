"""
Browser tests for Crank.py using Playwright

These tests load the actual PyScript examples in a browser and verify they work.
"""

import pytest
from playwright.sync_api import Page, expect
import time
import subprocess
import socket
from pathlib import Path
import tempfile
import os

# We'll create our own server
BASE_URL = "http://localhost:8888"

def test_counter_example(page: Page, http_server):
    """Test the counter example loads and works"""
    # Navigate to counter example
    page.goto(f"{BASE_URL}/examples/counter.html")
    
    # Check console for errors
    page.on("console", lambda msg: print(f"Console {msg.type}: {msg.text}"))
    
    # Wait for PyScript to load - wait for our component to render
    page.wait_for_selector(".counter-display", timeout=10000)
    
    # Wait a bit more for our component to render
    time.sleep(2)
    
    # Check that the counter rendered
    expect(page.locator("h2")).to_contain_text("Counter Example")
    
    # Check initial count
    expect(page.locator(".count-value")).to_contain_text("0")
    
    # Click increment button
    page.locator(".btn-increment").click()
    
    # Wait and check count increased
    time.sleep(0.5)
    expect(page.locator(".count-value")).to_contain_text("1")
    
    # Click decrement button
    page.locator(".btn-decrement").click()
    
    # Check count decreased
    time.sleep(0.5)
    expect(page.locator(".count-value")).to_contain_text("0")
    
    # Click reset button (should stay at 0)
    page.locator(".btn-reset").click()
    time.sleep(0.5)
    expect(page.locator(".count-value")).to_contain_text("0")

def test_greeting_example(page: Page, http_server):
    """Test the greeting example loads"""
    page.goto(f"{BASE_URL}/examples/greeting.html")
    
    # Wait for PyScript to load by waiting for content
    page.wait_for_selector("body *", timeout=10000)
    time.sleep(2)
    
    # Check that greeting rendered
    expect(page.get_by_text("Hello World!")).to_be_visible()

def test_magic_j_simple(page: Page, serve_inline_html):
    """Test the simple magic j syntax example works"""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Magic J Test</title>
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
from crank import j, component
from crank.dom import renderer
from js import document

@component
def SimpleDemo(ctx):
    for _ in ctx:
        yield j.div(className="simple-demo")[
            j.h1["Simple Magic J Demo"],
            j.p["This is created with j syntax"],
            j.ul[
                j.li["Item 1"],
                j.li["Item 2"], 
                j.li["Item 3"]
            ]
        ]

# Render using j component call 
renderer.render(j(SimpleDemo), document.body)
    </py-script>
</body>
</html>"""
    
    url = serve_inline_html("test_magic_j_simple.html", html_content)
    page.goto(url)
    
    # Check console for errors
    page.on("console", lambda msg: print(f"Console {msg.type}: {msg.text}"))
    page.on("pageerror", lambda error: print(f"Page error: {error}"))
    
    # Wait for PyScript to load by waiting for content
    try:
        page.wait_for_selector(".simple-demo", timeout=15000)
    except Exception as e:
        # Print any errors
        print(f"Page HTML: {page.content()[:2000]}")
        raise e
    time.sleep(1)
    
    # Check main components rendered
    expect(page.locator("h1")).to_contain_text("Simple Magic J Demo")
    expect(page.locator("li").nth(0)).to_contain_text("Item 1")
    expect(page.locator("li").nth(2)).to_contain_text("Item 3")

def test_magic_j_basic(page: Page, serve_inline_html):
    """Test the basic magic j syntax without component lookup"""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Basic Magic J</title>
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
from crank import j, component, h
from crank.dom import renderer
from js import document

@component
def BasicDemo(ctx):
    for _ in ctx:
        yield j.div(className="basic-demo")[
            j.h1["Basic Magic J - HTML Elements Only"],
            j.p["Paragraph 1"],
            j.p["Paragraph 2"],
            j.span["Span text"]
        ]

# Use h() to avoid component lookup  
renderer.render(h(BasicDemo, {}), document.body)
    </py-script>
</body>
</html>"""
    
    url = serve_inline_html("test_magic_j_basic.html", html_content)
    page.goto(url)
    
    # Wait for PyScript to load
    page.wait_for_selector(".basic-demo", timeout=15000)
    
    # Check main components rendered
    expect(page.locator("h1")).to_contain_text("Basic Magic J - HTML Elements Only")
    expect(page.locator("p").nth(0)).to_contain_text("Paragraph 1")
    expect(page.locator("p").nth(1)).to_contain_text("Paragraph 2")

@pytest.fixture(scope="session")
def http_server():
    """Start an HTTP server for the test session"""
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