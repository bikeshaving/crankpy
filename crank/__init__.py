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
createElement = _crank.createElement
Fragment = _crank.Fragment
Portal = Symbol.for_("crank.Portal")
Copy = Symbol.for_("crank.Copy")
Text = Symbol.for_("crank.Text")
Raw = Symbol.for_("crank.Raw")

# Context wrapper to add Python-friendly API
class Context:
    """Wrapper for Crank Context with additional Python conveniences"""

    def __init__(self, js_context):
        self._js_context = js_context
        # Store original methods
        self._refresh = js_context.refresh.bind(js_context) if hasattr(js_context, 'refresh') else None
        self._schedule = js_context.schedule.bind(js_context) if hasattr(js_context, 'schedule') else None
        self._after = js_context.after.bind(js_context) if hasattr(js_context, 'after') else None
        self._cleanup = js_context.cleanup.bind(js_context) if hasattr(js_context, 'cleanup') else None

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
class ElementBuilder:
    def __init__(self, tag_or_component, props=None):
        self.tag_or_component = tag_or_component
        self.props = props

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
        else:
            # If called with just props, return new ElementBuilder with props for chaining
            return ElementBuilder(self.tag_or_component, processed_props)

    def __getitem__(self, children):
        if not isinstance(children, (list, tuple)):
            children = [children]

        # Convert children to JS-compatible format
        js_children = [to_js(child) if not isinstance(child, str) else child for child in children]
        
        # Use stored props if available
        js_props = to_js(self.props) if self.props else None
        
        # Create element with children and props
        return createElement(self.tag_or_component, js_props, *js_children)

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
    h.div(id="main", **{**defaults, **overrides})["Content"]  # Multiple dict merge

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

# Hyperscript function with magic dot syntax
h = MagicH()

# Alias j for h (for backward compatibility with some tests)
j = h

# Exports
__all__ = ['Element', 'Context', 'createElement', 'component', 'Fragment', 'Portal', 'Copy', 'Text', 'Raw', 'h', 'j']
