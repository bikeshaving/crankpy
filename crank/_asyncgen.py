"""Async generator wrapper for component results.

This module is Pyodide-only. MicroPython cannot compile an async
generator (yield inside async def), so crank/__init__.py imports this
module only on Pyodide.
"""


def wrap_async_generator(agen, transform):
    """Delegate to a component async generator and transform each yielded tree."""

    async def wrapper():
        send_value = None
        while True:
            try:
                yielded = await agen.asend(send_value)
            except StopAsyncIteration:
                return
            send_value = yield transform(yielded)

    return wrapper()
