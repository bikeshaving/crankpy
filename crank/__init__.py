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
# Global cache to hold references to proxies to prevent garbage collection
# _proxy_cache = []

class ElementBuilder:
    def __init__(self, tag):
        self.tag = tag
    
    def __call__(self, *args, **props):
        # Convert props with underscore to hyphen conversion
        converted_props = {}
        for key, value in props.items():
            converted_props[key.replace('_', '-')] = value
        
        # Process props to handle callables (lambdas, functions)  
        processed_props = self._process_props_for_proxies(converted_props) if converted_props else {}
        js_props = to_js(processed_props) if processed_props else None
        
        # Create element with children as positional args
        return createElement(self.tag, js_props, *args)
    
    def __getitem__(self, children):
        if not isinstance(children, (list, tuple)):
            children = [children]
        
        # Create element with just children, no props
        return createElement(self.tag, None, *children)
    
    def _process_props_for_proxies(self, props):
        """Process props to create proxies for callables"""
        processed = {}
        for key, value in props.items():
            if callable(value):
                # Check if it's already a proxy by looking for pyproxy-specific attributes
                if hasattr(value, 'toString') or str(type(value)).startswith("<class 'pyodide.ffi.JsProxy'>"):
                    # Already a proxy
                    processed[key] = value
                else:
                    # Create a proxy for the callable
                    proxy = create_proxy(value)
                    # _proxy_cache.append(proxy)
                    processed[key] = proxy
            elif isinstance(value, dict):
                # Recursively process nested dicts
                processed[key] = self._process_props_for_proxies(value)
            elif isinstance(value, (list, tuple)):
                # Process lists/tuples for callables
                processed_list = []
                for item in value:
                    if callable(item) and not (hasattr(item, 'toString') or str(type(item)).startswith("<class 'pyodide.ffi.JsProxy'>")):
                        proxy = create_proxy(item)
                        # _proxy_cache.append(proxy)
                        processed_list.append(proxy)
                    else:
                        processed_list.append(item)
                processed[key] = processed_list
            else:
                processed[key] = value
        return processed

class ComponentBuilder:
    def __init__(self, component_func):
        self.component_func = component_func
        self.props = {}
    
    def __call__(self, **props):
        # Create the element immediately when called with props
        if not props:
            # No props, no children - create element now
            return self._create_element()
        
        # Store props for later use with children
        new_builder = ComponentBuilder(self.component_func)
        new_builder.props = props
        return new_builder
    
    def __getitem__(self, children):
        # Create element with children
        return self._create_element(children)
    
    def _create_element(self, children=None):
        # Process props to create proxies for callables
        props_to_convert = self.props.copy() if self.props else {}
        
        # Add children to props if provided
        if children:
            if not isinstance(children, (list, tuple)):
                children = [children]
            props_to_convert['children'] = children
        
        # Create proxies for any callable values in props
        if props_to_convert:
            processed_props = self._process_props_for_proxies(props_to_convert)
            js_props = to_js(processed_props)
        else:
            js_props = None
        
        return createElement(self.component_func, js_props)
    
    def _process_props_for_proxies(self, props):
        """Recursively process props to create proxies for callables"""
        processed = {}
        for key, value in props.items():
            if callable(value):
                # Check if it's already a proxy
                if hasattr(value, 'toString') or str(type(value)).startswith("<class 'pyodide.ffi.JsProxy'>"):
                    # Already a proxy
                    processed[key] = value
                else:
                    # Create a proxy for the callable
                    processed[key] = create_proxy(value)
            elif isinstance(value, dict):
                # Recursively process nested dicts
                processed[key] = self._process_props_for_proxies(value)
            elif isinstance(value, (list, tuple)):
                # Process lists/tuples for callables
                processed_list = []
                for item in value:
                    if callable(item) and not (hasattr(item, 'toString') or str(type(item)).startswith("<class 'pyodide.ffi.JsProxy'>")):
                        proxy = create_proxy(item)
                        # _proxy_cache.append(proxy)
                        processed_list.append(proxy)
                    else:
                        processed_list.append(item)
                processed[key] = processed_list
            else:
                processed[key] = value
        return processed


class MagicH:
    def __getattr__(self, name: str):
        if name[0].isupper():
            # Component/Symbol lookup in caller's scope (and module globals)
            frame = inspect.currentframe().f_back
            locals_dict = frame.f_locals
            globals_dict = frame.f_globals
            
            # Also check this module's globals for Crank symbols
            module_globals = globals()
            
            component_func = None
            if name in locals_dict:
                component_func = locals_dict[name]
            elif name in globals_dict:
                component_func = globals_dict[name]
            elif name in module_globals:
                component_func = module_globals[name]
            else:
                raise NameError(f"Component or symbol '{name}' not found in scope")
            
            # For components, create a ComponentBuilder; for symbols, create ElementBuilder
            if callable(component_func):
                return ComponentBuilder(component_func)
            else:
                # Assume it's a Crank symbol
                return ElementBuilder(component_func)
        else:
            # HTML element
            return ElementBuilder(name)
    
    def __getitem__(self, tag_or_component):
        # Dynamic tag/component access: j[variable]
        if isinstance(tag_or_component, str):
            # String tag name
            return ElementBuilder(tag_or_component)
        elif callable(tag_or_component):
            # Component function
            return ComponentBuilder(tag_or_component)
        else:
            raise ValueError(f"j[{tag_or_component}] expects a string tag name or callable component")
    
    def __call__(self, *args, **kwargs):
        # Support both old h(tag, props, children) and new h(children, **props) syntax
        if len(args) >= 1 and isinstance(args[0], str):
            # Old syntax: h("div", props, children)
            tag = args[0]
            props = args[1] if len(args) > 1 and isinstance(args[1], dict) else {}
            children = args[2:] if len(args) > 2 else ()
            
            # Process props for callables
            processed_props = self._process_props_for_proxies(props) if props else {}
            js_props = to_js(processed_props) if processed_props else None
            
            return createElement(tag, js_props, *children)
        elif len(args) >= 1 and callable(args[0]):
            # Old syntax: h(Component, props)
            component_func = args[0]
            props = args[1] if len(args) > 1 and isinstance(args[1], dict) else {}
            
            # Process props for callables
            processed_props = self._process_props_for_proxies(props) if props else {}
            js_props = to_js(processed_props) if processed_props else None
            
            return createElement(component_func, js_props)
        else:
            # New syntax: h(children) for Fragment
            return createElement(Fragment, None, *args)
    
    def _process_props_for_proxies(self, props):
        """Process props to create proxies for callables"""
        processed = {}
        for key, value in props.items():
            if callable(value):
                processed[key] = create_proxy(value)
            else:
                processed[key] = value
        return processed

# Hyperscript function with magic dot syntax
h = MagicH()

# Exports
__all__ = ['Element', 'Context', 'createElement', 'component', 'Fragment', 'Portal', 'Copy', 'Text', 'Raw', 'h']