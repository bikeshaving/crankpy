"""
Test what inspect functionality actually works in MicroPython
"""
from playwright.sync_api import Page, expect


def test_micropython_inspect_capabilities(page: Page):
    """Test what inspect functionality is available in MicroPython"""

    # Navigate to our inspect test page
    page.goto("http://localhost:3333/test_micropython_inspect.html")

    # Wait for PyScript to load and execute
    page.wait_for_timeout(8000)

    # Get all the output for analysis
    output = page.locator("#output").inner_text()
    print(f"MicroPython inspect test output:\n{output}")

    # Check that we got output
    expect(page.locator("text=Test completed")).to_be_visible()

    # Check specific capabilities
    if "inspect.signature exists" in output:
        print("✅ MicroPython HAS inspect.signature")
    else:
        print("❌ MicroPython does NOT have inspect.signature")

    if "co_argcount:" in output:
        print("✅ MicroPython HAS __code__.co_argcount")
    else:
        print("❌ MicroPython does NOT have __code__.co_argcount")

    if "co_varnames:" in output:
        print("✅ MicroPython HAS __code__.co_varnames")
    else:
        print("❌ MicroPython does NOT have __code__.co_varnames")
