"""
Counter Component - Stateful component with event handlers

Demonstrates state management, event handling, and component refresh patterns.
"""

from crank import h, component
from crank.dom import renderer
from js import document

@component
def Counter(ctx):
    """Counter with increment, decrement, and reset functionality"""
    count = ctx.props.initial_count or 0
    
    def increment():
        nonlocal count
        count += 1
        ctx.refresh()
    
    def decrement():
        nonlocal count
        count -= 1  
        ctx.refresh()
        
    def reset():
        nonlocal count
        count = 0
        ctx.refresh()
    
    for _ in ctx:
        yield h.div(className='counter-container')[
            h.h2['Counter Example'],
            h.div(className='counter-display')[
                h.span(className='count-label')['Count: '],
                h.span(className='count-value')[str(count)]
            ],
            h.div(className='counter-controls')[
                h.button(className='btn-decrement', onClick=decrement)['-'],
                h.button(className='btn-reset', onClick=reset)['Reset'], 
                h.button(className='btn-increment', onClick=increment)['+']
            ]
        ]

# Render the component
async def main():
    await renderer.render(h.Counter(initial_count=5), document.body)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())