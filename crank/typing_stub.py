"""Minimal typing stub for MicroPython, which has no typing module.

This provides only the names that crank/__init__.py imports.
"""

Any = object
Callable = object
Dict = dict
Iterable = object
Union = object


def TypeVar(name, *args, **kwargs):
    return object


class Generic:
    def __class_getitem__(cls, item):
        return cls
