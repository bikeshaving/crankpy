# 🔧 Crank.py Examples

This directory contains examples demonstrating all the features of Crank.py. Each example showcases different patterns and capabilities of the framework.

## 🏃 Running Examples

1. **Start a local server:**
   ```bash
   python -m http.server 8000
   ```

2. **Open examples in your browser:**
   - Visit `http://localhost:8000/examples/`
   - Click on any `.html` file to run the example

## 📝 Available Examples

### [`greeting.py`](greeting.py) - Hello World
**Basic component rendering**
- Simple component with no state
- Demonstrates `h.div["content"]` syntax
- Shows basic component rendering

### [`counter.py`](counter.py) - Interactive Counter  
**State management with lifecycle decorators**
- Uses `@ctx.refresh` decorators for clean event handling
- Demonstrates internal component state
- Shows button click handling

### [`animated_letters.py`](animated_letters.py) - Dynamic Animations
**Advanced lifecycle methods and animations**
- Uses `@ctx.after` for DOM manipulation
- Uses `@ctx.cleanup` for resource cleanup
- Demonstrates interval-based updates
- Shows CSS transitions and transforms

### [`props_example.py`](props_example.py) - Props Patterns
**Different component signature styles**
- Shows all three component signatures (0, 1, 2 params)
- Demonstrates props reassignment pattern
- Examples of `ctx.props` vs direct props parameter

### [`showcase.py`](showcase.py) - Complete Demo
**Full-featured application**
- Real-time clock component
- Complete TodoMVC implementation
- Hyperscript syntax showcase
- Demonstrates all major framework features

## 🎯 Key Patterns Demonstrated

### Component Signatures
```python
# Static component (0 params)
@component
def Logo():
    return h.div["🔧 Crank.py"]

# Context only (1 param)
@component
def Timer(ctx):
    for _ in ctx:
        yield h.div[f"Time: {time.time()}"]

# Context + Props (2 params)
@component
def UserCard(ctx, props):
    for props in ctx:  # Props reassignment!
        yield h.div[f"Hello, {props.name}"]
```

### Lifecycle Decorators
```python
@component
def MyComponent(ctx):
    @ctx.refresh
    def handle_click():
        # Automatically triggers re-render
        pass
    
    @ctx.after
    def after_render(node):
        # Runs after DOM update
        node.style.color = "blue"
    
    @ctx.cleanup
    def cleanup():
        # Runs when component unmounts
        pass
```

### Hyperscript Syntax
```python
# HTML elements
h.div["content"]
h.input(type="text", value="hello")
h.div(className="styled")["content"]

# Components
h(MyComponent)
h(MyComponent, prop="value")

# Fragments (just use lists!)
["child1", "child2"]
[h.span["Item 1"], h.span["Item 2"]]
```

### Props Reassignment
```python
@component
def ReactiveComponent(ctx, props):
    for props in ctx:  # 🔥 New props each iteration
        # Component automatically updates when parent changes props
        yield h.div[f"Current value: {props.value}"]
```

## 🏗️ HTML Structure

Each example includes:
- **`.py` file** - The Python component code
- **`.html` file** - PyScript setup and styling
- **Styling** - CSS for visual presentation

## 🧪 Testing Examples

All examples are covered by the test suite in [`../tests/`](../tests/):
- Browser tests using Playwright
- Component pattern validation
- Hyperscript syntax verification
- Lifecycle decorator testing

## 📚 Learning Path

**Recommended order for learning:**

1. **`greeting.py`** - Start here for basic concepts
2. **`counter.py`** - Learn state and event handling  
3. **`props_example.py`** - Understand props patterns
4. **`animated_letters.py`** - Explore advanced lifecycle
5. **`showcase.py`** - See everything together

## 🔗 Related Resources

- **[Main README](../README.md)** - Installation and setup
- **[Crank.js Examples](https://crank.js.org/guides/examples)** - Original JavaScript versions
- **[PyScript Documentation](https://pyscript.net/)** - Browser Python environment

---

**🔧 Built with Crank.py - Python Components with Generators**