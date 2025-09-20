"""
Animated Letters - Example showing dynamic letter animations
"""

import random
from crank import h, component
from crank.dom import renderer
from js import document, requestAnimationFrame, setTimeout, Promise

def shuffle(arr):
    """Shuffle array in place and return it."""
    arr_copy = arr[:]
    for i in range(len(arr_copy) - 1, 0, -1):
        j = random.randint(0, i)
        arr_copy[i], arr_copy[j] = arr_copy[j], arr_copy[i]
    return arr_copy


def get_random_letters():
    """Get a random subset of letters from the alphabet, sorted."""
    alphabet = list("abcdefghijklmnopqrstuvwxyz")
    shuffled = shuffle(alphabet)
    count = random.randint(1, len(alphabet))
    return sorted(shuffled[:count])


def defer_transition_styles(callback):
    """Defer style changes to next animation frame."""
    def inner():
        requestAnimationFrame(callback)
    requestAnimationFrame(inner)


base_style = {
    "position": "absolute",
    "top": "20px",
    "transition": "transform 750ms, opacity 750ms",
}


@component 
def Letter(ctx, props):
    """Component for individual animated letter."""
    letter = props.get("letter", "")
    index = props.get("index", 0)
    
    # After hook for entrance animation
    @ctx.after
    def after_mount(node):
        node.style.transform = f"translate({index * 1.1}em, -20px)"
        node.style.opacity = "0"
        defer_transition_styles(lambda: (
            setattr(node.style, "transform", f"translate({index * 1.1}em, 0)"),
            setattr(node.style, "opacity", "1")
        ))
    
    # Cleanup hook for exit animation
    @ctx.cleanup
    def cleanup_handler(node):
        def animate_out():
            node.style.color = "red"
            node.style.transform = f"translate({index * 1.1}em, 20px)"
            node.style.opacity = "0"
        
        defer_transition_styles(animate_out)
        # Return a promise that resolves after animation
        return Promise.new(lambda resolve, reject: setTimeout(resolve, 750))
    
    # Initial render with green color
    yield h.span(style={
        **base_style,
        "color": "green",
    })[letter]
    
    # Subsequent renders with black color and position updates
    for props in ctx:
        letter = props.get("letter", "")
        index = props.get("index", 0)
        
        @ctx.after
        def update_position(node):
            defer_transition_styles(lambda: setattr(node.style, "transform", f"translate({index * 1.1}em, 0)"))
        
        yield h.span(style={**base_style, "color": "black"})[letter]


@component
def Letters(ctx):
    """Container component that manages random letters."""
    # Set up interval for refreshing
    interval = setInterval(lambda: ctx.refresh(), 1500)
    
    # Clean up interval on unmount
    @ctx.cleanup
    def cleanup_interval():
        clearInterval(interval)
    
    # Render loop
    for _ in ctx:
        letters = get_random_letters()
        
        yield h.div(style={"height": "40px"})[
            [h(Letter,
                letter=letter,
                index=i,
                key=letter  # Use letter as key for proper animations
            ) for i, letter in enumerate(letters)]
        ]


# Import setInterval/clearInterval from JS
from js import setInterval, clearInterval

# Render the component
if __name__ == "__main__":
    renderer.render(h(Letters), document.body)