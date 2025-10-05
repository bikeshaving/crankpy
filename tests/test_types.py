"""
Type-only tests for Crank.py type system.

These tests validate TypedDict interfaces, component signatures, and type safety
without runtime execution. Use `pyright tests/test_types.py` to run.

Run with: uv run pyright tests/test_types.py
"""

import sys
from typing import Callable, Generic, List, Literal, TypedDict, TypeVar, Union
from unittest.mock import Mock

# Import existing mocks from test_crank to ensure consistency
from test_crank import mock_crank_core, mock_create_proxy, mock_JsProxy, mock_to_js

from crank import Children, Context, Element, Props, component, h


# Test basic type definitions
def test_basic_types() -> None:
    """Test that basic types are properly defined"""
    # Props should be Dict[str, Any]
    _props: Props = {"title": "test", "count": 42, "onclick": lambda: None}

    # Children should accept various formats
    _text_child: Children = "Hello"
    _element_child: Children = h.div["content"]
    _list_child: Children = [h.span["item1"], h.span["item2"]]
    _nested_child: Children = ["text", h.div["nested"], ["deep", "nesting"]]


# Test TypedDict component interfaces
class ButtonProps(TypedDict, total=False):
    """Button component props interface"""
    onclick: Callable[[], None]
    disabled: bool
    variant: Literal["primary", "secondary", "danger"]
    children: Children

class TodoItemProps(TypedDict):
    """Todo item props interface with required fields"""
    todo: "TodoDict"
    ontoggle: Callable[[int], None]
    ondelete: Callable[[int], None]

class TodoDict(TypedDict):
    """Todo data structure"""
    id: int
    title: str
    completed: bool

class UserProfileProps(TypedDict, total=False):
    """User profile props with optional fields"""
    user_id: int
    show_avatar: bool
    onupdate: Callable[[int, str], None]


def test_component_signatures() -> None:
    """Test that component decorators work with proper signatures"""

    # Static component (no parameters)
    @component
    def Logo() -> Element:
        return h.div["🔧 Crank.py"]

    # Context-only component with generic typing
    @component
    def Timer(ctx: Context[Props, Element]) -> Element:
        for _props in ctx:
            yield h.div["Timer"]

    # Context + Props component with specific prop types
    @component
    def Button(ctx: Context[ButtonProps, Element], props: ButtonProps) -> Element:
        for props in ctx:
            yield h.button(
                onclick=props.get("onclick"),
                disabled=props.get("disabled", False)
            )[props.get("children", "Click")]

    # Todo item with strict typing and generic Context
    @component
    def TodoItem(ctx: Context[TodoItemProps, Element], props: TodoItemProps) -> Element:
        for props in ctx:
            todo = props["todo"]  # Required field
            yield h.li[
                h.input(
                    type="checkbox",
                    checked=todo["completed"],
                    onchange=lambda props=props, todo=todo: props["ontoggle"](todo["id"])
                ),
                h.span[todo["title"]]
            ]


def test_component_usage() -> None:
    """Test proper component usage with type checking"""

    # Components are defined in test_component_signatures()
    # This would work if components were imported or defined here
    pass


def test_hyperscript_typing() -> None:
    """Test hyperscript syntax type safety"""

    # HTML elements  
    _div_element = h.div["content"]
    _input_element = h.input(type="text", value="test")
    _button_element = h.button(onclick=lambda: None)  # Don't use chainable syntax in type test

    # Fragments
    _fragment1 = [h.span["item1"], h.span["item2"]]
    _fragment2 = h("", key="frag")["children"]


# Test generic components
T = TypeVar('T')

class ListProps(TypedDict, Generic[T]):
    """Generic list component props"""
    items: List[T]
    render_item: Callable[[T], Element]
    onselect: Callable[[T], None]

def test_generic_components() -> None:
    """Test generic component patterns with typed Context"""

    @component
    def GenericList(ctx: Context[ListProps[T], Element], props: ListProps[T]) -> Element:
        for props in ctx:  # props is properly typed as ListProps[T]
            yield h.ul[
                [h.li(
                    key=i,
                    onclick=lambda props=props, item=item: props["onselect"](item)
                )[props["render_item"](item)]
                 for i, item in enumerate(props["items"])]
            ]

    # Usage with specific types
    _users = [{"name": "Alice"}, {"name": "Bob"}]
    _user_list = h(GenericList,
        items=_users,
        render_item=lambda user: h.span[user["name"]],
        onselect=lambda user: None
    )


def test_union_and_literal_types() -> None:
    """Test advanced type patterns"""

    class FormFieldProps(TypedDict):
        """Form field with discriminated union"""
        name: str
        value: Union[str, int, bool]
        onchange: Callable[[Union[str, int, bool]], None]
        field_type: Literal["text", "number", "checkbox"]

    @component
    def FormField(ctx: Context[FormFieldProps, Element], props: FormFieldProps) -> Element:
        for props in ctx:  # props is properly typed as FormFieldProps
            field_type = props["field_type"]

            if field_type == "checkbox":
                yield h.input(
                    type="checkbox",
                    name=props["name"],
                    checked=bool(props["value"]),
                    onchange=lambda e, props=props: props["onchange"](e.target.checked)
                )
            elif field_type == "number":
                yield h.input(
                    type="number",
                    name=props["name"],
                    value=str(props["value"]),
                    onchange=lambda e, props=props: props["onchange"](int(e.target.value))
                )
            else:  # text
                yield h.input(
                    type="text",
                    name=props["name"],
                    value=str(props["value"]),
                    onchange=lambda e, props=props: props["onchange"](e.target.value)
                )

    # Valid usage
    _text_field = h(FormField,
        name="username",
        value="alice",
        field_type="text",
        onchange=lambda val: None
    )

    _number_field = h(FormField,
        name="age",
        value=25,
        field_type="number",
        onchange=lambda val: None
    )

    _checkbox_field = h(FormField,
        name="subscribe",
        value=True,
        field_type="checkbox",
        onchange=lambda val: None
    )


def test_context_typing() -> None:
    """Test Context wrapper typing with generics"""

    # Define specific props interface
    class MyComponentProps(TypedDict, total=False):
        title: str
        count: int
        onclick: Callable[[], None]

    @component
    def TypedComponent(ctx: Context[MyComponentProps, Element], props: MyComponentProps) -> Element:
        # Context methods should be properly typed
        ctx.refresh()  # () -> None

        @ctx.refresh
        def handle_click() -> None:
            pass

        @ctx.schedule
        def before_render() -> None:
            pass

        @ctx.after
        def after_render(node) -> None:
            pass

        @ctx.cleanup
        def on_cleanup() -> None:
            pass

        # Iterator should yield typed props
        for props in ctx:  # props is now MyComponentProps type
            title: str = props.get("title", "Default")
            count: int = props.get("count", 0)
            yield h.div[f"{title}: {count}"]

        # Direct props access with typing
        current_props: MyComponentProps = ctx.props
        _current_title = current_props.get("title", "No title")


def test_event_props_convention() -> None:
    """Test lowercase event props convention"""

    class EventProps(TypedDict, total=False):
        """Props with lowercase event handlers"""
        onclick: Callable[[], None]
        onchange: Callable[[str], None]
        ontoggle: Callable[[bool], None]
        onsubmit: Callable[[], None]
        oninput: Callable[[str], None]

    @component
    def EventComponent(ctx: Context, props: EventProps) -> Element:
        for props in ctx:
            yield h.div[
                h.button(onclick=props.get("onclick"))["Click"],
                h.input(
                    onchange=lambda e, props=props: props.get("onchange", lambda x: None)(e.target.value),
                    oninput=lambda e, props=props: props.get("oninput", lambda x: None)(e.target.value)
                ),
                h.input(
                    type="checkbox",
                    onchange=lambda e, props=props: props.get("ontoggle", lambda x: None)(e.target.checked)
                )
            ]


# Type error examples (these should fail type checking if uncommented)
def test_type_errors() -> None:
    """Examples that should fail type checking"""

    # These lines should produce type errors when uncommented:

    # Wrong component signature
    # @component
    # def BadComponent(ctx: Context, props: Props, extra: str) -> Element:  # Too many params
    #     return h.div["bad"]

    # Missing required props
    # bad_todo = h(TodoItem, ontoggle=lambda x: None)  # Missing required 'todo' and 'ondelete'

    # Wrong prop types
    # bad_button = h(Button, variant="invalid")  # Not in Literal["primary", "secondary", "danger"]
    # bad_button2 = h(Button, onclick="not_callable")  # Should be Callable

    # Wrong event prop casing (should be lowercase)
    # class BadEventProps(TypedDict, total=False):
    #     onClick: Callable[[], None]  # Should be 'onclick'
    #     onChange: Callable[[str], None]  # Should be 'onchange'

    pass


if __name__ == "__main__":
    # This file is meant for type checking only
    # Run: uv run pyright tests/test_types.py
    print("Type-only tests - run with: uv run pyright tests/test_types.py")
