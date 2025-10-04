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

### PyScript (Pyodide)

```html
<py-config type="toml">
packages = ["crankpy"]

[js_modules.main]
"https://cdn.jsdelivr.net/npm/@b9g/crank@latest/crank.js" = "crank_core"
"https://cdn.jsdelivr.net/npm/@b9g/crank@latest/dom.js" = "crank_dom"
</py-config>
```

### PyScript (MicroPython)

```html
<py-config type="toml">
type = "micropython"
packages = ["crankpy"]

[js_modules.main]
"https://cdn.jsdelivr.net/npm/@b9g/crank@latest/crank.js" = "crank_core"
"https://cdn.jsdelivr.net/npm/@b9g/crank@latest/dom.js" = "crank_dom"
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
def UserProfile(ctx, props):
    for props in ctx:  # Props automatically update!
        user_id = props.user_id
        user = fetch_user(user_id)  # Fetches when props change

        yield h.div[
            h.img(src=user.avatar),
            h.h2[user.name],
            h.p[user.bio]
        ]

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

# With properties
h.input(type="text", value=text)
h.div(className="my-class")["Content"]

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
    def before_render():
        # Runs before each render
        pass

    @ctx.after
    def after_render(node):
        # Runs after DOM update
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

Crank.py supports optional TypeScript-style type safety with TypedDict for component props:

```python
from typing import TypedDict, Callable
from crank import component, Context, Props

# Define component prop interface
class ButtonProps(TypedDict, total=False):
    onclick: Callable[[], None]  # lowercase event props
    disabled: bool
    children: str

# Type-safe component (optional - basic Props works too)
@component
def Button(ctx: Context, props: ButtonProps):
    for props in ctx:
        yield h.button(
            onclick=props.get("onclick"),
            disabled=props.get("disabled", False)
        )[props.get("children", "Click me")]

# Usage with autocomplete and validation
h(Button, onclick=lambda: print("clicked"), children="Submit")
```

### Type Checking

Install and run Pyright for type checking:

```bash
# Install type checker
uv add --dev pyright

# Run type checking
uv run pyright crank/
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

## Learn More

- **[Crank.js Documentation](https://crank.js.org/)** - The underlying framework
- **[PyScript Guide](https://pyscript.net/)** - Running Python in browsers
- **[Examples](examples/)** - See Crank.py in action

## Contributing

Contributions welcome! Please read our [Contributing Guide](CONTRIBUTING.md) first.

## License

MIT © 2024
