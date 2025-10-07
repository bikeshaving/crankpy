"""
Simple MicroPython test to verify basic behavior
"""
from playwright.sync_api import Page, expect


def test_micropython_basic_behavior(page: Page):
    """Test basic MicroPython behavior using local server"""

    # Navigate to our simple test page
    page.goto("http://localhost:3333/test_simple_mpy.html")

    # Wait for PyScript to load and execute
    page.wait_for_timeout(8000)

    # Check that we got output
    expect(page.locator("text=Python implementation:")).to_be_visible()

    # Get all the output for analysis
    output = page.locator("#output").inner_text()
    print(f"MicroPython test output:\n{output}")

    # Key assertions
    expect(page.locator("text=✅ Test completed")).to_be_visible()

def test_micropython_crank_basic(page: Page):
    """Test basic Crank.py functionality with MicroPython"""

    # Use our existing test file
    page.goto("http://localhost:3333/test_micropython.html")

    # Wait longer for Crank.js to load
    page.wait_for_timeout(10000)

    # Get all output for debugging
    output = page.locator("#output").inner_text()
    print(f"Crank.py MicroPython test output:\n{output}")

    # Check what succeeded/failed
    success_count = page.locator("text=✅").count()
    failure_count = page.locator("text=❌").count()

    print(f"Successes: {success_count}, Failures: {failure_count}")

    # Check that basic functionality works
    expect(page.locator("text=✅ Component creation successful")).to_be_visible()

    # Check that we have no failures
    assert failure_count == 0, f"Expected 0 failures, got {failure_count}"
