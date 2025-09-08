"""
Crank.py DOM module

Direct import of Crank's DOM module from JavaScript.
Exposes the exact same API: Renderer class and renderer instance.
"""

from js import fetch
import js

# Import Crank's DOM module directly
async def _import_dom():
    response = await fetch('https://cdn.jsdelivr.net/npm/@b9g/crank@latest/dom.js')
    dom_code = await response.text()
    return js.eval(f"(async () => {{ {dom_code}; return this; }})()")

# Get the module
_dom_module = await _import_dom()

# Re-export exact Crank API
Renderer = _dom_module.Renderer
renderer = _dom_module.renderer

# Expose adapter (can be overwritten)
adapter = _dom_module.adapter

__all__ = ['Renderer', 'renderer', 'adapter']