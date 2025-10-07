# PyScript MicroPython Bug Reports

## Summary

During development of Crank.py (a Python wrapper for Crank.js), we discovered several critical compatibility issues in PyScript's MicroPython runtime that prevent proper iteration and object conversion. These bugs affect any code that tries to iterate over JavaScript proxy objects or convert them to Python dictionaries.

## Bug #1: `dict()` constructor fails on JsProxy objects with Symbol.iterator error

### Description
When attempting to convert a JavaScript object wrapped in a JsProxy to a Python dictionary using `dict(js_proxy_object)`, MicroPython throws a TypeError related to Symbol.iterator.

### Error Message
```
TypeError: proxy_js_ref[f_ref][Symbol.iterator] is not a function
```

### Root Cause
MicroPython's internal `js_get_iter` function attempts to access `Symbol.iterator` on JsProxy objects, but the Symbol.iterator identity is inconsistent - it returns different objects on each access, breaking equality comparisons.

### Minimal Reproduction
```html
<!DOCTYPE html>
<html>
<head>
    <title>MicroPython dict() Bug</title>
    <link rel="stylesheet" href="https://pyscript.net/releases/2025.8.1/core.css">
    <script type="module" src="https://pyscript.net/releases/2025.8.1/core.js"></script>
</head>
<body>
    <div id="output"></div>
    
    <script type="mpy">
from js import Object, document

output = document.getElementById("output")

# Create a JavaScript object
js_obj = Object.new()
js_obj.name = "test"
js_obj.value = 42

try:
    # This fails in MicroPython but works in Pyodide
    python_dict = dict(js_obj)
    output.innerHTML = f"✅ dict() conversion worked: {python_dict}"
except Exception as e:
    output.innerHTML = f"❌ dict() conversion failed: {e}"
    </script>
</body>
</html>
```

### Working Workaround
```python
# Use JavaScript to convert object safely
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
python_dict = convert_obj(js_obj).to_py()
```

## Bug #2: `dir()` function fails on JsProxy objects with same Symbol.iterator error

### Description
Similar to the dict() issue, calling `dir(js_proxy_object)` triggers the same Symbol.iterator bug.

### Error Message
```
TypeError: proxy_js_ref[f_ref][Symbol.iterator] is not a function
```

### Minimal Reproduction
```html
<!DOCTYPE html>
<html>
<head>
    <title>MicroPython dir() Bug</title>
    <link rel="stylesheet" href="https://pyscript.net/releases/2025.8.1/core.css">
    <script type="module" src="https://pyscript.net/releases/2025.8.1/core.js"></script>
</head>
<body>
    <div id="output"></div>
    
    <script type="mpy">
from js import Object, document

output = document.getElementById("output")

# Create a JavaScript object
js_obj = Object.new()
js_obj.name = "test"
js_obj.value = 42

try:
    # This fails in MicroPython but works in Pyodide
    attributes = dir(js_obj)
    output.innerHTML = f"✅ dir() worked: {attributes}"
except Exception as e:
    output.innerHTML = f"❌ dir() failed: {e}"
    </script>
</body>
</html>
```

### Working Workaround
```python
# Use JavaScript for-in enumeration instead of dir()
from js import eval as js_eval

js_code = """
(function(jsObj) {
    const props = [];
    for (const key in jsObj) {
        if (typeof key === 'string' && !key.startsWith('_')) {
            props.push(key);
        }
    }
    return props;
})
"""
get_props = js_eval(js_code)
attributes = get_props(js_obj).to_py()
```

## Bug #3: Symbol.iterator identity inconsistency

### Description
In MicroPython, accessing `Symbol.iterator` multiple times returns different objects, breaking the fundamental JavaScript iteration protocol that relies on Symbol.iterator identity.

### Minimal Reproduction
```html
<!DOCTYPE html>
<html>
<head>
    <title>Symbol.iterator Identity Bug</title>
    <link rel="stylesheet" href="https://pyscript.net/releases/2025.8.1/core.css">
    <script type="module" src="https://pyscript.net/releases/2025.8.1/core.js"></script>
</head>
<body>
    <div id="output"></div>
    
    <script type="mpy">
from js import Symbol, document

output = document.getElementById("output")

# Test Symbol.iterator identity
iter1 = Symbol.iterator
iter2 = Symbol.iterator

output.innerHTML = f"Symbol.iterator === Symbol.iterator: {iter1 is iter2}"
output.innerHTML += f"<br>iter1: {iter1}"
output.innerHTML += f"<br>iter2: {iter2}"

# This should be True but is False in MicroPython
if iter1 is iter2:
    output.innerHTML += "<br>✅ Symbol.iterator identity is consistent"
else:
    output.innerHTML += "<br>❌ Symbol.iterator identity is broken"
    </script>
</body>
</html>
```

### Expected vs Actual Behavior
- **Expected**: `Symbol.iterator` should return the same object on each access
- **Actual**: `Symbol.iterator` returns different objects each time in MicroPython
- **Works correctly in**: Pyodide

## Impact on Libraries

These bugs prevent proper JavaScript-Python interoperability for any library that needs to:

1. Convert JavaScript objects to Python dictionaries
2. Enumerate JavaScript object properties
3. Create JavaScript-compatible iterators
4. Use Python generators that get proxied to JavaScript

## Affected PyScript Version
- PyScript version: 2025.8.1
- MicroPython version: v1.26.0-preview.386.g17fbc5abd

## Suggested Fixes

1. **Fix Symbol.iterator identity**: Ensure `Symbol.iterator` returns the same object instance on each access
2. **Fix js_get_iter function**: Handle the case where Symbol.iterator comparison fails due to identity issues
3. **Add fallback mechanisms**: When `js_get_iter` fails, fallback to alternative iteration methods

## Workarounds Implemented

We've successfully worked around these issues in Crank.py by:

1. Detecting MicroPython runtime and using JavaScript-based object conversion
2. Avoiding `dict()` and `dir()` calls on JsProxy objects
3. Implementing custom Symbol.iterator wrapper that uses pure JavaScript
4. Using JavaScript `eval()` to perform operations that would normally use Python iteration

These workarounds maintain full compatibility between MicroPython and Pyodide while working around the underlying bugs.