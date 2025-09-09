"""
Browser tests for Crank.py using Playwright

These tests load the actual PyScript examples in a browser and verify they work.
"""

import pytest
from playwright.sync_api import Page, expect
import time

# Assuming we're serving from localhost:3333
BASE_URL = "http://localhost:3333"

def test_counter_example(page: Page):
    """Test the counter example loads and works"""
    # Navigate to counter example
    page.goto(f"{BASE_URL}/examples/counter.html")
    
    # Check console for errors
    page.on("console", lambda msg: print(f"Console {msg.type}: {msg.text}"))
    
    # Wait for PyScript to load - wait for our component to render
    page.wait_for_selector(".counter-container", timeout=10000)
    
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

def test_greeting_example(page: Page):
    """Test the greeting example loads"""
    page.goto(f"{BASE_URL}/examples/greeting.html")
    
    # Wait for PyScript to load by waiting for content
    page.wait_for_selector("body *", timeout=10000)
    time.sleep(2)
    
    # Check that greeting rendered
    expect(page.get_by_text("Hello World!")).to_be_visible()

@pytest.mark.skip(reason="Need server running")  
def test_examples_require_server():
    """
    Note: These tests require a local server to be running.
    
    To run these tests:
    1. Start a server: python -m http.server 3333
    2. Remove the @pytest.mark.skip decorator
    3. Run: pytest tests/test_browser.py
    """
    pass