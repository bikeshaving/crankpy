"""
Crank.py HTML module - Direct import of Crank's HTML renderer
"""

import js

# Access Crank HTML from global scope
_html = js.CrankHTML

Renderer = _html.Renderer
renderer = _html.renderer

__all__ = ['Renderer', 'renderer']