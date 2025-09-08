"""
Crank.py HTML module

Direct import of Crank's HTML module from JavaScript.
Exposes the exact same API: Renderer class and renderer instance.
"""

from js import fetch
import js

# Import Crank's HTML module directly
async def _import_html():
    response = await fetch('https://cdn.jsdelivr.net/npm/@b9g/crank@latest/html.js')
    html_code = await response.text()
    return js.eval(f"(async () => {{ {html_code}; return this; }})()")

# Get the module
_html_module = await _import_html()

# Re-export exact Crank API
Renderer = _html_module.Renderer
renderer = _html_module.renderer

# Expose adapter (can be overwritten)
adapter = _html_module.adapter

__all__ = ['Renderer', 'renderer', 'adapter']