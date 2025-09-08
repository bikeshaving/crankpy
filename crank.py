"""
Crank.py - Python wrapper for the Crank JavaScript framework

This module provides a Python bridge to Crank's component system using
async/await and generators to mirror JavaScript's async function* syntax.
"""

from typing import Any, Dict, List, Union, Optional, AsyncGenerator, Generator, Callable, Awaitable
import asyncio
from dataclasses import dataclass
from abc import ABC, abstractmethod


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


class Context:
    """
    Crank Context equivalent - manages component lifecycle and state.
    
    Provides methods for:
    - Async scheduling and lifecycle management
    - Context provision/consumption
    - Event handling
    """
    
    def __init__(self):
        self._provisions: Dict[Any, Any] = {}
        self._scheduled_tasks: List[Awaitable] = []
        self._iteration_count = 0
        
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


# Component decorators for different component types
def component(func: Callable) -> Component:
    """Decorator for synchronous components"""
    return func


def async_component(func: Callable) -> Component:
    """Decorator for async components"""
    return func


def generator_component(func: Callable) -> Component:
    """Decorator for generator components"""
    return func


def async_generator_component(func: Callable) -> Component:
    """Decorator for async generator components"""
    return func


# Built-in components
class Fragment:
    """Fragment component for grouping children"""
    @staticmethod
    def __call__(ctx: Context, props: Props) -> Children:
        return props.get('children', [])


# Async utilities (equivalent to Crank's async module)
def lazy(initializer: Callable[[], Awaitable[Component]]) -> Component:
    """
    Create a lazy-loaded component.
    
    Args:
        initializer: Function that returns a Promise resolving to a component
        
    Returns:
        Component that loads the target component on first render
    """
    async def lazy_component(ctx: Context, props: Props) -> AsyncGenerator[Children, None]:
        component_class = await initializer()
        
        # Handle module with default export
        if isinstance(component_class, dict) and 'default' in component_class:
            component_class = component_class['default']
            
        if not callable(component_class):
            raise ValueError("Lazy component initializer must return a Component")
            
        async for updated_props in ctx:
            yield create_element(component_class, updated_props)
            
    return lazy_component


async def suspense(ctx: Context, props: Props) -> AsyncGenerator[Children, None]:
    """
    Suspense component for handling loading states.
    
    Args:
        ctx: Component context
        props: Must include 'children' and 'fallback'
    """
    children = props.get('children')
    fallback = props.get('fallback')
    timeout = props.get('timeout', 300)  # milliseconds
    
    if fallback:
        # Show fallback first
        yield fallback
        
        # Wait for timeout
        await asyncio.sleep(timeout / 1000)
    
    # Then show children
    yield children


# Example usage and helper functions
def h(tag: Union[str, Component], props: Optional[Props] = None, *children: Children) -> Element:
    """Hyperscript helper (shorthand for create_element)"""
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
    'create_element', 'component', 'async_component', 'generator_component', 'async_generator_component',
    'Fragment', 'lazy', 'suspense', 'h', 'JSX'
]