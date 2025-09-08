# Crank.py Examples

This directory contains Python translations of all the examples from the original [Crank JavaScript repository](https://github.com/bikeshaving/crank/tree/main/examples).

## Examples

### 🚀 **Basic Examples**

- **[greeting.py](greeting.py)** / **[greeting.html](greeting.html)**  
  Simple component with props - perfect first example
  
- **[animated_letters.py](animated_letters.py)** / **[animated_letters.html](animated_letters.html)**  
  Complex animation with lifecycle hooks and keyed elements

- **[wizard.py](wizard.py)** / **[wizard.html](wizard.html)**  
  Multi-step form with event handling and state management

### 🎮 **Interactive Examples**

- **[counter.py](counter.py)** / **[counter.html](counter.html)**  
  Stateful counter with increment/decrement buttons
  
- **[todo_list.py](todo_list.py)** / **[todo_list.html](todo_list.html)**  
  Todo application with add/remove/toggle functionality

### 🎯 **Advanced Examples**

- **[async_data.py](async_data.py)** / **[async_data.html](async_data.html)**  
  Async data fetching and loading states
  
- **[portal_modal.py](portal_modal.py)** / **[portal_modal.html](portal_modal.html)**  
  Modal component using Portal for rendering outside normal flow

## Running the Examples

### In Browser (PyScript)
Simply open any `.html` file in your browser. The examples are self-contained and load Crank.py from the CDN.

### Local Development
```bash
python greeting.py
python animated_letters.py
# etc.
```

### With Crank DOM Renderer
```python
from crank.dom import renderer
from js import document

# Your component here
await renderer.render(h.MyComponent[], document.body)
```

## Key Patterns Demonstrated

### 📝 **Component Definition**
```python
@component
def MyComponent(ctx):
    for _ in ctx:  # Always use _ for iteration
        yield h.div[ctx.props.message]
```

### 🔄 **Stateful Components**
```python
@component  
def Counter(ctx):
    count = 0
    
    def increment():
        nonlocal count
        count += 1
        ctx.refresh()  # Trigger re-render
    
    for _ in ctx:
        yield h.div[
            h.span[f'Count: {count}'],
            h.button(onClick=increment)['++']
        ]
```

### 🎨 **JSX-like Syntax**
```python
# HTML elements (lowercase)
h.div(className='container')[
    h.h1['Title'],
    h.p['Content']
]

# Components (uppercase - auto-resolved)
h.UserCard(user_id=123)[
    h.span['Loading...']
]

# Fragments
h[child1, child2, child3]  # or h(child1, child2, child3)
```

### 🔗 **Props Access**
```python
@component
def UserProfile(ctx):
    for _ in ctx:
        # Clean props access with dash↔underscore conversion
        yield h.div(
            className='profile',
            data_user_id=ctx.props.user_id  # Becomes data-user-id  
        )[
            h.h2[ctx.props.name],
            h.img(src=ctx.props.avatar_url)  # Can access avatar-url too
        ]
```

## Comparison with JavaScript Crank

| Feature | JavaScript | Python (Crank.py) |
|---------|------------|-------------------|
| Components | `function* Component()` | `@component def component(ctx):` |
| Props | `{name, age}` destructuring | `ctx.props.name`, `ctx.props.age` |
| Iteration | `for (const props of this)` | `for _ in ctx:` |
| JSX | `<div>Hello</div>` | `h.div['Hello']` |
| Fragments | `<>children</>` | `h[children]` |
| State | `let count = 0` | `count = 0` (with `nonlocal`) |
| Refresh | `this.refresh()` | `ctx.refresh()` |
| Events | `onClick={handler}` | `onClick=handler` |

## File Structure

Each example includes:
- **`.py` file** - Pure Python component definition
- **`.html` file** - PyScript demo with side-by-side comparison
- **Inline documentation** explaining key concepts

## Next Steps

1. **Try the examples** - Open HTML files in your browser
2. **Modify components** - Edit the Python code and see changes
3. **Create new examples** - Use these as templates for your components
4. **Integrate with your app** - Import components into larger applications

Perfect 1:1 mapping between JavaScript Crank and Python! 🎉