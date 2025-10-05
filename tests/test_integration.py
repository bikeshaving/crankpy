"""
Full integration tests for Crank.py using Playwright

These tests run actual components in a real browser environment
without mocking, testing the complete PyScript + Crank.js + Crank.py stack.
Tests are organized by Python runtime implementation (Pyodide vs MicroPython).
"""


import pytest
from playwright.sync_api import Page, expect


class TestPyodideRuntime:
    """Test Pyodide runtime (default PyScript runtime)"""

    def test_pyodide_hello_world_renders(self, page: Page):
        """Test that a basic Hello World component renders with Pyodide"""
        page.goto("http://localhost:3333/tests/test_pages/hello_world.html")

        # Wait for PyScript to load and component to render
        page.wait_for_selector("[data-testid='greeting']", timeout=10000)

        greeting = page.locator("[data-testid='greeting']")
        expect(greeting).to_contain_text("Hello, Crank.py! ⚙️")

    def test_pyodide_nested_elements_render(self, page: Page):
        """Test that nested element structures render correctly with Pyodide"""
        page.goto("http://localhost:3333/tests/test_pages/nested_elements.html")

        page.wait_for_selector("[data-testid='list']", timeout=10000)

        list_element = page.locator("[data-testid='list']")
        expect(list_element).to_be_visible()

        # Check list items
        items = page.locator("[data-testid='list'] li")
        expect(items).to_have_count(3)
        expect(items.nth(0)).to_contain_text("Item 1")
        expect(items.nth(1)).to_contain_text("Item 2")
        expect(items.nth(2)).to_contain_text("nested")

    def test_pyodide_counter_increments(self, page: Page):
        """Test that counter component increments correctly with Pyodide"""
        page.goto("http://localhost:3333/tests/test_pages/counter.html")

        page.wait_for_selector("[data-testid='counter']", timeout=10000)

        # Check initial state
        count_display = page.locator("[data-testid='count']")
        expect(count_display).to_contain_text("Count: 0")

        # Click increment button
        increment_btn = page.locator("[data-testid='increment']")
        increment_btn.click()

        # Check count updated
        expect(count_display).to_contain_text("Count: 1")

        # Click multiple times
        increment_btn.click()
        increment_btn.click()
        expect(count_display).to_contain_text("Count: 3")

    def test_pyodide_counter_decrements(self, page: Page):
        """Test that counter component decrements correctly with Pyodide"""
        page.goto("http://localhost:3333/tests/test_pages/counter.html")

        page.wait_for_selector("[data-testid='counter']", timeout=10000)

        count_display = page.locator("[data-testid='count']")
        increment_btn = page.locator("[data-testid='increment']")
        decrement_btn = page.locator("[data-testid='decrement']")

        # Increment first
        increment_btn.click()
        increment_btn.click()
        expect(count_display).to_contain_text("Count: 2")

        # Then decrement
        decrement_btn.click()
        expect(count_display).to_contain_text("Count: 1")


class TestMicroPythonRuntime:
    """Test MicroPython runtime compatibility"""

    def test_micropython_hello_world_renders(self, page: Page):
        """Test that a basic Hello World component renders in MicroPython"""
        page.goto("http://localhost:3333/tests/test_pages/hello_world_micropython.html")

        # Wait for PyScript to load and component to render
        page.wait_for_selector("[data-testid='greeting']", timeout=10000)

        greeting = page.locator("[data-testid='greeting']")
        expect(greeting).to_contain_text("Hello, Crank.py MicroPython! ⚙️")

    def test_micropython_nested_elements_render(self, page: Page):
        """Test that nested element structures render correctly in MicroPython"""
        page.goto("http://localhost:3333/tests/test_pages/nested_elements_micropython.html")

        page.wait_for_selector("[data-testid='parent']", timeout=10000)

        parent_element = page.locator("[data-testid='parent']")
        expect(parent_element).to_be_visible()

        # Check child elements
        child1 = page.locator("[data-testid='child1']")
        child2 = page.locator("[data-testid='child2']")
        grandchild = page.locator("[data-testid='grandchild']")

        expect(child1).to_contain_text("First child")
        expect(child2).to_be_visible()
        expect(grandchild).to_contain_text("Nested span")

    def test_micropython_counter_increments(self, page: Page):
        """Test that counter component increments correctly in MicroPython"""
        page.goto("http://localhost:3333/tests/test_pages/counter_micropython.html")

        page.wait_for_selector("[data-testid='counter']", timeout=10000)

        # Check initial state
        count_display = page.locator("[data-testid='count']")
        expect(count_display).to_contain_text("Count: 0")

        # Click increment button
        increment_btn = page.locator("[data-testid='increment']")
        increment_btn.click()

        # Check count updated
        expect(count_display).to_contain_text("Count: 1")

        # Click multiple times
        increment_btn.click()
        increment_btn.click()
        expect(count_display).to_contain_text("Count: 3")


class TestCrossRuntimeCompatibility:
    """Test cross-runtime features and compatibility"""

    def test_pyodide_props_render_correctly(self, page: Page):
        """Test that component props render correctly"""
        page.goto("http://localhost:3333/tests/test_pages/props_test.html")

        page.wait_for_selector("[data-testid='user-profile']", timeout=10000)

        profile = page.locator("[data-testid='user-profile']")
        expect(profile).to_be_visible()

        # Check user data is rendered
        expect(profile.locator("h2")).to_contain_text("Test User")
        expect(profile.locator("p")).to_contain_text("Test bio")
        expect(profile.locator("img")).to_have_attribute("src", "avatar.jpg")

    def test_pyodide_todo_app_functionality(self, page: Page):
        """Test todo app add, toggle, and display functionality"""
        page.goto("http://localhost:3333/tests/test_pages/todo_app.html")

        page.wait_for_selector("[data-testid='todo-app']", timeout=10000)

        # Test adding todos
        todo_input = page.locator("[data-testid='todo-input']")
        add_button = page.locator("[data-testid='add-todo']")

        todo_input.fill("Buy groceries")
        add_button.click()

        # Check todo appears
        todo_list = page.locator("[data-testid='todo-list']")
        expect(todo_list.locator("li")).to_have_count(1)
        expect(todo_list).to_contain_text("Buy groceries")

        # Add another todo
        todo_input.fill("Walk the dog")
        add_button.click()

        expect(todo_list.locator("li")).to_have_count(2)
        expect(todo_list).to_contain_text("Walk the dog")

        # Test checking off todo
        first_checkbox = todo_list.locator("input[type='checkbox']").first
        first_checkbox.check()

        # Check that todo is marked as done (implementation dependent)
        expect(first_checkbox).to_be_checked()


class TestComponentLifecycle:
    """Test component lifecycle and context methods"""

    def test_pyodide_timer_component_updates(self, page: Page):
        """Test that timer component updates over time"""
        page.goto("http://localhost:3333/tests/test_pages/timer.html")

        page.wait_for_selector("[data-testid='timer']", timeout=10000)

        timer_display = page.locator("[data-testid='timer']")

        # Check initial state
        expect(timer_display).to_contain_text("Time: 0.")

        # Wait a bit and check it updates
        page.wait_for_timeout(1500)  # Wait 1.5 seconds
        expect(timer_display).to_contain_text("Time: 1.")

        # Wait more and check again
        page.wait_for_timeout(1000)  # Wait 1 more second
        expect(timer_display).to_contain_text("Time: 2.")

    def test_pyodide_cleanup_and_remount(self, page: Page):
        """Test component cleanup and remounting"""
        page.goto("http://localhost:3333/tests/test_pages/lifecycle.html")

        page.wait_for_selector("[data-testid='lifecycle-test']", timeout=10000)

        # Component should be mounted initially
        component = page.locator("[data-testid='mounted-component']")
        expect(component).to_be_visible()
        expect(component).to_contain_text("Component is mounted")

        # Click unmount button
        unmount_btn = page.locator("[data-testid='unmount']")
        unmount_btn.click()

        # Component should be gone
        expect(component).not_to_be_visible()

        # Click mount button
        mount_btn = page.locator("[data-testid='mount']")
        mount_btn.click()

        # Component should be back
        expect(component).to_be_visible()
        expect(component).to_contain_text("Component is mounted")


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_pyodide_component_with_error_handles_gracefully(self, page: Page):
        """Test that components with errors don't crash the page"""
        page.goto("http://localhost:3333/tests/test_pages/error_handling.html")

        page.wait_for_selector("[data-testid='error-test']", timeout=10000)

        # Page should still load and show error boundary
        error_boundary = page.locator("[data-testid='error-boundary']")
        expect(error_boundary).to_be_visible()
        expect(error_boundary).to_contain_text("Something went wrong")

        # Other components should still work
        working_component = page.locator("[data-testid='working-component']")
        expect(working_component).to_be_visible()
        expect(working_component).to_contain_text("This component works fine")

    def test_pyodide_invalid_props_handled(self, page: Page):
        """Test that invalid props are handled gracefully"""
        page.goto("http://localhost:3333/tests/test_pages/invalid_props.html")

        page.wait_for_selector("[data-testid='props-test']", timeout=10000)

        # Component should render with default values for invalid props
        component = page.locator("[data-testid='props-test']")
        expect(component).to_be_visible()
        expect(component).to_contain_text("Default content")


class TestFFIIntegration:
    """Test FFI (Foreign Function Interface) integration"""

    def test_pyodide_python_to_js_event_handlers(self, page: Page):
        """Test that Python event handlers work correctly"""
        page.goto("http://localhost:3333/tests/test_pages/event_handlers.html")

        page.wait_for_selector("[data-testid='event-test']", timeout=10000)

        # Test click handler
        click_button = page.locator("[data-testid='click-button']")
        result_display = page.locator("[data-testid='click-result']")

        expect(result_display).to_contain_text("Clicks: 0")

        click_button.click()
        expect(result_display).to_contain_text("Clicks: 1")

        click_button.click()
        click_button.click()
        expect(result_display).to_contain_text("Clicks: 3")

    def test_pyodide_python_to_js_data_conversion(self, page: Page):
        """Test that Python data structures convert to JS correctly"""
        page.goto("http://localhost:3333/tests/test_pages/data_conversion.html")

        page.wait_for_selector("[data-testid='data-test']", timeout=10000)

        # Test that Python data is correctly displayed
        data_display = page.locator("[data-testid='data-display']")
        expect(data_display).to_contain_text("Name: Test User")
        expect(data_display).to_contain_text("Age: 25")
        expect(data_display).to_contain_text("Items: 3")

    def test_pyodide_complex_props_conversion(self, page: Page):
        """Test complex nested props conversion"""
        page.goto("http://localhost:3333/tests/test_pages/complex_props.html")

        page.wait_for_selector("[data-testid='complex-props']", timeout=10000)

        component = page.locator("[data-testid='complex-props']")
        expect(component).to_be_visible()

        # Check nested data renders correctly
        expect(component).to_contain_text("User: John Doe")
        expect(component).to_contain_text("Role: admin")
        expect(component).to_contain_text("Permissions: 3")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for tests"""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    }


@pytest.fixture(autouse=True)
def setup_test_server():
    """Ensure test server is running before tests"""
    # This assumes you have a local server running on port 3333
    # You can start it with: make serve-test-server
    pass
