"""
Test the new props pattern with ctx.props and single ctx parameter
"""

from crank import h, component, Context, PropsProxy

def test_props_proxy():
    """Test PropsProxy dash-to-underscore conversion"""
    
    # Props with dashes (from HTML attributes)
    props_dict = {
        'data-id': '123',
        'aria-label': 'Button',
        'className': 'btn',
        'onClick': 'handler'
    }
    
    proxy = PropsProxy(props_dict)
    
    # Access with underscores (Python style)
    assert proxy.data_id == '123'
    assert proxy.aria_label == 'Button'
    
    # Access with original names
    assert proxy.className == 'btn'
    assert proxy.onClick == 'handler'
    
    # Dict-style access
    assert proxy.get('data_id') == '123'
    assert proxy.get('nonexistent', 'default') == 'default'
    
    # 'in' operator
    assert 'data_id' in proxy
    assert 'data-id' in proxy
    assert 'nonexistent' not in proxy
    
    print("✓ PropsProxy tests passed")


def test_single_ctx_parameter():
    """Test components with single ctx parameter"""
    
    @component
    def simple_component(ctx):
        return h.div[f"Hello {ctx.props.name or 'World'}"]
    
    @component
    def generator_component(ctx):
        count = 0
        for _ in ctx:
            count += 1
            yield h.div[
                h.span[f"Count: {count}"],
                h.p[f"Name: {ctx.props.name}"],
                h.button(
                    onClick=ctx.props.on_click,
                    data_id=ctx.props.data_id  # Can use Python underscore style
                )["Click me"]
            ]
    
    @component
    async def async_component(ctx):
        # Simulate async work
        import asyncio
        await asyncio.sleep(0.001)
        
        return h.div(className='async')[
            h.h2[ctx.props.title],
            h.p[f"User: {ctx.props.user_name}"]  # Underscore access
        ]
    
    print("✓ Component definitions work with single ctx parameter")


def test_error_on_wrong_signature():
    """Test that wrong signatures raise errors"""
    
    try:
        @component
        def bad_component(ctx, props):  # Should fail - 2 parameters
            return h.div["Bad"]
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "should only accept ctx parameter" in str(e)
        print("✓ Correctly rejects 2-parameter components")
    
    try:
        @component
        def bad_component2(ctx, props, extra):  # Should fail - 3 parameters
            return h.div["Bad"]
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "should only accept ctx parameter" in str(e)
        print("✓ Correctly rejects 3-parameter components")


def test_usage_examples():
    """Show clean usage examples"""
    
    @component
    def UserCard(ctx):
        return h.div(className='user-card', data_user_id=ctx.props.user_id)[
            h.img(src=ctx.props.avatar, alt='Avatar'),
            h.div(className='user-info')[
                h.h3[ctx.props.name],
                h.p[ctx.props.email],
                h.button(
                    onClick=ctx.props.on_view_profile,
                    aria_label=f"View {ctx.props.name}'s profile"
                )['View Profile']
            ]
        ]
    
    @component
    def Button(ctx):
        for _ in ctx:
            yield h.button(
                onClick=ctx.props.onClick,
                disabled=ctx.props.disabled or False,
                className=f"btn {ctx.props.variant or 'primary'}",
                data_testid=ctx.props.data_testid  # Underscore → dash conversion
            )[ctx.props.children or ctx.props.label or 'Button']
    
    @component
    async def LiveData(ctx):
        async for _ in ctx:
            # Simulate fetching live data
            import asyncio
            await asyncio.sleep(0.001)
            
            yield h.div(className='live-data')[
                h.h3['Live Data'],
                h.p[f"Source: {ctx.props.source}"],
                h.span[f"Refresh rate: {ctx.props.refresh_rate}s"]
            ]
    
    print("✓ Usage examples look clean and ergonomic")


if __name__ == '__main__':
    print("Testing Props Pattern")
    print("=" * 30)
    
    test_props_proxy()
    test_single_ctx_parameter()
    test_error_on_wrong_signature()
    test_usage_examples()
    
    print()
    print("All tests passed! 🎉")
    print()
    print("Clean usage pattern:")
    print("""
@component
def MyComponent(ctx):
    for _ in ctx:  # Always use _ for iteration
        yield h.div(className='component')[
            h.h2[ctx.props.title],
            h.p[ctx.props.description],
            h.button(
                onClick=ctx.props.on_click,
                data_id=ctx.props.data_id  # Underscore access works!
            )['Click me']
        ]
    """)