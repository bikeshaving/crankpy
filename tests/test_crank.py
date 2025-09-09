"""
Basic tests for Crank.py wrapper

Tests the core functionality and component patterns.
"""

import asyncio
import pytest
from crank import (
    Context, Element, create_element, component, async_component,
    generator_component, async_generator_component, Fragment, h
)


def test_create_element():
    """Test basic element creation"""
    el = create_element('div', {'class': 'test'}, 'Hello World')
    
    assert el.tag == 'div'
    assert el.props == {'class': 'test'}
    assert el.children == ['Hello World']


def test_element_with_no_props():
    """Test element creation without props"""
    el = create_element('span', None, 'text')
    
    assert el.tag == 'span'
    assert el.props == {}
    assert el.children == ['text']


def test_hyperscript_helper():
    """Test h() helper function"""
    el = h('button', {'onclick': 'click'}, 'Click me')
    
    assert isinstance(el, Element)
    assert el.tag == 'button'
    assert el.props['onclick'] == 'click'


def test_context_provide_consume():
    """Test context provision and consumption"""
    ctx = Context()
    
    ctx.provide('theme', 'dark')
    assert ctx.consume('theme') == 'dark'
    assert ctx.consume('nonexistent') is None


@pytest.mark.asyncio
async def test_context_scheduling():
    """Test async task scheduling in context"""
    ctx = Context()
    result = []
    
    async def task():
        result.append('executed')
    
    ctx.schedule(task())
    await ctx.flush_scheduled()
    
    assert result == ['executed']


def test_simple_component():
    """Test synchronous component"""
    @component
    def simple(ctx: Context, props):
        return f"Hello {props.get('name', 'World')}"
    
    ctx = Context()
    result = simple(ctx, {'name': 'Test'})
    
    assert result == "Hello Test"


@pytest.mark.asyncio
async def test_async_component():
    """Test async component"""
    @async_component
    async def async_comp(ctx: Context, props):
        await asyncio.sleep(0.01)  # Small delay
        return h('div', None, f"Async result: {props.get('value')}")
    
    ctx = Context()
    result = await async_comp(ctx, {'value': 42})
    
    assert isinstance(result, Element)
    assert result.tag == 'div'
    assert result.children == ['Async result: 42']


def test_generator_component():
    """Test generator component"""
    @generator_component
    def gen_comp(ctx: Context, props):
        count = 0
        # Simulate the context iteration (normally handled by renderer)
        props_updates = [{'increment': 1}, {'increment': 2}, {'increment': 3}]
        
        for update in props_updates:
            count += update.get('increment', 0)
            yield h('span', None, f'Count: {count}')
    
    ctx = Context()
    gen = gen_comp(ctx, {})
    
    results = list(gen)
    assert len(results) == 3
    assert results[0].children == ['Count: 1']
    assert results[1].children == ['Count: 3'] 
    assert results[2].children == ['Count: 6']


@pytest.mark.asyncio
async def test_async_generator_component():
    """Test async generator component"""
    @async_generator_component
    async def async_gen_comp(ctx: Context, props):
        count = 0
        # Simulate async updates
        for i in range(3):
            count += 1
            await asyncio.sleep(0.001)  # Tiny delay
            yield h('div', None, f'Async count: {count}')
    
    ctx = Context()
    gen = async_gen_comp(ctx, {})
    
    results = []
    async for result in gen:
        results.append(result)
    
    assert len(results) == 3
    assert results[0].children == ['Async count: 1']
    assert results[2].children == ['Async count: 3']


def test_fragment():
    """Test Fragment component"""
    result = Fragment()(Context(), {'children': ['a', 'b', 'c']})
    assert result == ['a', 'b', 'c']


def test_nested_elements():
    """Test nested element structures"""
    app = h('div', {'id': 'app'},
        h('header', None,
            h('h1', None, 'My App')
        ),
        h('main', None,
            h('p', None, 'Content here')
        )
    )
    
    assert app.tag == 'div'
    assert app.props['id'] == 'app'
    assert len(app.children) == 2
    
    header = app.children[0]
    assert header.tag == 'header'
    assert header.children[0].tag == 'h1'


def test_component_as_element_tag():
    """Test using a component function as element tag"""
    @component
    def my_component(ctx: Context, props):
        return h('span', None, props.get('text'))
    
    el = h(my_component, {'text': 'Hello'})
    assert el.tag == my_component
    assert el.props['text'] == 'Hello'


if __name__ == '__main__':
    import sys
    
    # Run basic tests
    test_create_element()
    test_element_with_no_props() 
    test_hyperscript_helper()
    test_context_provide_consume()
    test_simple_component()
    test_generator_component()
    test_fragment()
    test_nested_elements()
    test_component_as_element_tag()
    
    print("✓ All synchronous tests passed!")
    
    # Run async tests
    async def run_async_tests():
        await test_context_scheduling()
        await test_async_component()
        await test_async_generator_component()
        print("✓ All async tests passed!")
    
    asyncio.run(run_async_tests())
    
    print("✓ All tests completed successfully!")