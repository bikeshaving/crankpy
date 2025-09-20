"""
Props Example - Shows different ways to receive and reassign props in components
"""

from crank import h, component
from crank.dom import renderer
from js import document

# Method 1: Context only (backward compatibility)
@component
def OldStyleComponent(ctx):
    # Access props via ctx.props
    name = ctx.props.name if ctx.props and ctx.props.name else "World"
    
    for _ in ctx:
        yield h.div(className="old-style")[
            f"Hello, {name}!"
        ]

# Method 2: Context and props
@component  
def PropsAndContextComponent(ctx, props):
    # Direct access to props object
    for props in ctx:  # Props reassignment in for loop!
        name = props.name if props and props.name else "World"
        count = props.count if props and props.count else 0
        
        yield h.div(className="props-ctx")[
            h.p[f"Hello, {name}!"],
            h.p[f"Count: {count}"]
        ]

# Method 3: Manual destructuring in for loop
@component
def ManualDestructuringComponent(ctx, props):
    # Manually extract props in the for loop
    for props in ctx:
        # Extract specific props each time
        name = props.name if props and hasattr(props, 'name') else "Anonymous"
        count = props.count if props and hasattr(props, 'count') else 0
        
        yield h.div(className="destructured")[
            h.p[f"Name: {name}"],
            h.p[f"Count: {count}"]
        ]

# Container component that shows all styles
@component
def PropsExample(ctx):
    counter = 0
    
    @ctx.refresh
    def increment():
        nonlocal counter
        counter += 1
    
    for _ in ctx:
        yield h.div(className="props-example")[
            h.h2["Props Example"],
            
            h.h3["Method 1 - Context only:"],
            h(OldStyleComponent, name="Alice"),
            
            h.h3["Method 2 - Context and props:"],
            h(PropsAndContextComponent, name="Bob", count=counter),
            
            h.h3["Method 3 - Manual destructuring:"],
            h(ManualDestructuringComponent, name="Charlie", count=counter),
            
            h.button(onClick=increment)["Increment Count"],
            
            h.hr(),
            h.p["Click the button to see props reassignment in action!"]
        ]

# Render the example
if __name__ == "__main__":
    renderer.render(h(PropsExample), document.body)