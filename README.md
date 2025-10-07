# ⚙️🐍 Crank.py

Modern components for Python frontend development.

[![PyScript Compatible](https://img.shields.io/badge/PyScript-Compatible-blue)](https://pyscript.net)
[![Pyodide Compatible](https://img.shields.io/badge/Pyodide-Compatible-green)](https://pyodide.org)
[![MicroPython Compatible](https://img.shields.io/badge/MicroPython-Compatible-orange)](https://micropython.org)
[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Built on the [Crank.js](https://crank.js.org/) framework.

## Features

- **Pythonic Hyperscript** - Clean template `h.div["content"]` syntax inspired by JSX
- **Generator Components** - Natural state management using Python generators
- **Async Components** - Components can use `async def`/`await` and `await for`
- **Lifecycle Decorators** - `@ctx.refresh`, `@ctx.after`, `@ctx.cleanup`
- **Dual Runtime** - Full compatibility with both Pyodide and MicroPython runtimes
- **Browser Native** - No build step

## Installation

### PyScript

```html
<py-config type="toml">
packages = ["crankpy"]

[js_modules.main]
"https://esm.run/@b9g/crank@latest/crank.js" = "crank_core"
"https://esm.run/@b9g/crank@latest/dom.js" = "crank_dom"
</py-config>
```

### pip

```bash
pip install crankpy
```

## Quick Start

### Hello World

```python
from crank import h, component
from crank.dom import renderer
from js import document

@component
def Greeting(ctx):
    for _ in ctx:
        yield h.div["Hello, Crank.py!"]

renderer.render(h(Greeting), document.body)
```

### Interactive Counter

```python
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
            h.button(onclick=increment)["+"],
            h.button(onclick=decrement)["-"]
        ]
```

### Props Reassignment

```python
@component
async def UserProfile(ctx, props):
    old_user_id = None
    for props in ctx:  # Props automatically update!
        user_id = props.user_id
        if user_id != old_user_id:
            user = await fetch_user(user_id)  # Fetches when props change
            yield h.div[
                h.img(src=user.avatar),
                h.h2[user.name],
                h.p[user.bio]
            ]
        else:
            yield h(Copy)
        old_user_id = user_id

# Usage
h(UserProfile, user_id=123)
```

## Hyperscript Syntax Guide

Crank.py uses a clean, Pythonic hyperscript syntax:

### HTML Elements

```python
# Simple text content
h.div["Hello World"]
h.p["Some text"]

# With props
h.input(type="text", value=text)
h.div(className="my-class")["Content"]

# No props or children
h.hr()
h.br()

# Snake_case → kebab-case conversion
h.div(
    data_test_id="button",     # becomes data-test-id
    aria_hidden="true"         # becomes aria-hidden
)["Content"]

# Props spreading (explicit + spread)
h.button(className="btn", **userProps)["Click me"]
h.input(type="text", required=True, **formProps)

# Multiple dict merging (when needed)
h.div(**{**defaults, **themeProps, **userProps})["Content"]

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

# Style objects (snake_case → kebab-case)
h.div(style={
    "background_color": "#f0f0f0",  # becomes background-color
    "border_radius": "5px"          # becomes border-radius
})["Styled content"]

# Reserved keywords with spreading
h.div(**{"class": "container", **userProps})["Content"]
# Or better: use className instead of class
h.div(className="container", **userProps)["Content"]
```

### Components

```python
# Component without props
h(MyComponent)

# Component with props
h(MyComponent, name="Alice", count=42)

# Component with children
h(MyComponent)[
    h.p["Child content"]
]

# Component with props and children
h(MyComponent, title="Hello")[
    h.p["Child content"]
]
```

### Fragments

```python
# Simple fragments - just use Python lists!
["Multiple", "children", "without", "wrapper"]
[h.div["Item 1"], h.div["Item 2"]]

# Fragment with props (when you need keys, etc.)
h("", key="my-fragment")["Child 1", "Child 2"]

# In context
h.div[
    h.h1["Title"],
    [h.p["Para 1"], h.p["Para 2"]],  # Simple fragment
    h.footer["Footer"]
]
```

## Component Lifecycle

### Component Signatures

Crank.py supports three component signatures:

```python
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

# 3. Context + Props (dynamic)
@component
def TodoItem(ctx, props):
    for props in ctx:  # New props each iteration
        todo = props.todo
        yield h.li[
            h.input(type="checkbox", checked=todo.done),
            h.span[todo.text]
        ]
```

### Lifecycle Decorators

```python
@component
def MyComponent(ctx):
    @ctx.refresh
    def handle_click():
        # Automatically triggers re-render
        pass

    @ctx.schedule
    def schedule_render():
        # Runs before the DOM nodes are inserted
        pass

    @ctx.after
    def after_render(node):
        # Runs after DOM updates
        node.style.color = "blue"

    @ctx.cleanup
    def on_unmount():
        # Cleanup when component unmounts
        clear_interval(timer)

    for _ in ctx:
        yield h.div(onclick=handle_click)["Click me"]
```

## Examples

### Todo App

```python
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
            h.input(
                type="text",
                value=new_todo,
                oninput=lambda e: setattr(sys.modules[__name__], 'new_todo', e.target.value)
            ),
            h.button(onclick=add_todo)["Add"],
            h.ul[
                [h.li(key=i)[
                    h.input(
                        type="checkbox",
                        checked=todo["done"],
                        onchange=lambda i=i: toggle_todo(i)
                    ),
                    h.span[todo["text"]]
                ] for i, todo in enumerate(todos)]
            ]
        ]
```

### Real-time Clock

```python
@component
def Clock(ctx):
    import asyncio

    async def update_time():
        while True:
            await asyncio.sleep(1)
            ctx.refresh()

    # Start the update loop
    asyncio.create_task(update_time())

    for _ in ctx:
        current_time = time.strftime("%H:%M:%S")
        yield h.div[
            h.strong["Current time: "],
            current_time
        ]
```

## TypeScript-Style Typing

Crank.py provides comprehensive type safety with TypedDict interfaces, Context typing, and full IDE support through Pyright.

### Component Props with TypedDict

Define strict component interfaces using TypedDict:

```python
from typing import TypedDict, Callable, Optional
from crank import component, Context, Props, Children

# Required and optional props
class ButtonProps(TypedDict, total=False):
    onclick: Callable[[], None]  # Event handlers always lowercase
    disabled: bool
    variant: str  # e.g., "primary", "secondary"
    children: Children

# Complex component with nested data
class TodoItemProps(TypedDict):
    todo: "TodoDict"  # Reference to another type
    ontoggle: Callable[[int], None]
    ondelete: Callable[[int], None]
    onedit: Callable[[int, str], None]

class TodoDict(TypedDict):
    id: int
    title: str
    completed: bool

# Type-safe components
@component
def Button(ctx: Context, props: ButtonProps):
    for props in ctx:
        yield h.button(
            onclick=props.get("onclick"),
            disabled=props.get("disabled", False),
            className=f"btn btn-{props.get('variant', 'primary')}"
        )[props.get("children", "Click me")]

@component
def TodoItem(ctx: Context, props: TodoItemProps):
    for props in ctx:
        todo = props["todo"]
        yield h.li[
            h.input(
                type="checkbox",
                checked=todo["completed"],
                onchange=lambda: props["ontoggle"](todo["id"])
            ),
            h.span[todo["title"]],
            h.button(onclick=lambda: props["ondelete"](todo["id"]))["×"]
        ]
```

### Core Crank.py Types

```python
from crank import Element, Context, Props, Children

# Basic types
Props = Dict[str, Any]  # General props dict
Children = Union[str, Element, List["Children"]]  # Nested content

# Generic Context typing (similar to Crank.js)
Context[PropsType, ResultType]  # T = props type, TResult = element result type

# Context with full method typing
def my_component(ctx: Context[MyProps, Element], props: MyProps):
    # All context methods are typed
    ctx.refresh()  # () -> None
    ctx.schedule(callback)  # (Callable) -> None
    ctx.after(callback)    # (Callable) -> None
    ctx.cleanup(callback)  # (Callable) -> None

    # Iterator protocol for generator components
    for props in ctx:  # Each iteration gets updated props (typed as MyProps)
        yield h.div["Updated with new props"]

    # Direct props access with typing
    current_props: MyProps = ctx.props
```

### Component Patterns & Generics

Create reusable, typed component patterns:

```python
from typing import TypedDict, Generic, TypeVar, List

# Generic list component
T = TypeVar('T')

class ListProps(TypedDict, Generic[T]):
    items: List[T]
    render_item: Callable[[T], Element]
    onselect: Callable[[T], None]

@component
def GenericList(ctx: Context[ListProps[T], Element], props: ListProps[T]):
    for props in ctx:  # props is properly typed as ListProps[T]
        yield h.ul[
            [h.li(
                key=i,
                onclick=lambda item=item: props["onselect"](item)
            )[props["render_item"](item)]
             for i, item in enumerate(props["items"])]
        ]

# Usage with type inference
user_list_props: ListProps[User] = {
    "items": users,
    "render_item": lambda user: h.span[user.name],
    "onselect": handle_user_select
}
```

### Advanced Props Patterns

```python
# Union types for polymorphic components
from typing import Union, Literal

class IconButtonProps(TypedDict, total=False):
    variant: Literal["icon", "text", "both"]
    icon: str
    onclick: Callable[[], None]
    children: Children

class FormFieldProps(TypedDict):
    name: str
    value: Union[str, int, bool]
    onchange: Callable[[Union[str, int, bool]], None]
    # Discriminated union based on field type
    field_type: Literal["text", "number", "checkbox"]

@component
def FormField(ctx: Context, props: FormFieldProps):
    for props in ctx:
        field_type = props["field_type"]

        if field_type == "checkbox":
            yield h.input(
                type="checkbox",
                name=props["name"],
                checked=bool(props["value"]),
                onchange=lambda e: props["onchange"](e.target.checked)
            )
        elif field_type == "number":
            yield h.input(
                type="number",
                name=props["name"],
                value=str(props["value"]),
                onchange=lambda e: props["onchange"](int(e.target.value))
            )
        else:  # text
            yield h.input(
                type="text",
                name=props["name"],
                value=str(props["value"]),
                onchange=lambda e: props["onchange"](e.target.value)
            )
```

### Type Checking Setup

Install and configure Pyright for comprehensive type checking:

```bash
# Install type checker
uv add --dev pyright

# Run type checking
uv run pyright crank/

# Run all checks (lint + types)
make check
```

**pyproject.toml configuration:**
```toml
[tool.pyright]
pythonVersion = "3.8"
typeCheckingMode = "basic"
reportUnknownMemberType = false  # For JS interop
reportMissingImports = false     # Ignore PyScript imports
include = ["crank"]
exclude = ["tests", "examples"]
```

### Props as Dictionaries

Components receive props as Python dictionaries (converted from JS objects):

```python
@component
def MyComponent(ctx: Context, props: Props):
    for props in ctx:
        # Access props using dict syntax
        title = props["title"]
        onclick = props["onclick"]

        yield h.div[
            h.h1[title],
            h.button(onclick=onclick)["Click me"]
        ]
```

### Event Props Convention

Use lowercase for all event and callback props:

- `onclick` not `onClick`
- `onchange` not `onChange`
- `ontoggle` not `onToggle`

This matches HTML attribute conventions and provides consistency.

## Testing

Run the test suite:

```bash
# Install dependencies
pip install pytest playwright

# Run tests
pytest tests/
```

## Development

```bash
# Clone the repository
git clone https://github.com/bikeshaving/crankpy.git crankpy
cd crankpy

# Install in development mode
pip install -e ".[dev]"

# Run examples
python -m http.server 8000
# Visit http://localhost:8000/examples/
```

## Why Crank.py?

### Python Web Development, Modernized

Traditional Python web frameworks use templates and server-side rendering. Crank.py brings component-based architecture to Python:

- **Reusable Components** - Build UIs from composable pieces
- **Dynamic Updates** - Explicit re-rendering with ctx.refresh()
- **Generator-Powered** - Natural state management with Python generators
- **Browser-Native** - Run Python directly in the browser via PyScript

### Perfect for:

- **PyScript Applications** - Rich client-side Python apps
- **Educational Projects** - Teaching web development with Python
- **Prototyping** - Rapid UI development without JavaScript
- **Data Visualization** - Interactive Python data apps in the browser

## Advanced Features

### Refs - Direct DOM Access

Use `ref` callbacks to access rendered DOM elements directly:

```python
@component
def VideoPlayer(ctx):
    video_element = None

    def set_video_ref(el):
        nonlocal video_element
        video_element = el

    @ctx.refresh
    def play():
        if video_element:
            video_element.play()

    @ctx.refresh
    def pause():
        if video_element:
            video_element.pause()

    for _ in ctx:
        yield h.div[
            h.video(
                src="/path/to/video.mp4",
                ref=set_video_ref
            ),
            h.button(onclick=play)["Play"],
            h.button(onclick=pause)["Pause"]
        ]
```

**Ref Patterns:**
- Refs fire once when elements are first rendered
- Don't work on fragments - use on host elements only
- For components, explicitly pass `ref` prop to child elements, or call it yourself
- Useful for focus management, DOM measurements, third-party integrations

```python
@component
def AutoFocusInput(ctx, props):
    for props in ctx:
        yield h.input(
            type="text",
            placeholder=props.get("placeholder", ""),
            ref=lambda el: el.focus()  # Auto-focus when rendered
        )
```

### Fragments - Multiple Children Without Wrappers

Fragments let you return multiple elements without extra DOM nodes:

```python
# Simple fragments - just use Python lists!
@component
def UserInfo(ctx, props):
    user = props["user"]
    for props in ctx:
        yield [
            h.h2[user["name"]],
            h.p[user["bio"]],
            h.span[f"Joined: {user['joined']}"]
        ]

# Fragment with props (for keys, etc.)
@component
def ConditionalContent(ctx, props):
    show_content = props.get("show", False)
    for props in ctx:
        if show_content:
            yield h("", key="content-fragment")[
                h.div["Content block 1"],
                h.div["Content block 2"]
            ]
        else:
            yield h("", key="empty-fragment")["No content"]

# Mixed fragments in JSX-like syntax
@component
def Navigation(ctx):
    for _ in ctx:
        yield h.nav[
            h.div(className="logo")["MyApp"],
            [  # Fragment for nav items
                h.a(href="/home")["Home"],
                h.a(href="/about")["About"],
                h.a(href="/contact")["Contact"]
            ],
            h.button["Menu"]
        ]
```

### Key Prop - List Reconciliation

Keys help Crank identify which elements have changed in lists:

```python
@component
def TodoList(ctx, props):
    for props in ctx:
        todos = props["todos"]
        yield h.ul[
            [h.li(key=todo["id"])[
                h.input(
                    type="checkbox",
                    checked=todo["completed"],
                    onchange=lambda todo_id=todo["id"]: props["onToggle"](todo_id)
                ),
                h.span[todo["text"]],
                h.button(onclick=lambda todo_id=todo["id"]: props["onDelete"](todo_id))["×"]
            ] for todo in todos]
        ]

# Without keys - elements match by position (can cause issues)
# With keys - elements match by identity (preserves state correctly)

@component
def DynamicList(ctx):
    items = ["A", "B", "C", "D"]
    reversed_items = False

    @ctx.refresh
    def toggle_order():
        nonlocal reversed_items
        reversed_items = not reversed_items

    for _ in ctx:
        current_items = items[::-1] if reversed_items else items
        yield h.div[
            h.button(onclick=toggle_order)["Toggle Order"],
            h.ul[
                [h.li(key=item)[
                    f"Item {item} (with preserved state)"
                ] for item in current_items]
            ]
        ]
```

**Key Guidelines:**
- Use stable, unique values (IDs, not array indices)
- Keys only need to be unique among siblings
- Can be strings, numbers, or any JavaScript value
- Essential for stateful components and form inputs

### Copy Prop - Prevent Re-rendering

The `copy` prop prevents elements from re-rendering for performance optimization:

```python
@component
def ExpensiveList(ctx, props):
    for props in ctx:
        items = props["items"]
        yield h.ul[
            [h.li(
                key=item["id"],
                copy=not item.get("hasChanged", True)  # Skip render if unchanged
            )[
                h(ExpensiveComponent, data=item["data"])
            ] for item in items]
        ]

# Copy with string selectors (Crank 0.7+)
@component
def SmartForm():
    return h.form[
        # Copy all props except value (keeps input uncontrolled)
        h.input(
            copy="!value",
            type="text",
            placeholder="Enter text...",
            name="username"
            value=props["value"]
        ),

        # Copy only specific props
        h.div(
            copy="class id",
            className="form-section",
            id="user-info",
            data_updated=props.get("timestamp")
        )[
            h.label["Username"]
        ],

        # Copy children from previous render
        h.div(copy="children", className="dynamic")[
            # Children preserved from last render
            props["children"]
        ]
    ]
```

**Copy Prop Syntax:**
- `copy=True` - Prevent all re-rendering
- `copy=False` - Normal re-rendering (default)
- `copy="!value"` - Copy all props except `value`
- `copy="class children"` - Copy only `class` and `children`
- Cannot mix `!` and regular syntax

### Special Components

#### Raw - Inject HTML/DOM Nodes

```python
@component
def MarkdownRenderer(ctx, props):
    for props in ctx:
        # Process markdown to HTML
        markdown_text = props["markdown"]
        html_content = markdown_to_html(markdown_text)  # Your markdown processor

        yield h.div[
            h(Raw, value=html_content)
        ]

# Insert actual DOM nodes
@component
def CanvasChart(ctx, props):
    for props in ctx:
        # Create chart canvas with external library
        canvas_node = create_chart(props["data"])

        yield h.div[
            h.h3["Sales Chart"],
            h(Raw, value=canvas_node)
        ]
```

#### Portal - Render Into Different DOM Location

```python
from js import document

@component
def Modal(ctx, props):
    for props in ctx:
        is_open = props.get("isOpen", False)
        if is_open:
            # Render modal into document body instead of current location
            modal_root = document.getElementById("modal-root")
            yield h(Portal, root=modal_root)[
                h.div(className="modal-backdrop", onclick=props["onClose"])[
                    h.div(className="modal-content", onclick=lambda e: e.stopPropagation())[
                        h.div(className="modal-header")[
                            h.h2[props["title"]],
                            h.button(onclick=props["onClose"])["×"]
                        ],
                        h.div(className="modal-body")[
                            props.get("children", [])
                        ]
                    ]
                ]
            ]

# Usage
@component
def App(ctx):
    show_modal = False

    @ctx.refresh
    def open_modal():
        nonlocal show_modal
        show_modal = True

    @ctx.refresh
    def close_modal():
        nonlocal show_modal
        show_modal = False

    for _ in ctx:
        yield h.div[
            h.h1["My App"],
            h.button(onclick=open_modal)["Open Modal"],
            h(Modal,
                isOpen=show_modal,
                title="Example Modal",
                onClose=close_modal
            )["Modal content here!"]
        ]
```

#### Text - Explicit Text Node Control

```python
@component
def TextManipulator(ctx):
    text_node = None

    def set_text_ref(text):
        nonlocal text_node
        text_node = text

    @ctx.refresh
    def update_text():
        if text_node:
            text_node.data = "Updated directly!"

    for _ in ctx:
        yield h.div[
            h(Text, value="Original text", ref=set_text_ref),
            h.button(onclick=update_text)["Update Text"]
        ]
```

#### Copy - Prevent Subtree Re-rendering

```python
@component
def MemoizedComponent(ctx, props):
    last_props = None

    for props in ctx:
        if last_props and props_equal(props, last_props):
            # Don't re-render if props haven't changed
            yield h(Copy)
        else:
            yield h(ExpensiveComponent, **props)
        last_props = props

def props_equal(a, b):
    """Shallow comparison of props"""
    return (
        set(a.keys()) == set(b.keys()) and
        all(a[key] == b[key] for key in a.keys())
    )

# Higher-order memo component
def memo(Component):
    @component
    def MemoWrapper(ctx, props):
        last_props = None
        yield h(Component, **props)

        for props in ctx:
            if last_props and props_equal(props, last_props):
                yield h(Copy)
            else:
                yield h(Component, **props)
            last_props = props

    return MemoWrapper

# Usage
@memo
@component
def ExpensiveItem(ctx, props):
    for props in ctx:
        # Expensive computation here
        yield h.div[f"Processed: {props['data']}"]
```

### Performance Patterns

```python
# Combining keys, copy, and memoization
@component
def OptimizedList(ctx, props):
    for props in ctx:
        items = props["items"]
        yield h.ul[
            [h.li(
                key=item["id"],
                copy=not item.get("_dirty", False)  # Skip clean items
            )[
                h(MemoizedItem,
                    data=item["data"],
                    onUpdate=props["onItemUpdate"]
                )
            ] for item in items]
        ]

# Selective prop copying for performance
@component
def SmartComponent(ctx, props):
    for props in ctx:
        yield h.div[
            # Only re-renders children, does not touch class style
            h.div(
                className=props["className"],
                style=props["style"],
                copy="class style"
            )[
                props["dynamicContent"]
            ],

            # Expensive chart that rarely changes
            h.div(copy=not props.get("chartDataChanged", False))[
                h(ChartComponent, data=props["chartData"])
            ]
        ]
```

## Learn More

- **[Crank.js Documentation](https://crank.js.org/)** - The underlying framework
- **[PyScript Guide](https://pyscript.net/)** - Running Python in browsers
- **[Examples](examples/)** - See Crank.py in action

## Contributing

Contributions welcome! Please read our [Contributing Guide](CONTRIBUTING.md) first.

## License
MIT © 2025
