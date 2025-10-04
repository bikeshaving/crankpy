"""
Greeting Component - Simple component that displays a greeting message
"""

from js import document

from crank import component, h
from crank.dom import renderer


@component
def Greeting():
    return h.div["Hello, Crank.py!"]

# Render the component
renderer.render(h(Greeting), document.body)
