"""Crank.py HTML module - the Crank string renderer with the Python tree transform."""

from pyscript.js_modules import crank_html

from . import Renderer

HTMLRenderer = crank_html.HTMLRenderer
renderer = Renderer(crank_html.renderer)

__all__ = ["HTMLRenderer", "renderer"]
