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
    
    # Check function signature to determine how to call it
    sig = inspect.signature(func)
    params = list(sig.parameters.keys())
    
    def wrapper(props, ctx):
        """Wrapper that adapts Crank's (props, ctx) calling convention"""
        if len(params) == 0:
            # No parameters - just call the function
            return func()
        elif len(params) == 1:
            # Single parameter - pass ctx
            return func(ctx)
        elif len(params) == 2:
            # Two parameters - pass ctx, then props
            return func(ctx, props)
        else:
            # More than 2 parameters is not supported
            raise ValueError(f"Component function {func.__name__} has too many parameters. Expected 0-2, got {len(params)}")
    
    # Proxy the wrapper function for Crank to call
    return create_proxy(wrapper)

# Magic h element
# Global cache to hold references to proxies to prevent garbage collection
# _proxy_cache = []

class ElementBuilder:
    def __init__(self, tag_or_component):
        self.tag_or_component = tag_or_component
    
    def __call__(self, *args, **props):
        # Convert props with underscore to hyphen conversion
        converted_props = {}
        for key, value in props.items():
            converted_props[key.replace('_', '-')] = value
        
        # Process props to handle callables (lambdas, functions)  
        processed_props = self._process_props_for_proxies(converted_props) if converted_props else {}
        js_props = to_js(processed_props) if processed_props else None
        
        # Create element with children as positional args
        return createElement(self.tag_or_component, js_props, *args)
    
    def __getitem__(self, children):
        if not isinstance(children, (list, tuple)):
            children = [children]
        
        # Create element with just children, no props
        return createElement(self.tag_or_component, None, *children)
    
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


class FragmentBuilder:
    def __init__(self, js_props):
        self.js_props = js_props
    
    def __getitem__(self, children):
        if not isinstance(children, (list, tuple)):
            children = [children]
        
        return createElement(Fragment, self.js_props, *children)


class MagicH:
    def __getattr__(self, name: str):
        # Only support HTML elements, no dynamic component lookup
        return ElementBuilder(name)
    
    def __getitem__(self, tag_or_component):
        # Dynamic tag/component access: j[variable]
        if isinstance(tag_or_component, str):
            # String tag name
            return ElementBuilder(tag_or_component)
        elif callable(tag_or_component):
            # Component function
            return ElementBuilder(tag_or_component)
        else:
            raise ValueError(f"j[{tag_or_component}] expects a string tag name or callable component")
    
    def __call__(self, *args, **kwargs):
        # Support h(tag, props, children), h(Component, **props), h(Fragment, **props), and h(children) syntax
        if len(args) >= 1 and isinstance(args[0], str):
            # String tag: h("div", props, children) or h("div", **props) 
            tag = args[0]
            
            if len(args) > 1 and isinstance(args[1], dict) and len(kwargs) == 0:
                # Old syntax: h("div", {props}, children)
                props = args[1]
                children = args[2:]
            else:
                # New syntax: h("div", **props) - kwargs as props, no positional children
                props = kwargs
                children = args[1:]  # Any extra positional args as children
            
            # Process props for callables
            processed_props = self._process_props_for_proxies(props) if props else {}
            js_props = to_js(processed_props) if processed_props else None
            
            # Empty string means Fragment - return FragmentBuilder for bracket syntax
            if tag == "":
                if children:
                    # h("", {}, children) or h("", child1, child2) - direct fragment
                    return createElement(Fragment, js_props, *children)
                else:
                    # h("", **props) - return FragmentBuilder to support h("", **props)["children"]
                    return FragmentBuilder(js_props)
            else:
                if children:
                    return createElement(tag, js_props, *children)
                else:
                    # No children - could be used with bracket syntax later
                    return createElement(tag, js_props)
                
        elif len(args) >= 1 and args[0] is Fragment:
            # Fragment with props: h(Fragment, **props) - return FragmentBuilder for bracket syntax  
            props = kwargs
            
            # Process props for callables
            processed_props = self._process_props_for_proxies(props) if props else {}
            js_props = to_js(processed_props) if processed_props else None
            
            return FragmentBuilder(js_props)
                
        elif len(args) >= 1 and callable(args[0]):
            # Component function: h(Component, **props)
            component_func = args[0]
            children = args[1:] if len(args) > 1 else ()
            
            # Use kwargs as props
            props = kwargs
            
            # Process props for callables
            processed_props = self._process_props_for_proxies(props) if props else {}
            js_props = to_js(processed_props) if processed_props else None
            
            return createElement(component_func, js_props, *children)
        else:
            # Fragment with children: h(children)
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

# Alias j for h (for backward compatibility with some tests)
j = h

# Exports
__all__ = ['Element', 'Context', 'createElement', 'component', 'Fragment', 'Portal', 'Copy', 'Text', 'Raw', 'h', 'j']