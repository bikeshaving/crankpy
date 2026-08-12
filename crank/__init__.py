"""Crank.py - Python components for the Crank JavaScript framework.

Element construction is pure Python. The `h` builder makes `El` nodes,
which hold a tag, props, and children as plain Python data. The
`to_element` function transforms an `El` tree into Crank `createElement`
calls. This transform runs at two boundaries:

- when a renderer receives a tree (see crank.dom and crank.html)
- when a component returns or yields a tree

Because no JavaScript object is made during construction, the same
builder code runs on Pyodide and on MicroPython.
"""

import inspect
import sys

from js import Array, Object, Reflect
from pyscript.ffi import create_proxy
from pyscript.js_modules import crank_core as crank

_is_micropython = sys.implementation.name == "micropython"

# Typing imports, with a stub fallback for MicroPython. The static view
# (TYPE_CHECKING) is plain typing; the runtime view degrades gracefully.
TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from typing import Any, Dict, Generic, TypeVar, Union

    T = TypeVar("T", bound=dict[str, Any])
    TResult = TypeVar("TResult")
    Props = dict[str, Any]
    Children = Union[str, "El", bool, None, Iterable["Children"]]
    _ContextBase = Generic[T, TResult]
else:
    try:
        from collections.abc import Callable, Iterable
        from typing import Any, Dict, Generic, TypeVar, Union
    except ImportError:
        if not _is_micropython:
            raise
        from .typing_stub import (
            Any,
            Callable,
            Dict,
            Generic,
            Iterable,
            TypeVar,
            Union,
        )

    try:
        T = TypeVar("T", bound=Dict[str, Any])
        TResult = TypeVar("TResult")
        Props = Dict[str, Any]
        Children = Union[str, "El", bool, None, Iterable["Children"]]
        _ContextBase = Generic[T, TResult]
    except TypeError:
        # MicroPython cannot subscript typing constructs
        T = TypeVar("T")
        TResult = TypeVar("TResult")
        Props = dict
        Children = object
        _ContextBase = object

# Re-export Crank classes directly
Element = crank.Element
createElement = crank.createElement
Fragment = crank.Fragment
Portal = crank.Portal
Copy = crank.Copy
Raw = crank.Raw
Text = crank.Text

if _is_micropython:
    _JsProxy = None
else:
    from pyodide.ffi import JsProxy as _JsProxy

    from ._asyncgen import wrap_async_generator as _wrap_async_generator


def _create_proxy(func):
    """Proxy a Python callable for JavaScript. MicroPython passes functions directly."""
    if _is_micropython:
        return func
    return create_proxy(func)


def _js_to_python_dict(js_obj):
    """Convert a JavaScript object to a Python dict on either runtime."""
    if js_obj is None:
        return {}
    if isinstance(js_obj, dict):
        return js_obj
    if hasattr(js_obj, "to_py"):
        return js_obj.to_py()
    if not hasattr(js_obj, "hasOwnProperty"):
        # Not a JavaScript object, for example a mock in a direct call
        return {}

    # MicroPython has no to_py(). Walk own properties by hand. Do not
    # filter callable values: functions, arrays, and elements are all
    # callable proxies on MicroPython, and all of them are valid props.
    result = {}
    for prop_name in dir(js_obj):
        if js_obj.hasOwnProperty(prop_name):
            result[prop_name] = getattr(js_obj, prop_name)
    return result


# --- Pure Python element tree ---------------------------------------------


class El:
    """A plain Python element node: tag, props, and children."""

    __slots__ = ("tag", "props", "children")

    def __init__(self, tag, props, children):
        self.tag = tag
        self.props = props
        self.children = children

    def __repr__(self):
        tag = (
            self.tag
            if isinstance(self.tag, str)
            else getattr(self.tag, "__name__", self.tag)
        )
        return f"El({tag!r}, props={self.props!r}, children={len(self.children)})"


def _convert_props(tag, props):
    """Convert prop names for a tag. HTML attributes get kebab-case names."""
    if isinstance(tag, str):
        return {key.replace("_", "-"): value for key, value in props.items()}
    return dict(props)


class ElementBuilder:
    """Builds `El` nodes for one tag or component.

    h.div                     -> builder (renders as an empty element)
    h.div["text"]             -> El
    h.div(id="a")             -> builder with props
    h.div(id="a")["text"]     -> El with props and children
    h.div(id="a", "text")     -> El (children as positional args)
    """

    __slots__ = ("tag", "props")

    def __init__(self, tag, props=None):
        self.tag = tag
        self.props = props

    def __call__(self, *children, **props):
        merged = dict(self.props) if self.props else {}
        merged.update(_convert_props(self.tag, props))

        if children:
            return El(self.tag, merged or None, list(children))
        return ElementBuilder(self.tag, merged or None)

    def __getitem__(self, children):
        if isinstance(children, tuple):
            children = list(children)
        elif not isinstance(children, list):
            children = [children]
        return El(self.tag, self.props, children)

    def __repr__(self):
        tag = (
            self.tag
            if isinstance(self.tag, str)
            else getattr(self.tag, "__name__", self.tag)
        )
        return f"ElementBuilder({tag!r}, props={self.props!r})"


class MagicH:
    """
    Pythonic HyperScript - Supported Patterns

    1. Simple elements with text:
        h.div["Hello World"]

    2. Elements with props:
        h.input(type="text", value=text)
        h.div(className="my-class")["Content"]

    3. Props with snake_case -> kebab-case conversion:
        h.div(data_test_id="button", aria_hidden="true")["Content"]

    4. Props spreading:
        h.button(className="btn", **user_props)["Click me"]

    5. Nested elements:
        h.ul[
            h.li["Item 1"],
            h.li["Item 2"],
        ]

    6. Components:
        h(MyComponent)
        h(MyComponent, prop1="value")["children"]

    7. Fragments:
        h(Fragment)["children"]
        h("", key="frag")["children"]

    8. Dynamic tags:
        h[tag_name]["children"]
    """

    def __getattr__(self, name: str):
        return ElementBuilder(name)

    def __getitem__(self, tag_or_component):
        if isinstance(tag_or_component, (str, JsComponent)) or callable(
            tag_or_component
        ):
            return ElementBuilder(tag_or_component)
        raise ValueError(
            f"h[{tag_or_component!r}] expects a string tag name or callable component"
        )

    def __call__(self, tag, *args, **kwargs):
        if tag is None:
            raise ValueError("h(None) is not a valid element tag")
        if isinstance(tag, str) and tag == "":
            tag = Fragment

        # Old syntax: h(tag, {props}, *children)
        if args and isinstance(args[0], dict) and not kwargs:
            props = args[0]
            children = args[1:]
        else:
            props = kwargs
            children = args

        builder = ElementBuilder(tag, _convert_props(tag, props) or None)
        if children:
            return builder[list(children)]
        return builder


h = MagicH()


# --- JavaScript components on MicroPython ----------------------------------
#
# The MicroPython FFI wraps a JavaScript function in a new function when it
# passes through Python. The wrapper does not forward `this`, and Crank calls
# components with `this` set to the Context. So a JavaScript component (for
# example Suspense) breaks when its function makes a Python round trip.
#
# The fix: never round-trip the function. At import time, a JavaScript helper
# copies the export into a JavaScript-side Map. Python holds only a string
# key, and another helper makes the createElement call on the JavaScript side.


class JsComponent:
    """A key that points to a JavaScript component stored on the JS side."""

    __slots__ = ("key",)

    def __init__(self, key):
        self.key = key

    def __repr__(self):
        return f"JsComponent({self.key!r})"


if _is_micropython:
    from js import Function as _JsFunction

    _js_tags = _JsFunction.new("return new Map()")()
    _js_store_tag = _JsFunction.new(
        "tags", "mod", "name", "key", "tags.set(key, mod[name])"
    )
    _js_create_with_tag = _JsFunction.new(
        "ce",
        "tags",
        "key",
        "props",
        "children",
        "return ce(tags.get(key), props, ...children)",
    )


def js_component(module, name):
    """Import a JavaScript component so that it works on both runtimes."""
    if not _is_micropython:
        return getattr(module, name)
    key = f"{name}@{id(module)}"
    _js_store_tag(_js_tags, module, name, key)
    return JsComponent(key)


# --- Transform: Python tree to Crank elements ------------------------------


def _proxy_if_callable(value):
    if callable(value) and (_JsProxy is None or not isinstance(value, _JsProxy)):
        return _create_proxy(value)
    return value


def _prop_value_to_js(value):
    # Elements can appear in props, for example Suspense fallback and children
    if isinstance(value, (El, ElementBuilder)):
        return to_element(value)
    if isinstance(value, dict):
        return _dict_to_js_object(value)
    if isinstance(value, (list, tuple)):
        array = Array.new()
        for item in value:
            array.push(_prop_value_to_js(item))
        return array
    return _proxy_if_callable(value)


def _dict_to_js_object(props):
    """Build a plain JavaScript object. Both runtimes get the same shape."""
    obj = Object.new()
    for key, value in props.items():
        Reflect.set(obj, key, _prop_value_to_js(value))
    return obj


def _child_to_js(child):
    if isinstance(child, (El, ElementBuilder)):
        return to_element(child)
    if isinstance(child, (list, tuple)):
        array = Array.new()
        for item in child:
            array.push(_child_to_js(item))
        return array
    return child


def to_element(node):
    """Transform a Python element tree into Crank elements.

    Strings, numbers, None, and JavaScript elements pass through unchanged.
    A bare list or tuple becomes a Fragment.
    """
    if isinstance(node, ElementBuilder):
        node = El(node.tag, node.props, [])
    if isinstance(node, El):
        js_props = _dict_to_js_object(node.props) if node.props else None
        if isinstance(node.tag, JsComponent):
            children = Array.new()
            for child in node.children:
                children.push(_child_to_js(child))
            return _js_create_with_tag(
                createElement, _js_tags, node.tag.key, js_props, children
            )
        return createElement(
            node.tag, js_props, *[_child_to_js(c) for c in node.children]
        )
    if isinstance(node, (list, tuple)):
        return createElement(Fragment, None, *[_child_to_js(c) for c in node])
    return node


class Renderer:
    """Wraps a Crank renderer. Transforms Python element trees before render."""

    def __init__(self, js_renderer):
        self._js_renderer = js_renderer

    def render(self, children, root=None, ctx=None):
        if ctx is not None:
            return self._js_renderer.render(to_element(children), root, ctx)
        return self._js_renderer.render(to_element(children), root)

    def __getattr__(self, name):
        return getattr(self._js_renderer, name)


# --- Context ----------------------------------------------------------------


class Context(_ContextBase):
    """Wrapper for the Crank Context with Python conveniences."""

    def __init__(self, js_context):
        self._js_context = js_context

    def _js_method(self, name) -> Any:
        """Get a bound method from the JavaScript context, or None."""
        method = getattr(self._js_context, name, None)
        if method is None:
            return None
        bind = getattr(method, "bind", None)
        if bind is not None:
            return bind(self._js_context)
        return method

    def refresh(self, func=None):
        """Use as a method call, ctx.refresh(), or as a decorator, @ctx.refresh."""
        if func is None:
            return self._js_method("refresh")()
        return self._register_callback(func, self._js_method("refresh"))

    def _register_callback(self, func, callback_method):
        """Register a callback with a wrapper that adapts to its arity."""
        if callback_method and callable(func):
            try:
                param_count = len(inspect.signature(func).parameters)
            except (AttributeError, ValueError):
                # MicroPython has no inspect.signature
                param_count = None

            def variadic_wrapper(*args):
                if param_count == 0 or not args:
                    return func()
                if param_count is not None:
                    return func(args[0])
                # MicroPython: arity is unknown, so probe
                try:
                    return func(args[0])
                except TypeError:
                    return func()

            callback_method(_create_proxy(variadic_wrapper))
        return func

    def schedule(self, func):
        """Decorator. Run the callback before rendering."""
        return self._register_callback(func, self._js_method("schedule"))

    def after(self, func):
        """Decorator. Run the callback after rendering."""
        return self._register_callback(func, self._js_method("after"))

    def cleanup(self, func):
        """Decorator. Run the callback when the component unmounts."""
        return self._register_callback(func, self._js_method("cleanup"))

    def provide(self, *args, **kwargs):
        return self._js_method("provide")(*args, **kwargs)

    def consume(self, *args, **kwargs):
        return self._js_method("consume")(*args, **kwargs)

    def __iter__(self):
        for js_props in self._js_context:
            yield _js_to_python_dict(js_props)

    def __aiter__(self):
        return self._async_iterator()

    async def _async_iterator(self):
        async for js_props in self._js_context:
            yield _js_to_python_dict(js_props)

    @property
    def props(self) -> T:
        return _js_to_python_dict(self._js_context.props)  # type: ignore[return-value]


# --- Component results across the FFI ---------------------------------------


def _wrap_generator(gen):
    """Delegate to a component generator and transform each yielded tree."""
    send_value = None
    throw_exc = None
    while True:
        try:
            if throw_exc is not None:
                exc, throw_exc = throw_exc, None
                yielded = gen.throw(exc)
            else:
                yielded = gen.send(send_value)
        except StopIteration as stop:
            return to_element(getattr(stop, "value", None))
        try:
            send_value = yield to_element(yielded)
        except BaseException as exc:
            throw_exc = exc


async def _wrap_coroutine(coro):
    return to_element(await coro)


class MicroPythonGeneratorWrapper:
    """Adapt a Python generator to the JavaScript iterator protocol.

    MicroPython proxies do not expose Symbol.iterator, so Crank drives
    this object through its next/throw/return methods.
    """

    def __init__(self, python_generator):
        self.python_generator = python_generator

    def next(self, value=None):
        try:
            if value is None:
                result = next(self.python_generator)
            else:
                result = self.python_generator.send(value)
            return {"value": to_element(result), "done": False}
        except StopIteration as e:
            return {"value": to_element(getattr(e, "value", None)), "done": True}

    def throw(self, exception):
        try:
            result = self.python_generator.throw(exception)
            return {"value": to_element(result), "done": False}
        except StopIteration as e:
            return {"value": to_element(getattr(e, "value", None)), "done": True}

    def return_(self, value=None):
        try:
            self.python_generator.close()
        except GeneratorExit:
            pass
        return {"value": value, "done": True}

    def __iter__(self):
        # Make the wrapper awaitable from Python. On MicroPython an async
        # function is a generator, and await drives it through __iter__.
        return self.python_generator


# JavaScript expects a method named 'return', which is a Python keyword
setattr(MicroPythonGeneratorWrapper, "return", MicroPythonGeneratorWrapper.return_)


def _adapt_result(result):
    """Prepare a component result for Crank."""
    if _is_micropython:
        # Async generators do not exist on MicroPython. Async functions
        # produce generator-like objects, which this wrapper also drives.
        if inspect.isgenerator(result):
            return MicroPythonGeneratorWrapper(result)
        return to_element(result)

    if inspect.isgenerator(result):
        return _wrap_generator(result)
    if inspect.isasyncgen(result):
        return _wrap_async_generator(result, to_element)
    if inspect.iscoroutine(result):
        return _wrap_coroutine(result)
    return to_element(result)


def component(func: Callable) -> Callable:
    """Adapt a Python function to a Crank component.

    The function can take 0 parameters, 1 (ctx), or 2 (ctx, props).
    """
    cached_param_count = None

    try:
        cached_param_count = len(inspect.signature(func).parameters)
        if cached_param_count > 2:
            raise ValueError(
                f"Component function {getattr(func, '__name__', '<anonymous>')} "
                f"must take 0, 1 (ctx), or 2 (ctx, props) parameters."
            )
    except AttributeError:
        # MicroPython has no inspect.signature. Arity is probed on first call.
        pass

    def wrapper(js_props, js_ctx):
        nonlocal cached_param_count
        ctx = Context(js_ctx)

        if cached_param_count is not None:
            if cached_param_count == 0:
                return _adapt_result(func())
            if cached_param_count == 1:
                return _adapt_result(func(ctx))
            props = _js_to_python_dict(js_props)
            return _adapt_result(func(ctx, props))

        # MicroPython: probe arity on the first call. A call with the
        # wrong arity raises TypeError before the function body runs.
        props = _js_to_python_dict(js_props)
        for count in (2, 1, 0):
            try:
                if count == 2:
                    result = func(ctx, props)
                elif count == 1:
                    result = func(ctx)
                else:
                    result = func()
            except TypeError as e:
                message = str(e).lower()
                is_arity_error = any(
                    phrase in message
                    for phrase in ("takes", "positional argument", "missing", "given")
                )
                if is_arity_error and count > 0:
                    continue
                cached_param_count = count
                raise
            cached_param_count = count
            return _adapt_result(result)

        raise ValueError(
            f"Component function {getattr(func, '__name__', '<anonymous>')} "
            f"must take 0, 1 (ctx), or 2 (ctx, props) parameters."
        )

    return _create_proxy(wrapper)


__all__ = [
    "Children",
    "Context",
    "Copy",
    "El",
    "Element",
    "Fragment",
    "JsComponent",
    "Portal",
    "Props",
    "Raw",
    "Renderer",
    "Text",
    "component",
    "crank",
    "createElement",
    "h",
    "js_component",
    "to_element",
]
