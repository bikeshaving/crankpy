"""
Counter Component - Simple working example with generator state management
"""

from crank import h, component
from crank.dom import renderer
from js import document

@component
def Counter(ctx):
    # State stored in generator scope
    count = 0

    @ctx.refresh
    def increment(event):
        nonlocal count
        count += 1

    @ctx.refresh
    def decrement(event):
        nonlocal count
        count -= 1

    @ctx.refresh
    def reset(event):
        nonlocal count
        count = 0

    for _ in ctx:
        yield h.div[
            h.h2["Counter Example"],
            h.div(className="counter-display")[
                h.span(className="count-label")["Count: "],
                h.span(className="count-value")[str(count)],
            ],
            h.div(className="counter-controls")[
                h.button(className="btn-decrement", onClick=decrement)["-"],
                h.button(className="btn-reset", onClick=reset)["Reset"],
                h.button(className="btn-increment", onClick=increment)["+"],
            ],
        ]

# Render the component
renderer.render(h(Counter), document.body)
