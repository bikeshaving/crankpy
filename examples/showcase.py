"""
Crank.py Showcase - Demonstrates all major features
"""

from crank import h, component
from crank.dom import renderer
from js import document
import random
import time

# 1. Simple static component (0 params)
@component
def Logo():
    return h.div(className="logo")[
        h.h1["🔧 Crank.py"],
        h.p["Python Components with Generators"]
    ]

# 2. Component with context only (1 param)
@component
def Clock(ctx):
    """Updates every second to show current time"""
    import asyncio
    
    async def update_time():
        while True:
            await asyncio.sleep(1)
            ctx.refresh()
    
    # Start the async update loop
    asyncio.create_task(update_time())
    
    for _ in ctx:
        current_time = time.strftime("%H:%M:%S")
        yield h.div(className="clock")[
            h.span["Current time: "],
            h.strong[current_time]
        ]

# 3. Component with context and props (2 params)
@component
def TodoItem(ctx, props):
    """Individual todo item with toggle functionality"""
    for props in ctx:
        todo = props.todo
        on_toggle = props.on_toggle
        
        yield h.li(className="completed" if todo["done"] else "")[
            h.input(
                type="checkbox",
                checked=todo["done"],
                onChange=lambda: on_toggle(todo["id"])
            ),
            h.span[todo["text"]],
            h.small[f" (ID: {todo['id']})"]
        ]

# 4. Complex stateful component demonstrating all features
@component
def TodoApp(ctx):
    """Main todo application with full CRUD operations"""
    todos = [
        {"id": 1, "text": "Learn Crank.py", "done": True},
        {"id": 2, "text": "Build awesome components", "done": False},
        {"id": 3, "text": "Master generators", "done": False}
    ]
    next_id = 4
    new_todo_text = ""
    filter_mode = "all"  # all, active, completed
    
    @ctx.refresh
    def add_todo():
        nonlocal todos, next_id, new_todo_text
        if new_todo_text.strip():
            todos.append({
                "id": next_id,
                "text": new_todo_text.strip(),
                "done": False
            })
            next_id += 1
            new_todo_text = ""
    
    @ctx.refresh
    def toggle_todo(todo_id):
        nonlocal todos
        for todo in todos:
            if todo["id"] == todo_id:
                todo["done"] = not todo["done"]
                break
    
    @ctx.refresh
    def update_input(event):
        nonlocal new_todo_text
        new_todo_text = event.target.value
    
    def handle_submit(event):
        event.preventDefault()
        add_todo()
    
    @ctx.refresh
    def set_filter(mode):
        nonlocal filter_mode
        filter_mode = mode
    
    @ctx.refresh
    def clear_completed():
        nonlocal todos
        todos = [t for t in todos if not t["done"]]
    
    for _ in ctx:
        # Filter todos based on current mode
        if filter_mode == "active":
            visible_todos = [t for t in todos if not t["done"]]
        elif filter_mode == "completed":
            visible_todos = [t for t in todos if t["done"]]
        else:
            visible_todos = todos
        
        completed_count = sum(1 for t in todos if t["done"])
        active_count = len(todos) - completed_count
        
        yield h.div(className="todo-app")[
            h.h2["Todo List"],
            
            # Add todo form
            h.form(onSubmit=handle_submit, className="add-form")[
                h.input(
                    type="text",
                    placeholder="What needs to be done?",
                    value=new_todo_text,
                    onInput=update_input,
                    className="todo-input"
                ),
                h.button(type="submit")["Add"]
            ],
            
            # Filter buttons
            h.div(className="filters")[
                h.button(
                    className="active" if filter_mode == "all" else "",
                    onClick=lambda: set_filter("all")
                )["All"],
                h.button(
                    className="active" if filter_mode == "active" else "",
                    onClick=lambda: set_filter("active")
                )[f"Active ({active_count})"],
                h.button(
                    className="active" if filter_mode == "completed" else "",
                    onClick=lambda: set_filter("completed")
                )[f"Completed ({completed_count})"]
            ],
            
            # Todo list
            h.ul(className="todo-list")[
                [h(TodoItem, 
                    todo=todo,
                    on_toggle=toggle_todo,
                    key=todo["id"]
                ) for todo in visible_todos]
            ],
            
            # Footer
            h.div(className="todo-footer")[
                h.span[f"{active_count} item{'s' if active_count != 1 else ''} left"],
                h.button(
                    onClick=clear_completed,
                    disabled=completed_count == 0
                )["Clear completed"]
            ] if todos else None
        ]

# 5. Component demonstrating hyperscript syntax variations
@component
def SyntaxShowcase(ctx):
    """Shows different ways to use the h function"""
    
    for _ in ctx:
        yield h.div(className="syntax-showcase")[
            h.h3["Hyperscript Syntax Examples"],
            
            # Basic element with text
            h.p["Simple paragraph with text"],
            
            # Element with props
            h.p(className="styled", id="my-paragraph")["Paragraph with props"],
            
            # Nested elements
            h.ul[
                h.li["First item"],
                h.li["Second item"],
                h.li[
                    "Third item with ",
                    h.strong["nested"],
                    " content"
                ]
            ],
            
            # Element with style object
            h.div(style={
                "background-color": "#f0f0f0",
                "padding": "10px",
                "border-radius": "5px"
            })[
                "Styled div with object notation"
            ],
            
            # Fragment with key prop (when you need fragment properties)
            h("", key="fragment-example")[
                h.span["Fragment "],
                h.span["with "],
                h.span["multiple "],
                h.span["children"]
            ],
            
            # Component composition
            h.div(className="composition")[
                "Nested component: ",
                h(Logo)
            ]
        ]

# 6. Main showcase app that combines everything
@component
def ShowcaseApp(ctx):
    """Main application demonstrating all Crank.py features"""
    
    for _ in ctx:
        yield h.div(className="showcase-container")[
            h(Logo),
            
            h.div(className="features")[
                h.section[
                    h.h2["⏰ Real-time Updates"],
                    h(Clock)
                ],
                
                h.section[
                    h.h2["📝 Stateful Components"],
                    h(TodoApp)
                ],
                
                h.section[
                    h.h2["🎨 Syntax Flexibility"],
                    h(SyntaxShowcase)
                ]
            ],
            
            h.footer[
                h.p["Built with ", h.strong["Crank.py"], " - Python Components for the Web"],
                h.p[
                    h.a(href="https://crank.js.org", target="_blank")["Crank.js"],
                    " | ",
                    h.a(href="https://github.com/bikeshaving/crankpy", target="_blank")["GitHub"]
                ]
            ]
        ]

# Render the showcase app
if __name__ == "__main__":
    renderer.render(h(ShowcaseApp), document.body)