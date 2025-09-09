"""
Crank.py - Lightweight Python wrapper for Crank JavaScript framework
"""

from typing import Callable
import inspect
from js import Symbol, Object
from pyscript.ffi import to_js, create_proxy

# Import Crank core from PyScript's js_modules
from pyscript.js_modules import crank_core as _crank

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
    
    def wrapper(props, ctx):
        """Wrapper that converts Crank's (props, ctx) calling convention to just (ctx)"""
        return func(ctx)
    
    # Proxy the wrapper function for Crank to call
    return create_proxy(wrapper)

# Magic h element
class ElementBuilder:
    def __init__(self, tag):
        self.tag = tag
        self.props = {}
    
    def __call__(self, **props):
        if not props:
            # h.div() with no props - create element with no children
            return createElement(self.tag, to_js({}), [])
        
        converted_props = {}
        for key, value in props.items():
            # Convert Python functions to JS proxies for event handlers
            if callable(value):
                converted_props[key.replace('_', '-')] = create_proxy(value)
            else:
                converted_props[key.replace('_', '-')] = value
        
        new_builder = ElementBuilder(self.tag)
        new_builder.props = converted_props
        return new_builder
    
    def __getitem__(self, children):
        if not isinstance(children, (list, tuple)):
            children = [children]
        # Convert Python dict props to JavaScript object
        # PyScript's to_js should handle this properly
        js_props = to_js(self.props) if self.props else None
        return createElement(self.tag, js_props, *children)

class ComponentBuilder:
    def __init__(self, component_func):
        self.component_func = component_func
        self.props = {}
    
    def __call__(self, **props):
        # Store props for later use
        new_builder = ComponentBuilder(self.component_func)
        new_builder.props = props
        return new_builder
    
    def __getitem__(self, children):
        # Convert props to JS object and create element
        js_props = to_js(self.props) if self.props else None
        
        # For components, children go in props, not as separate arguments
        if children:
            if not isinstance(children, (list, tuple)):
                children = [children]
            # Add children to props
            props_dict = dict(self.props) if self.props else {}
            props_dict['children'] = children
            js_props = to_js(props_dict)
        
        # Component function needs FFI conversion!
        component_proxy = create_proxy(self.component_func)
        return createElement(component_proxy, js_props)

class MagicH:
    def __getattr__(self, name: str):
        if name[0].isupper():
            # Component lookup in caller's scope
            frame = inspect.currentframe().f_back
            locals_dict = frame.f_locals
            globals_dict = frame.f_globals
            
            component_func = None
            if name in locals_dict:
                component_func = locals_dict[name]
            elif name in globals_dict:
                component_func = globals_dict[name]
            else:
                raise NameError(f"Component '{name}' not found in scope")
            
            # For components, create a ComponentBuilder that calls createElement
            return ComponentBuilder(component_func)
        else:
            # HTML element
            return ElementBuilder(name)
    
    def __getitem__(self, children):
        if not isinstance(children, (list, tuple)):
            children = [children]
        return createElement(Fragment, None, *children)
    
    def __call__(self, *children):
        return createElement(Fragment, None, *children)

# Simple hyperscript h function (magic moved to j)
def h(tag, props=None, *children):
    """Simple hyperscript function: h('div', {props}, children...)"""
    if props is None:
        props = {}
    
    # Convert props to JS object
    js_props = to_js(props) if props else None
    
    # If tag is a string (HTML element)
    if isinstance(tag, str):
        return createElement(tag, js_props, *children)
    
    # If tag is a component function, use it directly (assume already proxied by @component)
    elif callable(tag):
        return createElement(tag, js_props, *children)
    
    else:
        raise ValueError(f"Invalid tag type: {type(tag)}")

# Magic h instance (renamed to j to avoid confusion)
j = MagicH()

# Exports
__all__ = ['Element', 'Context', 'createElement', 'component', 'Fragment', 'Portal', 'Copy', 'Text', 'Raw', 'h']