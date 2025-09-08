"""
Test the new magic h syntax with JSX-like features
"""

from crank import h, component, Context, Fragment, Portal

def test_html_elements():
    """Test lowercase HTML elements"""
    # Simple element with no props
    el1 = h.div['Hello World']
    print("h.div['Hello World']:", el1)
    
    # Element with props
    el2 = h.div(className='container', id='main')['Content']
    print("h.div(className='container'):", el2)
    
    # Underscore to hyphen conversion
    el3 = h.input(data_id='user', aria_label='Username')
    print("h.input(data_id='user'):", el3)


def test_components():
    """Test uppercase component lookup"""
    
    @component
    def MyButton(ctx, props):
        return h.button(className='btn')[props.get('label', 'Click')]
    
    @component  
    def MyApp(ctx, props):
        return h.div(className='app')[
            h.h1['My App'],
            h.MyButton(label='Submit'),  # Should auto-resolve MyButton
            h.Fragment[                  # Should auto-resolve Fragment
                h.p['Fragment content'],
                h.span['More content']
            ]
        ]
    
    # Test the app
    ctx = Context()
    result = MyApp(ctx, {})
    print("MyApp result:", result)


def test_fragment_shorthand():
    """Test h[] and h() fragment syntax"""
    
    # h[] syntax
    frag1 = h[
        h.p['First'],
        h.p['Second']
    ]
    print("h[...] fragment:", frag1)
    
    # h() syntax  
    frag2 = h(
        h.span['Item 1'],
        h.span['Item 2']
    )
    print("h(...) fragment:", frag2)


def test_nested_structure():
    """Test complex nested structure"""
    
    @component
    def UserCard(ctx, props):
        user = props.get('user', {})
        return h.div(className='user-card', data_user_id=user.get('id'))[
            h.img(src=user.get('avatar'), alt='Avatar'),
            h.div(className='user-info')[
                h.h3[user.get('name')],
                h.p[user.get('email')],
                h.button(onClick='viewProfile')['View Profile']
            ]
        ]
    
    @component
    def UserList(ctx, props):
        users = props.get('users', [])
        return h.div(className='user-list')[
            h.h2['Users'],
            h[  # Fragment for list items
                *[h.UserCard(user=user) for user in users]
            ]
        ]
    
    # Test with sample data
    sample_users = [
        {'id': 1, 'name': 'John', 'email': 'john@example.com', 'avatar': '/avatar1.jpg'},
        {'id': 2, 'name': 'Jane', 'email': 'jane@example.com', 'avatar': '/avatar2.jpg'},
    ]
    
    ctx = Context()
    result = UserList(ctx, {'users': sample_users})
    print("UserList result:", result)


def test_backwards_compatibility():
    """Test backwards compatibility with old h() syntax"""
    
    # Old style should still work
    old_style = h('div', {'className': 'old'}, 'Old style')
    print("Old h() syntax:", old_style)
    
    # New style
    new_style = h.div(className='new')['New style']  
    print("New h.div syntax:", new_style)


if __name__ == '__main__':
    print("Testing Magic H Syntax")
    print("=" * 40)
    
    test_html_elements()
    print()
    
    test_components()
    print()
    
    test_fragment_shorthand() 
    print()
    
    test_nested_structure()
    print()
    
    test_backwards_compatibility()
    print()
    
    print("All tests completed!")