"""
Browser tests for FFI functionality using Playwright

Tests PyScript FFI integration in real browser environment:
- Function proxying and event handling
- Object conversion between Python and JavaScript
- Performance and memory management
- Error handling in browser context
"""

import pytest
from playwright.sync_api import Page, expect
from pathlib import Path


def test_ffi_event_handler_proxying(page: Page, serve_inline_html):
    """Test that Python event handlers work correctly through FFI"""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>FFI Event Handler Test</title>
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
from js import document, console

@component
def FFITestComponent(ctx):
    result = "No events yet"
    
    def handle_click(event):
        nonlocal result
        # Test that event object is properly passed through FFI
        result = f"Click at ({event.clientX}, {event.clientY})"
        console.log(f"Python handler received: {type(event)}")
        ctx.refresh()
    
    def handle_input(event):
        nonlocal result
        # Test string data passing through FFI
        result = f"Input value: {event.target.value}"
        ctx.refresh()
    
    def handle_keydown(event):
        nonlocal result
        # Test complex event data through FFI
        result = f"Key: {event.key}, Code: {event.code}, Ctrl: {event.ctrlKey}"
        ctx.refresh()
    
    def handle_submit(event):
        nonlocal result
        # Test event.preventDefault() through FFI
        event.preventDefault()
        result = "Form submission prevented"
        ctx.refresh()
    
    # Test multiple event types and complex handlers
    def handle_mouse_events(event):
        nonlocal result
        result = f"Mouse: {event.type} button={event.button}"
        ctx.refresh()
    
    for _ in ctx:
        yield h.div(id="ffi-test-container")[
            h.p(id="result")[result],
            h.button(
                onClick=handle_click,
                onMouseDown=handle_mouse_events,
                onMouseUp=handle_mouse_events,
                id="click-button"
            )["Click Me"],
            h.input(
                type="text",
                onInput=handle_input,
                onKeyDown=handle_keydown,
                placeholder="Type here",
                id="text-input"
            ),
            h.form(onSubmit=handle_submit)[
                h.button(type="submit", id="submit-button")["Submit"]
            ]
        ]

renderer.render(h(FFITestComponent), document.body)
    </py-script>
</body>
</html>"""
    
    url = serve_inline_html("test_ffi_events.html", html_content)
    page.goto(url)
    
    # Wait for component to load
    page.wait_for_selector("#result", timeout=15000)
    expect(page.locator("#result")).to_contain_text("No events yet")
    
    # Test click event with coordinates
    page.click("#click-button")
    page.wait_for_timeout(100)
    expect(page.locator("#result")).to_match(r"Click at \(\d+, \d+\)")
    
    # Test input event
    page.fill("#text-input", "Hello FFI")
    page.wait_for_timeout(100)
    expect(page.locator("#result")).to_contain_text("Input value: Hello FFI")
    
    # Test keydown event
    page.press("#text-input", "Control+A")
    page.wait_for_timeout(100)
    expect(page.locator("#result")).to_contain_text("Key: a, Code: KeyA, Ctrl: true")
    
    # Test form submit prevention
    page.click("#submit-button")
    page.wait_for_timeout(100)
    expect(page.locator("#result")).to_contain_text("Form submission prevented")
    
    # Test mouse events
    page.hover("#click-button")
    page.mouse.down()
    page.wait_for_timeout(100)
    expect(page.locator("#result")).to_contain_text("Mouse: mousedown button=0")


def test_ffi_complex_props_conversion(page: Page, serve_inline_html):
    """Test complex Python data structures conversion through FFI"""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>FFI Props Conversion Test</title>
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
from js import document, console, JSON

@component
def PropsConversionTest(ctx):
    test_results = []
    
    def test_simple_props():
        nonlocal test_results
        test_results.append("✓ Simple props test")
        ctx.refresh()
    
    def test_nested_handlers():
        nonlocal test_results
        test_results.append("✓ Nested handlers test")
        ctx.refresh()
    
    def test_array_handlers():
        nonlocal test_results
        test_results.append("✓ Array handlers test")
        ctx.refresh()
    
    # Test complex nested structure with handlers
    complex_props = {
        "data-complex": "true",
        "style": {
            "backgroundColor": "lightblue",
            "padding": "10px"
        },
        "events": {
            "onClick": test_nested_handlers,
            "onDoubleClick": lambda e: test_results.append("✓ Lambda handler") or ctx.refresh()
        },
        "handlers": [test_array_handlers],
        "config": {
            "nested": {
                "deep": {
                    "callback": test_simple_props
                }
            }
        }
    }
    
    for _ in ctx:
        yield h.div(id="conversion-test")[
            h.div(id="results")[
                h.p[f"Test Results: {len(test_results)}"],
                h.ul[[h.li[result] for result in test_results]]
            ],
            h.div(**complex_props, id="complex-element")["Complex Element"],
            h.button(
                onClick=complex_props["events"]["onClick"],
                id="nested-handler-btn"
            )["Test Nested Handler"],
            h.button(
                onClick=complex_props["events"]["onDoubleClick"],
                id="lambda-handler-btn"
            )["Test Lambda Handler"],
            h.button(
                onClick=complex_props["handlers"][0],
                id="array-handler-btn"
            )["Test Array Handler"],
            h.button(
                onClick=complex_props["config"]["nested"]["deep"]["callback"],
                id="deep-nested-btn"
            )["Test Deep Nested Handler"]
        ]

renderer.render(h(PropsConversionTest), document.body)
    </py-script>
</body>
</html>"""
    
    url = serve_inline_html("test_ffi_props.html", html_content)
    page.goto(url)
    
    # Wait for component to load
    page.wait_for_selector("#results", timeout=15000)
    expect(page.locator("#results p")).to_contain_text("Test Results: 0")
    
    # Test nested handler
    page.click("#nested-handler-btn")
    page.wait_for_timeout(100)
    expect(page.locator("#results p")).to_contain_text("Test Results: 1")
    expect(page.locator("#results")).to_contain_text("✓ Nested handlers test")
    
    # Test lambda handler
    page.click("#lambda-handler-btn")
    page.wait_for_timeout(100)
    expect(page.locator("#results p")).to_contain_text("Test Results: 2")
    expect(page.locator("#results")).to_contain_text("✓ Lambda handler")
    
    # Test array handler
    page.click("#array-handler-btn")
    page.wait_for_timeout(100)
    expect(page.locator("#results p")).to_contain_text("Test Results: 3")
    expect(page.locator("#results")).to_contain_text("✓ Array handlers test")
    
    # Test deep nested handler
    page.click("#deep-nested-btn")
    page.wait_for_timeout(100)
    expect(page.locator("#results p")).to_contain_text("Test Results: 4")
    expect(page.locator("#results")).to_contain_text("✓ Simple props test")
    
    # Verify complex element has correct styling
    complex_element = page.locator("#complex-element")
    expect(complex_element).to_have_css("background-color", "rgb(173, 216, 230)")  # lightblue
    expect(complex_element).to_have_css("padding", "10px")


def test_ffi_memory_management(page: Page, serve_inline_html):
    """Test FFI memory management with many proxies"""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>FFI Memory Management Test</title>
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
def MemoryTestComponent(ctx):
    handlers_created = 0
    components_rendered = 0
    
    def create_handler(index):
        # Create unique handler for each element
        def handler():
            nonlocal components_rendered
            components_rendered += 1
            ctx.refresh()
        return handler
    
    def add_more_handlers():
        nonlocal handlers_created
        handlers_created += 10
        ctx.refresh()
    
    for _ in ctx:
        # Create many handlers to test proxy creation/cleanup
        elements = []
        for i in range(handlers_created):
            handler = create_handler(i)
            elements.append(
                h.button(
                    onClick=handler,
                    key=f"btn-{i}",
                    id=f"handler-btn-{i}"
                )[f"Handler {i}"]
            )
        
        yield h.div(id="memory-test")[
            h.div(id="stats")[
                h.p[f"Handlers Created: {handlers_created}"],
                h.p[f"Components Rendered: {components_rendered}"]
            ],
            h.button(
                onClick=add_more_handlers,
                id="add-handlers"
            )["Add 10 More Handlers"],
            h.div(id="handlers-container")[elements]
        ]

renderer.render(h(MemoryTestComponent), document.body)
    </py-script>
</body>
</html>"""
    
    url = serve_inline_html("test_ffi_memory.html", html_content)
    page.goto(url)
    
    # Wait for component to load
    page.wait_for_selector("#stats", timeout=15000)
    expect(page.locator("#stats")).to_contain_text("Handlers Created: 0")
    
    # Add handlers progressively
    page.click("#add-handlers")
    page.wait_for_timeout(200)
    expect(page.locator("#stats")).to_contain_text("Handlers Created: 10")
    
    # Test that all handlers work
    page.click("#handler-btn-0")
    page.wait_for_timeout(100)
    expect(page.locator("#stats")).to_contain_text("Components Rendered: 1")
    
    page.click("#handler-btn-5")
    page.wait_for_timeout(100)
    expect(page.locator("#stats")).to_contain_text("Components Rendered: 2")
    
    # Add more handlers
    page.click("#add-handlers")
    page.wait_for_timeout(200)
    expect(page.locator("#stats")).to_contain_text("Handlers Created: 20")
    
    # Test new handlers work
    page.click("#handler-btn-15")
    page.wait_for_timeout(100)
    expect(page.locator("#stats")).to_contain_text("Components Rendered: 3")


def test_ffi_error_handling(page: Page, serve_inline_html):
    """Test FFI error handling and recovery"""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>FFI Error Handling Test</title>
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
from js import document, console

@component
def ErrorHandlingTest(ctx):
    error_count = 0
    last_error = "None"
    
    def handler_that_throws():
        nonlocal error_count, last_error
        error_count += 1
        last_error = "Handler threw exception"
        raise Exception("Test exception from Python handler")
    
    def handler_with_js_error():
        nonlocal error_count, last_error
        error_count += 1
        last_error = "Accessing undefined JS property"
        # Try to access undefined JS property
        from js import someUndefinedJSObject
        console.log(someUndefinedJSObject.nonexistentProperty)
    
    def safe_handler():
        nonlocal last_error
        last_error = "Safe handler executed successfully"
        ctx.refresh()
    
    def recovery_handler():
        nonlocal error_count, last_error
        try:
            handler_that_throws()
        except Exception as e:
            last_error = f"Caught and recovered: {str(e)}"
            ctx.refresh()
    
    for _ in ctx:
        yield h.div(id="error-test")[
            h.div(id="error-stats")[
                h.p[f"Error Count: {error_count}"],
                h.p(id="last-error")[f"Last Error: {last_error}"]
            ],
            h.button(
                onClick=handler_that_throws,
                id="throw-error-btn"
            )["Throw Python Error"],
            h.button(
                onClick=handler_with_js_error,  
                id="js-error-btn"
            )["JS Error"],
            h.button(
                onClick=safe_handler,
                id="safe-btn"
            )["Safe Handler"],
            h.button(
                onClick=recovery_handler,
                id="recovery-btn"
            )["Recovery Handler"]
        ]

renderer.render(h(ErrorHandlingTest), document.body)
    </py-script>
</body>
</html>"""
    
    url = serve_inline_html("test_ffi_errors.html", html_content)
    page.goto(url)
    
    # Wait for component to load
    page.wait_for_selector("#error-stats", timeout=15000)
    expect(page.locator("#last-error")).to_contain_text("Last Error: None")
    
    # Test safe handler works
    page.click("#safe-btn")
    page.wait_for_timeout(100)
    expect(page.locator("#last-error")).to_contain_text("Last Error: Safe handler executed successfully")
    
    # Test recovery mechanism
    page.click("#recovery-btn")
    page.wait_for_timeout(200)
    expect(page.locator("#last-error")).to_contain_text("Last Error: Caught and recovered: Test exception from Python handler")
    
    # Verify system still works after errors
    page.click("#safe-btn")
    page.wait_for_timeout(100)
    expect(page.locator("#last-error")).to_contain_text("Last Error: Safe handler executed successfully")


@pytest.fixture
def serve_inline_html(http_server):
    """Fixture to create temporary HTML files for testing"""
    created_files = []
    
    def _create_html(filename: str, content: str):
        # Create in examples directory
        filepath = Path(__file__).parent.parent / "examples" / filename
        filepath.parent.mkdir(exist_ok=True)
        filepath.write_text(content)
        created_files.append(filepath)
        return f"http://localhost:8888/examples/{filename}"
    
    yield _create_html
    
    # Cleanup
    for filepath in created_files:
        if filepath.exists():
            filepath.unlink()


@pytest.fixture(scope="session")
def http_server():
    """HTTP server fixture for browser tests"""
    import socket
    import subprocess
    import time
    
    # Find an available port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        port = s.getsockname()[1]
    
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


if __name__ == '__main__':
    pytest.main([__file__, "-v"])