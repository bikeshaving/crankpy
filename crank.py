"""
Crank.py - Python wrapper for the Crank JavaScript framework

This module provides a Python bridge to Crank's component system using
async/await and generators to mirror JavaScript's async function* syntax.
"""

from typing import Any, Dict, List, Union, Optional, AsyncGenerator, Generator, Callable, Awaitable
import asyncio
from dataclasses import dataclass
from abc import ABC, abstractmethod

# PyScript imports for DOM and JS interop
from js import Symbol, document, window, fetch, console
import js


# Type aliases matching Crank's TypeScript types
Children = Union[str, int, float, bool, None, 'Element', List['Children']]
Props = Dict[str, Any]
Component = Union[
    Callable[['Context', Props], Children],
    Callable[['Context', Props], Awaitable[Children]],
    Callable[['Context', Props], Generator[Children, None, Optional[Children]]],
    Callable[['Context', Props], AsyncGenerator[Children, Optional[Children]]]
]


@dataclass
class Element:
    """Represents a Crank element (equivalent to JSX elements)"""
    tag: Union[str, Component]
    props: Props
    children: List[Children]
    
    def __post_init__(self):
        if self.children is None:
            self.children = []


class PropsProxy:
    """Proxy object for clean props access with dash-to-underscore conversion"""
    
    def __init__(self, props: Props):
        self._props = props or {}
        
    def __getattr__(self, name: str):
        """Convert underscores back to dashes when accessing props"""
        # Try underscore name first (for Python-style access)
        if name in self._props:
            return self._props[name]
        
        # Try dash version (for HTML attributes that were converted)
        dash_name = name.replace('_', '-')
        if dash_name in self._props:
            return self._props[dash_name]
            
        # Return None if not found (like dict.get())
        return None
    
    def get(self, key: str, default=None):
        """Dict-style access with dash conversion"""
        if key in self._props:
            return self._props[key]
        
        dash_key = key.replace('_', '-')
        return self._props.get(dash_key, default)
    
    def __contains__(self, key: str):
        """Support 'in' operator"""
        return key in self._props or key.replace('_', '-') in self._props
    
    def __repr__(self):
        return f"PropsProxy({self._props})"


class Context:
    """
    Crank Context equivalent - manages component lifecycle and state.
    
    Provides methods for:
    - Async scheduling and lifecycle management
    - Context provision/consumption
    - Event handling
    - Props access via ctx.props
    """
    
    def __init__(self):
        self._provisions: Dict[Any, Any] = {}
        self._scheduled_tasks: List[Awaitable] = []
        self._iteration_count = 0
        self.props: PropsProxy = PropsProxy({})  # Current props proxy
        
    def provide(self, key: Any, value: Any) -> None:
        """Provide a value to child components"""
        self._provisions[key] = value
        
    def consume(self, key: Any) -> Any:
        """Consume a provided value from parent components"""
        return self._provisions.get(key)
        
    def schedule(self, task: Awaitable) -> None:
        """Schedule an async task to run"""
        self._scheduled_tasks.append(task)
        
    async def flush_scheduled(self) -> None:
        """Execute all scheduled tasks"""
        if self._scheduled_tasks:
            await asyncio.gather(*self._scheduled_tasks)
            self._scheduled_tasks.clear()
            
    def __iter__(self):
        """Allow iteration over props updates (for generator components)"""
        # This would be implemented by the renderer
        return self
        
    def __next__(self):
        """Get next props update"""
        # This would be implemented by the renderer
        raise StopIteration
        
    async def __aiter__(self):
        """Allow async iteration over props updates"""
        # This would be implemented by the renderer
        return self
        
    async def __anext__(self):
        """Get next props update asynchronously"""
        # This would be implemented by the renderer
        raise StopAsyncIteration


def create_element(tag: Union[str, Component], props: Optional[Props] = None, *children: Children) -> Element:
    """
    Create a Crank element (equivalent to createElement/JSX).
    
    Args:
        tag: Component function or HTML tag name
        props: Properties to pass to the component
        *children: Child elements
        
    Returns:
        Element instance
    """
    if props is None:
        props = {}
        
    return Element(tag=tag, props=props, children=list(children))


# Single component decorator that auto-detects function type
def component(func: Callable) -> Component:
    """
    Universal component decorator that auto-detects function type.
    
    Supports:
    - Regular functions: def component(ctx) -> Children
    - Async functions: async def component(ctx) -> Children  
    - Generators: def component(ctx) -> Generator[Children, None, Optional[Children]]
    - Async generators: async def component(ctx) -> AsyncGenerator[Children, Optional[Children]]
    
    Usage:
        @component
        def my_component(ctx):
            return h.div['Hello World']
            
        @component  
        async def async_component(ctx):
            data = await fetch_data()
            return h.div[data]
            
        @component
        def stateful_component(ctx):
            for _ in ctx:
                yield h.div[f'Count: {ctx.props.count}']
                
        @component
        async def live_component(ctx):
            async for _ in ctx:
                data = await fetch_live_data(ctx.props.source)
                yield h.div[data]
    """
    import inspect
    
    # Check function signature - should only accept ctx
    sig = inspect.signature(func)
    if len(sig.parameters) != 1:
        raise ValueError(f"Component '{func.__name__}' should only accept ctx parameter, got {len(sig.parameters)} parameters")
    
    # Check if function is async
    is_async = inspect.iscoroutinefunction(func)
    
    # Check if function is generator by inspecting its code
    # This is a heuristic - functions with 'yield' are generators
    is_generator = 'yield' in inspect.getsource(func)
    
    if is_async and is_generator:
        # async function* equivalent
        return func  # Already an async generator
    elif is_generator:
        # function* equivalent  
        return func  # Already a generator
    elif is_async:
        # async function equivalent
        return func  # Already an async function
    else:
        # Regular function
        return func


# Legacy decorators for backward compatibility
def async_component(func: Callable) -> Component:
    """Legacy decorator - use @component instead"""
    return component(func)


def generator_component(func: Callable) -> Component:
    """Legacy decorator - use @component instead"""
    return component(func)


def async_generator_component(func: Callable) -> Component:
    """Legacy decorator - use @component instead"""
    return component(func)


# Special element types (exact JS Symbol.for interop for PyScript)
Fragment = ""  # Empty string for grouping children

# Use JavaScript Symbol.for for exact interop in PyScript
Portal = Symbol.for_("crank.Portal")  # For rendering into different root nodes
Copy = Symbol.for_("crank.Copy")      # Preserves previously rendered content  
Text = Symbol.for_("crank.Text")      # For explicit text nodes
Raw = Symbol.for_("crank.Raw")        # For injecting raw HTML/nodes




# Magic h element with JSX-like syntax
import inspect

class ElementBuilder:
    """Builder for individual elements with props and children syntax"""
    
    def __init__(self, tag: Union[str, Component]):
        self.tag = tag
        self.props = {}
    
    def __call__(self, **props):
        """Handle props: h.div(className='app')"""
        # Convert underscores to hyphens, leave camelCase alone
        converted_props = {}
        for key, value in props.items():
            converted_props[key.replace('_', '-')] = value
        
        new_builder = ElementBuilder(self.tag)
        new_builder.props = converted_props
        return new_builder
    
    def __getitem__(self, children):
        """Handle children: h.div[...] or h.div(props)[...]"""
        if not isinstance(children, (list, tuple)):
            children = [children]
        return create_element(self.tag, self.props, *children)


class MagicH:
    """Magic h object supporting h.element and component lookup"""
    
    def __getattr__(self, name: str):
        """
        Handle h.element syntax:
        - Lowercase: HTML elements (h.div, h.span)  
        - Uppercase: Component/symbol lookup (h.MyComponent, h.Fragment)
        """
        if name[0].isupper():
            # Uppercase: lookup component/symbol in caller's scope
            frame = inspect.currentframe().f_back
            locals_dict = frame.f_locals
            globals_dict = frame.f_globals
            
            # Try locals first, then globals
            if name in locals_dict:
                component = locals_dict[name]
                if callable(component) or hasattr(component, '__name__'):
                    return ElementBuilder(component)
            
            if name in globals_dict:
                component = globals_dict[name]
                if callable(component) or hasattr(component, '__name__'):
                    return ElementBuilder(component)
            
            # If not found, raise error
            raise NameError(f"Component or symbol '{name}' not found in scope")
        else:
            # Lowercase: HTML element
            return ElementBuilder(name)
    
    def __getitem__(self, children):
        """Fragment shorthand: h[...]"""
        if not isinstance(children, (list, tuple)):
            children = [children]
        return create_element(Fragment, None, *children)
    
    def __call__(self, *children, **props):
        """Fragment shorthand: h(...) or original h(tag, props, children) for backwards compatibility"""
        if len(children) == 0:
            # h() - empty fragment
            return create_element(Fragment, None)
        elif len(children) >= 1 and isinstance(children[0], (str, type(Fragment))) or callable(children[0]):
            # Backwards compatibility: h(tag, props, *children)
            tag = children[0]
            if len(children) >= 2 and isinstance(children[1], dict):
                # h(tag, props, *children)
                props_dict = children[1]
                child_elements = children[2:]
            else:
                # h(tag, *children) 
                props_dict = props if props else None
                child_elements = children[1:]
            return create_element(tag, props_dict, *child_elements)
        else:
            # h(children...) - fragment with children
            return create_element(Fragment, None, *children)


# Create the magic h instance
h = MagicH()

# Legacy function for backwards compatibility
def create_element_legacy(tag: Union[str, Component], props: Optional[Props] = None, *children: Children) -> Element:
    """Legacy hyperscript helper (shorthand for create_element)"""
    return create_element(tag, props, *children)


# JSX-style component creation
class JSX:
    """JSX-style helper class"""
    
    @staticmethod
    def create_element(tag: Union[str, Component], props: Optional[Props] = None, *children: Children) -> Element:
        return create_element(tag, props, *children)


# Export main API
__all__ = [
    'Children', 'Props', 'Component', 'Element', 'Context',
    'create_element', 'component', 
    'Fragment', 'Portal', 'Copy', 'Text', 'Raw',
    'h', 'JSX'
]