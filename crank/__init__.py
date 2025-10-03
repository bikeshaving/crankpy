"""
Crank.py - Lightweight Python wrapper for Crank JavaScript framework
"""

from typing import Callable
import inspect
from js import Symbol, Object
from pyscript.ffi import to_js, create_proxy
from pyodide.ffi import JsProxy

from pyscript.js_modules import crank_core as crank

# Global variable to track if we've patched the as_object_map type yet
_as_object_map_type_patched = False

def _patch_as_object_map_type():
    """Patch the dynamic type created by as_object_map() to support chainable elements"""
    global _as_object_map_type_patched
    if _as_object_map_type_patched:
        return
    
    # Create a dummy element to get the as_object_map type
    dummy_elem = createElement('div', None)
    if hasattr(dummy_elem, 'as_object_map'):
        mapped = dummy_elem.as_object_map()
        mapped_type = type(mapped)
        
        # Create our chainable __getitem__
        def chainable_getitem(self, children):
            # Check if this is a chainable element with our custom properties
            if hasattr(self, '_crank_tag') and hasattr(self, '_crank_props'):
                # This is our chainable element - create element with children
                if not isinstance(children, (list, tuple)):
                    children = [children]
                js_children = [to_js(child) if not isinstance(child, str) else child for child in children]
                js_props = to_js(self._crank_props) if self._crank_props else None
                return createElement(self._crank_tag, js_props, *js_children)
            else:
                # Regular as_object_map behavior - try property access
                try:
                    return getattr(self, children)
                except AttributeError:
                    raise KeyError(children)
        
        # Patch the type
        mapped_type.__getitem__ = chainable_getitem
        _as_object_map_type_patched = True

# Re-export Crank classes directly
Element = crank.Element
createElement = crank.createElement
Fragment = crank.Fragment
Portal = crank.Portal
Copy = crank.Copy
Raw = crank.Raw
Text = crank.Text

# Context wrapper to add Python-friendly API
class Context:
    """Wrapper for Crank Context with additional Python conveniences"""

    def __init__(self, js_context):
        self._js_context = js_context
        # Store original methods with safe access
        self._refresh = getattr(js_context, 'refresh', None)
        if self._refresh and hasattr(self._refresh, 'bind'):
            self._refresh = self._refresh.bind(js_context)
        
        self._schedule = getattr(js_context, 'schedule', None)
        if self._schedule and hasattr(self._schedule, 'bind'):
            self._schedule = self._schedule.bind(js_context)
            
        self._after = getattr(js_context, 'after', None)
        if self._after and hasattr(self._after, 'bind'):
            self._after = self._after.bind(js_context)
            
        self._cleanup = getattr(js_context, 'cleanup', None)
        if self._cleanup and hasattr(self._cleanup, 'bind'):
            self._cleanup = self._cleanup.bind(js_context)

        # Copy over all properties from JS context
        for attr in dir(js_context):
            if not attr.startswith('_') and attr not in ['refresh', 'schedule', 'after', 'cleanup']:
                try:
                    value = getattr(js_context, attr)
                    setattr(self, attr, value)
                except:
                    pass

    def refresh(self, func=None):
        """Can be used as a method call or decorator"""
        if func is None:
            # Direct method call: ctx.refresh()
            if self._refresh:
                self._refresh()
            return

        # Decorator usage: @ctx.refresh
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if self._refresh:
                self._refresh()
            return result

        # Preserve function metadata
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper

    def schedule(self, func):
        """Decorator to schedule a callback before rendering"""
        if self._schedule:
            proxy = create_proxy(func)
            self._schedule(proxy)
        return func

    def after(self, func):
        """Decorator to schedule a callback after rendering"""
        if self._after:
            proxy = create_proxy(func)
            self._after(proxy)
        return func

    def cleanup(self, func):
        """Decorator to register cleanup callback"""
        if self._cleanup:
            proxy = create_proxy(func)
            self._cleanup(proxy)
        return func

    def __iter__(self):
        """Delegate to JS context's iterator protocol"""
        # Let PyScript convert the JS iterator to Python iterator
        return iter(self._js_context)

    def __aiter__(self):
        """Delegate to JS context's async iterator protocol"""
        # Let PyScript convert the JS async iterator to Python async iterator
        return aiter(self._js_context)

    def __getattr__(self, name):
        """Fallback to JS context for any missing attributes"""
        return getattr(self._js_context, name)

# Component decorator
def component(func: Callable) -> Callable:
    """Universal component decorator for any function type"""

    # Check function signature to determine how to call it
    sig = inspect.signature(func)
    params = list(sig.parameters.keys())

    def wrapper(props, ctx):
        """Wrapper that adapts Crank's (props, ctx) calling convention"""
        # Wrap the JS context with our Python Context wrapper
        wrapped_ctx = Context(ctx)

        if len(params) == 0:
            # No parameters - just call the function
            return func()
        elif len(params) == 1:
            # Single parameter - pass wrapped ctx
            return func(wrapped_ctx)
        elif len(params) == 2:
            # Two parameters - pass wrapped ctx, then props
            return func(wrapped_ctx, props)
        else:
            # More than 2 parameters is not supported
            raise ValueError(f"Component function {func.__name__} has too many parameters. Expected 0-2, got {len(params)}")

    # Proxy the wrapper function for Crank to call
    return create_proxy(wrapper)

# MagicH element
# Also known as Pythonic HyperScript

class MagicH:
    """
Pythonic HyperScript - Supported Patterns

1. Simple elements with text:
    h.div["Hello World"]
    h.p["Some text"]

2. Elements with props:
    h.input(type="text", value=text)
    h.div(className="my-class")["Content"]

3. Props with snake_case → kebab-case conversion:
    h.div(data_test_id="button", aria_hidden="true")["Content"]
    # Becomes: data-test-id="button" aria-hidden="true"

4. Props spreading:
    h.button(className="btn", **userProps)["Click me"]
    # Multiple dict merge
    h.div(id="main", **{**defaults, **overrides})["Content"]

5. Nested elements:
    h.ul[
        h.li["Item 1"],
        h.li["Item 2"],
    ]

6. Components:
    h(MyComponent)
    h(MyComponent)["children"]
    h(MyComponent, prop1="value")
    h(MyComponent, prop1="value")["children"]

7. Fragments (just use Python lists!):
    ["children"]  # Simple fragment
    [h.span["Item 1"], h.span["Item 2"]]  # Fragment with elements
    h("", key="frag")["children"]  # Fragment with props when needed

8. Reserved keywords with spreading:
    h.div(**{"class": "container", **userProps})["Content"]
    # Or use className instead of class
    """

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

class ChainableElement:
    """Element that perfectly mimics a JS element but supports __getitem__ for chaining"""
    def __init__(self, element, tag_or_component, props):
        # Store the JS element and creation info
        object.__setattr__(self, '_element', element)
        object.__setattr__(self, '_tag_or_component', tag_or_component)
        object.__setattr__(self, '_props', props)
        
    def __getitem__(self, children):
        # Recreate element with children
        if not isinstance(children, (list, tuple)):
            children = [children]
        js_children = [to_js(child) if not isinstance(child, str) else child for child in children]
        js_props = to_js(self._props) if self._props else None
        return createElement(self._tag_or_component, js_props, *js_children)
    
    def __getattr__(self, name):
        # Delegate everything to the wrapped element
        return getattr(self._element, name)
    
    def __setattr__(self, name, value):
        # Delegate attribute setting to wrapped element
        return setattr(self._element, name, value)
    
    def __str__(self):
        return str(self._element)
    
    def __repr__(self):
        return repr(self._element)
    
    def __bool__(self):
        return bool(self._element)
    
    def __eq__(self, other):
        if hasattr(other, '_element'):
            return self._element == other._element
        return self._element == other

class MicroPythonChainableProxy:
    """Chainable element proxy for MicroPython runtime."""
    
    def __init__(self, js_element, tag, props):
        self._js_element = js_element
        self._tag = tag
        self._props = props
        
    def __getitem__(self, children):
        """Create final element with children when subscripted."""
        if not isinstance(children, (list, tuple)):
            children = [children]
        js_props = to_js(self._props) if self._props else None
        return createElement(self._tag, js_props, *children)
        
    def __getattr__(self, name):
        """Delegate attribute access to the wrapped JS element."""
        return getattr(self._js_element, name)
        
    def __repr__(self):
        return f"MicroPythonChainableProxy({self._tag}, {self._props})"


class ElementBuilder:
    def __init__(self, tag_or_component, props=None):
        self.tag_or_component = tag_or_component
        self.props = props
        self._element = None  # Lazy-created element
    
    def _is_micropython(self):
        """Detect if running on MicroPython runtime."""
        import sys
        return sys.implementation.name == 'micropython'
    
    def _create_micropython_chainable(self, element, props):
        """Create MicroPython chainable proxy."""
        return MicroPythonChainableProxy(element, self.tag_or_component, props)
    
    def _ensure_element(self):
        """Create the element if it doesn't exist yet"""
        if self._element is None:
            js_props = to_js(self.props) if self.props else None
            self._element = createElement(self.tag_or_component, js_props)
        return self._element
    
    def __iter__(self):
        """Make ElementBuilder iterable like an element for Crank"""
        return iter(self._ensure_element())
    
    def __str__(self):
        return str(self._ensure_element())
    
    def __repr__(self):
        return repr(self._ensure_element())
    
    def __getattr__(self, name):
        """Delegate attribute access to the element"""
        return getattr(self._ensure_element(), name)

    def __getitem__(self, children):
        if not isinstance(children, (list, tuple)):
            children = [children]

        # Convert children to JS-compatible format
        js_children = [to_js(child) if not isinstance(child, str) else child for child in children]

        # Use stored props if available
        js_props = to_js(self.props) if self.props else None

        # Create element with children and props
        return createElement(self.tag_or_component, js_props, *js_children)

    def __call__(self, *args, **props):
        # Convert props with underscore to hyphen conversion
        converted_props = {}
        for key, value in props.items():
            converted_props[key.replace('_', '-')] = value

        # Process props to handle callables (lambdas, functions)
        processed_props = self._process_props_for_proxies(converted_props) if converted_props else {}

        if args:
            # If called with children args, create element immediately
            js_props = to_js(processed_props) if processed_props else None
            return createElement(self.tag_or_component, js_props, *args)
        elif props:
            # If called with just props, create chainable element
            js_props = to_js(processed_props) if processed_props else None
            element = createElement(self.tag_or_component, js_props)
            return self._make_chainable_element(element, processed_props)
        else:
            # If called with no args and no props, create empty element immediately
            return createElement(self.tag_or_component, None)
    
    def _make_chainable_element(self, element, props):
        """Convert element into a chainable version using runtime-specific approach"""
        try:
            if self._is_micropython():
                # MicroPython: Use simple Python proxy wrapper
                return self._create_micropython_chainable(element, props)
            else:
                # Pyodide: Use as_object_map approach with dynamic type patching
                return self._make_pyodide_chainable_element(element, props)
        except Exception:
            # Fallback to original element if anything goes wrong
            return element
    
    def _make_pyodide_chainable_element(self, element, props):
        """Create Pyodide chainable element using as_object_map approach"""
        try:
            # Ensure the as_object_map type is patched
            _patch_as_object_map_type()
            
            # Use as_object_map to make the element subscriptable
            if hasattr(element, 'as_object_map'):
                chainable = element.as_object_map()
                
                # Mark this as a chainable element for our patched __getitem__
                chainable._crank_tag = self.tag_or_component
                chainable._crank_props = props
                
                return chainable
            else:
                # Fallback to original element if as_object_map not available
                return element
        except Exception:
            # Fallback to original element if anything goes wrong
            return element

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

# Hyperscript function with magic dot syntax
h = MagicH()

# Exports
__all__ = [
        'Element',
        'Context',
        'createElement',
        'component',
        'Fragment',
        'Portal',
        'Copy',
        'Text',
        'Raw',
        'h',
        'crank',
]
