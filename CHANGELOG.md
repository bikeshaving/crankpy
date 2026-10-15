# Changelog

## 0.2.1 (2026-08-13)

Targets Crank 0.7.x. Tested against PyScript 2026.7.3 (Pyodide 314 /
Python 3.14, MicroPython v1.28.0). Requires Python 3.9 or later.

### Breaking changes

- `h` returns plain Python `El` objects, not Crank elements. They become
  Crank elements when they are rendered or returned from a component.
- Snake_case to kebab-case conversion applies only to HTML elements.
  Component props keep their names: `h(Profile, user_id=1)` passes
  `props["user_id"]`, not `props["user-id"]`.
- `crank.async` is now `crank.async_`, because `async` is a Python
  keyword. It loads Crank from the `crank_async` entry in your PyScript
  `js_modules`, not from a `CrankAsync` global.
- `crank.html` loads Crank from the `crank_html` entry in `js_modules`,
  not from a `CrankHTML` global. `crank.html.Renderer` is now
  `crank.html.HTMLRenderer`.
- `crank.dom.Renderer` is removed. Use `crank.dom.DOMRenderer`.

### New features

- `crank.template`: `jsx` and `html` template tags for PEP 750
  t-strings (Python 3.14 and MicroPython v1.28.0 or later). The grammar
  is a port of the Crank.js `jsx` template tag.
- Namespaced props (`prop:name`, `attr:name`) work in both syntaxes:
  `**{"prop:innerHTML": x}` or `prop__innerHTML=x` in Pyperscript, and
  `prop:innerHTML={x}` in templates.
- `crank.Renderer` wraps any Crank renderer so that it accepts `El`
  trees. `crank.dom.renderer` and `crank.html.renderer` are already
  wrapped.
- `js_component()` imports JavaScript components (Suspense,
  SuspenseList) so that they work on MicroPython.
- Async function components (`async def` without `yield`) work on
  MicroPython. Async generator components still need Pyodide, because
  MicroPython cannot compile them.
- The package ships a `py.typed` marker, so type checkers read its
  types.

### Fixes

- The `@ctx.refresh` decorator now works. It returns a wrapper that
  runs the function and then refreshes through Crank's
  `refresh(callback)`. Before, event handlers crashed on arity and
  components never re-rendered.
- `h(Component)[children]` works on Pyodide. Before, it raised
  "'JsProxy' object is not subscriptable".
- MicroPython: form controls with attributes no longer hang the
  renderer.
- MicroPython: Suspense and SuspenseList work.
- MicroPython: integers larger than 32 bits no longer truncate. They
  cross the boundary as floats, exact up to 2**53.
- MicroPython: props no longer lose callable values (`ref`, `children`,
  arrays).
- MicroPython: generator components no longer fail with
  "Symbol.iterator is not a function".
- `h(None)` raises a clear `ValueError` instead of crashing the
  renderer.

## 0.2.0 (2025-10-06)

Targets Crank 0.7.x.

### Breaking changes

- Components receive props as a Python `dict`. Use `props["key"]` or
  `props.get("key")`, not `props.key`.

### New features

- MicroPython support. Crank.py runs on both of PyScript's runtimes.
- Chainable element syntax: `h.div(id="a")["children"]`, and `h.span()`
  for empty elements.
- Typing: `Context[Props, Result]` is generic, and component props can
  be declared with `TypedDict`.

### Fixes

- `async for props in ctx` keeps iterating after the first render, like
  Crank.js continuous mode. Before, it stopped after one pass.
- Crank no longer logs `ctx.value` deprecation warnings.
