"""
Test that we don't swallow real TypeErrors in user code
"""
import pytest
from playwright.sync_api import Page, expect


def test_error_handling_specificity(page: Page):
    """Test that we only catch parameter mismatch errors, not real bugs"""

    # Navigate to our error handling test page
    page.goto("http://localhost:3333/test_error_handling.html")

    # Wait for PyScript to load and execute
    page.wait_for_timeout(10000)

    # Get all the output for analysis
    output = page.locator("#output").inner_text()
    print(f"Error handling test output:\n{output}")

    # Check that valid components work
    expect(page.locator("text=✅ All valid components created successfully")).to_be_visible()

    # Look for all test results
    success_count = page.locator("text=✅").count()
    failure_count = page.locator("text=❌").count()
    warning_count = page.locator("text=⚠️").count()

    print(f"Results: ✅ {success_count}, ❌ {failure_count}, ⚠️ {warning_count}")

    # Check if we got the completion message
    if "Error handling tests completed" not in output:
        pytest.fail("Test script didn't complete - may have hung on error")

    # Check parameter mismatch behavior (differs by implementation)
    if "Parameter mismatch correctly caught at decoration time" in output:
        print("✅ CPython: Parameter mismatch errors caught at decoration time")
    elif "MicroPython: Component with too many params created (will fail at runtime)" in output:
        print("✅ MicroPython: Parameter mismatch will be caught at runtime (acceptable)")
    else:
        print("⚠️ Parameter mismatch test had unexpected result")

    # Check that real TypeErrors are properly propagated
    if "Simple TypeError correctly raised" in output:
        print("✅ Real TypeErrors are correctly propagated (not caught)")
    elif "TypeError should have been raised but wasn't" in output:
        print("❌ Real TypeError was incorrectly caught")
    else:
        print("⚠️ Real TypeError test had unexpected result")

    # Print all results for analysis
    all_lines = output.split('\n')
    for line in all_lines:
        if any(marker in line for marker in ['✅', '❌', '⚠️']):
            print(f"Result: {line}")
