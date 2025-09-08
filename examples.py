"""
Examples demonstrating Crank.py usage

Shows how to create components using Python's async/generator features
that mirror Crank's JavaScript async function* components.
"""

import asyncio
from crank import (
    Context, h, component, Fragment, Portal
)


# Simple synchronous component  
@component
def greeting(ctx: Context, props):
    name = props.get('name', 'World')
    return h.span[f"Hello, {name}!"]


# Async component that fetches data
@component
async def user_profile(ctx: Context, props):
    user_id = props.get('user_id')
    
    # Simulate API call
    await asyncio.sleep(0.1)
    user_data = {'name': f'User {user_id}', 'email': f'user{user_id}@example.com'}
    
    return h.div(className='profile')[
        h.h2[user_data['name']],
        h.p[user_data['email']]
    ]


# Generator component for stateful behavior
@component
def counter(ctx: Context, props):
    count = 0
    
    for updated_props in ctx:
        increment = updated_props.get('increment', 1)
        count += increment
        
        yield h.div(className='counter')[
            h.span[f'Count: {count}'],
            h.button(onClick='increment')['Increment']
        ]


# Async generator component (most powerful)
@component
async def live_data(ctx: Context, props):
    """Component that updates with live data"""
    
    async for updated_props in ctx:
        # Simulate fetching fresh data
        await asyncio.sleep(0.5)
        
        data_source = updated_props.get('source', 'default')
        fresh_data = f"Live data from {data_source} at {asyncio.get_event_loop().time():.2f}"
        
        yield h('div', {'class': 'live-data'},
            h('h3', None, 'Live Data'),
            h('p', None, fresh_data),
            h('small', None, f'Source: {data_source}')
        )


# Timer component using async generator
@component  
async def timer(ctx: Context, props):
    """Timer that updates every second"""
    start_time = asyncio.get_event_loop().time()
    
    async for updated_props in ctx:
        interval = updated_props.get('interval', 1.0)
        
        while True:
            current_time = asyncio.get_event_loop().time()
            elapsed = current_time - start_time
            
            yield h('div', {'class': 'timer'},
                h('h3', None, 'Timer'),
                h('p', None, f'Elapsed: {elapsed:.1f}s')
            )
            
            await asyncio.sleep(interval)


# Lazy loaded component
async def load_heavy_component():
    """Simulate loading a heavy component"""
    await asyncio.sleep(2)  # Simulate bundle loading
    
    @component
    def heavy_component(ctx: Context, props):
        return h('div', {'class': 'heavy'},
            h('h2', None, 'Heavy Component Loaded!'),
            h('p', None, 'This component was loaded asynchronously.')
        )
    
    return heavy_component


# Using lazy loading
lazy_heavy = lazy(load_heavy_component)


# App component demonstrating composition
@component
async def app(ctx: Context, props):
    """Main application component"""
    
    async for updated_props in ctx:
        user_id = updated_props.get('user_id', 1)
        
        yield h('div', {'class': 'app'},
            h('header', None,
                h('h1', None, 'Crank.py Demo App')
            ),
            
            h('main', None,
                # Simple greeting
                h(greeting, {'name': 'Crank.py'}),
                
                # Async user profile
                h(suspense, {
                    'fallback': h('div', None, 'Loading user profile...'),
                    'children': h(user_profile, {'user_id': user_id})
                }),
                
                # Stateful counter
                h(counter, {'increment': 2}),
                
                # Live updating data
                h(live_data, {'source': 'websocket'}),
                
                # Timer
                h(timer, {'interval': 0.5}),
                
                # Lazy loaded component
                h(suspense, {
                    'fallback': h('div', None, 'Loading heavy component...'),
                    'children': h(lazy_heavy, {})
                })
            ),
            
            h('footer', None,
                h('p', None, 'Powered by Crank.py')
            )
        )


# Higher-order component example
def with_loading(component_func):
    """HOC that adds loading state"""
    
    @component
    async def wrapper(ctx: Context, props):
        loading = True
        
        async for updated_props in ctx:
            if loading:
                yield h('div', {'class': 'loading'}, 'Loading...')
                await asyncio.sleep(0.1)  # Brief loading state
                loading = False
            
            # Render the wrapped component
            yield h(component_func, updated_props)
    
    return wrapper


# Use the HOC
@with_loading
@component
def slow_component(ctx: Context, props):
    return h('div', None, 'Slow component loaded!')


# Custom hook equivalent using classes
class UseState:
    """State management hook equivalent"""
    
    def __init__(self, initial_value):
        self.value = initial_value
        self.listeners = []
    
    def set_value(self, new_value):
        self.value = new_value
        # Notify listeners (would trigger re-render in real implementation)
        for listener in self.listeners:
            listener()
    
    def subscribe(self, listener):
        self.listeners.append(listener)


# Component using "hooks"
@component
def stateful_component(ctx: Context, props):
    state = UseState(0)
    
    for updated_props in ctx:
        yield h('div', None,
            h('p', None, f'State value: {state.value}'),
            h('button', {
                'onclick': lambda: state.set_value(state.value + 1)
            }, 'Increment State')
        )


if __name__ == '__main__':
    print("Crank.py Examples")
    print("=================")
    print()
    print("This file demonstrates various component patterns:")
    print("- Simple synchronous components")
    print("- Async components with data fetching") 
    print("- Generator components for state")
    print("- Async generator components for live updates")
    print("- Lazy loading with suspense")
    print("- Higher-order components")
    print("- Custom hooks equivalent")
    print()
    print("To use these components, you'd need a renderer that")
    print("can execute the component functions and handle the")
    print("async/generator protocols.")