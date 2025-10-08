"""
Global setup and teardown for upytest test suite.

This file provides global configuration for all upytest tests.
"""
import sys


def setup():
    """Global setup function called before all tests"""
    print(f"\n🧪 Setting up test environment for {sys.implementation.name}")
    print(f"Python version: {sys.version}")
    
    # Verify core imports work
    try:
        from crank import h, component
        print("✅ Crank.py imports successful")
    except ImportError as e:
        print(f"❌ Crank.py import failed: {e}")
        raise
    
    # Test runtime detection
    if sys.implementation.name == 'micropython':
        print("🐍 Running on MicroPython - async generator limitations expected")
    else:
        print("🐍 Running on Pyodide/CPython - full async support available")


def teardown():
    """Global teardown function called after all tests"""
    print(f"\n🧹 Cleaning up test environment for {sys.implementation.name}")
    print("✅ Test cleanup complete")