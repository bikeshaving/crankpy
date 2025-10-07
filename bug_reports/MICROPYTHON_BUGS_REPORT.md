# Critical MicroPython PyScript Bugs - Bug Report

This document details several critical bugs discovered in MicroPython's PyScript integration that severely impact JavaScript interoperability. These bugs affect any Python code that needs to interact with JavaScript objects, iterate over them, or implement JavaScript iterator protocols.

## Environment
- **PyScript Version**: 2025.8.1
- **MicroPython Implementation**: Latest (as of PyScript 2025.8.1)
- **Browser**: All modern browsers
- **Context**: Web applications using MicroPython via PyScript

## Summary of Bugs

### 1. **Critical: `dir()` on JsProxy Objects Triggers js_get_iter Error**

**Bug**: Calling `dir()` on any JsProxy object causes `TypeError: proxy_js_ref[f_ref][Symbol.iterator] is not a function`

**Impact**: 
- Breaks object introspection
- Prevents dynamic attribute access patterns
- Affects any library that uses `dir()` for JavaScript interop

**Minimal Reproduction**: See `micropython_dir_bug.html`

```python
from js import Object
js_obj = Object.new()
dir(js_obj)  # Fails with Symbol.iterator error
```

### 2. **Critical: `dict()` Constructor on JsProxy Objects Triggers js_get_iter Error**

**Bug**: Using `dict(js_proxy_object)` causes the same `TypeError: proxy_js_ref[f_ref][Symbol.iterator] is not a function`

**Impact**:
- Breaks conversion of JavaScript objects to Python dictionaries  
- Affects data exchange between JavaScript and Python
- Common pattern in web frameworks

**Minimal Reproduction**: See `micropython_dict_bug.html`

```python
from js import Object
js_obj = Object.new()
js_obj.prop = "value"
dict(js_obj)  # Fails with Symbol.iterator error
```

### 3. **Critical: Symbol.iterator Identity Inconsistency**

**Bug**: `Symbol.iterator` returns different object instances on each access, breaking equality comparisons

**Impact**:
- Breaks JavaScript iterator protocol implementations
- Prevents proper Symbol.iterator detection
- Makes it impossible to implement JavaScript-compatible iterators

**Minimal Reproduction**: See `micropython_symbol_iterator_bug.html`

```python
from js import Symbol
sym1 = Symbol.iterator
sym2 = Symbol.iterator
print(sym1 is sym2)  # False (should be True)
print(sym1 == sym2)  # False (should be True)
```

## Root Cause Analysis

All three bugs appear to stem from MicroPython's internal `js_get_iter` function, which is called when:
1. Python tries to iterate over a JsProxy object (via `dir()`, `dict()`, etc.)
2. The function attempts to access `proxy_js_ref[f_ref][Symbol.iterator]`
3. The Symbol.iterator lookup fails due to identity inconsistency
4. This results in the error: `proxy_js_ref[f_ref][Symbol.iterator] is not a function`

## Workarounds Implemented

We've developed working workarounds for all these issues:

### 1. Safe Attribute Enumeration (replaces `dir()`)
```python
def safe_get_js_attributes(js_obj):
    from js import eval as js_eval
    js_code = """
    (function(jsObj) {
        const props = [];
        for (const key in jsObj) {
            if (typeof key === 'string') {
                props.push(key);
            }
        }
        return props;
    })
    """
    get_props = js_eval(js_code)
    attrs = get_props(js_obj)
    return attrs.to_py() if hasattr(attrs, 'to_py') else []
```

### 2. Safe Dictionary Conversion (replaces `dict()`)
```python
def safe_js_to_dict(js_obj):
    from js import eval as js_eval
    js_code = """
    (function(jsObj) {
        if (!jsObj) return {};
        const result = {};
        for (const key in jsObj) {
            if (jsObj.hasOwnProperty(key)) {
                result[key] = jsObj[key];
            }
        }
        return result;
    })
    """
    convert_obj = js_eval(js_code)
    js_dict = convert_obj(js_obj)
    return js_dict.to_py() if hasattr(js_dict, 'to_py') else {}
```

### 3. Symbol.iterator Wrapper (fixes iterator protocol)
```python
class SymbolIteratorWrapper:
    def __init__(self, python_generator):
        self.python_generator = python_generator
    
    def __getitem__(self, key):
        from js import eval as js_eval
        js_code = """
        (function(pythonKey, pythonGen) {
            if (pythonKey === Symbol.iterator) {
                return function() {
                    return {
                        next: function() {
                            try {
                                const value = pythonGen.__next__();
                                return { value: value, done: false };
                            } catch (e) {
                                return { value: undefined, done: true };
                            }
                        }
                    };
                };
            }
            throw new Error('Not Symbol.iterator');
        })
        """
        js_func = js_eval(js_code)
        return js_func(key, self.python_generator)
```

## Impact on Real Projects

These bugs were discovered while implementing **Crank.py**, a Python wrapper for the Crank.js framework. The bugs completely prevented:
- Component context iteration
- Props object conversion  
- Generator-based component rendering
- Any JavaScript framework integration requiring iteration

Our workarounds have restored full functionality, enabling TodoMVC and other complex applications to work correctly.

## Testing

All bugs and workarounds have been thoroughly tested:
- **Reproduction Cases**: `bug_reports/micropython_*_bug.html`
- **Working Solutions**: `bug_reports/working_workarounds.html`
- **Real-world Validation**: TodoMVC and Counter examples in Crank.py

## Recommendations

1. **Immediate Fix Needed**: The `js_get_iter` function should properly handle Symbol.iterator lookup failures
2. **Symbol.iterator Consistency**: Symbol.iterator should return the same object instance on repeated access
3. **Better Error Messages**: The current error message is cryptic and doesn't indicate the actual problem
4. **Documentation**: These limitations should be documented until fixed

## Files for Reproduction

All reproduction cases and workarounds are available in the `bug_reports/` directory:
- `micropython_dir_bug.html` - Reproduces dir() bug
- `micropython_dict_bug.html` - Reproduces dict() bug  
- `micropython_symbol_iterator_bug.html` - Reproduces Symbol.iterator identity bug
- `working_workarounds.html` - Demonstrates all working solutions

## Contact

These bugs were discovered and documented during the development of Crank.py. For questions or additional details, please reference this investigation in issues to the MicroPython and PyScript projects.

---

**Severity**: Critical - Breaks fundamental JavaScript interop functionality  
**Priority**: High - Affects any project requiring JavaScript integration  
**Workaround**: Available (documented above)  
**Status**: Needs upstream fix in MicroPython PyScript integration