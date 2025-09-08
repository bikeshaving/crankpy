# Crank.py

A Python wrapper for the Crank JavaScript framework, providing 1:1 mappings between JavaScript async generators and Python's async/await and generator syntax.

## Overview

Crank.py brings Crank's component-based architecture to Python by leveraging:

- **Async/await** for async components (`async function` → `async def`)
- **Generators** for stateful components (`function*` → generator functions)
- **Async generators** for live-updating components (`async function*` → `async def` with `yield`)
- **Type hints** matching Crank's TypeScript interfaces

## Installation

### For PyScript (Browser)

PyScript projects use direct URLs. Import from GitHub releases:

```html
<py-script>
    # From latest GitHub release
    from js import fetch
    response = await fetch('https://github.com/bikeshaving/crank-py/releases/latest/download/crank.py')
    exec(await response.text())
</py-script>
```

Or use jsdelivr CDN for specific versions:
```html
<py-script>
    from js import fetch
    response = await fetch('https://cdn.jsdelivr.net/gh/bikeshaving/crank-py@v0.1.0/crank.py')
    exec(await response.text())
</py-script>
```

### For Local Python Development

```bash
pip install git+https://github.com/bikeshaving/crank-py.git
```

Or clone for development:
```bash
git clone https://github.com/bikeshaving/crank-py.git
cd crank-py
pip install -e ".[dev]"
```

## Quick Start

### Basic Components

```python
from crank import component, h, Context

# Simple component
@component
def greeting(ctx: Context, props):
    name = props.get('name', 'World')
    return f"Hello, {name}!"

# Create elements
element = h('div', {'class': 'app'}, 
    h(greeting, {'name': 'Crank.py'})
)
```

### Async Components

```python
from crank import async_component
import asyncio

@async_component
async def user_profile(ctx: Context, props):
    user_id = props.get('user_id')
    
    # Fetch data asynchronously
    user_data = await fetch_user(user_id)
    
    return h('div', {'class': 'profile'},
        h('h2', None, user_data['name']),
        h('p', None, user_data['email'])
    )
```

### Generator Components (Stateful)

```python
from crank import generator_component

@generator_component
def counter(ctx: Context, props):
    count = 0
    
    # Iterate over props updates
    for updated_props in ctx:
        increment = updated_props.get('increment', 1)
        count += increment
        
        yield h('div', None, f'Count: {count}')
```

### Async Generator Components (Live Updates)

```python
from crank import async_generator_component

@async_generator_component
async def live_data(ctx: Context, props):
    async for updated_props in ctx:
        # Fetch fresh data
        data = await fetch_live_data(updated_props.get('source'))
        
        yield h('div', None, 
            h('h3', None, 'Live Data'),
            h('p', None, data)
        )
```

## API Reference

### Core Types

- `Children`: Union of renderable values (str, int, Element, lists)
- `Props`: Dictionary of component properties
- `Component`: Function that returns Children/Promise/Generator/AsyncGenerator
- `Element`: Represents a component or HTML element
- `Context`: Component lifecycle and state management

### Functions

- `create_element(tag, props, *children)`: Create elements
- `h(tag, props, *children)`: Hyperscript shorthand
- `component`, `async_component`, `generator_component`, `async_generator_component`: Decorators

### Async Utilities

- `lazy(initializer)`: Lazy load components
- `suspense(ctx, props)`: Handle loading states

## Component Patterns

### 1:1 JavaScript Mappings

| JavaScript | Python |
|------------|--------|
| `function Component()` | `@component def component()` |
| `async function Component()` | `@async_component async def component()` |
| `function* Component()` | `@generator_component def component()` |
| `async function* Component()` | `@async_generator_component async def component()` |

### Context Usage

```python
# Provide/consume values
ctx.provide('theme', 'dark')
theme = ctx.consume('theme')

# Schedule async tasks
ctx.schedule(some_async_task())
await ctx.flush_scheduled()
```

## Examples

See `examples.py` for comprehensive examples including:

- Data fetching components
- Real-time updates
- Lazy loading with Suspense
- Higher-order components
- State management patterns

## Testing

```bash
python test_crank.py
# or
pytest test_crank.py
```

## PyScript Compatibility

Designed to work with PyScript for browser execution, providing the same async/generator interoperability as JavaScript Crank components.

## Development

This package mirrors Crank's TypeScript implementation:
- Same component lifecycle
- Same async patterns  
- Same element tree structure
- Compatible with Crank's renderer architecture

## License

MIT - Same as Crank JavaScript framework