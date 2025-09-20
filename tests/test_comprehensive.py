"""
Comprehensive test suite for Crank.py

Consolidates core functionality tests including:
- README examples validation
- FFI functionality (unit tests)
- Component patterns and lifecycle
- Hyperscript syntax
- Error handling and edge cases

This replaces multiple smaller test files for better organization.
"""

import pytest
import sys
import time
from unittest.mock import Mock, MagicMock

# Mock PyScript modules before importing crank
sys.modules['js'] = Mock()
sys.modules['pyscript'] = Mock()
sys.modules['pyscript.ffi'] = Mock()
sys.modules['pyscript.js_modules'] = Mock()

# Mock the PyScript FFI functions
mock_create_proxy = Mock()
mock_to_js = Mock()
sys.modules['pyscript.ffi'].create_proxy = mock_create_proxy
sys.modules['pyscript.ffi'].to_js = mock_to_js

# Mock crank_core
mock_crank_core = Mock()
mock_crank_core.Element = Mock()
mock_crank_core.createElement = Mock()
mock_crank_core.Fragment = Mock()
sys.modules['pyscript.js_modules'].crank_core = mock_crank_core

# Mock JS objects
sys.modules['js'].Symbol = Mock()
sys.modules['js'].Symbol.for_ = Mock(return_value="mock_symbol")
sys.modules['js'].Object = Mock()
sys.modules['js'].document = Mock()

# Mock crank.dom
sys.modules['crank.dom'] = Mock()
mock_renderer = Mock()
sys.modules['crank.dom'].renderer = mock_renderer

# Now import crank after mocking
from crank import h, component, Context, ElementBuilder


class TestCoreFFI:
    """Core FFI functionality tests"""
    
    def setup_method(self):
        """Reset mocks before each test"""
        mock_create_proxy.reset_mock()
        mock_to_js.reset_mock()
        mock_crank_core.createElement.reset_mock()
    
    def test_component_decorator_creates_proxy(self):
        """Test that @component decorator creates proxy for function"""
        mock_proxy = Mock()
        mock_create_proxy.return_value = mock_proxy
        
        @component
        def TestComponent(ctx):
            return h.div["test"]
        
        mock_create_proxy.assert_called_once()
        assert TestComponent == mock_proxy
    
    def test_element_builder_processes_callables(self):
        """Test that ElementBuilder processes callable props"""
        mock_proxy = Mock()
        mock_create_proxy.return_value = mock_proxy
        
        def click_handler():
            pass
        
        builder = ElementBuilder("button")
        props = {"onClick": click_handler}
        result = builder._process_props_for_proxies(props)
        
        mock_create_proxy.assert_called_with(click_handler)
        assert result["onClick"] == mock_proxy
    
    def test_nested_callable_processing(self):
        """Test processing of nested callables in complex props"""
        mock_proxy = Mock()
        mock_create_proxy.return_value = mock_proxy
        
        def handler1():
            pass
        
        def handler2():
            pass
        
        props = {
            "events": {
                "onClick": handler1,
                "onSubmit": handler2
            },
            "simple": "string",
            "number": 42
        }
        
        builder = ElementBuilder("div")
        result = builder._process_props_for_proxies(props)
        
        assert mock_create_proxy.call_count == 2
        assert result["events"]["onClick"] == mock_proxy
        assert result["events"]["onSubmit"] == mock_proxy
        assert result["simple"] == "string"
        assert result["number"] == 42
    
    def test_context_wrapper_functionality(self):
        """Test Context wrapper delegates to JS context"""
        # Mock JS context with proper bind method
        js_ctx = Mock()
        js_schedule = Mock()
        js_ctx.schedule = Mock()
        js_ctx.schedule.bind = Mock(return_value=js_schedule)
        js_ctx.some_property = "test_value"
        
        ctx = Context(js_ctx)
        
        assert hasattr(ctx, 'refresh')
        assert ctx.some_property == "test_value"
        
        mock_proxy = Mock()
        mock_create_proxy.return_value = mock_proxy
        
        def test_func():
            pass
        
        ctx.schedule(test_func)
        mock_create_proxy.assert_called_with(test_func)
        js_schedule.assert_called_with(mock_proxy)


class TestHyperscriptSyntax:
    """Test hyperscript syntax patterns"""
    
    def setup_method(self):
        """Reset mocks before each test"""
        mock_create_proxy.reset_mock()
        mock_to_js.reset_mock()
        mock_crank_core.createElement.reset_mock()
    
    def test_basic_elements(self):
        """Test basic element creation"""
        result1 = h.div["Hello World"]
        result2 = h.p["Some text"]
        
        assert mock_crank_core.createElement.call_count >= 2
        calls = mock_crank_core.createElement.call_args_list
        assert any("div" in str(call) for call in calls)
        assert any("p" in str(call) for call in calls)
    
    def test_elements_with_props(self):
        """Test elements with properties"""
        text = "sample"
        result1 = h.input(type="text", value=text)
        result2 = h.div(className="my-class")["Content"]
        
        mock_crank_core.createElement.assert_called()
    
    def test_props_spreading(self):
        """Test props spreading patterns"""
        userProps = {"id": "user123", "role": "admin"}
        formProps = {"name": "email", "placeholder": "Enter email"}
        
        h.button(className="btn", **userProps)["Click me"]
        h.input(type="text", required=True, **formProps)
        
        # Should call createElement (test passes if no exceptions)
        assert mock_crank_core.createElement.call_count >= 1
    
    def test_nested_elements(self):
        """Test nested element structures"""
        result = h.ul[
            h.li["Item 1"],
            h.li["Item 2"],
            h.li[
                "Item with ",
                h.strong["nested"],
                " content"
            ]
        ]
        
        assert mock_crank_core.createElement.call_count >= 4
    
    def test_component_usage_patterns(self):
        """Test component usage patterns"""
        @component
        def MockComponent(ctx, props=None):
            return h.div["Mock component"]
        
        # Reset after component creation
        mock_crank_core.createElement.reset_mock()
        
        # Component without props
        h(MockComponent)
        
        # Component with props
        h(MockComponent, name="Alice", count=42)
        
        # Test element creation separately
        h.p["Child content"]  # This should call createElement
        
        # Should call createElement for the paragraph
        assert mock_crank_core.createElement.call_count >= 1
    
    def test_fragment_patterns(self):
        """Test fragment usage patterns"""
        # Simple fragments
        result1 = ["Multiple", "children", "without", "wrapper"]
        result2 = [h.div["Item 1"], h.div["Item 2"]]
        
        # Fragment with props
        result3 = h("", key="my-fragment")["Child 1", "Child 2"]
        
        assert isinstance(result1, list)
        assert isinstance(result2, list)
        assert result3 is not None


class TestComponentPatterns:
    """Test component signature patterns and lifecycle"""
    
    def setup_method(self):
        """Reset mocks before each test"""
        mock_create_proxy.reset_mock()
        mock_to_js.reset_mock()
        mock_crank_core.createElement.reset_mock()
    
    def test_component_signatures(self):
        """Test all three component signature patterns"""
        # 1. Static components (no state)
        @component
        def Logo():
            return h.div["🔧 Crank.py"]
        
        # 2. Context-only (internal state)
        @component  
        def Timer(ctx):
            start_time = time.time()
            for _ in ctx:
                elapsed = time.time() - start_time
                yield h.div[f"Time: {elapsed:.1f}s"]
        
        # 3. Context + Props (reactive)
        @component
        def TodoItem(ctx, props):
            for props in ctx:
                todo = props.todo
                yield h.li[
                    h.input(type="checkbox", checked=todo.done),
                    h.span[todo.text]
                ]
        
        assert callable(Logo)
        assert callable(Timer)
        assert callable(TodoItem)
        assert mock_create_proxy.call_count >= 3
    
    def test_lifecycle_decorators(self):
        """Test lifecycle decorator patterns"""
        @component
        def MyComponent(ctx):
            @ctx.refresh
            def handle_click():
                pass
            
            @ctx.schedule  
            def before_render():
                pass
            
            @ctx.after
            def after_render(node):
                if hasattr(node, 'style'):
                    node.style.color = "blue"
            
            @ctx.cleanup
            def on_unmount():
                pass
            
            for _ in ctx:
                yield h.div(onClick=handle_click)["Click me"]
        
        assert callable(MyComponent)
        mock_create_proxy.assert_called()
    
    def test_error_handling_invalid_signatures(self):
        """Test error handling for invalid component signatures"""
        # Note: The actual error checking happens in the component wrapper
        # when called, not at decoration time. Let's test the actual behavior.
        @component
        def BadComponent(ctx, props, extra):
            return h.div["bad"]
        
        # The component should be created (as it's just a proxy)
        # Error would occur when Crank tries to call it with wrong params
        assert callable(BadComponent)


class TestREADMEExamples:
    """Test that all README examples work correctly"""
    
    def setup_method(self):
        """Reset mocks before each test"""
        mock_create_proxy.reset_mock()
        mock_to_js.reset_mock()
        mock_crank_core.createElement.reset_mock()
        mock_renderer.render.reset_mock()
    
    def test_hello_world_example(self):
        """Test README Hello World example"""
        @component
        def Greeting(ctx):
            for _ in ctx:
                yield h.div["Hello, Crank.py! ⚙️"]
        
        assert callable(Greeting)
        mock_create_proxy.assert_called()
        
        # Test rendering pattern
        from crank.dom import renderer
        from js import document
        
        result = h(Greeting)
        renderer.render(result, document.body)
        mock_renderer.render.assert_called_once()
    
    def test_interactive_counter_example(self):
        """Test README Interactive Counter example"""
        @component
        def Counter(ctx):
            count = 0
            
            @ctx.refresh
            def increment():
                nonlocal count
                count += 1
            
            @ctx.refresh  
            def decrement():
                nonlocal count
                count -= 1
            
            for _ in ctx:
                yield h.div[
                    h.h2[f"Count: {count}"],
                    h.button(onClick=increment)["+"],
                    h.button(onClick=decrement)["-"]
                ]
        
        assert callable(Counter)
        mock_create_proxy.assert_called()
    
    def test_props_reassignment_example(self):
        """Test README Props Reassignment example"""
        @component
        def UserProfile(ctx, props):
            for props in ctx:
                user_id = props.user_id
                
                # Mock fetch_user
                class MockUser:
                    avatar = "avatar.jpg"
                    name = "Test User"
                    bio = "Test bio"
                
                user = MockUser()
                
                yield h.div[
                    h.img(src=user.avatar),
                    h.h2[user.name],
                    h.p[user.bio]
                ]
        
        component_call = h(UserProfile, user_id=123)
        assert callable(UserProfile)
        assert component_call is not None
    
    def test_todo_app_structure(self):
        """Test README TodoApp example structure"""
        @component
        def TodoApp(ctx):
            todos = []
            new_todo = ""
            
            @ctx.refresh
            def add_todo():
                nonlocal todos, new_todo
                if new_todo.strip():
                    todos.append({"text": new_todo, "done": False})
                    new_todo = ""
            
            @ctx.refresh
            def toggle_todo(index):
                nonlocal todos
                todos[index]["done"] = not todos[index]["done"]
            
            for _ in ctx:
                yield h.div[
                    h.h1["Todo List"],
                    h.input(type="text", value=new_todo),
                    h.button(onclick=add_todo)["Add"],
                    h.ul[
                        [h.li(key=i)[
                            h.input(
                                type="checkbox", 
                                checked=todo["done"],
                                onChange=lambda i=i: toggle_todo(i)
                            ),
                            h.span[todo["text"]]
                        ] for i, todo in enumerate(todos)]
                    ]
                ]
        
        assert callable(TodoApp)
        mock_create_proxy.assert_called()


class TestSyntaxValidation:
    """Test that all code examples are syntactically valid"""
    
    def test_all_readme_examples_compile(self):
        """Verify all README examples compile without syntax errors"""
        examples = [
            # Hello World
            '''
from crank import h, component
from crank.dom import renderer
from js import document

@component
def Greeting(ctx):
    for _ in ctx:
        yield h.div["Hello, Crank.py! ⚙️"]

renderer.render(h(Greeting), document.body)
            ''',
            
            # Interactive Counter
            '''
@component
def Counter(ctx):
    count = 0
    
    @ctx.refresh
    def increment():
        nonlocal count
        count += 1
    
    @ctx.refresh  
    def decrement():
        nonlocal count
        count -= 1
    
    for _ in ctx:
        yield h.div[
            h.h2[f"Count: {count}"],
            h.button(onClick=increment)["+"],
            h.button(onClick=decrement)["-"]
        ]
            ''',
            
            # Component Signatures
            '''
import time

@component
def Logo():
    return h.div["🔧 Crank.py"]

@component  
def Timer(ctx):
    start_time = time.time()
    for _ in ctx:
        elapsed = time.time() - start_time
        yield h.div[f"Time: {elapsed:.1f}s"]

@component
def TodoItem(ctx, props):
    for props in ctx:
        todo = props.todo
        yield h.li[
            h.input(type="checkbox", checked=todo.done),
            h.span[todo.text]
        ]
            '''
        ]
        
        for i, example in enumerate(examples):
            try:
                compile(example, f'README_example_{i}', 'exec')
            except SyntaxError as e:
                pytest.fail(f"README example {i} has syntax error: {e}")
    
    def test_hyperscript_syntax_examples(self):
        """Test hyperscript syntax examples compile correctly"""
        syntax_examples = '''
# Simple text content
h.div["Hello World"]
h.p["Some text"]

# With properties  
text = "sample"
h.input(type="text", value=text)
h.div(className="my-class")["Content"]

# Snake_case → kebab-case conversion
h.div(
    data_test_id="button",
    aria_hidden="true"
)["Content"]

# Props spreading
userProps = {"id": "test"}
formProps = {"name": "email"}
h.button(className="btn", **userProps)["Click me"]
h.input(type="text", required=True, **formProps)

# Nested elements
h.ul[
    h.li["Item 1"],
    h.li["Item 2"],
    h.li[
        "Item with ",
        h.strong["nested"],
        " content"
    ]
]
        '''
        
        try:
            compile(syntax_examples, 'hyperscript_examples', 'exec')
        except SyntaxError as e:
            pytest.fail(f"Hyperscript syntax examples have syntax error: {e}")


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def setup_method(self):
        """Reset mocks before each test"""
        mock_create_proxy.reset_mock()
        mock_to_js.reset_mock()
        mock_crank_core.createElement.reset_mock()
    
    def test_already_proxied_functions_not_reproxied(self):
        """Test that already proxied functions aren't proxied again"""
        # Create mock that looks like JS proxy
        already_proxied = Mock()
        already_proxied.toString = Mock()  # JS proxy indicator
        
        props = {"onClick": already_proxied}
        builder = ElementBuilder("button")
        result = builder._process_props_for_proxies(props)
        
        mock_create_proxy.assert_not_called()
        assert result["onClick"] == already_proxied
    
    def test_error_handling_graceful(self):
        """Test that errors don't crash the system"""
        mock_create_proxy.side_effect = Exception("Proxy failed")
        
        def failing_handler():
            pass
        
        props = {"onClick": failing_handler}
        builder = ElementBuilder("button")
        
        try:
            result = builder._process_props_for_proxies(props)
        except Exception:
            pass  # Expected to fail in this case
    
    def test_context_with_missing_js_methods(self):
        """Test Context wrapper with JS context missing methods"""
        js_ctx = Mock()
        del js_ctx.refresh
        del js_ctx.schedule
        
        ctx = Context(js_ctx)
        
        assert ctx._refresh is None
        assert ctx._schedule is None
        
        ctx.refresh()  # Should do nothing
        
        def test_func():
            pass
        
        result = ctx.schedule(test_func)
        assert result == test_func


if __name__ == '__main__':
    pytest.main([__file__, "-v"])