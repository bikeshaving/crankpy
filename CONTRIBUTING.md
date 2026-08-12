# Contributing to Crank.py

## Setup

1. Install [uv](https://docs.astral.sh/uv/).
2. Run `npm install` to get the Crank and PyScript modules.
3. Run `uv sync --group test` to get the test dependencies.

## Tests

The test suite runs in a real browser through Playwright, once per runtime
(Pyodide and MicroPython).

1. Start the file server: `make serve`
2. In another terminal, run `make test`

Use `make test-pyodide` or `make test-micropython` to test one runtime.

## Checks

- `make lint` runs ruff.
- `make typecheck` runs pyright.

## Pull requests

Keep changes small and focused. Add or update tests for behavior changes.
Make sure `make test` passes on both runtimes before you open a PR.
