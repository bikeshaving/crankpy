"""
Counter Component - Simple working example with generator state management
"""

from js import document

from crank import component, h
from crank.dom import renderer


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
                h.button(className="btn-decrement", onclick=decrement)["-"],
                h.button(className="btn-reset", onclick=reset)["Reset"],
                h.button(className="btn-increment", onclick=increment)["+"],
            ],
        ]

# Render the component
renderer.render(h(Counter), document.body)
