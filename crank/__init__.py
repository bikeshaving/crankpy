"""
Crank.py - Lightweight Python wrapper for Crank JavaScript framework
"""

import inspect
import sys

# Conditional typing imports for MicroPython compatibility
try:
    from typing import (
        Any,
        AsyncIterator,
        Callable,
        Dict,
        Generic,
        Iterator,
        List,
        TypedDict,
        TypeVar,
        Union,
    )
except ImportError:
    # MicroPython fallback - use minimal typing stub
    if sys.implementation.name == 'micropython':
        from .typing_stub import (
            Any,
            AsyncIterator,
            Callable,
            Dict,
            Generic,
            Iterator,
            List,
            TypedDict,
            TypeVar,
            Union,
        )
    else:
        # Re-raise if not MicroPython
        raise

# Conditional imports for different Python implementations
try:
    from pyodide.ffi import JsProxy
except ImportError:
    # MicroPython and regular Python don't have pyodide.ffi
    JsProxy = object  # Fallback type

# Import PyScript modules only when available (browser environment)
try:
    from pyscript.ffi import create_proxy, to_js
    from pyscript.js_modules import crank_core as crank
    
    _PYSCRIPT_AVAILABLE = True
except ImportError:
    # Regular Python environment - create mock functions for testing
    _PYSCRIPT_AVAILABLE = False
    
    def create_proxy(func):
        """Mock create_proxy for testing environments"""
        return func
    
    def to_js(obj):
        """Mock to_js for testing environments"""
        return obj
    
    # Mock crank_core for testing
    class _MockCrank:
        class Element:
            def __getitem__(self, children):
                """Support chainable syntax in mock environment"""
                return _MockCrank.Element()
        
        @staticmethod
        def createElement(*args):
            return _MockCrank.Element()
        
        class Fragment:
            pass
            
        class Portal:
            pass
            
        class Copy:
            pass
            
        class Raw:
            pass
            
        class Text:
            pass
    
    crank = _MockCrank()

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
                    raise KeyError(children) from None

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

# Type variables for generic Context
# Use try/except for MicroPython compatibility with subscript syntax
try:
    T = TypeVar('T', bound=Dict[str, Any])  # Props type
    TResult = TypeVar('TResult')  # Element result type

    # Type definitions for props and components
    Props = Dict[str, Any]
    Children = Union[str, Element, List["Children"]]
except TypeError:
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
    # Full Python with generic typing - need to avoid subscript syntax too
    try:
        _ContextBase = Generic[T, TResult]
    except TypeError:
        # Fallback if Generic subscripting fails
        _ContextBase = Generic

class Context(_ContextBase):
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

        # Copy over all properties from JS context (except deprecated ones)
        # In MicroPython, dir() on JsProxy triggers js_get_iter bug, so use JavaScript approach
        if sys.implementation.name == 'micropython':
            try:
                # Use JavaScript to safely enumerate properties
                from js import eval as js_eval
                js_code = """
                (function(jsObj) {
                    const props = [];
                    for (const key in jsObj) {
                        if (typeof key === 'string' && !key.startsWith('_') && 
                            !['refresh', 'schedule', 'after', 'cleanup', 'value'].includes(key)) {
                            props.push(key);
                        }
                    }
                    return props;
                })
                """
                get_props = js_eval(js_code)
                attrs = get_props(js_context)
                
                # Convert to Python list if needed
                if hasattr(attrs, 'to_py'):
                    attrs = attrs.to_py()
                elif hasattr(attrs, '__iter__'):
                    attrs = list(attrs)
                else:
                    attrs = []
                    
            except Exception:
                # Fallback to empty list if JavaScript enumeration fails
                attrs = []
        else:
            # Pyodide: Use normal dir() which works fine
            attrs = [attr for attr in dir(js_context) 
                    if not attr.startswith('_') and attr not in ['refresh', 'schedule', 'after', 'cleanup', 'value']]
        
        # Copy the enumerated attributes
        for attr in attrs:
            try:
                value = getattr(js_context, attr)
                setattr(self, attr, value)
            except Exception:
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

    def __iter__(self) -> Iterator[T]:
        """Custom iterator that avoids deprecated ctx.value access"""
        # Use generator instead of class-based iterator for MicroPython compatibility
        # Class-based iterators get proxied to JavaScript in MicroPython PyScript
        def context_generator():
            # Crank.js contexts yield props indefinitely in for-of loops
            while True:
                if hasattr(self._js_context, 'props'):
                    props = self._js_context.props
                    # Convert JsProxy to Python dict for dual runtime compatibility
                    if hasattr(props, 'to_py'):
                        # Pyodide: Use to_py() method
                        yield props.to_py() if props else {}  # type: ignore[misc]
                    else:
                        # MicroPython: Use safe conversion to avoid dict() iteration bug
                        if props:
                            try:
                                from js import eval as js_eval
                                js_code = """
                                (function(jsObj) {
                                    if (!jsObj) return {};
                                    const result = {};
                                    for (const key in jsObj) {
                                        if (jsObj.hasOwnProperty(key)) {
                                            result[key] = jsObj[key];
                                        }
                                    }
                                    return result;
                                })
                                """
                                convert_obj = js_eval(js_code)
                                js_dict = convert_obj(props)
                                if hasattr(js_dict, 'to_py'):
                                    yield js_dict.to_py()  # type: ignore[misc]
                                else:
                                    yield {}  # type: ignore[misc]
                            except Exception:
                                yield {}  # type: ignore[misc]
                        else:
                            yield {}  # type: ignore[misc]
                else:
                    yield {}  # type: ignore[misc]

        generator = context_generator()
        
        # Apply SymbolIteratorWrapper in MicroPython to fix iteration bugs
        if sys.implementation.name == 'micropython':
            return SymbolIteratorWrapper(generator)
        else:
            return generator

    def __aiter__(self) -> AsyncIterator[T]:
        """Custom async iterator that avoids deprecated ctx.value access"""
        # Use async generator instead of class-based iterator for MicroPython compatibility
        async def async_context_generator():
            # Crank.js async iterators should yield continuously for "continuous mode"
            while True:
                if hasattr(self._js_context, 'props'):
                    props = self._js_context.props
                    # Convert JsProxy to Python dict for dual runtime compatibility
                    if hasattr(props, 'to_py'):
                        # Pyodide: Use to_py() method
                        yield props.to_py() if props else {}  # type: ignore[misc]
                    else:
                        # MicroPython: Use safe conversion to avoid dict() iteration bug
                        if props:
                            try:
                                from js import eval as js_eval
                                js_code = """
                                (function(jsObj) {
                                    if (!jsObj) return {};
                                    const result = {};
                                    for (const key in jsObj) {
                                        if (jsObj.hasOwnProperty(key)) {
                                            result[key] = jsObj[key];
                                        }
                                    }
                                    return result;
                                })
                                """
                                convert_obj = js_eval(js_code)
                                js_dict = convert_obj(props)
                                if hasattr(js_dict, 'to_py'):
                                    yield js_dict.to_py()  # type: ignore[misc]
                                else:
                                    yield {}  # type: ignore[misc]
                            except Exception:
                                yield {}  # type: ignore[misc]
                        else:
                            yield {}  # type: ignore[misc]
                else:
                    yield {}  # type: ignore[misc]

        return async_context_generator()

    @property
    def props(self) -> T:
        """Access current props with proper typing"""
        if hasattr(self._js_context, 'props'):
            props = self._js_context.props
            # Convert JsProxy to Python dict for dual runtime compatibility
            if hasattr(props, 'to_py'):
                # Pyodide: Use to_py() method
                return props.to_py() if props else {}  # type: ignore[return-value]
            else:
                # MicroPython: Use JavaScript to convert object to avoid dict() iteration bug
                if props and sys.implementation.name == 'micropython':
                    try:
                        from js import eval as js_eval
                        js_code = """
                        (function(jsObj) {
                            if (!jsObj) return {};
                            const result = {};
                            for (const key in jsObj) {
                                if (jsObj.hasOwnProperty(key)) {
                                    result[key] = jsObj[key];
                                }
                            }
                            return result;
                        })
                        """
                        convert_obj = js_eval(js_code)
                        js_dict = convert_obj(props)
                        
                        # Convert to Python dict safely
                        if hasattr(js_dict, 'to_py'):
                            # PyScript's to_py() method should work safely
                            return js_dict.to_py()  # type: ignore[return-value]
                        else:
                            # Fallback: return empty dict if no to_py method
                            return {}  # type: ignore[return-value]
                    except Exception:
                        # Fallback to empty dict if JavaScript conversion fails
                        return {}  # type: ignore[return-value]
                else:
                    # MicroPython with null/empty props, or non-MicroPython fallback
                    return {}  # type: ignore[return-value]
        return {}  # type: ignore[return-value]

    def __getattr__(self, name):
        """Fallback to JS context for any missing attributes"""
        if name == 'value':
            print("DEBUG: ctx.value accessed via __getattr__!")
        return getattr(self._js_context, name)


# Symbol.iterator wrapper for MicroPython generators
class SymbolIteratorWrapper:
    """Wrapper that makes Python generators compatible with JavaScript Symbol.iterator protocol"""
    
    def __init__(self, python_generator):
        self.python_generator = python_generator
        # Mark as wrapped to prevent double-wrapping
        self._is_symbol_iterator_wrapped = True
    
    def __getitem__(self, key):
        """Handle Symbol.iterator access using pure JavaScript approach"""
        # Use JavaScript eval to handle everything (workaround for MicroPython iteration bugs)
        from js import eval as js_eval
        
        js_code = """
        (function(pythonKey, pythonGen) {
            if (pythonKey === Symbol.iterator) {
                return function() {
                    return {
                        next: function() {
                            try {
                                const value = pythonGen.__next__();
                                return { value: value, done: false };
                            } catch (e) {
                                return { value: undefined, done: true };
                            }
                        }
                    };
                };
            }
            throw new Error('SymbolIteratorWrapper: Not Symbol.iterator');
        })
        """
        
        try:
            js_func = js_eval(js_code)
            return js_func(key, self.python_generator)
        except Exception:
            raise KeyError(f"SymbolIteratorWrapper: Unsupported key {key}")
    
    def __iter__(self):
        """Return self for Python iteration protocol"""
        return self
    
    def __next__(self):
        """Make this a proper Python iterator"""
        return next(self.python_generator)
    
    def __repr__(self):
        return f"SymbolIteratorWrapper({self.python_generator})"


# Component decorator
# JavaScript helper for creating proper iterables in MicroPython
def _ensure_iterable_helper():
    """Ensure the JavaScript iterable helper function exists"""
    from js import window
    
    # Check if helper already exists
    if not hasattr(window, 'crankPyCreateIterable'):
        # Inject the helper function into global scope
        from js import eval as js_eval
        js_eval("""
        window.crankPyCreateIterable = function(items) {
            return {
                [Symbol.iterator]: function() {
                    let index = 0;
                    return {
                        next: function() {
                            if (index < items.length) {
                                return { value: items[index++], done: false };
                            } else {
                                return { value: undefined, done: true };
                            }
                        }
                    };
                }
            };
        };
        """)

def create_js_iterable(generator_or_value):
    """Create a JavaScript-compatible iterable from a Python generator or value"""
    from pyscript.ffi import to_js
    from js import window
    
    # Ensure helper function exists
    _ensure_iterable_helper()
    
    # Convert generator to list of items
    if hasattr(generator_or_value, 'send') or hasattr(generator_or_value, '__next__'):
        # It's a generator, convert to list
        items = list(generator_or_value)
    else:
        # Single value, wrap in list
        items = [generator_or_value]
    
    # Convert to JavaScript array and create proper iterable
    js_items = to_js(items)
    return window.crankPyCreateIterable(js_items)


def component(func: Callable) -> Callable:
    """Universal component decorator for any function type"""

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
                f"Component function {func.__name__} has incompatible signature. "
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
            # MicroPython: Use safe conversion to avoid dict() iteration bug
            if props and sys.implementation.name == 'micropython':
                try:
                    from js import eval as js_eval
                    js_code = """
                    (function(jsObj) {
                        if (!jsObj) return {};
                        const result = {};
                        for (const key in jsObj) {
                            if (jsObj.hasOwnProperty(key)) {
                                result[key] = jsObj[key];
                            }
                        }
                        return result;
                    })
                    """
                    convert_obj = js_eval(js_code)
                    js_dict = convert_obj(props)
                    if hasattr(js_dict, 'to_py'):
                        python_props = js_dict.to_py()
                    else:
                        python_props = {}
                except Exception:
                    python_props = {}
            else:
                python_props = {}

        def wrap_result(result):
            """Wrap generator results for JavaScript interop in MicroPython"""
            # Check if already wrapped to prevent double-wrapping
            if hasattr(result, '_is_symbol_iterator_wrapped'):
                return result
            
            # Check if we're in MicroPython and result needs wrapping
            if (sys.implementation.name == 'micropython' and 
                (hasattr(result, 'send') or hasattr(result, '__next__') or 
                 hasattr(result, 'asend') or hasattr(result, '__anext__'))):
                # Use Symbol.iterator mapping instead of JavaScript helper
                return SymbolIteratorWrapper(result)
            return result

        # Check if we have cached parameter count
        if cached_param_count is not None:
            # Use cached parameter count
            if cached_param_count == 0:
                return wrap_result(func())
            elif cached_param_count == 1:
                return wrap_result(func(wrapped_ctx))
            else:  # cached_param_count == 2
                return wrap_result(func(wrapped_ctx, python_props))
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
                f"Component function {func.__name__} has incompatible signature. "
                f"Expected 0, 1 (ctx), or 2 (ctx, props) parameters."
            )

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
    h.div(class_name="my-class")["Content"]

3. Props with snake_case → kebab-case conversion:
    h.div(data_test_id="button", aria_hidden="true")["Content"]
    # Becomes: data-test-id="button" aria-hidden="true"

4. Props spreading:
    h.button(class_name="btn", **userProps)["Click me"]
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
    # Or use class_name (converts to className for React compatibility)
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
        # Type definitions
        'Props',
        'Children',
]
