"""JSX-style template tag for PEP 750 t-strings.

This is a port of the `jsx` template tag from @b9g/crank/jsx-tag.js.
It parses the static strings of a Template and fills the interpolations
into the parsed tree. The result is a pure Python `El` tree, which the
renderer transforms at the render boundary (see crank/__init__.py).

Usage:

    from crank.jsx import jsx

    element = jsx(t'<div class="greeting">Hello, {name}</div>')

    element = jsx(t'''
        <{Timer} milliseconds={1000}>
            <p>Elapsed: {elapsed}</p>
        <//>
    ''')

Both runtimes support t-strings: Pyodide ships Python 3.14, and
MicroPython v1.28.0 ships string.templatelib in the PyScript build.

The scanner is hand written. The MicroPython re module compiles without
match position support (match.start/match.end), so the regular
expressions of the original port do not work there.
"""

from . import El, Fragment

# Scanner modes
_CHILDREN = 0
_PROPS = 1
_CLOSING_BRACKET = 2
_CLOSING_SINGLE_QUOTE = 3
_CLOSING_DOUBLE_QUOTE = 4
_CLOSING_COMMENT = 5

_WORD_EXTRA = "-_$"


def _is_word_char(c):
    return c.isalpha() or c.isdigit() or c in _WORD_EXTRA


def _skip_space(span, i):
    n = len(span)
    while i < n and span[i].isspace():
        i += 1
    return i


def _match_children(span, i):
    """Find the next children-mode token from position i.

    Returns None or a dict with match start/end and token fields, like
    the groups of the original CHILDREN_RE: newline, comment, tag.
    """
    n = len(span)
    j = i
    while j < n:
        c = span[j]
        if c == "\r" or c == "\n":
            end = _skip_space(span, j + 1)
            return {"start": j, "end": end, "kind": "newline"}
        if c == "<":
            if span.startswith("<!--", j):
                idx = span.find("-->", j + 4)
                end = n if idx == -1 else idx + 3
                return {"start": j, "end": end, "kind": "comment"}
            k = _skip_space(span, j + 1)
            slash = ""
            while k < n and span[k] == "/" and len(slash) < 2:
                slash += "/"
                k += 1
            k = _skip_space(span, k)
            m = k
            while m < n and _is_word_char(span[m]):
                m += 1
            return {
                "start": j,
                "end": m,
                "kind": "tag",
                "slash": slash,
                "name": span[k:m],
            }
        j += 1
    return None


def _match_prop_string(span, i):
    """Match a quoted prop value at position i. Returns its end (exclusive).

    An escaped quote (backslash before the quote character) does not end
    the string. An unterminated string runs to the end of the span.
    """
    n = len(span)
    quote = span[i]
    m = i + 1
    while m < n:
        c = span[m]
        if c == "\\" and m + 1 < n and span[m + 1] == quote:
            m += 2
        elif c == quote:
            return m + 1
        else:
            m += 1
    return n


def _match_props(span, i):
    """Find the next props-mode token from position i.

    Mirrors PROPS_RE: leading whitespace, then a tag end (> or />), a
    spread (...), or a prop name with an optional value string.
    """
    n = len(span)
    search = i
    while search < n:
        j = _skip_space(span, search)
        if j >= n:
            return None
        c = span[j]
        if c == ">":
            return {"start": search, "end": j + 1, "kind": "tagend", "text": ">"}
        if c == "/":
            k = _skip_space(span, j + 1)
            if k < n and span[k] == ">":
                return {"start": search, "end": k + 1, "kind": "tagend", "text": "/>"}
        elif span.startswith("...", j):
            end = _skip_space(span, j + 3)
            return {"start": search, "end": end, "kind": "spread"}
        elif _is_word_char(c):
            m = j
            while m < n and _is_word_char(span[m]):
                m += 1
            name = span[j:m]
            k = _skip_space(span, m)
            equals = False
            if k < n and span[k] == "=":
                equals = True
                k = _skip_space(span, k + 1)
            string = None
            end = k
            if k < n and (span[k] == '"' or span[k] == "'"):
                end = _match_prop_string(span, k)
                string = span[k:end]
            return {
                "start": search,
                "end": end,
                "kind": "prop",
                "name": name,
                "equals": equals,
                "string": string,
            }
        # No token starts here. Advance past this character, like a
        # regex search would, so the caller can report unexpected text.
        search = j + 1
    return None


def _match_closing_bracket(span, i):
    idx = span.find(">", i)
    if idx == -1:
        return None
    return {"start": idx, "end": idx + 1}


def _match_closing_quote(span, i, quote):
    """Mirror /[^\\\\]?'/ : the first quote, or non-backslash char + quote."""
    n = len(span)
    p = i
    while p < n:
        if p + 1 < n and span[p] != "\\" and span[p + 1] == quote:
            return {"start": p, "end": p + 2}
        if span[p] == quote:
            return {"start": p, "end": p + 1}
        p += 1
    return None


def _match_closing_comment(span, i):
    idx = span.find("-->", i)
    if idx == -1:
        return None
    return {"start": idx, "end": idx + 3}


def _new_element(tag_name, span_index=None, char_index=None):
    return {
        "type": "element",
        "open": {
            "type": "tag",
            "slash": "",
            "value": tag_name,
            "spanIndex": span_index,
            "charIndex": char_index,
        },
        "close": None,
        "props": [],
        "children": [],
    }


def _format_tag_for_error(tag):
    if isinstance(tag, str):
        return f'"{tag}"'
    return getattr(tag, "__name__", None) or repr(tag)


def _format_syntax_error(message, spans, span_index, char_index):
    source = spans[0]
    for span in spans[1:]:
        source += "{}" + span
    offset = char_index
    for i in range(span_index):
        offset += len(spans[i]) + 2  # 2 = len("{}")
    lines = source.split("\n")
    line = 0
    col = offset
    for i, text in enumerate(lines):
        if col <= len(text):
            line = i
            break
        col -= len(text) + 1
    result = f"{message}\n\n"
    start = max(0, line - 1)
    end = min(len(lines) - 1, line + 1)
    gutter = len(str(end + 1))
    for i in range(start, end + 1):
        num = str(i + 1)
        num = " " * (gutter - len(num)) + num  # MicroPython has no str.rjust
        if i == line:
            result += f"> {num} | {lines[i]}\n"
            result += f"  {' ' * gutter} | {' ' * col}^\n"
        else:
            result += f"  {num} | {lines[i]}\n"
    return result.rstrip()


def _parse(spans):
    mode = _CHILDREN
    stack = []
    element = _new_element("")
    targets = []
    line_start = True

    for s, span in enumerate(spans):
        expressing = s < len(spans) - 1
        expression_target = None
        i = 0
        n = len(span)
        while i < n:
            if mode == _CHILDREN:
                match = _match_children(span, i)
                end = match["end"] if match else n
                if match:
                    is_newline = match["kind"] == "newline"
                    if i < match["start"]:
                        before = span[i : match["start"]]
                        if line_start:
                            before = before.lstrip()
                        if is_newline:
                            if span[max(0, match["start"] - 1)] == "\\":
                                # Keep whitespace before an escaped newline
                                before = before[:-1]
                            else:
                                before = before.rstrip()
                        if before:
                            element["children"].append(
                                {"type": "value", "value": before}
                            )
                    line_start = is_newline
                    if match["kind"] == "comment":
                        if end == n:
                            # Expression in a comment: jsx(t'<!-- {exp} -->')
                            mode = _CLOSING_COMMENT
                    elif match["kind"] == "tag":
                        tag_name = match["name"]
                        if match["slash"]:
                            element["close"] = {
                                "type": "tag",
                                "slash": match["slash"],
                                "value": tag_name,
                                "spanIndex": s,
                                "charIndex": match["start"],
                            }
                            if not stack:
                                if end != n:
                                    raise SyntaxError(
                                        _format_syntax_error(
                                            f'Unmatched closing tag "{tag_name}"',
                                            spans,
                                            s,
                                            match["start"],
                                        )
                                    )
                                expression_target = {
                                    "type": "error",
                                    "message": "Unmatched closing tag {}",
                                    "value": None,
                                    "spanIndex": s,
                                    "charIndex": match["start"],
                                }
                            else:
                                if end == n:
                                    expression_target = element["close"]
                                element = stack.pop()
                                mode = _CLOSING_BRACKET
                        else:
                            next_element = _new_element(tag_name, s, match["start"])
                            element["children"].append(next_element)
                            stack.append(element)
                            element = next_element
                            mode = _PROPS
                            if end == n:
                                expression_target = element["open"]
                else:
                    if i < n:
                        after = span[i:]
                        if not expressing:
                            after = after.rstrip()
                        if after:
                            element["children"].append(
                                {"type": "value", "value": after}
                            )

            elif mode == _PROPS:
                match = _match_props(span, i)
                end = match["end"] if match else n
                if match:
                    if i < match["start"]:
                        raise SyntaxError(
                            _format_syntax_error(
                                f"Unexpected text `{span[i : match['start']].strip()}`",
                                spans,
                                s,
                                i,
                            )
                        )
                    if match["kind"] == "tagend":
                        if match["text"][0] == "/":
                            # Self-closing element
                            element = stack.pop()
                        mode = _CHILDREN
                    elif match["kind"] == "spread":
                        value = {"type": "value", "value": None}
                        element["props"].append(value)
                        expression_target = value
                        if not (expressing and end == n):
                            raise SyntaxError(
                                _format_syntax_error(
                                    'Expression expected after "..."',
                                    spans,
                                    s,
                                    match["start"],
                                )
                            )
                    else:
                        name = match["name"]
                        string = match["string"]
                        if string is None:
                            if not match["equals"]:
                                value = {"type": "value", "value": True}
                            elif end < n:
                                raise SyntaxError(
                                    _format_syntax_error(
                                        f"Unexpected text `{span[end : end + 20]}`",
                                        spans,
                                        s,
                                        end,
                                    )
                                )
                            else:
                                value = {"type": "value", "value": None}
                                expression_target = value
                                if not (expressing and end == n):
                                    raise SyntaxError(
                                        _format_syntax_error(
                                            f'Expression expected for prop "{name}"',
                                            spans,
                                            s,
                                            match["start"],
                                        )
                                    )
                        else:
                            value = {"type": "propString", "parts": [string]}
                            if end == n:
                                mode = (
                                    _CLOSING_SINGLE_QUOTE
                                    if string[0] == "'"
                                    else _CLOSING_DOUBLE_QUOTE
                                )
                        element["props"].append(
                            {"type": "prop", "name": name, "value": value}
                        )
                else:
                    if not expressing:
                        if i == n:
                            raise SyntaxError(
                                _format_syntax_error(
                                    "Expected props but reached end of template",
                                    spans,
                                    s,
                                    i,
                                )
                            )
                        raise SyntaxError(
                            _format_syntax_error(
                                f"Unexpected text `{span[i : i + 20].strip()}`",
                                spans,
                                s,
                                i,
                            )
                        )

            elif mode == _CLOSING_BRACKET:
                match = _match_closing_bracket(span, i)
                end = match["end"] if match else n
                if match:
                    if i < match["start"]:
                        raise SyntaxError(
                            _format_syntax_error(
                                f"Unexpected text `{span[i : match['start']].strip()}`",
                                spans,
                                s,
                                i,
                            )
                        )
                    mode = _CHILDREN
                else:
                    if not expressing:
                        raise SyntaxError(
                            _format_syntax_error(
                                f"Unexpected text `{span[i : i + 20].strip()}`",
                                spans,
                                s,
                                i,
                            )
                        )

            elif mode in (_CLOSING_SINGLE_QUOTE, _CLOSING_DOUBLE_QUOTE):
                quote = "'" if mode == _CLOSING_SINGLE_QUOTE else '"'
                match = _match_closing_quote(span, i, quote)
                end = match["end"] if match else n
                string = span[i:end]
                prop = element["props"][-1]
                prop["value"]["parts"].append(string)
                if match:
                    mode = _PROPS
                else:
                    if not expressing:
                        raise SyntaxError(
                            _format_syntax_error(f"Missing `{quote}`", spans, s, i)
                        )

            else:  # _CLOSING_COMMENT
                match = _match_closing_comment(span, i)
                end = match["end"] if match else n
                if match:
                    mode = _CHILDREN
                else:
                    if not expressing:
                        raise SyntaxError(
                            _format_syntax_error(
                                "Expected `-->` but reached end of template",
                                spans,
                                s,
                                i,
                            )
                        )

            i = end

        if expressing:
            if expression_target:
                targets.append(expression_target)
                if expression_target["type"] == "error":
                    break
                continue
            if mode == _CHILDREN:
                target = {"type": "value", "value": None}
                element["children"].append(target)
                targets.append(target)
            elif mode in (_CLOSING_SINGLE_QUOTE, _CLOSING_DOUBLE_QUOTE):
                prop = element["props"][-1]
                target = {"type": "value", "value": None}
                prop["value"]["parts"].append(target)
                targets.append(target)
            elif mode == _CLOSING_COMMENT:
                targets.append(None)
            else:
                raise SyntaxError(
                    _format_syntax_error("Unexpected expression", spans, s, len(span))
                )
        elif expression_target:
            raise SyntaxError(
                _format_syntax_error("Expression expected", spans, s, len(span))
            )
        line_start = False

    if stack:
        opener = element["open"]
        try:
            ti = targets.index(opener)
        except ValueError:
            raise SyntaxError(
                _format_syntax_error(
                    f'Unmatched opening tag "{opener["value"]}"',
                    spans,
                    opener["spanIndex"] or 0,
                    opener["charIndex"] or 0,
                )
            ) from None
        targets[ti] = {
            "type": "error",
            "message": "Unmatched opening tag {}",
            "value": None,
            "spanIndex": opener["spanIndex"],
            "charIndex": opener["charIndex"],
        }

    root = element
    if len(root["children"]) == 1 and root["children"][0]["type"] == "element":
        root = root["children"][0]
    return {"element": root, "targets": targets, "spans": spans}


_SIMPLE_ESCAPES = {
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
    "v": "\v",
    "0": "\0",
}


def _unescape(text):
    if "\\" not in text:
        return text
    out = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == "\\" and i + 1 < n:
            nxt = text[i + 1]
            out.append(_SIMPLE_ESCAPES.get(nxt, nxt))
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def _build(parsed, spans):
    close = parsed["close"]
    open_tag = parsed["open"]
    if close is not None and close["slash"] != "//":
        open_value = open_tag["value"]
        close_value = close["value"]
        matches = (
            open_value == close_value
            if isinstance(open_value, str) and isinstance(close_value, str)
            else open_value is close_value
        )
        if not matches:
            message = (
                f"Unmatched closing tag {_format_tag_for_error(close_value)}, "
                f"expected {_format_tag_for_error(open_value)}"
            )
            if close["spanIndex"] is not None and close["charIndex"] is not None:
                raise SyntaxError(
                    _format_syntax_error(
                        message, spans, close["spanIndex"], close["charIndex"]
                    )
                )
            raise SyntaxError(message)

    children = []
    for child in parsed["children"]:
        if child["type"] == "element":
            children.append(_build(child, spans))
        else:
            children.append(child["value"])

    props = {}
    for prop in parsed["props"]:
        if prop["type"] == "prop":
            value = prop["value"]
            if value["type"] == "value":
                props[prop["name"]] = value["value"]
            else:
                text = ""
                for part in value["parts"]:
                    if isinstance(part, str):
                        text += part
                    elif part["value"] is not None and not isinstance(
                        part["value"], bool
                    ):
                        text += (
                            part["value"]
                            if isinstance(part["value"], str)
                            else str(part["value"])
                        )
                # Remove the quotes, then unescape backslash sequences
                props[prop["name"]] = _unescape(text[1:-1])
        else:
            # Spread prop
            spread_value = prop["value"]
            if spread_value:
                props.update(spread_value)

    tag = open_tag["value"]
    if isinstance(tag, str) and tag == "":
        tag = Fragment
    return El(tag, props or None, children)


_cache = {}


def _interpolation_value(interpolation):
    value = interpolation.value
    conversion = getattr(interpolation, "conversion", None)
    if conversion == "r":
        value = repr(value)
    elif conversion == "s":
        value = str(value)
    elif conversion == "a":
        value = ascii(value)
    format_spec = getattr(interpolation, "format_spec", "")
    if format_spec:
        # MicroPython has no format() builtin, so go through str.format
        value = ("{:" + format_spec + "}").format(value)
    return value


def jsx(template):
    """Build an element tree from a t-string template.

    The tag follows the grammar of the Crank.js `jsx` template tag:
    elements, props, spread props (...{expr}), comments, fragments
    (bare children), component tags (<{Component}>), and the generic
    closing tag (<//>).
    """
    spans = tuple(template.strings)
    parse_result = _cache.get(spans)
    if parse_result is None:
        parse_result = _parse(spans)
        has_error = any(
            t is not None and t["type"] == "error" for t in parse_result["targets"]
        )
        if not has_error:
            _cache[spans] = parse_result

    targets = parse_result["targets"]
    # MicroPython zip has no strict parameter
    for interpolation, target in zip(template.interpolations, targets):  # noqa: B905
        if target is None:
            continue
        value = _interpolation_value(interpolation)
        if target["type"] == "error":
            message = target["message"].replace("{}", _format_tag_for_error(value))
            raise SyntaxError(
                _format_syntax_error(
                    message,
                    spans,
                    target["spanIndex"] or 0,
                    target["charIndex"] or 0,
                )
            )
        target["value"] = value

    return _build(parse_result["element"], spans)


__all__ = ["jsx"]
