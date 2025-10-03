"""
Greeting Component - Simple component that displays a greeting message
"""

from crank import h, component
from crank.dom import renderer
from js import document

@component
def Greeting(ctx):
    name = "World"
    for _ in ctx:
        yield [
            h.div[f"Hellooooo {name}!"],
            h.span(data_data="number"),
            h.span(data_data="number")["hello"],
        ]

# Render the component
renderer.render(h(Greeting), document.body)
