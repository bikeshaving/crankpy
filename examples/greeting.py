"""
Greeting Component - Simple component that displays a greeting message
"""

from crank import h, component
from crank.dom import renderer
from js import document

@component
def Greeting():
    return h.div["Hello, Crank.py!"]

# Render the component
renderer.render(h(Greeting), document.body)
