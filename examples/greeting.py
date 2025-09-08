"""
Greeting Component - Python translation of examples/greeting.js

Simple component that displays a greeting message.
"""

from crank import h, component
from crank.dom import renderer
from js import document

@component
def Greeting(ctx):
    for _ in ctx:
        name = ctx.props.name or "World"
        yield h.div[f"Hello {name}"]

# Render the component
async def main():
    await renderer.render(h.Greeting(name="Crank"), document.body)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())