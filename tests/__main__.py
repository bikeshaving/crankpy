#!/usr/bin/env python3
import asyncio
import sys
import argparse
import os
import glob

from playwright.async_api import async_playwright

async def run_test(test_file: str, runtime: str):
    config = {}
    if runtime == "micropython":
        config["experimental_create_proxy"] = "auto"
        script_type = "mpy"
    else:
        script_type = "py"

    config["files"] = {
        "https://raw.githubusercontent.com/ntoll/upytest/1.0.10/upytest.py": "upytest.py",
        "./crank/__init__.py": "crank/__init__.py",
        "./crank/dom.py": "crank/dom.py",
        "./crank/html.py": "crank/html.py",
        "./crank/typing_stub.py": "crank/typing_stub.py",
        "./crank/async_.py": "crank/async_.py",
        f"./tests/{test_file}": test_file
    }

    config["js_modules"] = {
        "main": {
            "/node_modules/@b9g/crank/crank.js": "crank_core",
            "/node_modules/@b9g/crank/dom.js": "crank_dom",
            "/node_modules/@b9g/crank/async.js": "crank_async"
        }
    }

    import json
    config_html = f"<{script_type}-config>{json.dumps(config)}</{script_type}-config>"

    html = f"""<!DOCTYPE html><html>
        <head>
            <title>Single Test: {test_file}</title>
            <link rel="stylesheet" href="/node_modules/@pyscript/core/dist/core.css">
            <script type="module" src="/node_modules/@pyscript/core/dist/core.js"></script>
        </head>
        <body>
            {config_html}
            <{script_type}-script>
import js
import upytest

async def main():
    result = await upytest.run("{test_file}")

    passes = len(result.get("passes", []))
    fails = len(result.get("fails", []))
    skipped = len(result.get("skipped", []))

    js.window.TEST_RESULT = {{"passes": passes, "fails": fails, "skipped": skipped}}

await main()
            </{script_type}-script>
        </body>
    </html>"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Forward console messages and capture errors from the browser
        script_error = None

        def handle_error(err):
            nonlocal script_error
            script_error = str(err)
            print(f"Script error: {err}")

        page.on("console", lambda msg: print(msg.text))
        page.on("pageerror", handle_error)

        await page.goto("http://localhost:3333")
        await page.set_content(html)

        # Wait for results - increase timeout for both runtimes as they can be slow
        # Pyodide especially needs more time for initial loading
        await page.wait_for_function("() => window.TEST_RESULT !== undefined", timeout=10000)
        result = await page.evaluate("() => window.TEST_RESULT")

        await browser.close()

        # If there was a script error, raise it
        if script_error:
            raise RuntimeError(f"PyScript execution failed: {script_error}")

        return result


async def main():
    parser = argparse.ArgumentParser(description="Run Crank.py tests")
    parser.add_argument("--runtime", choices=["pyodide", "micropython"],
                       help="Run tests for specific runtime only")
    parser.add_argument("tests", nargs="*",
                       help="Test files or patterns to run (e.g., test_basic.py, basic, async)")
    parser.add_argument("-k", "--keyword", dest="keyword",
                       help="Run tests matching given substring expression")
    args = parser.parse_args()

    # Find all test files in the tests directory
    all_test_files = [os.path.basename(f) for f in glob.glob("tests/test_*.py")]

    # Determine which test files to run
    if args.tests:
        test_files = []
        for test_pattern in args.tests:
            # Allow both "basic" and "test_basic.py" formats
            if test_pattern.endswith(".py"):
                test_file = test_pattern
            else:
                test_file = f"test_{test_pattern}.py"

            if test_file in all_test_files:
                test_files.append(test_file)
            else:
                print(f"Warning: Unknown test '{test_pattern}'")

        if not test_files:
            available = ', '.join([f.replace('test_', '').replace('.py', '') for f in all_test_files])
            print(f"No valid tests specified. Available: {available}")
            return 1
    elif args.keyword:
        # Filter test files by keyword
        test_files = []
        for test_file in all_test_files:
            test_name = test_file.replace("test_", "").replace(".py", "")
            if args.keyword.lower() in test_name.lower():
                test_files.append(test_file)

        if not test_files:
            available = ', '.join([f.replace('test_', '').replace('.py', '') for f in all_test_files])
            print(f"No tests match keyword '{args.keyword}'. Available: {available}")
            return 1
    else:
        # Run all tests if no specific tests specified
        test_files = all_test_files

    # Determine which runtimes to run
    runtimes = []
    if args.runtime:
        runtimes = [args.runtime]
    else:
        runtimes = ["pyodide", "micropython"]

    total_fails = 0

    for runtime in runtimes:
        print(f"\nRunning {len(test_files)} test files for {runtime}...")

        runtime_fails = 0

        for test_file in test_files:
            print(f"\nRunning {test_file} on {runtime}...")
            try:
                result = await run_test(test_file, runtime)
                runtime_fails += result["fails"]
            except Exception as e:
                print(f"{test_file}: Error running test - {e}")
                runtime_fails += 1

        total_fails += runtime_fails

    return 1 if total_fails > 0 else 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
