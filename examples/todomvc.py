"""
TodoMVC implementation in crankpy
Complete TodoMVC app following the official spec at todomvc.com
"""

from crank import h, component
from crank.dom import renderer
from js import document

# Custom TodoMVC event that bubbles by default
class TodoEvent:
    def __init__(self, event_type, detail=None):
        if detail is None:
            detail = {}
        self.event = CustomEvent.new(event_type, {
            "bubbles": True,
            "detail": detail
        })

@component
def Header(ctx):
    title = ""

    @ctx.refresh
    def oninput(ev):
        nonlocal title
        title = ev.target.value

    @ctx.refresh
    def onkeydown(ev):
        nonlocal title
        if ev.key == "Enter" and title.strip():
            ev.preventDefault()
            ctx.dispatchEvent(TodoEvent("todocreate", {"title": title.strip()}).event)
            title = ""

    for _ in ctx:
        yield h.header(className="header")[
            h.h1["todos"],
            h.div["Write a todo...",
        ]

#@component
#def TodoItem(ctx, props):
#    editing = False
#    edit_title = ""
#
#    @ctx.refresh
#    def ontoggle():
#        todo = props.todo
#        ctx.dispatchEvent(TodoEvent("todotoggle", {
#            "id": todo["id"],
#            "completed": not todo["completed"]
#        }).event)
#
#    @ctx.refresh
#    def ondelete():
#        todo = props.todo
#        ctx.dispatchEvent(TodoEvent("tododelete", {"id": todo["id"]}).event)
#
#    @ctx.refresh
#    def onedit():
#        nonlocal editing, edit_title
#        editing = True
#        edit_title = props.todo["title"]
#
#    @ctx.refresh
#    def onsave():
#        nonlocal editing
#        if edit_title.strip():
#            ctx.dispatchEvent(TodoEvent("todoedit", {
#                "id": props.todo["id"],
#                "title": edit_title.strip()
#            }).event)
#        editing = False
#
#    @ctx.refresh
#    def oncancel():
#        nonlocal editing, edit_title
#        editing = False
#        edit_title = props.todo["title"]
#
#    @ctx.refresh
#    def onkeydown(ev):
#        if ev.key == "Enter":
#            onsave()
#        elif ev.key == "Escape":
#            oncancel()
#
#    @ctx.refresh
#    def oneditinput(ev):
#        nonlocal edit_title
#        edit_title = ev.target.value
#
#    for props in ctx:
#        todo = props.todo
#        edit_title = todo["title"] if not editing else edit_title
#
#        yield h.li(className={
#            "completed": todo["completed"],
#            "editing": editing
#        })[
#            h.div(className="view")[
#                h.input(
#                    className="toggle",
#                    type="checkbox",
#                    checked=todo["completed"],
#                    onChange=ontoggle
#                ),
#                h.label(onDoubleClick=onedit)[todo["title"]],
#                h.button(className="destroy", onClick=ondelete)
#            ],
#            h.input(
#                className="edit",
#                type="text",
#                value=edit_title,
#                onInput=oneditinput,
#                onKeyDown=onkeydown,
#                onBlur=onsave,
#                autoFocus=True
#            ) if editing else None
#        ]
#
#@component
#def TodoList(ctx, props):
#    for props in ctx:
#        todos = props.todos
#        filter_type = props.filter
#
#        # Filter todos based on current filter
#        if filter_type == "active":
#            filtered_todos = [t for t in todos if not t["completed"]]
#        elif filter_type == "completed":
#            filtered_todos = [t for t in todos if t["completed"]]
#        else:
#            filtered_todos = todos
#
#        yield h.ul(className="todo-list")[
#            [h(TodoItem, todo=todo, key=todo["id"]) for todo in filtered_todos]
#        ]
#
#@component
#def Footer(ctx, props):
#    @ctx.refresh
#    def set_filter(new_filter):
#        ctx.dispatchEvent(TodoEvent("filterchange", {"filter": new_filter}).event)
#
#    @ctx.refresh
#    def clear_completed():
#        ctx.dispatchEvent(TodoEvent("todoclearcompleted").event)
#
#    for props in ctx:
#        todos = props.todos
#        filter_type = props.filter
#
#        active_count = len([t for t in todos if not t["completed"]])
#        completed_count = len([t for t in todos if t["completed"]])
#
#        yield h.footer(className="footer")[
#            h.span(className="todo-count")[
#                h.strong[str(active_count)],
#                f" item{'s' if active_count != 1 else ''} left"
#            ],
#            h.ul(className="filters")[
#                [h.li(key=f)[
#                    h.a(
#                        href="javascript:void(0)",
#                        onClick=lambda f=f: set_filter("" if f == "all" else f),
#                        className={"selected": filter_type == ("" if f == "all" else f)}
#                    )[f.capitalize() if f != "all" else "All"]
#                ] for f in ["all", "active", "completed"]]
#            ],
#            h.button(
#                className="clear-completed",
#                onClick=clear_completed
#            )["Clear completed"] if completed_count > 0 else None
#        ]
#
#@component
#def App(ctx):
#    todos = []
#    next_id = 1
#    filter_type = ""
#
#    @ctx.refresh
#    def on_todo_create(ev):
#        nonlocal todos, next_id
#        todos.append({
#            "id": next_id,
#            "title": ev.detail["title"],
#            "completed": False
#        })
#        next_id += 1
#
#    @ctx.refresh
#    def on_todo_toggle(ev):
#        nonlocal todos
#        todo = next((t for t in todos if t["id"] == ev.detail["id"]), None)
#        if todo:
#            todo["completed"] = ev.detail["completed"]
#
#    @ctx.refresh
#    def on_todo_edit(ev):
#        nonlocal todos
#        todo = next((t for t in todos if t["id"] == ev.detail["id"]), None)
#        if todo:
#            todo["title"] = ev.detail["title"]
#
#    @ctx.refresh
#    def on_todo_delete(ev):
#        nonlocal todos
#        todos = [t for t in todos if t["id"] != ev.detail["id"]]
#
#    @ctx.refresh
#    def on_todo_clear_completed():
#        nonlocal todos
#        todos = [t for t in todos if not t["completed"]]
#
#    @ctx.refresh
#    def on_filter_change(ev):
#        nonlocal filter_type
#        filter_type = ev.detail["filter"]
#
#    @ctx.refresh
#    def on_toggle_all(ev):
#        nonlocal todos
#        completed = ev.target.checked
#        for todo in todos:
#            todo["completed"] = completed
#
#    # Set up event listeners
#    ctx.addEventListener("todocreate", on_todo_create)
#    ctx.addEventListener("todotoggle", on_todo_toggle)
#    ctx.addEventListener("todoedit", on_todo_edit)
#    ctx.addEventListener("tododelete", on_todo_delete)
#    ctx.addEventListener("todoclearcompleted", on_todo_clear_completed)
#    ctx.addEventListener("filterchange", on_filter_change)
#
#    for _ in ctx:
#        yield h.section(className="todoapp")[
#            h(Header),
#            h.section(className="main")[
#                h.input(
#                    id="toggle-all",
#                    className="toggle-all",
#                    type="checkbox",
#                    checked=len(todos) > 0 and all(t["completed"] for t in todos),
#                    onChange=on_toggle_all
#                ),
#                h.label(htmlFor="toggle-all")["Mark all as complete"],
#                h(TodoList, todos=todos, filter=filter_type),
#                h(Footer, todos=todos, filter=filter_type)
#            ] if len(todos) > 0 else None
#        ]

# Set up TodoMVC CSS
# def setup_todomvc_css():
#     # Remove default stylesheet for playground
#     existing_link = document.head.querySelector("link")
#     if existing_link:
#         existing_link.remove()
#
#     # Add TodoMVC CSS
#     link = document.createElement("link")
#     link.rel = "stylesheet"
#     link.href = "https://unpkg.com/todomvc-app-css@2.4.2/index.css"
#     document.head.appendChild(link)

renderer.render(h(Header), document.body)
