"""
Crank.py DOM module - Direct import of Crank's DOM renderer
"""

# Import Crank DOM from PyScript's js_modules
from pyscript.js_modules import crank_dom as _dom

# Export the correct names
DOMRenderer = _dom.DOMRenderer
renderer = _dom.renderer

# Alias for compatibility  
Renderer = DOMRenderer

__all__ = ['DOMRenderer', 'Renderer', 'renderer']