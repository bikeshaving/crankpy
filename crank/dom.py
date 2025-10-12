"""
Crank.py DOM module - Direct import of Crank's DOM renderer
"""

from pyscript.js_modules import crank_dom

# Export the correct names
DOMRenderer = crank_dom.DOMRenderer
renderer = crank_dom.renderer

__all__ = ['DOMRenderer', 'renderer']
