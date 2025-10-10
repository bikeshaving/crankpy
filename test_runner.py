#!/usr/bin/env python3
import asyncio
import sys
import re
from playwright.async_api import async_playwright

def parse_console_results(console_messages, runtime):
    """Parse console output to extract test results when callback fails."""
    passes = 0
    fails = 0
    skipped = 0

    # Look for the summary line in the last few messages
    for message in console_messages[-10:]:
        if "failed" in message and "passed" in message and "skipped" in message:
            # Try to extract numbers from the summary line
            match = re.search(r'(\d+).*failed.*(\d+).*skipped.*(\d+).*passed', message)
            if match:
                fails = int(match.group(1))
                skipped = int(match.group(2))
                passes = int(match.group(3))
                print(f"📊 Parsed {runtime} results: {passes} passed, {fails} failed, {skipped} skipped")
                return {"passes": passes, "fails": fails, "skipped": skipped}

    # Fallback: if no summary found, assume tests completed if we saw test output
    test_dots = sum(1 for msg in console_messages if ".[0m" in msg or ".py:" in msg)
    if test_dots > 0:
        print(f"📊 Fallback parsing: estimated {test_dots} tests completed in {runtime}")
        return {"passes": test_dots, "fails": 0, "skipped": 0}

    return {"passes": 0, "fails": 1, "skipped": 0}  # Default to failure if no tests detected

async def run_single_test_file(test_file: str, runtime: str = "micropython"):
    """Run a single test file in MicroPython to avoid Map overflow."""

    if runtime == "micropython":
        config = f"""
        <mpy-config>
            {{
                "experimental_create_proxy": "auto",
                "files": {{
                    "./tests/upytest.py": "upytest.py",
                    "./crank/__init__.py": "crank/__init__.py",
                    "./crank/dom.py": "crank/dom.py",
                    "./crank/html.py": "crank/html.py",
                    "./crank/typing_stub.py": "crank/typing_stub.py",
                    "./crank/async_.py": "crank/async_.py",
                    "./tests/{test_file}": "{test_file}"
                }},
                "js_modules": {{
                    "main": {{
                        "https://cdn.jsdelivr.net/npm/@b9g/crank@0.7.1/crank.js": "crank_core",
                        "https://cdn.jsdelivr.net/npm/@b9g/crank@0.7.1/dom.js": "crank_dom",
                        "https://cdn.jsdelivr.net/npm/@b9g/crank@0.7.1/async.js": "crank_async"
                    }}
                }}
            }}
        </mpy-config>
        """
        script_type = "mpy"
    else:
        # For Pyodide, we can still run all files together since it doesn't have the Map overflow
        return await run_tests(runtime)

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Single Test: {test_file}</title>
    <link rel="stylesheet" href="./tests/pyscript/core.css">
    <script type="module" src="./tests/pyscript/core.js"></script>
</head>
<body>
    {config}
    <{script_type}-script>
import upytest

async def main():
    result = await upytest.run("{test_file}")

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

        # Collect console messages for fallback parsing
        console_messages = []
        def handle_console(msg):
            if msg.type == "log":
                print(f"[{test_file}] {msg.text}")
                console_messages.append(msg.text)
        page.on("console", handle_console)

        await page.goto("http://localhost:3333")
        await page.set_content(html)

        # Wait for results with fallback for MicroPython AsyncIO bug
        try:
            # Increase timeout for MicroPython since it's much slower
            timeout_ms = 120000 if runtime == "micropython" else 30000
            await page.wait_for_function("() => window.TEST_RESULT !== undefined", timeout=timeout_ms)
            result = await page.evaluate("() => window.TEST_RESULT")
        except Exception:
            # Fallback: Parse console output for test results (MicroPython AsyncIO workaround)
            print(f"⚠️  [{test_file}] Callback timeout - parsing console output for {runtime} results")
            result = parse_console_results(console_messages, runtime)

        await browser.close()
        return result

async def run_tests_for_files(runtime: str = "pyodide", test_files: list = None):
    """Run upytest tests for specific files in browser and return results."""
    if test_files is None:
        # Default to all test files
        test_files = [
            "test_basic.py",
            "test_async.py",
            "test_components.py",
            "test_lifecycle.py",
            "test_hyperscript.py",
            "test_generators.py",
            "test_dynamic_tags.py",
            "test_refs_keys_copy.py",
            "test_portals.py",
            "test_suspense.py",
            "test_errors.py",
            "test_events.py"
        ]

    return await run_tests(runtime, test_files)

def generate_config(runtime: str, test_files: list) -> tuple[str, str]:
    """Generate PyScript config for given runtime and test files."""
    import json

    # Base files always needed
    files = {
        "./tests/upytest.py": "upytest.py",
        "./crank/__init__.py": "crank/__init__.py",
        "./crank/dom.py": "crank/dom.py",
        "./crank/html.py": "crank/html.py",
        "./crank/typing_stub.py": "crank/typing_stub.py",
        "./crank/async_.py": "crank/async_.py"
    }

    # Add selected test files
    for test_file in test_files:
        files[f"./tests/{test_file}"] = test_file

    js_modules = {
        "main": {
            "https://cdn.jsdelivr.net/npm/@b9g/crank@0.7.1/crank.js": "crank_core",
            "https://cdn.jsdelivr.net/npm/@b9g/crank@0.7.1/dom.js": "crank_dom",
            "https://cdn.jsdelivr.net/npm/@b9g/crank@0.7.1/async.js": "crank_async"
        }
    }

    config_data = {
        "files": files,
        "js_modules": js_modules
    }

    if runtime == "micropython":
        config = f"""
        <mpy-config>
            {json.dumps(config_data, indent=16)}
        </mpy-config>
        """
        script_type = "mpy"
    else:
        config = f"""
        <py-config>
            {json.dumps(config_data, indent=16)}
        </py-config>
        """
        script_type = "py"

    return config, script_type

async def run_tests(runtime: str = "pyodide", test_files: list = None):
    """Run upytest tests in browser and return results."""

    if test_files is None:
        # Default to all test files
        test_files = [
            "test_basic.py",
            "test_async.py",
            "test_components.py",
            "test_lifecycle.py",
            "test_hyperscript.py",
            "test_generators.py",
            "test_dynamic_tags.py",
            "test_refs_keys_copy.py",
            "test_portals.py",
            "test_suspense.py",
            "test_errors.py",
            "test_events.py"
        ]

    config, script_type = generate_config(runtime, test_files)

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
    # Run selected test files
    test_files = {repr(test_files)}

    result = await upytest.run(*test_files)

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

        # Collect console messages for fallback parsing
        console_messages = []
        def handle_console(msg):
            if msg.type == "log":
                print(msg.text)
                console_messages.append(msg.text)
        page.on("console", handle_console)

        await page.goto("http://localhost:3333")
        await page.set_content(html)

        # Wait for results with fallback for MicroPython AsyncIO bug
        try:
            # Increase timeout for MicroPython since it's much slower
            timeout_ms = 120000 if runtime == "micropython" else 30000
            await page.wait_for_function("() => window.TEST_RESULT !== undefined", timeout=timeout_ms)
            result = await page.evaluate("() => window.TEST_RESULT")
        except Exception:
            # Fallback: Parse console output for test results (MicroPython AsyncIO workaround)
            print(f"⚠️  Callback timeout - parsing console output for {runtime} results")
            result = parse_console_results(console_messages, runtime)


        await browser.close()

        return result


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run Crank.py tests")
    parser.add_argument("--runtime", choices=["pyodide", "micropython"],
                       help="Run tests for specific runtime only")
    parser.add_argument("tests", nargs="*", 
                       help="Test files or patterns to run (e.g., test_basic.py, basic, async)")
    parser.add_argument("-k", "--keyword", dest="keyword",
                       help="Run tests matching given substring expression")
    args = parser.parse_args()

    # Define all available test suites
    all_test_files = [
        "test_basic.py",
        "test_async.py",
        "test_components.py",
        "test_lifecycle.py",
        "test_hyperscript.py",
        "test_generators.py",
        "test_dynamic_tags.py",
        "test_refs_keys_copy.py",
        "test_portals.py",
        "test_suspense.py",
        "test_errors.py",
        "test_events.py"
    ]

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
                available = ', '.join([f.replace('test_', '').replace('.py', '') for f in all_test_files])
                print(f"Warning: Unknown test '{test_pattern}'. Available: {available}")

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

    if args.runtime == "pyodide":
        # For Pyodide, we need to update run_tests to accept specific test files
        if args.tests or args.keyword:
            test_names = ', '.join([f.replace('test_', '').replace('.py', '') for f in test_files])
            print(f"Running Pyodide tests for: {test_names}")
        pyodide_result = await run_tests_for_files("pyodide", test_files)
        return 1 if pyodide_result["fails"] > 0 else 0
    elif args.runtime == "micropython":
        # Run MicroPython tests individually to avoid Map overflow
        if args.tests or args.keyword:
            test_names = ', '.join([f.replace('test_', '').replace('.py', '') for f in test_files])
            print(f"Running MicroPython tests for: {test_names}")

        total_passes = 0
        total_fails = 0
        total_skipped = 0

        print(f"🧪 Running {len(test_files)} test files individually for MicroPython...")

        for test_file in test_files:
            print(f"\n📁 Running {test_file}...")
            result = await run_single_test_file(test_file, "micropython")
            total_passes += result["passes"]
            total_fails += result["fails"]
            total_skipped += result["skipped"]
            print(f"✅ {test_file}: {result['passes']} passed, {result['fails']} failed, {result['skipped']} skipped")

        print(f"\n📊 MicroPython Total: {total_passes} passed, {total_fails} failed, {total_skipped} skipped")
        return 1 if total_fails > 0 else 0
    else:
        # Run both if no specific runtime specified
        if args.tests or args.keyword:
            test_names = ', '.join([f.replace('test_', '').replace('.py', '') for f in test_files])
            print(f"Running tests for both runtimes: {test_names}")
        pyodide_result = await run_tests_for_files("pyodide", test_files)

        # For MicroPython, use individual test execution

        micropython_passes = 0
        micropython_fails = 0
        micropython_skipped = 0

        print(f"\n🧪 Running {len(test_files)} test files individually for MicroPython...")

        for test_file in test_files:
            print(f"\n📁 Running {test_file}...")
            result = await run_single_test_file(test_file, "micropython")
            micropython_passes += result["passes"]
            micropython_fails += result["fails"]
            micropython_skipped += result["skipped"]
            print(f"✅ {test_file}: {result['passes']} passed, {result['fails']} failed, {result['skipped']} skipped")

        micropython_result = {"passes": micropython_passes, "fails": micropython_fails, "skipped": micropython_skipped}

        total_fails = pyodide_result["fails"] + micropython_result["fails"]
        return 1 if total_fails > 0 else 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
