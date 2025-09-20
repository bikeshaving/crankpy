"""
Browser tests for context lifecycle decorator functionality
"""

import pytest
from playwright.sync_api import Page, expect
import time
from pathlib import Path

BASE_URL = "http://localhost:8888"

def test_ctx_after_decorator(page: Page, serve_inline_html):
    """Test @ctx.after decorator for post-render callbacks"""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Context After Decorator Test</title>
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
def AfterTest(ctx):
    bg_color = "white"
    
    @ctx.refresh
    def change_color():
        nonlocal bg_color
        bg_color = "lightblue" if bg_color == "white" else "white"
    
    for _ in ctx:
        # Register after callback for this render
        @ctx.after
        def update_bg(node):
            # This runs after the DOM is updated
            node.style.backgroundColor = bg_color
            # Also update a data attribute for testing
            node.setAttribute("data-bg", bg_color)
        
        yield h.div(id="after-test")[
            h.p["Background changes after render"],
            h.button(onClick=change_color, id="change-btn")["Change Background"]
        ]

renderer.render(h(AfterTest), document.body)
    </py-script>
</body>
</html>"""
    
    url = serve_inline_html("test_ctx_after.html", html_content)
    page.goto(url)
    
    # Check initial state
    page.wait_for_selector("#after-test", timeout=15000)
    div = page.locator("#after-test")
    
    # Verify after callback was applied
    expect(div).to_have_attribute("data-bg", "white")
    
    # Click to change
    page.click("#change-btn")
    page.wait_for_timeout(100)
    expect(div).to_have_attribute("data-bg", "lightblue")
    
    # Click again
    page.click("#change-btn")
    page.wait_for_timeout(100)
    expect(div).to_have_attribute("data-bg", "white")

def test_ctx_cleanup_decorator(page: Page, serve_inline_html):
    """Test @ctx.cleanup decorator for component unmount"""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Context Cleanup Decorator Test</title>
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
from js import document, window

@component
def CleanupChild(ctx):
    # Set a flag when mounted
    window.childMounted = True
    
    @ctx.cleanup
    def cleanup_handler():
        # This should run when component unmounts
        window.childCleanedup = True
    
    for _ in ctx:
        yield h.div(id="cleanup-child")["I will be cleaned up"]

@component
def CleanupParent(ctx):
    show_child = True
    
    @ctx.refresh
    def toggle_child():
        nonlocal show_child
        show_child = not show_child
        window.childCleanedup = False  # Reset flag
    
    for _ in ctx:
        yield h.div[
            h.button(onClick=toggle_child, id="toggle-btn")[
                "Toggle Child" 
            ],
            h(CleanupChild) if show_child else h.div["Child removed"],
            h.div(id="cleanup-status")[
                "Child cleaned up" if hasattr(window, 'childCleanedup') and window.childCleanedup else "Child active"
            ]
        ]

renderer.render(h(CleanupParent), document.body)
    </py-script>
</body>
</html>"""
    
    url = serve_inline_html("test_ctx_cleanup.html", html_content)
    page.goto(url)
    
    # Check initial state
    page.wait_for_selector("#cleanup-child", timeout=15000)
    expect(page.locator("#cleanup-status")).to_contain_text("Child active")
    
    # Toggle to remove child
    page.click("#toggle-btn")
    page.wait_for_timeout(100)
    
    # Verify cleanup was called
    expect(page.locator("#cleanup-child")).not_to_be_visible()
    expect(page.locator("#cleanup-status")).to_contain_text("Child cleaned up")

def test_ctx_schedule_decorator(page: Page, serve_inline_html):
    """Test @ctx.schedule decorator for pre-render callbacks"""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Context Schedule Decorator Test</title>
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
from js import document, window

@component
def ScheduleTest(ctx):
    render_count = 0
    scheduled_value = ""
    
    @ctx.refresh
    def trigger_render():
        pass  # Just triggers a re-render
    
    for _ in ctx:
        render_count += 1
        
        # Schedule runs before render completes
        @ctx.schedule
        def pre_render_callback():
            nonlocal scheduled_value
            scheduled_value = f"Scheduled for render {render_count}"
            # Store in window for testing
            window.scheduledValue = scheduled_value
        
        yield h.div[
            h.p(id="render-count")[f"Render count: {render_count}"],
            h.p(id="scheduled")[f"Scheduled: {scheduled_value}"],
            h.button(onClick=trigger_render, id="schedule-btn")["Trigger Render"]
        ]

renderer.render(h(ScheduleTest), document.body)
    </py-script>
</body>
</html>"""
    
    url = serve_inline_html("test_ctx_schedule.html", html_content)
    page.goto(url)
    
    # Check initial state
    page.wait_for_selector("#render-count", timeout=15000)
    expect(page.locator("#render-count")).to_contain_text("Render count: 1")
    expect(page.locator("#scheduled")).to_contain_text("Scheduled: Scheduled for render 1")
    
    # Trigger another render
    page.click("#schedule-btn")
    page.wait_for_timeout(100)
    
    expect(page.locator("#render-count")).to_contain_text("Render count: 2")
    expect(page.locator("#scheduled")).to_contain_text("Scheduled: Scheduled for render 2")

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