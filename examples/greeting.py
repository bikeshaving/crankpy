"""
Greeting Component - Simple component that displays a greeting message
"""

from crank import h, component
from crank.dom import renderer
from js import document

@component
def Greeting(ctx):
    # Simple generator component
    for _ in ctx:
        name = "World"  # Keep it simple for now
        yield h.div[f"Hello {name}!"]

# Render the component
renderer.render(h(Greeting), document.body)