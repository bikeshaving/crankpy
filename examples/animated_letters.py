"""
Animated Letters - Python translation of examples/animated-letters.js

Demonstrates stateful components with animations and lifecycle management.
"""

from crank import h, component
from crank.dom import renderer
from js import document, setInterval, clearInterval, requestAnimationFrame, Math
import random

def shuffle(arr):
    """Shuffle array in place"""
    for i in range(len(arr) - 1, 0, -1):
        j = Math.floor(Math.random() * (i + 1))
        arr[i], arr[j] = arr[j], arr[i]
    return arr

def get_random_letters():
    """Get random selection of letters"""
    alphabet = list('abcdefghijklmnopqrstuvwxyz')
    shuffle(alphabet)
    return sorted(alphabet[:Math.floor(Math.random() * len(alphabet))])

style = {
    'position': 'absolute',
    'top': '20px',
    'transition': 'transform 750ms, opacity 750ms'
}

def defer_transition_styles(callback):
    """Double requestAnimationFrame for smooth transitions"""
    def frame1():
        requestAnimationFrame(callback)
    requestAnimationFrame(frame1)

@component
def Letter(ctx):
    """Individual animated letter component"""
    
    def after_mount(node):
        """Animation when letter appears"""
        index = ctx.props.index
        node.style.transform = f'translate({index * 1.1}em, -20px)'
        node.style.opacity = '0'
        
        def animate_in():
            node.style.transform = f'translate({index * 1.1}em, 0)'
            node.style.opacity = '1'
            
        defer_transition_styles(animate_in)
    
    def before_unmount(node):
        """Animation when letter disappears"""
        index = ctx.props.index
        
        def animate_out():
            node.style.color = 'red'
            node.style.transform = f'translate({index * 1.1}em, 20px)'
            node.style.opacity = '0'
            
        defer_transition_styles(animate_out)
        
        # Return promise that resolves after animation
        return new Promise(lambda resolve: setTimeout(resolve, 750))
    
    # Set up lifecycle hooks
    ctx.after(after_mount)
    ctx.cleanup(before_unmount)
    
    first_render = True
    
    for _ in ctx:
        letter = ctx.props.letter
        index = ctx.props.index
        
        if not first_render:
            # Update position for existing letter
            def update_position(node):
                def animate():
                    node.style.transform = f'translate({index * 1.1}em, 0)'
                defer_transition_styles(animate)
            ctx.after(update_position)
        
        yield h.span(style={
            **style,
            'color': 'green' if first_render else 'black'
        })[letter]
        
        first_render = False

@component  
def Letters(ctx):
    """Container component that manages letter lifecycle"""
    
    def refresh_letters():
        ctx.refresh()
    
    # Set up interval to refresh letters
    interval = setInterval(refresh_letters, 1500)
    
    for _ in ctx:
        letters = get_random_letters()
        
        yield h.div(style='height: 40px')[
            *[h.Letter(crank_key=letter, letter=letter, index=i) 
              for i, letter in enumerate(letters)]
        ]
    
    # Cleanup interval when component unmounts
    clearInterval(interval)

# Render the component
async def main():
    await renderer.render(h.Letters[], document.body)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())