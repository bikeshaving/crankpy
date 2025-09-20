"""
Browser tests for h magic syntax functionality using Playwright
"""

import pytest
from playwright.sync_api import Page, expect
import time
from pathlib import Path

BASE_URL = "http://localhost:8888"

def test_h_div_basic_syntax(page: Page, serve_inline_html):
    """Test h.div[children] syntax creates proper div element"""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>H Div Basic Test</title>
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
def TestBasicDiv(ctx):
    for _ in ctx:
        yield h.div["Hello World"]

renderer.render(h(TestBasicDiv), document.body)
    </py-script>
</body>
</html>"""
    
    url = serve_inline_html("test_h_div_basic.html", html_content)
    page.goto(url)
    
    page.wait_for_selector("div", timeout=15000)
    expect(page.locator("div")).to_contain_text("Hello World")

def test_h_div_with_props(page: Page, serve_inline_html):
    """Test h.div(props)[children] syntax"""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>H Div Props Test</title>
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
def TestDivProps(ctx):
    for _ in ctx:
        yield h.div(className="test-div", id="my-div")["Content with props"]

renderer.render(h(TestDivProps), document.body)
    </py-script>
</body>
</html>"""
    
    url = serve_inline_html("test_h_div_props.html", html_content)
    page.goto(url)
    
    page.wait_for_selector(".test-div", timeout=15000)
    expect(page.locator(".test-div")).to_contain_text("Content with props")
    expect(page.locator("#my-div")).to_be_visible()

def test_h_component_call_syntax(page: Page, serve_inline_html):
    """Test h(Component, props) syntax works correctly"""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>H Component Call Test</title>
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
def Greeting(ctx):
    name = ctx.props.name if ctx.props and ctx.props.name else "World"
    for _ in ctx:
        yield h.div(className="greeting")[f"Hello, {name}!"]

@component
def TestComponentCall(ctx):
    for _ in ctx:
        yield h.div[
            h(Greeting),
            h(Greeting, name="Alice"),
            h(Greeting, name="Bob")
        ]

renderer.render(h(TestComponentCall), document.body)
    </py-script>
</body>
</html>"""
    
    url = serve_inline_html("test_h_component_call.html", html_content)
    page.goto(url)
    
    page.wait_for_selector(".greeting", timeout=15000)
    
    greetings = page.locator(".greeting")
    expect(greetings.nth(0)).to_contain_text("Hello, World!")
    expect(greetings.nth(1)).to_contain_text("Hello, Alice!")
    expect(greetings.nth(2)).to_contain_text("Hello, Bob!")

def test_h_no_dynamic_component_lookup(page: Page, serve_inline_html):
    """Test that h.Component syntax doesn't work (no dynamic lookup)"""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>H No Dynamic Lookup Test</title>
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
def TestComponent(ctx):
    for _ in ctx:
        yield h.div["I'm a real component"]

@component 
def TestNoDynamicLookup(ctx):
    for _ in ctx:
        # This should create an HTML element called "TestComponent", not look up the component
        yield h.div[
            h(TestComponent),  # This works - direct component call
            h.TestComponent["This should be an HTML tag"]  # This should create <TestComponent> tag
        ]

renderer.render(h(TestNoDynamicLookup), document.body)
    </py-script>
</body>
</html>"""
    
    url = serve_inline_html("test_h_no_dynamic_lookup.html", html_content)
    page.goto(url)
    
    page.wait_for_selector("div", timeout=15000)
    
    # The real component should work
    expect(page.locator("div").first).to_contain_text("I'm a real component")
    
    # The h.TestComponent should create a custom HTML element, not run the component
    expect(page.locator("TestComponent")).to_contain_text("This should be an HTML tag")

def test_h_fragment_with_props(page: Page, serve_inline_html):
    """Test h("", key="foo") and h(Fragment, key="foo") syntax for fragments with props"""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>H Fragment Props Test</title>
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
from crank import h, component, Fragment
from crank.dom import renderer
from js import document

@component
def TestFragmentProps(ctx):
    for _ in ctx:
        yield h.div(id="container")[
            "Empty string fragment: ",
            h("", key="empty-str"),
            "Fragment symbol: ",
            h(Fragment, key="empty-frag"),
            "Fragment with children: ",
            h("", key="with-children")["Fragment child"],
            h.span[" - Done"]
        ]

renderer.render(h(TestFragmentProps), document.body)
    </py-script>
</body>
</html>"""
    
    url = serve_inline_html("test_h_fragment_props.html", html_content)
    page.goto(url)
    
    page.wait_for_selector("#container", timeout=15000)
    
    # Fragment content should render
    expect(page.locator("#container")).to_contain_text("Empty string fragment:")
    expect(page.locator("#container")).to_contain_text("Fragment symbol:")
    expect(page.locator("#container")).to_contain_text("Fragment with children:")
    expect(page.locator("#container")).to_contain_text("Fragment child")
    expect(page.locator("span")).to_contain_text("Done")

def test_h_nested_elements(page: Page, serve_inline_html):
    """Test nested h syntax elements"""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>H Nested Test</title>
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
def TestNested(ctx):
    for _ in ctx:
        yield h.div(className="container")[
            h.h1["Title"],
            h.p["Paragraph"],
            h.ul[
                h.li["Item 1"],
                h.li["Item 2"],
                h.li["Item 3"]
            ]
        ]

renderer.render(h(TestNested), document.body)
    </py-script>
</body>
</html>"""
    
    url = serve_inline_html("test_h_nested.html", html_content)
    page.goto(url)
    
    page.wait_for_selector(".container", timeout=15000)
    
    expect(page.locator("h1")).to_contain_text("Title")
    expect(page.locator("p")).to_contain_text("Paragraph")
    expect(page.locator("li").nth(0)).to_contain_text("Item 1")
    expect(page.locator("li").nth(2)).to_contain_text("Item 3")

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
    """Use the same http_server fixture from test_browser.py"""
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