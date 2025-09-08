"""
Wizard Form - Python translation of examples/wizard.js

Multi-step form component with event handling and state management.
"""

from crank import h, component
from crank.dom import renderer
from js import document, FormData, JSON, Object
import json

@component
def Wizard(ctx):
    """Multi-step wizard form component"""
    step = 0
    form_data = {}
    
    def handle_submit(event):
        nonlocal step, form_data
        
        # Check form validity
        is_valid = event.target.reportValidity()
        if is_valid:
            event.preventDefault()
            
            # Extract form data
            data = FormData(event.target)
            for entry in data.entries():
                key, value = entry
                form_data[key] = value
            
            # Move to next step
            step += 1
            ctx.refresh()
    
    # Set up event listener
    ctx.addEventListener('submit', handle_submit)
    
    for _ in ctx:
        if step == 0:
            # Step 1: Basic info
            form_content = h[
                h.label(htmlFor='name')['Name:'],
                h.br[],
                h.input(name='name', type='text', required=True),
                h.br[],
                h.label(htmlFor='email')['Email:'],
                h.br[],
                h.input(name='email', type='email', required=True),
                h.br[],
                h.br[],
                h.button(type='submit')['Next']
            ]
        elif step == 1:
            # Step 2: Profile info
            form_content = h[
                h.label(htmlFor='profile')['Profile:'],
                h.br[],
                h.textarea(name='profile', required=True),
                h.br[],
                h.label(htmlFor='avatar')['Avatar:'],
                h.br[],
                h.input(name='avatar', type='file'),
                h.br[],
                h.br[],
                h.button(type='submit')['Submit']
            ]
        else:
            # Step 3: Show results
            form_content = h.pre[json.dumps(form_data, indent=2)]
        
        yield h.form(key=str(step))[form_content]

# Render the component  
async def main():
    await renderer.render(h.Wizard[], document.body)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())