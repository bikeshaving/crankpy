"""
Minimal typing module stub for MicroPython compatibility.
This provides the typing constructs used by Crank.py without the full typing module.
"""

# Basic type aliases that are used by Crank.py
Any = object
Dict = dict
List = list
Union = object
Callable = object

# Type variables (just return object for MicroPython)
def TypeVar(name, *args, **kwargs):
    return object

# Generic base class (no-op for MicroPython)
class Generic:
    def __class_getitem__(cls, item):
        return cls

# TypedDict (simplified for MicroPython)
class TypedDict(dict):
    def __init_subclass__(cls, total=True, **kwargs):
        super().__init_subclass__(**kwargs)

# Iterator types (use built-ins)
Iterator = object
AsyncIterator = object
