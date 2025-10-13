"""Crank.py - Lightweight Python wrapper for Crank JavaScript framework"""
import inspect
import sys
from pyscript.ffi import to_js, create_proxy
from pyscript.js_modules import crank_core as crank

# Typing imports with MicroPython compatibility
try:
    from typing import Any, AsyncIterator, Callable, Dict, Generic, Iterator, List, TypedDict, TypeVar, Union
except ImportError:
    if sys.implementation.name != 'micropython':
        raise

    from .typing_stub import Any, AsyncIterator, Callable, Dict, Generic, Iterator, List, TypedDict, TypeVar, Union

# Re-export Crank classes directly
Element = crank.Element
createElement = crank.createElement
Fragment = crank.Fragment
Portal = crank.Portal
Copy = crank.Copy
Raw = crank.Raw
Text = crank.Text

# Global state
_as_object_map_type_patched = False
_is_micropython = sys.implementation.name == 'micropython'

def _create_proxy(func):
    """Create proxy without caching - auto mode handles cleanup"""
    if _is_micropython:
        return func
    return create_proxy(func)


def _js_to_python_dict(js_obj):
    """Convert JavaScript object to Python dict across runtimes"""
    # Pyodide: Use to_py()
    if hasattr(js_obj, 'to_py'):
        return js_obj.to_py()

    # MicroPython: Manual conversion using hasOwnProperty
    result = {}
    for prop_name in dir(js_obj):
        if js_obj.hasOwnProperty(prop_name):
            prop_value = getattr(js_obj, prop_name)
            if not callable(prop_value):
                result[prop_name] = prop_value
    return result


def _patch_as_object_map_type():
    """Patch the dynamic type created by as_object_map() to support chainable elements"""
    global _as_object_map_type_patched
    if _as_object_map_type_patched:
        return

    dummy_elem = createElement('div', None)
    if hasattr(dummy_elem, 'as_object_map'):
        mapped = dummy_elem.as_object_map()
        mapped_type = type(mapped)

        def chainable_getitem(self, children):
            if hasattr(self, '_crank_tag') and hasattr(self, '_crank_props'):
                if not isinstance(children, (list, tuple)):
                    children = [children]
                js_children = [to_js(child) if not isinstance(child, str) else child for child in children]
                js_props = to_js(self._crank_props) if self._crank_props else None
                return createElement(self._crank_tag, js_props, *js_children)
            else:
                try:
                    return getattr(self, children)
                except AttributeError:
                    raise KeyError(children) from None

        mapped_type.__getitem__ = chainable_getitem
        _as_object_map_type_patched = True


# Type variables for generic Context
try:
    from typing import Iterable
    T = TypeVar('T', bound=Dict[str, Any])
    TResult = TypeVar('TResult')
    Props = Dict[str, Any]
    Children = Union[str, Element, bool, None, Iterable["Children"]]
except (TypeError, ImportError):
    # MicroPython fallback - no subscript syntax
    T = TypeVar('T')
    TResult = TypeVar('TResult')

    # Simplified types for MicroPython
    Props = dict
    Children = object


# Context wrapper to add Python-friendly API with generic typing
# MicroPython doesn't support Generic subscripting, so use conditional inheritance
if sys.implementation.name == 'micropython':
    # MicroPython fallback - plain class without generics
    _ContextBase = object
else:
    _ContextBase = Generic[T, TResult]


class Context(_ContextBase):
    """Wrapper for Crank Context with additional Python conveniences"""

    def __init__(self, js_context):
        self._js_context = js_context
        # Store original methods with safe access
        self._refresh = getattr(js_context, 'refresh').bind(js_context)
        self._schedule = getattr(js_context, 'schedule').bind(js_context)
        self._after = getattr(js_context, 'after').bind(js_context)
        self._cleanup = getattr(js_context, 'cleanup').bind(js_context)
        self._provide = getattr(js_context, 'provide').bind(js_context)
        self._consume = getattr(js_context, 'consume').bind(js_context)


    def refresh(self, func=None):
        """Can be used as a method call or decorator"""
        if func is None:
            # Direct method call: ctx.refresh()
            return self._refresh()

        # Decorator usage: @ctx.refresh - pass func directly to Crank
        # This allows Crank to handle async functions with special logic
        return self._register_callback(func, self._refresh)

    def _register_callback(self, func, callback_method):
        """Common logic for registering callbacks with proper proxy handling"""
        if callback_method and callable(func):
            # Create a variadic wrapper that adapts to function signature
            try:
                sig = inspect.signature(func)
                param_count = len(sig.parameters)
            except (AttributeError, ValueError):
                # MicroPython fallback - try calling with different arg counts
                param_count = None

            def variadic_wrapper(*args):
                if param_count is not None:
                    # Use signature inspection
                    if param_count == 0:
                        return func()
                    elif param_count >= 1 and len(args) >= 1:
                        return func(args[0])
                    elif len(args) == 0:
                        return func()
                    else:
                        raise TypeError(f"Function expects {param_count} args, got {len(args)}")
                else:
                    # MicroPython fallback - try different calling patterns
                    if len(args) == 0:
                        return func()
                    elif len(args) == 1:
                        try:
                            return func(args[0])
                        except TypeError:
                            # Function doesn't accept arguments
                            return func()
                    else:
                        raise TypeError(f"Callback function takes at most 1 argument, got {len(args)}")

            proxy = _create_proxy(variadic_wrapper)
            callback_method(proxy)
        return func

    def schedule(self, func):
        """Decorator to schedule a callback before rendering"""
        return self._register_callback(func, self._schedule)

    def after(self, func):
        """Decorator to schedule a callback after rendering"""
        return self._register_callback(func, self._after)

    def cleanup(self, func):
        """Decorator to register cleanup callback"""
        return self._register_callback(func, self._cleanup)

    def provide(self, *args, **kwargs):
        """Provide context value"""
        return self._provide(*args, **kwargs)

    def consume(self, *args, **kwargs):
        """Consume context value"""
        return self._consume(*args, **kwargs)

    def __iter__(self):
        """Delegate to JS context iteration with props conversion"""
        for js_props in self._js_context:
            yield _js_to_python_dict(js_props)

    def __aiter__(self):
        """Return async iterator"""
        return self._async_iterator()

    async def _async_iterator(self):
        """Async generator for context iteration"""
        async for js_props in self._js_context:
            yield _js_to_python_dict(js_props)


    @property
    def props(self) -> T:
        """Access current props with proper typing"""
        return _js_to_python_dict(self._js_context.props)  # type: ignore[return-value]


class MicroPythonGeneratorWrapper:
    """Wrapper that makes Python generators compatible with JavaScript"""

    def __init__(self, python_generator):
        self.python_generator = python_generator

    def next(self, value=None):
        try:
            if value is None:
                result = next(self.python_generator)
            else:
                result = self.python_generator.send(value)
            return {"value": result, "done": False}
        except StopIteration as e:
            return {"value": getattr(e, 'value', None), "done": True}

    def throw(self, exception):
        try:
            result = self.python_generator.throw(exception)
            return {"value": result, "done": False}
        except StopIteration as e:
            return {"value": getattr(e, 'value', None), "done": True}

    def return_(self, value=None):
        try:
            self.python_generator.close()
        except GeneratorExit:
            pass
        return {"value": value, "done": True}


# Bind return_ as 'return' for JavaScript compatibility
setattr(MicroPythonGeneratorWrapper, 'return', MicroPythonGeneratorWrapper.return_)


def component(func: Callable) -> Callable:
    # Cache parameter count per component instance using nonlocal
    cached_param_count = None

    # Only validate signature using static inspection at decoration time
    # Don't call the function to avoid side effects

    # In full Python, use inspect.signature for accurate detection
    try:
        sig = inspect.signature(func)
        param_count = len(sig.parameters)
        # Cache the result for later use
        cached_param_count = param_count

        # Validate parameter count - Crank components can have 0, 1, or 2 parameters
        if param_count > 2:
            raise ValueError(
                f"Component function {getattr(func, '__name__', '<anonymous>')} has incompatible signature. "
                f"Expected 0, 1 (ctx), or 2 (ctx, props) parameters."
            )
    except AttributeError:
        # MicroPython fallback - we'll determine parameter count at runtime
        # Don't call the function here to avoid side effects
        pass

    def wrapper(props, ctx):
        """Wrapper that adapts Crank's (props, ctx) calling convention"""
        nonlocal cached_param_count


        # Wrap the JS context with our Python Context wrapper
        wrapped_ctx = Context(ctx)

        # Convert props to Python dict for dual runtime compatibility
        if hasattr(props, 'to_py'):
            # Pyodide: Use to_py() method
            python_props = props.to_py() if props else {}
        else:
            # MicroPython: Use direct property access instead of JavaScript evaluation
            if props and sys.implementation.name == 'micropython':
                try:
                    # Convert all available properties from JavaScript object
                    python_props = {}
                    for prop_name in dir(props):
                        # Skip internal properties and common object methods
                        if (not prop_name.startswith('_') and
                            prop_name not in ['constructor', 'toString', 'valueOf', 'hasOwnProperty']):
                            try:
                                prop_value = getattr(props, prop_name)
                                if prop_value is not None and not callable(prop_value):
                                    python_props[prop_name] = prop_value
                            except:
                                # Ignore props we can't access
                                pass

                except Exception:
                    # If any error occurs, fall back to empty props
                    python_props = {}
            else:
                python_props = {}

        def wrap_result(result):
            """Wrap generator results for JavaScript interop"""
            # MicroPython generators need wrapping for JavaScript interop
            if sys.implementation.name == 'micropython' and inspect.isgenerator(result):
                return MicroPythonGeneratorWrapper(result)

            # Default: treat as sync function component result, return as-is
            return result

        # Check if we have cached parameter count
        if cached_param_count is not None:
            # Use cached parameter count
            if cached_param_count == 0:
                result = func()
                return wrap_result(result)
            elif cached_param_count == 1:
                result = func(wrapped_ctx)
                return wrap_result(result)
            else:  # cached_param_count == 2
                result = func(wrapped_ctx, python_props)
                return wrap_result(result)
        else:
            # MicroPython runtime - determine parameter count on first call
            # Try different parameter counts and cache the successful one
            for test_count in [2, 1, 0]:  # Try most common first
                try:
                    if test_count == 0:
                        result = func()
                    elif test_count == 1:
                        result = func(wrapped_ctx)
                    else:  # test_count == 2
                        result = func(wrapped_ctx, python_props)

                    # Success! Cache this parameter count for future calls
                    cached_param_count = test_count
                    return wrap_result(result)

                except TypeError as e:
                    # Check if this looks like a parameter count error
                    error_msg = str(e).lower()
                    if any(phrase in error_msg for phrase in [
                        'takes', 'positional argument', 'missing', 'given'
                    ]):
                        # This is likely a parameter count mismatch, try next count
                        continue
                    else:
                        # This is likely a real error in user code
                        # Cache this parameter count and re-raise the error
                        cached_param_count = test_count
                        raise
                except Exception:
                    # Some other error - cache this parameter count and re-raise
                    cached_param_count = test_count
                    raise

            # If we get here, none of the parameter counts worked
            raise ValueError(
                f"Component function {getattr(func, '__name__', '<anonymous>')} has incompatible signature. "
                f"Expected 0, 1 (ctx), or 2 (ctx, props) parameters."
            )

    # Create proxy without caching - auto mode handles cleanup
    return _create_proxy(wrapper)

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
    # Or use className (converts to className for React compatibility)
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
        if len(args) >= 1:
            # Any first argument: h(tag/component/variable, **props)
            tag_or_component = args[0]

            # Handle old syntax: h(tag, {props}, children)
            if len(args) > 1 and isinstance(args[1], dict) and len(kwargs) == 0:
                props = args[1]
                children = args[2:]
            else:
                # New syntax: h(tag, **props) - kwargs as props, remaining args as children
                props = kwargs
                children = args[1:]  # Any extra positional args as children

            # Process props for callables
            processed_props = self._process_props_for_proxies(props) if props else {}
            js_props = to_js(processed_props) if processed_props else None

            # Special handling for Fragment
            if tag_or_component is Fragment or (isinstance(tag_or_component, str) and tag_or_component == ""):
                if children:
                    return createElement(Fragment, js_props, *children)
                else:
                    # Fragment with no children - return FragmentBuilder for bracket syntax
                    return FragmentBuilder(js_props)

            # For any other tag/component
            element = createElement(tag_or_component, js_props, *children)

            # Always make it chainable for bracket syntax (can overwrite children like JSX)
            return self._make_element_chainable(element, tag_or_component, processed_props)
        else:
            # Fragment with children: h(children)
            return createElement(Fragment, None, *args)

    def _process_props_for_proxies(self, props):
        """Process props to create proxies for callables"""
        processed = {}
        for key, value in props.items():
            if callable(value):
                # Hybrid proxy: use appropriate strategy based on interpreter
                processed[key] = _create_proxy(value)
            else:
                processed[key] = value
        return processed


    def _make_element_chainable(self, element, tag_or_component, props):
        """Make an element chainable for bracket syntax"""
        import sys

        # MicroPython doesn't need special handling - subscription works directly
        if sys.implementation.name == 'micropython':
            return element

        # Pyodide: Use as_object_map and mark it for our patched __getitem__
        try:
            _patch_as_object_map_type()  # Ensure patch is applied

            if hasattr(element, 'as_object_map'):
                chainable = element.as_object_map()
                # Mark this as a chainable element for our patched __getitem__
                chainable._crank_tag = tag_or_component
                chainable._crank_props = props
                return chainable
            else:
                return element
        except Exception:
            return element



class ElementBuilder:
    def __init__(self, tag_or_component, props=None):
        self.tag_or_component = tag_or_component
        self.props = props
        self._element = None  # Lazy-created element

    def _is_micropython_runtime(self):
        """Detect if running on MicroPython runtime."""
        import sys
        return sys.implementation.name == 'micropython'


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

            if self._is_micropython_runtime():
                # MicroPython: Store the element and props in ElementBuilder for bracket syntax
                self._element = element
                self.props = processed_props
                return self  # Return ElementBuilder itself for bracket syntax
            else:
                # Pyodide: Use the chainable element approach
                return self._make_chainable_element(element, processed_props)
        else:
            # If called with no args and no props, create empty element immediately
            return createElement(self.tag_or_component, None)

    def _make_chainable_element(self, element, props):
        """Convert element into a chainable version using runtime-specific approach"""
        if self._is_micropython_runtime():
            # MicroPython: Return raw element to avoid proxy issues
            # ElementBuilder will handle bracket syntax via its own __getitem__
            return element

        # Pyodide: Use as_object_map approach with dynamic type patching
        return self._make_pyodide_chainable_element(element, props)

    def _make_pyodide_chainable_element(self, element, props):
        """Create Pyodide chainable element using as_object_map approach"""
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
                    # Hybrid proxy: use appropriate strategy based on interpreter
                    processed[key] = _create_proxy(value)
            elif isinstance(value, dict):
                # Recursively process nested dicts
                processed[key] = self._process_props_for_proxies(value)
            elif isinstance(value, (list, tuple)):
                # Process lists/tuples for callables
                processed_list = []
                for item in value:
                    if callable(item) and not (hasattr(item, 'toString') or str(type(item)).startswith("<class 'pyodide.ffi.JsProxy'>")):
                        # Hybrid proxy: use appropriate strategy based on interpreter
                        processed_list.append(_create_proxy(item))
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
        'Children',
        'Context',
        'Copy',
        'Element',
        'Fragment',
        'Portal',
        'Props',
        'Raw',
        'Text',
        'h',
        'component',
        'crank',
        'createElement',
]
