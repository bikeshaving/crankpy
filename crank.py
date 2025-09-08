"""
Crank.py - Lightweight Python wrapper for Crank JavaScript framework
"""

from typing import Callable
import inspect
from js import Symbol, fetch

# Import Crank core
async def _import_crank():
    response = await fetch('https://cdn.jsdelivr.net/npm/@b9g/crank@latest/crank.js')
    code = await response.text()
    return js.eval(f"(() => {{ {code}; return this; }})()")

_crank = await _import_crank()

# Re-export Crank classes directly
Element = _crank.Element
Context = _crank.Context
createElement = _crank.createElement
Fragment = _crank.Fragment
Portal = Symbol.for_("crank.Portal") 
Copy = Symbol.for_("crank.Copy")
Text = Symbol.for_("crank.Text")
Raw = Symbol.for_("crank.Raw")

# Component decorator  
def component(func: Callable) -> Callable:
    """Universal component decorator for any function type"""
    sig = inspect.signature(func)
    if len(sig.parameters) != 1:
        raise ValueError(f"Component should only accept ctx parameter")
    return func

# Magic h element
class ElementBuilder:
    def __init__(self, tag):
        self.tag = tag
        self.props = {}
    
    def __call__(self, **props):
        converted_props = {}
        for key, value in props.items():
            converted_props[key.replace('_', '-')] = value
        
        new_builder = ElementBuilder(self.tag)
        new_builder.props = converted_props
        return new_builder
    
    def __getitem__(self, children):
        if not isinstance(children, (list, tuple)):
            children = [children]
        return createElement(self.tag, self.props, *children)

class MagicH:
    def __getattr__(self, name: str):
        if name[0].isupper():
            # Component lookup in caller's scope
            frame = inspect.currentframe().f_back
            locals_dict = frame.f_locals
            globals_dict = frame.f_globals
            
            if name in locals_dict:
                return ElementBuilder(locals_dict[name])
            if name in globals_dict:
                return ElementBuilder(globals_dict[name])
            
            raise NameError(f"Component '{name}' not found in scope")
        else:
            # HTML element
            return ElementBuilder(name)
    
    def __getitem__(self, children):
        if not isinstance(children, (list, tuple)):
            children = [children]
        return createElement(Fragment, None, *children)
    
    def __call__(self, *children):
        return createElement(Fragment, None, *children)

# Magic h instance
h = MagicH()

# Exports
__all__ = ['Element', 'Context', 'createElement', 'component', 'Fragment', 'Portal', 'Copy', 'Text', 'Raw', 'h']