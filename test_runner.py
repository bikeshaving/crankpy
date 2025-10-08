#!/usr/bin/env python3
import asyncio
import sys
import re
from playwright.async_api import async_playwright

async def run_tests(runtime: str = "pyodide"):
    """Run upytest tests in browser and return results."""

    if runtime == "micropython":
        config = """
        <mpy-config>
            {
                "files": {
                    "./tests/upytest.py": "upytest.py",
                    "./crank/__init__.py": "crank/__init__.py",
                    "./crank/dom.py": "crank/dom.py",
                    "./crank/html.py": "crank/html.py",
                    "./crank/typing_stub.py": "crank/typing_stub.py",
                    "./crank/async_.py": "crank/async_.py",
                    "./tests/test_basic.py": "test_basic.py",
                    "./tests/test_async.py": "test_async.py",
                    "./tests/test_components.py": "test_components.py",
                    "./tests/test_lifecycle.py": "test_lifecycle.py",
                    "./tests/test_hyperscript.py": "test_hyperscript.py",
                    "./tests/test_generators.py": "test_generators.py",
                    "./tests/test_dynamic_tags.py": "test_dynamic_tags.py"
                },
                "js_modules": {
                    "main": {
                        "https://cdn.jsdelivr.net/npm/@b9g/crank@0.7.1/crank.js": "crank_core",
                        "https://cdn.jsdelivr.net/npm/@b9g/crank@0.7.1/dom.js": "crank_dom",
                        "https://cdn.jsdelivr.net/npm/@b9g/crank@0.7.1/async.js": "crank_async"
                    }
                }
            }
        </mpy-config>
        """
        script_type = "mpy"
    else:
        config = """
        <py-config>
            {
                "files": {
                    "./tests/upytest.py": "upytest.py",
                    "./crank/__init__.py": "crank/__init__.py",
                    "./crank/dom.py": "crank/dom.py",
                    "./crank/html.py": "crank/html.py",
                    "./crank/typing_stub.py": "crank/typing_stub.py",
                    "./crank/async_.py": "crank/async_.py",
                    "./tests/test_basic.py": "test_basic.py",
                    "./tests/test_async.py": "test_async.py",
                    "./tests/test_components.py": "test_components.py",
                    "./tests/test_lifecycle.py": "test_lifecycle.py",
                    "./tests/test_hyperscript.py": "test_hyperscript.py",
                    "./tests/test_generators.py": "test_generators.py",
                    "./tests/test_dynamic_tags.py": "test_dynamic_tags.py"
                },
                "js_modules": {
                    "main": {
                        "https://cdn.jsdelivr.net/npm/@b9g/crank@0.7.1/crank.js": "crank_core",
                        "https://cdn.jsdelivr.net/npm/@b9g/crank@0.7.1/dom.js": "crank_dom",
                        "https://cdn.jsdelivr.net/npm/@b9g/crank@0.7.1/async.js": "crank_async"
                    }
                }
            }
        </py-config>
        """
        script_type = "py"

    html = f"""<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="./tests/pyscript/core.css">
    <script type="module" src="./tests/pyscript/core.js"></script>
</head>
<body>
    {config}
    <{script_type}-script>
import upytest

async def main():
    result = await upytest.run(".")

    passes = len(result.get("passes", []))
    fails = len(result.get("fails", []))
    skipped = len(result.get("skipped", []))

    import js
    js.window.TEST_RESULT = {{"passes": passes, "fails": fails, "skipped": skipped}}

await main()
    </{script_type}-script>
</body>
</html>"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Print console messages directly to stdout
        def handle_console(msg):
            if msg.type == "log":
                print(msg.text)
        page.on("console", handle_console)

        await page.goto("http://localhost:3333")
        await page.set_content(html)

        # Wait for results
        await page.wait_for_function("() => window.TEST_RESULT !== undefined", timeout=30000)

        result = await page.evaluate("() => window.TEST_RESULT")


        await browser.close()

        return result


async def main():
    pyodide_result = await run_tests("pyodide")
    micropython_result = await run_tests("micropython")

    total_fails = pyodide_result["fails"] + micropython_result["fails"]

    if total_fails > 0:
        return 1
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
