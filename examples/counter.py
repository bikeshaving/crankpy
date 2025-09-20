"""
Counter Component - Simple working example with generator state management
"""

from crank import h, component
from crank.dom import renderer
from js import document

@component
def Counter(ctx):
    # State stored in generator scope
    count = 0
    
    def increment(event):
        nonlocal count
        count += 1
        ctx.refresh()
    
    def decrement(event):
        nonlocal count  
        count -= 1
        ctx.refresh()
        
    def reset(event):
        nonlocal count
        count = 0
        ctx.refresh()
    
    # Generator loop - state persists in this scope
    for _ in ctx:
        yield h.div(
            h.h2("Counter Example"),
            h.div(
                h.span("Count: ", className="count-label"),
                h.span(str(count), className="count-value"),
                className="counter-display"
            ),
            h.div(
                h.button("-", className="btn-decrement", onClick=decrement),
                h.button("Reset", className="btn-reset", onClick=reset), 
                h.button("+", className="btn-increment", onClick=increment),
                className="counter-controls"
            ),
            className="counter-container"
        )

# Render the component
renderer.render(h(Counter), document.body)