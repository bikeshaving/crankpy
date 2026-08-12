"""Crank.py DOM module - the Crank DOM renderer with the Python tree transform."""

from pyscript.js_modules import crank_dom

from . import Renderer

DOMRenderer = crank_dom.DOMRenderer
renderer = Renderer(crank_dom.renderer)

__all__ = ["DOMRenderer", "renderer"]
