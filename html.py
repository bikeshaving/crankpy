"""
Crank.py HTML module - Direct import of Crank's HTML renderer
"""

from js import fetch

async def _import_html():
    response = await fetch('https://cdn.jsdelivr.net/npm/@b9g/crank@latest/html.js')
    code = await response.text()
    return js.eval(f"(() => {{ {code}; return this; }})()")

_html = await _import_html()

Renderer = _html.Renderer
renderer = _html.renderer

__all__ = ['Renderer', 'renderer']