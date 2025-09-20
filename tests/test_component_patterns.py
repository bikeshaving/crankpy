"""
Browser tests for component patterns and lifecycle using Playwright
"""

import pytest
from playwright.sync_api import Page, expect
import time
from pathlib import Path

BASE_URL = "http://localhost:8888"

def test_component_signatures(page: Page, serve_inline_html):
    """Test all three component signature variations"""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Component Signatures Test</title>
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

# 0 parameters - static component
@component
def NoParamsComponent():
    return h.div(className="no-params")["Static component"]

# 1 parameter - context only
@component
def ContextOnlyComponent(ctx):
    count = 0
    for _ in ctx:
        count += 1
        yield h.div(className="ctx-only")[f"Count: {count}"]

# 2 parameters - context and props
@component
def CtxAndPropsComponent(ctx, props):
    for props in ctx:
        name = props.name if props and hasattr(props, 'name') else "Default"
        yield h.div(className="ctx-props")[f"Hello, {name}!"]

@component
def TestSignatures(ctx):
    for _ in ctx:
        yield h.div[
            h(NoParamsComponent),
            h(ContextOnlyComponent),
            h(CtxAndPropsComponent, name="Alice")
        ]

renderer.render(h(TestSignatures), document.body)
    </py-script>
</body>
</html>"""
    
    url = serve_inline_html("test_component_signatures.html", html_content)
    page.goto(url)
    
    # Test all three component types render
    page.wait_for_selector(".no-params", timeout=15000)
    expect(page.locator(".no-params")).to_contain_text("Static component")
    expect(page.locator(".ctx-only")).to_contain_text("Count: 1")
    expect(page.locator(".ctx-props")).to_contain_text("Hello, Alice!")

def test_props_reassignment(page: Page, serve_inline_html):
    """Test props reassignment pattern (for props in ctx:)"""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Props Reassignment Test</title>
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
def ChildComponent(ctx, props):
    # Each iteration gets fresh props
    for props in ctx:
        color = props.color if props and hasattr(props, 'color') else "black"
        yield h.div(style={"color": color})[f"Color: {color}"]

@component
def ParentComponent(ctx):
    colors = ["red", "green", "blue"]
    current_index = 0
    
    def next_color():
        nonlocal current_index
        current_index = (current_index + 1) % len(colors)
        ctx.refresh()
    
    for _ in ctx:
        yield h.div[
            h(ChildComponent, color=colors[current_index]),
            h.button(onClick=next_color, id="color-button")["Next Color"]
        ]

renderer.render(h(ParentComponent), document.body)
    </py-script>
</body>
</html>"""
    
    url = serve_inline_html("test_props_reassignment.html", html_content)
    page.goto(url)
    
    # Initial color
    page.wait_for_selector("div[style]", timeout=15000)
    expect(page.locator("div[style]").first).to_have_css("color", "rgb(255, 0, 0)")  # red
    
    # Click to change color
    page.click("#color-button")
    page.wait_for_timeout(100)
    expect(page.locator("div[style]").first).to_have_css("color", "rgb(0, 128, 0)")  # green
    
    # Click again
    page.click("#color-button")
    page.wait_for_timeout(100)
    expect(page.locator("div[style]").first).to_have_css("color", "rgb(0, 0, 255)")  # blue

def test_event_handling(page: Page, serve_inline_html):
    """Test event handler patterns and proxying"""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Event Handling Test</title>
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
def EventTestComponent(ctx):
    clicks = 0
    input_value = ""
    
    def handle_click():
        nonlocal clicks
        clicks += 1
        ctx.refresh()
    
    def handle_input(event):
        nonlocal input_value
        input_value = event.target.value
        ctx.refresh()
    
    def handle_submit(event):
        event.preventDefault()
        nonlocal clicks
        clicks = 0
        ctx.refresh()
    
    for _ in ctx:
        yield h.div[
            h.p(id="click-count")[f"Clicks: {clicks}"],
            h.button(onClick=handle_click, id="click-button")["Click Me"],
            h.input(type="text", onInput=handle_input, value=input_value, id="text-input"),
            h.p(id="input-value")[f"Input: {input_value}"],
            h.form(onSubmit=handle_submit)[
                h.button(type="submit", id="reset-button")["Reset"]
            ]
        ]

renderer.render(h(EventTestComponent), document.body)
    </py-script>
</body>
</html>"""
    
    url = serve_inline_html("test_event_handling.html", html_content)
    page.goto(url)
    
    # Test click handling
    page.wait_for_selector("#click-count", timeout=15000)
    expect(page.locator("#click-count")).to_contain_text("Clicks: 0")
    
    page.click("#click-button")
    page.wait_for_timeout(100)
    expect(page.locator("#click-count")).to_contain_text("Clicks: 1")
    
    page.click("#click-button")
    page.wait_for_timeout(100)
    expect(page.locator("#click-count")).to_contain_text("Clicks: 2")
    
    # Test input handling
    page.fill("#text-input", "Hello World")
    page.wait_for_timeout(100)
    expect(page.locator("#input-value")).to_contain_text("Input: Hello World")
    
    # Test form submit (reset)
    page.click("#reset-button")
    page.wait_for_timeout(100)
    expect(page.locator("#click-count")).to_contain_text("Clicks: 0")

def test_generator_state_persistence(page: Page, serve_inline_html):
    """Test that generator state persists across renders"""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Generator State Test</title>
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
import time

@component
def StatefulComponent(ctx):
    # State defined outside the loop persists
    counter = 0
    history = []
    
    def increment():
        nonlocal counter
        counter += 1
        history.append(counter)
        ctx.refresh()
    
    # This runs once at component mount
    start_time = time.time()
    
    for _ in ctx:
        elapsed = int(time.time() - start_time)
        yield h.div[
            h.p(id="counter")[f"Counter: {counter}"],
            h.p(id="history")[f"History: {', '.join(map(str, history))}"],
            h.p(id="elapsed")[f"Component alive for: {elapsed}s"],
            h.button(onClick=increment, id="inc-button")["Increment"]
        ]

renderer.render(h(StatefulComponent), document.body)
    </py-script>
</body>
</html>"""
    
    url = serve_inline_html("test_generator_state.html", html_content)
    page.goto(url)
    
    # Initial state
    page.wait_for_selector("#counter", timeout=15000)
    expect(page.locator("#counter")).to_contain_text("Counter: 0")
    expect(page.locator("#history")).to_contain_text("History:")
    
    # Click to update
    page.click("#inc-button")
    page.wait_for_timeout(100)
    expect(page.locator("#counter")).to_contain_text("Counter: 1")
    expect(page.locator("#history")).to_contain_text("History: 1")
    
    page.click("#inc-button")
    page.wait_for_timeout(100)
    expect(page.locator("#counter")).to_contain_text("Counter: 2")
    expect(page.locator("#history")).to_contain_text("History: 1, 2")
    
    # Verify component persists (elapsed time increases)
    initial_elapsed = page.locator("#elapsed").text_content()
    page.wait_for_timeout(1100)
    page.click("#inc-button")  # Trigger re-render
    page.wait_for_timeout(100)
    new_elapsed = page.locator("#elapsed").text_content()
    assert initial_elapsed != new_elapsed

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