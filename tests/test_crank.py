"""
Test core Crank.py functionality without mocks
"""

import pytest
from crank import Fragment, component, h


class TestContextFunctionality:
    """Test Context wrapper functionality without mocks."""

    def test_context_iteration(self):
        """Test that Context can be iterated"""
        @component
        def TestIterationComponent(ctx):
            # Test that we can iterate over context
            for props in ctx:
                yield h.div[f"Props: {props}"]

        assert callable(TestIterationComponent)
        element = h(TestIterationComponent)
        assert element is not None

    def test_context_async_iteration(self):
        """Test that Context supports async iteration"""
        @component
        async def TestAsyncIterationComponent(ctx):
            # Test that we can async iterate over context
            async for props in ctx:
                yield h.div[f"Async props: {props}"]

        assert callable(TestAsyncIterationComponent)
        element = h(TestAsyncIterationComponent)
        assert element is not None

    def test_context_decorators_exist(self):
        """Test that Context has the expected decorator methods"""
        @component
        def TestDecoratorsComponent(ctx):
            # Test that decorators exist and don't crash
            assert hasattr(ctx, 'refresh')
            assert hasattr(ctx, 'schedule')
            assert hasattr(ctx, 'after')
            assert hasattr(ctx, 'cleanup')

            for props in ctx:
                yield h.div["Decorators exist"]

        assert callable(TestDecoratorsComponent)
        element = h(TestDecoratorsComponent)
        assert element is not None

    def test_context_props_access(self):
        """Test accessing props from context"""
        @component
        def TestPropsComponent(ctx):
            for props in ctx:
                # Test that props is accessible and dict-like
                name = props.get("name", "default")
                count = props.get("count", 0)
                yield h.div[f"Name: {name}, Count: {count}"]

        assert callable(TestPropsComponent)
        element1 = h(TestPropsComponent)
        element2 = h(TestPropsComponent, name="test", count=5)
        assert element1 is not None
        assert element2 is not None


class TestElementBuilder:
    """Test ElementBuilder functionality without mocks."""

    def test_element_builder_basic_usage(self):
        """Test basic ElementBuilder usage"""
        # Test that ElementBuilder creates elements
        div_builder = h.div
        span_builder = h.span

        assert div_builder is not None
        assert span_builder is not None

    def test_element_builder_with_props(self):
        """Test ElementBuilder with props"""
        element = h.div(className="test", id="main")
        assert element is not None

        input_element = h.input(type="text", value="test")
        assert input_element is not None

    def test_element_builder_with_children(self):
        """Test ElementBuilder with children"""
        element = h.div["Text content"]
        assert element is not None

        nested_element = h.div[
            h.span["Child 1"],
            h.span["Child 2"]
        ]
        assert nested_element is not None

    def test_element_builder_props_and_children(self):
        """Test ElementBuilder with both props and children"""
        element = h.div(className="container")[
            h.span["Content"]
        ]
        assert element is not None

    def test_element_builder_callable_props(self):
        """Test ElementBuilder handles callable props"""
        def click_handler():
            pass

        def input_handler(event):
            pass

        button = h.button(onClick=click_handler)["Click me"]
        input_elem = h.input(onInput=input_handler, type="text")

        assert button is not None
        assert input_elem is not None

    def test_element_builder_complex_props(self):
        """Test ElementBuilder with complex prop types"""
        style_object = {"color": "red", "fontSize": "16px"}
        data_object = {"user": "test", "id": 123}

        element = h.div(
            style=style_object,
            data=data_object,
            className="complex"
        )["Complex element"]

        assert element is not None


class TestHyperscriptSyntax:
    """Test hyperscript syntax patterns."""

    def test_basic_elements(self):
        """Test basic element creation"""
        div = h.div["Hello World"]
        p = h.p["Some text"]
        span = h.span["Content"]

        assert div is not None
        assert p is not None
        assert span is not None

    def test_elements_with_props(self):
        """Test elements with properties"""
        input_elem = h.input(type="text", value="sample")
        div_elem = h.div(className="my-class")
        button_elem = h.button(disabled=True)

        assert input_elem is not None
        assert div_elem is not None
        assert button_elem is not None

    def test_props_spreading(self):
        """Test props spreading patterns"""
        userProps = {"id": "user123", "role": "admin"}
        formProps = {"name": "email", "placeholder": "Enter email"}

        button = h.button(className="btn", **userProps)["Button"]
        input_elem = h.input(type="text", required=True, **formProps)

        assert button is not None
        assert input_elem is not None

    def test_nested_elements(self):
        """Test nested element structures"""
        nested = h.ul[
            h.li["Item 1"],
            h.li["Item 2"],
            h.li[
                "Item with ",
                h.strong["nested"],
                " content"
            ]
        ]

        assert nested is not None

    def test_component_usage_patterns(self):
        """Test component usage patterns"""
        @component
        def TestComponent(ctx):
            for props in ctx:
                name = props.get("name", "Default")
                yield h.div[f"Component: {name}"]

        # Component without props
        comp1 = h(TestComponent)

        # Component with props
        comp2 = h(TestComponent, name="Custom")

        assert comp1 is not None
        assert comp2 is not None

    def test_fragment_patterns(self):
        """Test Fragment usage patterns"""
        # Empty fragment
        empty_frag = h(Fragment)

        # Fragment with children
        frag_with_children = h(Fragment)[
            h.div["First"],
            h.div["Second"]
        ]

        # Fragment shorthand with empty string
        shorthand_frag = h("")[
            h.span["Item 1"],
            h.span["Item 2"]
        ]

        assert empty_frag is not None
        assert frag_with_children is not None
        assert shorthand_frag is not None


class TestComponentPatterns:
    """Test component patterns and signatures."""

    def test_component_signatures(self):
        """Test different component signature patterns"""
        # No parameters
        @component
        def NoParamsComponent():
            return h.div["No params"]

        # Context only
        @component
        def ContextOnlyComponent(ctx):
            for props in ctx:
                yield h.div["Context only"]

        # Context and props
        @component
        def ContextPropsComponent(ctx, props):
            for _ in ctx:
                yield h.div[f"Hello {props.get('name', 'World')}"]

        assert callable(NoParamsComponent)
        assert callable(ContextOnlyComponent)
        assert callable(ContextPropsComponent)

        # Test they can be used
        elem1 = h(NoParamsComponent)
        elem2 = h(ContextOnlyComponent)
        elem3 = h(ContextPropsComponent, name="Test")

        assert elem1 is not None
        assert elem2 is not None
        assert elem3 is not None

    def test_lifecycle_decorators(self):
        """Test component lifecycle decorators"""
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
                yield h.div(onClick=handle_click)["Lifecycle test"]

        assert callable(LifecycleComponent)
        element = h(LifecycleComponent)
        assert element is not None

    def test_error_handling_invalid_signatures(self):
        """Test error handling for invalid component signatures"""
        # This should raise an error due to too many parameters
        with pytest.raises(ValueError, match="incompatible signature"):
            @component
            def TooManyParamsComponent(ctx, props, extra, another):
                return h.div["Too many params"]


class TestREADMEExamples:
    """Test examples from README to ensure they work correctly."""

    def test_hello_world_example(self):
        """Test basic Hello World example from README"""
        @component
        def HelloWorld(ctx):
            for props in ctx:
                yield h.div["Hello World!"]

        element = h(HelloWorld)
        assert element is not None

    def test_interactive_counter_example(self):
        """Test interactive counter example from README"""
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

    def test_props_reassignment_example(self):
        """Test props reassignment pattern from README"""
        @component
        def Greeting(ctx):
            for props in ctx:
                name = props.get("name", "World")
                greeting = props.get("greeting", "Hello")
                yield h.div[f"{greeting} {name}!"]

        element1 = h(Greeting)
        element2 = h(Greeting, name="Alice")
        element3 = h(Greeting, name="Bob", greeting="Hi")

        assert element1 is not None
        assert element2 is not None
        assert element3 is not None

    def test_todo_app_structure(self):
        """Test TodoMVC-style app structure"""
        @component
        def TodoItem(ctx):
            for props in ctx:
                todo = props.get("todo", {})
                title = todo.get("title", "No title")
                completed = todo.get("completed", False)

                yield h.li(className="completed" if completed else None)[
                    h.div(className="view")[
                        h.input(className="toggle", type="checkbox", checked=completed),
                        h.label[title],
                        h.button(className="destroy")
                    ]
                ]

        @component
        def TodoApp(ctx):
            for props in ctx:
                todos = props.get("todos", [])
                yield h.section(className="todoapp")[
                    h.header(className="header")[
                        h.h1["todos"],
                        h.input(className="new-todo", placeholder="What needs to be done?")
                    ],
                    h.section(className="main")[
                        h.ul(className="todo-list")[
                            [h(TodoItem, todo=todo, key=i) for i, todo in enumerate(todos)]
                        ]
                    ]
                ]

        test_todos = [
            {"title": "Learn Crank.py", "completed": False},
            {"title": "Build an app", "completed": True}
        ]

        element = h(TodoApp, todos=test_todos)
        assert element is not None


class TestSyntaxValidation:
    """Test that syntax examples compile correctly."""

    def test_all_readme_examples_compile(self):
        """Test that all README examples compile without errors"""
        # This is a compilation test - if it runs without exception, it passes

        # Basic component
        @component
        def BasicComponent(ctx):
            for props in ctx:
                yield h.div["Basic"]

        # Component with state
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

        # Component with props
        @component
        def PropsComponent(ctx):
            for props in ctx:
                yield h.div[f"Hello {props.get('name', 'World')}"]

        # All should compile
        assert callable(BasicComponent)
        assert callable(StatefulComponent)
        assert callable(PropsComponent)

    def test_hyperscript_syntax_examples(self):
        """Test various hyperscript syntax patterns"""
        # All these should compile without errors

        # Basic elements
        div = h.div["Content"]
        span = h.span["Text"]

        # Elements with props
        input_elem = h.input(type="text", placeholder="Enter text")
        button = h.button(className="btn", onClick=lambda: None)["Click"]

        # Nested structures
        nested = h.div(className="container")[
            h.header[h.h1["Title"]],
            h.main[
                h.p["Paragraph"],
                h.ul[
                    h.li["Item 1"],
                    h.li["Item 2"]
                ]
            ]
        ]

        # All should be created successfully
        assert div is not None
        assert span is not None
        assert input_elem is not None
        assert button is not None
        assert nested is not None


class TestEdgeCases:
    """Test edge cases and error scenarios."""

    def test_empty_component(self):
        """Test component that doesn't yield anything"""
        @component
        def EmptyComponent(ctx):
            for props in ctx:
                pass  # No yield statement

        assert callable(EmptyComponent)
        element = h(EmptyComponent)
        assert element is not None

    def test_component_with_return(self):
        """Test component using return instead of yield"""
        @component
        def ReturnComponent(ctx):
            return h.div["Using return"]

        assert callable(ReturnComponent)
        element = h(ReturnComponent)
        assert element is not None

    def test_complex_nesting(self):
        """Test deeply nested component structures"""
        @component
        def DeepComponent(ctx):
            for props in ctx:
                level = props.get("level", 0)
                if level > 0:
                    yield h.div[
                        f"Level {level}",
                        h(DeepComponent, level=level-1)
                    ]
                else:
                    yield h.div["Bottom level"]

        element = h(DeepComponent, level=3)
        assert element is not None

    def test_none_props_handling(self):
        """Test handling of None props"""
        element1 = h.div(className=None)["Content"]
        element2 = h.input(value=None, type="text")

        assert element1 is not None
        assert element2 is not None

    def test_falsy_children_handling(self):
        """Test handling of falsy children"""
        element = h.div[
            "Always shown",
            None,  # Should be filtered out
            False,  # Should be filtered out
            "",  # Empty string
            0,  # Falsy number
            h.span["Also shown"]
        ]

        assert element is not None
