# Introducing Crank.py: Component-Based Web Development for Python

Python web development has long been dominated by template-based frameworks like Django and Flask. While these tools are powerful, they often lead us away from the component-based thinking that has revolutionized frontend development. What if we could bring the elegance of React's component model to Python, with a syntax that feels natural and Pythonic?

Enter **Crank.py** - a Python wrapper for the innovative [Crank.js framework](https://crank.js.org/) that brings generator-based components and beautiful hyperscript syntax to Python web development.

## The Magic of HyperScript Syntax

At the heart of Crank.py is an elegant syntax we’ve called "MagicH" or "Phyperscript (Python Hyperscript)". Instead of wrestling with template languages or verbose HTML construction, you write components using intuitive Python expressions:

```python
from crank import h, component
from crank.dom import renderer

@component
def Greeting(ctx, props):
    for props in ctx:  # Props can be reassigned on each render!
        name = props.name or "World"
        yield h.div(className="greeting")[
            h.h1[f"Hello, {name}!"],
            h.p["Welcome to Crank.py"]
        ]

# Render to the DOM
renderer.render(h(Greeting, name="Alice"), document.body)
```

Notice the beautiful bracket syntax: `h.div["content"]` for simple children, and `h.div(className="test")["content"]` when you need props. It's JSX-like expressiveness without the build step complexity.

## Generator-Powered Components

Crank.py's secret weapon is Python generators. Unlike traditional frameworks where components are stateless functions or classes with complex lifecycle methods, Crank components are generators that can maintain state naturally:

```python
@component
def Counter(ctx):
    count = 0  # State lives in the generator scope
    @ctx.refresh
    def increment():
        nonlocal count
        count += 1

    for _ in ctx: # Generator loop handles updates
        yield h.div(className="counter")[
            h.p[f"Count: {count}"],
            h.button(onClick=increment)["Increment"]
        ]
```

No `useState` hooks, no `componentDidMount` lifecycle methods - just natural Python generator functions that maintain state between renders.

## Props Reassignment: A Unique Feature

One of Crank's most innovative features is props reassignment. Components can receive new props on each render cycle:

```python
@component
def UserProfile(ctx, props):
    for props in ctx:  # New props on each iteration
        user_id = props.user_id
        # Fetch user data when props change
        user = fetch_user(user_id)

        yield h.div(className="profile")[
            h.img(src=user.avatar),
            h.h2[user.name],
            h.p[user.bio]
        ]
```

This eliminates the need for complex effect systems or prop comparison logic. When parent components pass new props, your component automatically receives them in the next iteration of the `for` loop.

## Snake Case to Kebab Case: Pythonic Props

Python developers love snake_case, but HTML attributes use kebab-case. Crank.py handles this conversion automatically:

```python
h.div(
    data_test_id="button",     # Becomes data-test-id
    aria_hidden="true"         # Becomes aria-hidden
)["Content"]
```

Write natural Python, get correct HTML attributes.

## No Dynamic Lookups: FFI-Friendly Architecture

Unlike other Python web frameworks that rely on string-based template lookups, Crank.py uses direct function references:

```python
# Components are just functions - no string lookups
h(MyComponent, props)    # ✅ Direct reference
h.div["content"]         # ✅ Built-in HTML elements

# Not:
h.MyComponent(props)     # ❌ No dynamic lookup
```

This approach eliminates Foreign Function Interface (FFI) issues when running in environments like PyScript or Pyodide, making Crank.py perfect for client-side Python web development.

## Three Component Signatures

Crank.py supports three component signatures to match different use cases:

```python
# 1. Static components (no state or props)
@component
def Header():
    return h.header[h.h1["My App"]]

# 2. Context-only components (internal state)
@component
def Timer(ctx):
    start_time = time.time()
    for _ in ctx:
        elapsed = time.time() - start_time
        yield h.div[f"Time: {elapsed:.1f}s"]

# 3. Full components (props + state)
@component
def TodoItem(ctx, props):
    for props in ctx:
        todo = props.todo
        yield h.li(
            className="completed" if todo.done else ""
        )[
            h.input(type="checkbox", checked=todo.done),
            h.span[todo.text]
        ]
```

## Fragments: Just Use Lists!

Need to group elements without extra DOM nodes? Just use Python lists - Crank.js automatically wraps them in fragments:

```python
# Simple fragments
["Item 1", "Item 2"]
[h.span["Hello"], h.span["World"]]

# In context  
h.div[
    h.h1["Title"],
    [h.p["Paragraph 1"], h.p["Paragraph 2"]],  # Fragment
    h.footer["Footer"]
]
```

## Why Python Needs This

Python web development has been stuck in the template era while frontend development has moved to components. Crank.py bridges this gap by bringing:

1. **Component-based architecture** - Components are Python functions, including async `async def :`,
2. **Beautiful syntax** - JSX-like expressiveness with Python elegance
3. **Generator-powered state** - Natural Python `for props of ctx: yield h.div["hello world"]`, state management with nonlocal
3. **Props reassignment** - Dynamic updates without complex effect systems
5. **No build step** - Pure Python, runs anywhere Python runs

## Getting Started

Install Crank.py and start building:

```bash
pip install crankpy
```

```python
from crank import h, component
from crank.dom import renderer
from js import document

@component
def App(ctx):
    for _ in ctx:
        yield h.div[
            h.h1["Welcome to Crank.py!"],
            h.p["The future of Python web development"]
        ]

renderer.render(h(App), document.body)
```

## The Future is Pythonic

Web development doesn't have to be a choice between Python on the backend and JavaScript on the frontend. With Crank.py, you can build entire web applications in Python, using familiar patterns and elegant syntax.

Whether you're building PyScript applications, experimenting with client-side Python, or just want a more component-driven approach to Python web development, Crank.py offers a fresh perspective on what Python web development can be.

Ready to try a new approach? [Check out Crank.py on GitHub](https://github.com/bikeshaving/crankpy) and start building the future of Python web development today.

---

*Crank.py is built on top of the excellent [Crank.js framework](https://crank.js.org/) by the Bikeshedding team. Special thanks to the Crank.js maintainers for creating such an innovative foundation.*
