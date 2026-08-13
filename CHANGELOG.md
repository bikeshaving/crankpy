# Changelog

## 0.2.1 (2026-08-13)

Targets Crank 0.7.x. Tested against PyScript 2026.7.3 (Pyodide 314 /
Python 3.14, MicroPython v1.28.0).

### Architecture

- Element construction is pure Python on both runtimes. The `h` builder
  makes plain `El` nodes, and one `to_element()` transform converts the
  tree to `createElement` calls at the render and component boundaries.
- All tree transforms use explicit stacks, not recursion. MicroPython
  allows only a small number of Python frames.

### New features

- `crank.template`: `jsx` and `html` template tags for PEP 750
  t-strings. The grammar is a port of the Crank.js `jsx` template tag.
- Namespaced props (`prop:name`, `attr:name`) work in both syntaxes:
  `**{"prop:innerHTML": x}` or `prop__innerHTML=x` in Pyperscript, and
  `prop:innerHTML={x}` in templates.
- `crank.Renderer` wraps any Crank renderer with the Python transform.
- `js_component()` imports JavaScript components (Suspense,
  SuspenseList) so that they work on MicroPython.

### Fixes

- The `@ctx.refresh` decorator now works. It returns a wrapper that
  runs the function and then refreshes through Crank's
  `refresh(callback)`. Before, event handlers crashed on arity and
  components never re-rendered.
- MicroPython: form controls with attributes no longer hang the
  renderer. Props cross the FFI as plain objects, not Maps.
- MicroPython: Suspense and SuspenseList work. Their functions stay on
  the JavaScript side, because a round trip through Python drops the
  `this` binding.
- MicroPython: integers larger than 32 bits no longer truncate. They
  cross the boundary as floats, exact up to 2**53.
- Props no longer lose callable values (`ref`, `children`, arrays) on
  MicroPython.
- `h(None)` raises a clear `ValueError` instead of crashing the
  renderer.

### Tooling

- Test runner reports passes, failures, skips, and file errors per
  runtime. 172 tests pass on Pyodide, 164 on MicroPython (8 skips for
  async generators, which MicroPython cannot compile).
- pyright is clean on `crank/`. Ruff targets Python 3.14.
