"""
TodoMVC implementation in crankpy
Complete TodoMVC app following the official spec at todomvc.com
"""

from crank import h, component
from crank.dom import renderer
from js import document

@component
def TodoItem(ctx, props):
    editing = False
    edit_title = ""

    @ctx.refresh
    def toggle_todo(ev):
        if editing:
            return
        props.on_toggle(props.todo.id)

    @ctx.refresh
    def delete_todo(ev):
        props.on_delete(props.todo.id)

    @ctx.refresh
    def start_editing(ev):
        nonlocal editing, edit_title
        editing = True
        edit_title = props.todo.title

    @ctx.refresh
    def save_edit(ev):
        nonlocal editing
        if edit_title.strip():
            props.on_edit(props.todo.id, edit_title.strip())
        editing = False

    @ctx.refresh
    def cancel_edit(ev):
        nonlocal editing, edit_title
        editing = False
        edit_title = props.todo.title

    @ctx.refresh
    def handle_keydown(ev):
        if ev.key == "Enter":
            save_edit()
        elif ev.key == "Escape":
            cancel_edit()

    @ctx.refresh
    def handle_input(ev):
        nonlocal edit_title
        edit_title = ev.target.value

    for props in ctx:
        # Convert JS proxy to Python dict for easier access  
        todo_obj = props.todo
        todo = {
            "id": todo_obj.id, 
            "title": todo_obj.title, 
            "completed": todo_obj.completed
        }
        if not editing:
            edit_title = todo["title"]

        classes = []
        if todo["completed"]:
            classes.append("completed")
        if editing:
            classes.append("editing")

        yield h.li(className=" ".join(classes) if classes else None)[
            h.div(className="view")[
                h.input(
                    className="toggle",
                    type="checkbox",
                    checked=todo["completed"],
                    onchange=toggle_todo
                ),
                h.label(ondblclick=start_editing)[todo["title"]],
                h.button(className="destroy", onclick=delete_todo)
            ],
            h.input(
                className="edit",
                type="text",
                value=edit_title,
                oninput=handle_input,
                onkeydown=handle_keydown,
                onblur=save_edit
            ) if editing else None
        ]

@component
def TodoApp(ctx):
    todos = []
    next_id = 1
    filter_type = "all"

    @ctx.refresh
    def add_todo(title):
        nonlocal todos, next_id
        todos.append({
            "id": next_id,
            "title": title,
            "completed": False
        })
        next_id += 1

    @ctx.refresh
    def toggle_todo(todo_id):
        nonlocal todos
        for todo in todos:
            if todo["id"] == todo_id:
                todo["completed"] = not todo["completed"]
                break

    @ctx.refresh
    def edit_todo(todo_id, new_title):
        nonlocal todos
        for todo in todos:
            if todo["id"] == todo_id:
                todo["title"] = new_title
                break

    @ctx.refresh
    def delete_todo(todo_id):
        nonlocal todos
        todos = [t for t in todos if t["id"] != todo_id]

    @ctx.refresh
    def clear_completed(ev):
        nonlocal todos
        todos = [t for t in todos if not t["completed"]]

    @ctx.refresh
    def toggle_all(ev):
        nonlocal todos
        all_completed = ev.target.checked
        for todo in todos:
            todo["completed"] = all_completed

    @ctx.refresh
    def set_filter(new_filter):
        def handler(ev):
            nonlocal filter_type
            filter_type = new_filter
        return handler

    @ctx.refresh
    def handle_new_todo(ev):
        if ev.key == "Enter":
            title = ev.target.value.strip()
            if title:
                add_todo(title)
                ev.target.value = ""

    for _ in ctx:
        # Filter todos based on current filter
        if filter_type == "active":
            filtered_todos = [t for t in todos if not t["completed"]]
        elif filter_type == "completed":
            filtered_todos = [t for t in todos if t["completed"]]
        else:
            filtered_todos = todos

        active_count = len([t for t in todos if not t["completed"]])
        completed_count = len([t for t in todos if t["completed"]])

        yield h.section(className="todoapp")[
            h.header(className="header")[
                h.h1["todos"],
                h.input(
                    className="new-todo",
                    placeholder="What needs to be done?",
                    onkeydown=handle_new_todo,
                    autofocus=True
                )
            ],
            h.section(className="main", style={"display": "block" if todos else "none"})[
                h.input(
                    id="toggle-all",
                    className="toggle-all",
                    type="checkbox",
                    checked=len(todos) > 0 and all(t["completed"] for t in todos),
                    onchange=toggle_all
                ),
                h.label(htmlfor="toggle-all")["Mark all as complete"],
                h.ul(className="todo-list")[
                    [h(TodoItem, 
                       todo=todo, 
                       key=todo["id"],
                       on_toggle=toggle_todo,
                       on_edit=edit_todo,
                       on_delete=delete_todo
                     ) for todo in filtered_todos]
                ]
            ],
            h.footer(className="footer", style={"display": "block" if todos else "none"})[
                h.span(className="todo-count")[
                    h.strong[str(active_count)],
                    f" item{'s' if active_count != 1 else ''} left"
                ],
                h.ul(className="filters")[
                    h.li[
                        h.a(
                            href="#/",
                            onclick=lambda: set_filter("all"),
                            className="selected" if filter_type == "all" else None
                        )["All"]
                    ],
                    h.li[
                        h.a(
                            href="#/active",
                            onclick=lambda: set_filter("active"),
                            className="selected" if filter_type == "active" else None
                        )["Active"]
                    ],
                    h.li[
                        h.a(
                            href="#/completed",
                            onclick=lambda: set_filter("completed"),
                            className="selected" if filter_type == "completed" else None
                        )["Completed"]
                    ]
                ],
                h.button(
                    className="clear-completed",
                    onclick=clear_completed,
                    style={"display": "block" if completed_count > 0 else "none"}
                )["Clear completed"]
            ]
        ]

# Render the app
renderer.render(h(TodoApp), document.body)
