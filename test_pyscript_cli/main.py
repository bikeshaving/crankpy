"""
Test script to demonstrate Crankpy compatibility with PyScript CLI
"""

from pyscript.js_modules import crank_core
from crank import h, component
from crank.dom import renderer
from js import document

@component
def Greeting(ctx):
    for _ in ctx:
        yield h.div["Hello from Crankpy via PyScript CLI! ⚙️"]

@component
def Counter(ctx):
    count = 0
    
    @ctx.refresh
    def increment():
        nonlocal count
        count += 1
    
    @ctx.refresh  
    def decrement():
        nonlocal count
        count -= 1
    
    for _ in ctx:
        yield h.div[
            h.h2[f"Count: {count}"],
            h.button(onClick=increment)["+"],
            h.button(onClick=decrement)["-"]
        ]

@component
def App(ctx):
    for _ in ctx:
        yield h.div[
            h.h1["PyScript CLI + Crankpy Test"],
            h(Greeting),
            h.hr,
            h(Counter)
        ]

# Render the app
renderer.render(h(App), document.body)