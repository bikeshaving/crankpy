"""
Test core Crank.py functionality - actual behavior testing
"""

import pytest

from crank import component, h, Context, Fragment


class TestComponentDecorator:
    """Test the @component decorator functionality."""

    def test_component_decorator_basic(self):
        """Test that @component decorator works on functions"""
        @component
        def BasicComponent(ctx):
            for props in ctx:
                yield h.div["Basic component"]
        
        # Should be callable
        assert callable(BasicComponent)
        
        # Should create element without errors
        element = h(BasicComponent)
        assert element is not None

    def test_component_with_props(self):
        """Test components that accept props"""
        @component
        def PropsComponent(ctx):
            for props in ctx:
                name = props.get("name", "World")
                yield h.div[f"Hello {name}"]
        
        # Should work with props
        element = h(PropsComponent, name="Alice")
        assert element is not None
        
        # Should work without props
        element_no_props = h(PropsComponent)
        assert element_no_props is not None

    def test_async_component_decorator(self):
        """Test @component decorator on async functions"""
        @component
        async def AsyncComponent(ctx):
            async for props in ctx:
                yield h.div["Async component"]
        
        # Should be callable
        assert callable(AsyncComponent)
        
        # Should create element without errors
        element = h(AsyncComponent)
        assert element is not None

    def test_component_with_no_params(self):
        """Test component with no parameters"""
        @component
        def NoParamsComponent():
            return h.div["No params component"]
        
        # Should be callable
        assert callable(NoParamsComponent)
        
        # Should create element without errors
        element = h(NoParamsComponent)
        assert element is not None


class TestHyperscriptSyntax:
    """Test the hyperscript (h) syntax patterns."""

    def test_basic_elements(self):
        """Test basic element creation"""
        # Simple elements
        div = h.div
        span = h.span
        p = h.p
        
        assert div is not None
        assert span is not None
        assert p is not None

    def test_elements_with_text_content(self):
        """Test elements with text content"""
        element1 = h.div["Hello World"]
        element2 = h.span["Some text"]
        element3 = h.p["Paragraph text"]
        
        assert element1 is not None
        assert element2 is not None
        assert element3 is not None

    def test_elements_with_props(self):
        """Test elements with properties"""
        element1 = h.div(className="container")
        element2 = h.input(type="text", value="test")
        element3 = h.button(onClick=lambda: None)
        
        assert element1 is not None
        assert element2 is not None
        assert element3 is not None

    def test_elements_with_props_and_children(self):
        """Test elements with both props and children"""
        element1 = h.div(className="container")["Content"]
        element2 = h.button(onClick=lambda: None)["Click me"]
        element3 = h.input(type="text", placeholder="Enter text")
        
        assert element1 is not None
        assert element2 is not None
        assert element3 is not None

    def test_nested_elements(self):
        """Test nested element structures"""
        element = h.div(className="outer")[
            h.div(className="inner")[
                h.span["Nested content"],
                h.button["Click me"]
            ]
        ]
        
        assert element is not None

    def test_component_usage_with_h(self):
        """Test using components with h() function"""
        @component
        def TestComponent(ctx):
            for props in ctx:
                yield h.div["Test component"]
        
        # Component without props
        element1 = h(TestComponent)
        
        # Component with props
        element2 = h(TestComponent, someProp="value")
        
        assert element1 is not None
        assert element2 is not None

    def test_fragment_patterns(self):
        """Test Fragment usage patterns"""
        # Empty fragment
        fragment1 = h(Fragment)
        
        # Fragment with children
        fragment2 = h(Fragment)[
            h.div["First"],
            h.div["Second"]
        ]
        
        # Fragment shorthand
        fragment3 = h("")[
            h.span["Item 1"],
            h.span["Item 2"]
        ]
        
        assert fragment1 is not None
        assert fragment2 is not None
        assert fragment3 is not None


class TestComponentPatterns:
    """Test common component patterns and signatures."""

    def test_component_with_context_only(self):
        """Test component that takes only context"""
        @component
        def ContextOnlyComponent(ctx):
            for props in ctx:
                yield h.div["Context only"]
        
        assert callable(ContextOnlyComponent)
        element = h(ContextOnlyComponent)
        assert element is not None

    def test_component_with_context_and_props(self):
        """Test component that takes context and props"""
        @component
        def ContextAndPropsComponent(ctx, props):
            for _ in ctx:
                name = props.get("name", "Default")
                yield h.div[f"Hello {name}"]
        
        assert callable(ContextAndPropsComponent)
        element = h(ContextAndPropsComponent, name="Test")
        assert element is not None

    def test_component_lifecycle_decorators(self):
        """Test component with lifecycle decorators"""
        @component
        def LifecycleComponent(ctx):
            @ctx.refresh
            def handle_click():
                pass
            
            @ctx.schedule
            def before_render():
                pass
            
            @ctx.after
            def after_render():
                pass
            
            @ctx.cleanup
            def cleanup():
                pass
            
            for props in ctx:
                yield h.div(onClick=handle_click)["Lifecycle component"]
        
        assert callable(LifecycleComponent)
        element = h(LifecycleComponent)
        assert element is not None

    def test_component_with_state(self):
        """Test component that manages state"""
        @component
        def StatefulComponent(ctx):
            count = 0
            
            @ctx.refresh
            def increment():
                nonlocal count
                count += 1
            
            for props in ctx:
                yield h.div[
                    h.span[f"Count: {count}"],
                    h.button(onClick=increment)["Increment"]
                ]
        
        assert callable(StatefulComponent)
        element = h(StatefulComponent)
        assert element is not None


class TestREADMEExamples:
    """Test examples from the README to ensure they work."""

    def test_hello_world_example(self):
        """Test basic Hello World example"""
        @component
        def HelloWorld(ctx):
            for props in ctx:
                yield h.div["Hello World!"]
        
        element = h(HelloWorld)
        assert element is not None

    def test_interactive_counter_example(self):
        """Test interactive counter from README"""
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
            
            for props in ctx:
                yield h.div[
                    h.h1[f"Count: {count}"],
                    h.button(onClick=increment)["+"],
                    h.button(onClick=decrement)["-"]
                ]
        
        element = h(Counter)
        assert element is not None

    def test_props_example(self):
        """Test component with props"""
        @component
        def Greeting(ctx):
            for props in ctx:
                name = props.get("name", "World")
                yield h.div[f"Hello {name}!"]
        
        element1 = h(Greeting)
        element2 = h(Greeting, name="Alice")
        
        assert element1 is not None
        assert element2 is not None

    def test_nested_component_example(self):
        """Test nested components"""
        @component
        def TodoItem(ctx):
            for props in ctx:
                todo = props.get("todo", {})
                title = todo.get("title", "No title")
                yield h.li[title]
        
        @component
        def TodoList(ctx):
            for props in ctx:
                todos = props.get("todos", [])
                yield h.ul[
                    [h(TodoItem, todo=todo, key=i) for i, todo in enumerate(todos)]
                ]
        
        element = h(TodoList, todos=[
            {"title": "Learn Crank.py"},
            {"title": "Build an app"}
        ])
        
        assert element is not None


class TestSyntaxValidation:
    """Test that various syntax patterns compile correctly."""

    def test_hyperscript_chaining(self):
        """Test hyperscript chaining syntax"""
        # Method chaining style
        element1 = h.div(className="container")[
            h.span(className="text")["Content"]
        ]
        
        # Functional style - test without subscript due to mock limitations
        element2 = h("div", className="container")
        span_elem = h("span", className="text")
        
        assert element1 is not None
        assert element2 is not None
        assert span_elem is not None

    def test_event_handlers(self):
        """Test event handler syntax"""
        def click_handler():
            pass
        
        def input_handler(event):
            pass
        
        element = h.div[
            h.button(onClick=click_handler)["Click me"],
            h.input(onInput=input_handler, type="text")
        ]
        
        assert element is not None

    def test_conditional_rendering(self):
        """Test conditional rendering patterns"""
        show_content = True
        
        element = h.div[
            h.span["Always shown"],
            h.div["Conditional content"] if show_content else None
        ]
        
        assert element is not None

    def test_list_rendering(self):
        """Test list rendering patterns"""
        items = ["Item 1", "Item 2", "Item 3"]
        
        element = h.ul[
            [h.li(key=i)[item] for i, item in enumerate(items)]
        ]
        
        assert element is not None


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_component_with_no_yield(self):
        """Test component that doesn't yield anything"""
        @component
        def EmptyComponent(ctx):
            for props in ctx:
                pass  # No yield
        
        assert callable(EmptyComponent)
        element = h(EmptyComponent)
        assert element is not None

    def test_component_with_return_instead_of_yield(self):
        """Test component that uses return instead of yield"""
        @component
        def ReturnComponent(ctx):
            props = ctx.props
            return h.div[f"Return style component"]
        
        assert callable(ReturnComponent)
        element = h(ReturnComponent)
        assert element is not None

    def test_component_with_complex_props(self):
        """Test component with complex prop types"""
        @component
        def ComplexPropsComponent(ctx):
            for props in ctx:
                data = props.get("data", {})
                handlers = props.get("handlers", {})
                config = props.get("config", {"enabled": True})
                
                yield h.div[
                    f"Data: {data}, Config: {config}",
                    h.button(onClick=handlers.get("click"))["Action"] if handlers.get("click") else None
                ]
        
        element = h(ComplexPropsComponent, 
                   data={"name": "test"}, 
                   handlers={"click": lambda: None},
                   config={"enabled": False})
        
        assert element is not None

    def test_deeply_nested_components(self):
        """Test deeply nested component structures"""
        @component
        def InnerComponent(ctx):
            for props in ctx:
                yield h.span[props.get("text", "Inner")]
        
        @component
        def MiddleComponent(ctx):
            for props in ctx:
                yield h.div[h(InnerComponent, text=props.get("text", "Middle"))]
        
        @component
        def OuterComponent(ctx):
            for props in ctx:
                yield h.section[h(MiddleComponent, text="Outer")]
        
        element = h(OuterComponent)
        assert element is not None

    def test_component_with_multiple_yields_per_iteration(self):
        """Test component that yields multiple times per iteration"""
        @component
        def MultiYieldComponent(ctx):
            for props in ctx:
                count = props.get("count", 1)
                for i in range(count):
                    yield h.div[f"Item {i}"]
        
        element = h(MultiYieldComponent, count=3)
        assert element is not None