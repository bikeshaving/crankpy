"""
Crank.py DOM module - Direct import of Crank's DOM renderer
"""

from pyscript.js_modules import crank_html

# Export the correct names
HTMLRenderer = crank_html.HTMLRenderer
renderer = crank_html.renderer

__all__ = ['HTMLRenderer', 'renderer']
