"""
Crank.py DOM module - Direct import of Crank's DOM renderer
"""

from js import fetch

async def _import_dom():
    response = await fetch('https://cdn.jsdelivr.net/npm/@b9g/crank@latest/dom.js')
    code = await response.text()
    return js.eval(f"(() => {{ {code}; return this; }})()")

_dom = await _import_dom()

Renderer = _dom.Renderer
renderer = _dom.renderer

__all__ = ['Renderer', 'renderer']