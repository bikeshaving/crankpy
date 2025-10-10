"""Crank.py - Lightweight Python wrapper for Crank JavaScript framework"""

import inspect
import sys
from pyscript.ffi import to_js
from pyscript.js_modules import crank_core as crank

# Typing imports with MicroPython compatibility
try:
    from typing import Any, AsyncIterator, Callable, Dict, Generic, Iterator, List, TypedDict, TypeVar, Union
except ImportError:
    if sys.implementation.name == 'micropython':
        from .typing_stub import Any, AsyncIterator, Callable, Dict, Generic, Iterator, List, TypedDict, TypeVar, Union
    else:
        raise

# Pyodide compatibility
try:
    from pyodide.ffi import JsProxy
except ImportError:
    JsProxy = object

# Global state
_as_object_map_type_patched = False
_is_micropython = sys.implementation.name == 'micropython'
_proxy_cache = {} if not _is_micropython else None

# Hybrid proxy strategy
if _is_micropython:
    def _create_proxy_hybrid(func):
        return func
else:
    from pyscript.ffi import create_proxy
    def _create_proxy_hybrid(func):
        func_id = id(func)
        if func_id not in _proxy_cache:
            _proxy_cache[func_id] = create_proxy(func)
        return _proxy_cache[func_id]

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

# Re-export Crank classes directly
Element = crank.Element
createElement = crank.createElement
Fragment = crank.Fragment
Portal = crank.Portal
Copy = crank.Copy
Raw = crank.Raw
Text = crank.Text

# Type variables for generic Context
try:
    T = TypeVar('T', bound=Dict[str, Any])
    TResult = TypeVar('TResult')
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

        # Hybrid proxy: cache callbacks only for Pyodide
        self._proxied_callbacks = {} if not _is_micropython else None

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

    def _register_callback(self, func, callback_method):
        """Common logic for registering callbacks with proper proxy handling"""
        if callback_method and callable(func):
            if _is_micropython:
                callback_method(func)
            else:
                func_id = id(func)
                if func_id not in self._proxied_callbacks:
                    self._proxied_callbacks[func_id] = _create_proxy_hybrid(func)
                callback_method(self._proxied_callbacks[func_id])
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

    def __iter__(self):
        """Delegate to JavaScript context's native iterator with props conversion"""
        # Get the JavaScript iterator
        js_iterator = iter(self._js_context)
        
        # Wrap it to convert props to Python dicts
        for js_props in js_iterator:
            # Convert JavaScript props to Python dict
            if hasattr(js_props, 'to_py'):
                # Pyodide: Use to_py() method
                yield js_props.to_py() if js_props else {}
            else:
                # MicroPython or fallback: Convert manually
                if js_props:
                    try:
                        # Check if it's already a Python dict
                        if isinstance(js_props, dict):
                            yield js_props
                        # Check if it's a string (not a dict-like object)
                        elif isinstance(js_props, str):
                            # Strings are not props objects, yield empty dict
                            yield {}
                        else:
                            # Try to convert JavaScript object to Python dict
                            python_props = {}
                            if hasattr(js_props, '__iter__') and not isinstance(js_props, str):
                                # If it's iterable but not a string, try to extract key-value pairs
                                for key in js_props:
                                    try:
                                        python_props[key] = js_props[key]
                                    except:
                                        pass
                            yield python_props
                    except:
                        yield {}
                else:
                    yield {}

    def __aiter__(self):
        """Delegate to JavaScript context's native async iterator with props conversion"""
        # Return an async generator that wraps the JavaScript async iterator
        return self._async_props_iterator()
    
    async def _async_props_iterator(self):
        """Async generator that converts JavaScript props to Python dicts"""
        # Get the JavaScript async iterator
        js_async_iterator = aiter(self._js_context)
        
        # Wrap it to convert props to Python dicts
        async for js_props in js_async_iterator:
            # Convert JavaScript props to Python dict (same logic as __iter__)
            if hasattr(js_props, 'to_py'):
                # Pyodide: Use to_py() method
                yield js_props.to_py() if js_props else {}
            else:
                # MicroPython or fallback: Convert manually
                if js_props:
                    try:
                        # Check if it's already a Python dict
                        if isinstance(js_props, dict):
                            yield js_props
                        # Check if it's a string (not a dict-like object)
                        elif isinstance(js_props, str):
                            # Strings are not props objects, yield empty dict
                            yield {}
                        else:
                            # Try to convert JavaScript object to Python dict
                            python_props = {}
                            if hasattr(js_props, '__iter__') and not isinstance(js_props, str):
                                # If it's iterable but not a string, try to extract key-value pairs
                                for key in js_props:
                                    try:
                                        python_props[key] = js_props[key]
                                    except:
                                        pass
                            yield python_props
                    except:
                        yield {}
                else:
                    yield {}


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
                # MicroPython: Use direct property access instead of JavaScript evaluation
                if props and sys.implementation.name == 'micropython':
                    try:
                        # Simplified: Direct property access for common props
                        result = {}
                        common_props = ['name', 'value', 'id', 'className', 'onClick', 'onChange', 'children', 'delay', 'error', 'type', 'placeholder', 'disabled', 'checked', 'src', 'alt', 'href', 'target']
                        
                        for prop in common_props:
                            try:
                                if hasattr(props, prop):
                                    prop_value = getattr(props, prop, None)
                                    if prop_value is not None:
                                        result[prop] = prop_value
                            except:
                                # Ignore props we can't access
                                pass
                        
                        return result  # type: ignore[return-value]
                    except Exception:
                        # Fallback to empty dict if conversion fails
                        return {}  # type: ignore[return-value]
                else:
                    # MicroPython with null/empty props, or non-MicroPython fallback
                    return {}  # type: ignore[return-value]
        return {}  # type: ignore[return-value]

    def __getattr__(self, name):
        """Fallback to JS context for any missing attributes"""
        return getattr(self._js_context, name)


# Symbol.iterator wrapper for MicroPython generators
class SymbolIteratorWrapper:
    """Wrapper that makes Python generators compatible with JavaScript Symbol.iterator and Symbol.asyncIterator protocols"""

    def __init__(self, python_generator, first_value=None):
        self.python_generator = python_generator
        # Store first value if we consumed it during detection
        self._first_value = first_value
        self._first_value_consumed = False
        # Mark as wrapped to prevent double-wrapping
        self._is_symbol_iterator_wrapped = True

    def __getitem__(self, key):
        """Handle Symbol.iterator and Symbol.asyncIterator access with MicroPython-compatible approach"""
        from js import Symbol
        
        if key == Symbol.iterator:
            return self._create_sync_iterator_function()
        elif key == Symbol.asyncIterator:
            return self._create_async_iterator_function()
        else:
            raise KeyError(f"SymbolIteratorWrapper: Unsupported key {key}")
    
    def _create_sync_iterator_function(self):
        """Create a JavaScript function that returns a sync iterator"""
        def iterator_function():
            return self._create_sync_iterator()
        return _create_proxy_hybrid(iterator_function)
    
    def _create_sync_iterator(self):
        """Create the actual sync iterator object"""
        def next_method():
            try:
                # Handle first value if we have one cached
                if self._first_value is not None and not self._first_value_consumed:
                    self._first_value_consumed = True
                    return {"value": self._first_value, "done": False}
                
                # Get next value from generator
                value = self.python_generator.__next__()
                return {"value": value, "done": False}
            except StopIteration:
                return {"value": None, "done": True}
            except Exception:
                return {"value": None, "done": True}
        
        # Return iterator object with hybrid-proxied next method
        return {"next": _create_proxy_hybrid(next_method)}
    
    def _create_async_iterator_function(self):
        """Create a JavaScript function that returns an async iterator"""
        def iterator_function():
            return self._create_async_iterator()
        return _create_proxy_hybrid(iterator_function)
    
    def _create_async_iterator(self):
        """Create the actual async iterator object"""
        from js import Promise
        
        def next_method():
            try:
                # Handle first value if we have one cached
                if self._first_value is not None and not self._first_value_consumed:
                    self._first_value_consumed = True
                    return Promise.resolve({"value": self._first_value, "done": False})
                
                # Get next value from generator
                value = self.python_generator.__next__()
                return Promise.resolve({"value": value, "done": False})
            except StopIteration:
                return Promise.resolve({"value": None, "done": True})
            except Exception:
                return Promise.resolve({"value": None, "done": True})
        
        # Return async iterator object with hybrid-proxied next method
        return {"next": _create_proxy_hybrid(next_method)}

    def __iter__(self):
        """Return self for Python iteration protocol"""
        return self

    def __next__(self):
        """Make this a proper Python iterator"""
        # Return preserved first value if we have it and haven't consumed it yet
        if self._first_value is not None and not self._first_value_consumed:
            self._first_value_consumed = True
            return self._first_value
        return next(self.python_generator)

    def __aiter__(self):
        """Return self for Python async iteration protocol"""
        return self

    async def __anext__(self):
        """Make this a proper Python async iterator"""
        # Return preserved first value if we have it and haven't consumed it yet
        if self._first_value is not None and not self._first_value_consumed:
            self._first_value_consumed = True
            return self._first_value

        if hasattr(self.python_generator, '__anext__'):
            try:
                result = await self.python_generator.__anext__()
                return result
            except Exception as e:
                raise
        else:
            # Sync generator wrapped as async - convert sync next to async
            try:
                result = next(self.python_generator)
                return result
            except StopIteration as e:
                raise StopAsyncIteration

    def next(self, value=None):
        """JavaScript-style next method"""
        # Check if this is an async generator by looking at detection metadata
        is_async_generator = self._is_async_generator()

        if is_async_generator:
            # For async generators, return a Promise but handle ThenableEvent errors gracefully
            try:
                from js import Promise

                def promise_executor(resolve, reject):
                    try:
                        # Return preserved first value if we have it and haven't consumed it yet
                        if self._first_value is not None and not self._first_value_consumed:
                            self._first_value_consumed = True
                            resolve({"value": self._first_value, "done": False})
                            return

                        # Use send() if we have a value, otherwise use next()
                        if value is not None and hasattr(self.python_generator, 'send'):
                            result = self.python_generator.send(value)
                        else:
                            result = next(self.python_generator)
                        resolve({"value": result, "done": False})
                    except StopIteration:
                        resolve({"value": None, "done": True})
                    except Exception as e:
                        # Check if this is a ThenableEvent error
                        error_str = str(e)
                        if "ThenableEvent" in error_str and "no attribute" in error_str:
                            # This is the PyScript Promise interop issue
                            # Instead of rejecting, resolve with an error value that can be yielded
                            resolve({"value": f"Error: JavaScript Promise await not supported in MicroPython generators. Use Python async operations instead.", "done": False})
                        else:
                            reject(str(e))

                return Promise.new(promise_executor)
            except (ImportError, Exception):
                # Fallback to sync behavior if Promise creation fails
                pass

        # Sync generator or fallback behavior
        try:
            # Return preserved first value if we have it and haven't consumed it yet
            if self._first_value is not None and not self._first_value_consumed:
                self._first_value_consumed = True
                return {"value": self._first_value, "done": False}

            # Use send() if we have a value, otherwise use next()
            if value is not None and hasattr(self.python_generator, 'send'):
                result = self.python_generator.send(value)
            else:
                result = next(self.python_generator)
            return {"value": result, "done": False}
        except StopIteration:
            return {"value": None, "done": True}

    def throw(self, exception_type, exception_value=None, traceback=None):
        """JavaScript iterator protocol: throw() method for error injection"""
        # Handle throwing errors into generators (like Crank.js)
        try:
            if hasattr(self.python_generator, 'throw'):
                # Python generator supports throw()
                if exception_value is not None:
                    result = self.python_generator.throw(exception_type, exception_value, traceback)
                else:
                    # If only one argument, it could be an exception instance
                    result = self.python_generator.throw(exception_type)
                return {"value": result, "done": False}
            else:
                # Fallback: raise the exception normally
                if exception_value is not None:
                    raise exception_type(exception_value)
                else:
                    raise exception_type
        except StopIteration:
            return {"value": None, "done": True}
        except Exception as e:
            # Re-raise the exception if it wasn't caught by the generator
            raise e

    def _is_async_generator(self):
        """Detect if this is wrapping an async generator"""
        # Use the metadata we stored during detection
        return hasattr(self, '_detected_as_async_generator') and self._detected_as_async_generator

    def __repr__(self):
        return f"SymbolIteratorWrapper({self.python_generator})"


def create_js_iterable(generator_or_value):
    """Create a JavaScript-compatible iterable from a Python generator or value"""
    from pyscript.ffi import to_js
    from js import window, eval as js_eval

    # Ensure helper function exists
    if not hasattr(window, 'crankPyCreateIterable'):
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

    # Convert generator to list of items
    if hasattr(generator_or_value, 'send') or hasattr(generator_or_value, '__next__'):
        items = list(generator_or_value)
    else:
        items = [generator_or_value]

    js_items = to_js(items)
    return window.crankPyCreateIterable(js_items)


def _create_micropython_context_iterator(context_obj):
    """Create a JavaScript object with Symbol.iterator for Context objects in MicroPython"""
    from js import eval as js_eval
    
    def get_current_props():
        """Get current props from context each time next() is called"""
        try:
            if hasattr(context_obj._js_context, 'props'):
                props = context_obj._js_context.props
                if props:
                    # Use simplified direct property access instead of JS evaluation
                    result = {}
                    common_props = ['name', 'value', 'id', 'className', 'onClick', 'onChange', 'children', 'delay', 'error', 'type', 'placeholder', 'disabled', 'checked', 'src', 'alt', 'href', 'target']
                    
                    for prop in common_props:
                        try:
                            if hasattr(props, prop):
                                prop_value = getattr(props, prop, None)
                                if prop_value is not None:
                                    result[prop] = prop_value
                        except:
                            pass
                    return result
                else:
                    return {}
            else:
                return {}
        except Exception:
            return {}
    
    def context_next():
        """Always return current props - never done for infinite iteration"""
        try:
            props = get_current_props()
            return {"value": props, "done": False}
        except Exception:
            return {"value": {}, "done": False}
    
    # Hybrid proxy: use appropriate strategy based on interpreter
    proxied_next = _create_proxy_hybrid(context_next)
    
    # Use JavaScript to create the wrapper object with Symbol.iterator
    js_code = """
    (function(nextFunc) {
        const obj = {};
        obj[Symbol.iterator] = function() {
            return {
                next: nextFunc
            };
        };
        return obj;
    })
    """
    
    js_func = js_eval(js_code)
    return js_func(proxied_next)


def _create_micropython_iterator_wrapper(python_generator, first_value):
    """Create a JavaScript object with Symbol.iterator that works in MicroPython"""
    from js import eval as js_eval
    
    # Create a simple next function that MicroPython can call
    first_value_consumed = [False]  # Use list for closure
    
    def python_next():
        try:
            # Handle first value if we have one cached
            if first_value is not None and not first_value_consumed[0]:
                first_value_consumed[0] = True
                return {"value": first_value, "done": False}
            
            # Get next value from generator - this should only be called when Crank.js wants it
            value = python_generator.__next__()
            return {"value": value, "done": False}
        except StopIteration:
            return {"value": None, "done": True}
        except Exception:
            return {"value": None, "done": True}
    
    # Hybrid proxy: use appropriate strategy based on interpreter
    proxied_next = _create_proxy_hybrid(python_next)
    
    # Use JavaScript to create the wrapper object with Symbol.iterator
    js_code = """
    (function(nextFunc) {
        const obj = {};
        obj[Symbol.iterator] = function() {
            return {
                next: nextFunc
            };
        };
        return obj;
    })
    """
    
    js_func = js_eval(js_code)
    return js_func(proxied_next)


def _create_controlled_thenable_wrapper(python_generator):
    """Create a thenable wrapper that only advances when Crank.js explicitly calls next()"""
    from js import eval as js_eval
    
    def python_next():
        try:
            # Only advance generator when explicitly called by Crank.js
            value = python_generator.__next__()
            return {"value": value, "done": False}
        except StopIteration:
            return {"value": None, "done": True}
        except Exception:
            return {"value": None, "done": True}
    
    # Create proxy for the next function
    proxied_next = _create_proxy_hybrid(python_next)
    
    # Create a thenable object that Crank.js can work with
    js_code = """
    (function(nextFunc) {
        const generator = {
            next: nextFunc,
            // Make it thenable by adding then() method
            then: function(resolve, reject) {
                try {
                    const result = nextFunc();
                    resolve(result);
                } catch (e) {
                    reject(e);
                }
            },
            // Add Symbol.iterator for proper iteration protocol
            [Symbol.iterator]: function() {
                return this;
            }
        };
        return generator;
    })
    """
    
    js_func = js_eval(js_code)
    return js_func(proxied_next)


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
                    # Simplified: Try direct property access for common props only
                    python_props = {}
                    # Common props that components typically use
                    common_props = ['name', 'value', 'id', 'className', 'onClick', 'onChange', 'children', 'delay', 'error', 'type', 'placeholder', 'disabled', 'checked', 'src', 'alt', 'href', 'target']
                    
                    for prop in common_props:
                        try:
                            if hasattr(props, prop):
                                prop_value = getattr(props, prop, None)
                                if prop_value is not None:
                                    python_props[prop] = prop_value
                        except:
                            # Ignore props we can't access
                            pass
                    
                except Exception:
                    # If any error occurs, fall back to empty props
                    python_props = {}
            else:
                python_props = {}

        def wrap_result(result):
            """Wrap generator results for JavaScript interop in MicroPython"""
            # Check if already wrapped to prevent double-wrapping
            if hasattr(result, '_is_symbol_iterator_wrapped'):
                return result

            # Check if we're in MicroPython and result needs wrapping
            if sys.implementation.name == 'micropython':
                # Check if this is a generator (MicroPython returns raw generators)
                if hasattr(result, '__next__'):
                    # Create a thenable wrapper that doesn't auto-advance
                    return _create_controlled_thenable_wrapper(result)
                # MicroPython async generator strategy:
                # Treat ALL generators as sync generators to avoid ThenableEvent issues

                is_generator_func = inspect.isgeneratorfunction(func) if hasattr(inspect, 'isgeneratorfunction') else False

                # If inspect says it's not a generator function, trust that
                if not is_generator_func:
                    # sync_function - return as-is
                    return result

                # Use non-destructive generator detection instead of calling next()
                if hasattr(result, '__next__'):
                    # Check if this is actually a generator using non-destructive methods
                    is_generator = False
                    try:
                        # Method 1: Use inspect.isgenerator if available
                        import inspect
                        if hasattr(inspect, 'isgenerator'):
                            is_generator = inspect.isgenerator(result)
                        else:
                            # Method 2: Use types.GeneratorType if available
                            import types
                            if hasattr(types, 'GeneratorType'):
                                is_generator = isinstance(result, types.GeneratorType)
                            else:
                                # Method 3: Check type string as fallback
                                is_generator = 'generator' in str(type(result)).lower()
                    except:
                        # Fallback: assume it's a generator if it has __next__
                        is_generator = True
                    
                    if is_generator:

                        # Determine if this is an async generator
                        # MicroPython limitation: async generators are converted to regular generators
                        # See: https://github.com/micropython/micropython/pull/6668
                        # See: https://github.com/micropython/micropython/issues/14331
                        is_async_generator = False

                        if sys.implementation.name == 'micropython':
                            # MicroPython does not support async generators (PEP 525)
                            # All generators are treated as sync regardless of async def syntax
                            is_async_generator = False
                        else:
                            # In full Python environments, check for async generator characteristics
                            try:
                                # Check if the generator has async iterator methods
                                has_anext = hasattr(result, '__anext__')
                                has_aiter = hasattr(result, '__aiter__')

                                # Check generator type for async characteristics
                                generator_type_name = str(type(result))
                                is_async_gen_type = 'async_generator' in generator_type_name.lower()

                                # If generator has clear async characteristics, it's async
                                if is_async_gen_type or has_anext or has_aiter:
                                    is_async_generator = True

                            except Exception:
                                # If detection fails, fall back to safe default
                                is_async_generator = False

                        # For MicroPython, create JavaScript-based iterator wrapper
                        # Return generator as-is - Crank.js handles iteration natively
                        return result
                    else:
                        # Not a generator despite having __next__ - return as-is
                        return result
                else:
                    # No __next__ method - not a generator result
                    return result

                # Non-generator results pass through unchanged
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

    # Hybrid proxy: use appropriate strategy based on interpreter
    return _create_proxy_hybrid(wrapper)

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
                processed[key] = _create_proxy_hybrid(value)
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

    def _is_micropython_runtime(self):
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
            if self._is_micropython_runtime():
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
                    processed[key] = _create_proxy_hybrid(value)
            elif isinstance(value, dict):
                # Recursively process nested dicts
                processed[key] = self._process_props_for_proxies(value)
            elif isinstance(value, (list, tuple)):
                # Process lists/tuples for callables
                processed_list = []
                for item in value:
                    if callable(item) and not (hasattr(item, 'toString') or str(type(item)).startswith("<class 'pyodide.ffi.JsProxy'>")):
                        # Hybrid proxy: use appropriate strategy based on interpreter
                        processed_list.append(_create_proxy_hybrid(item))
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
