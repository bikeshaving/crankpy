"""
Test suite with intentional failures and skips to verify test runner reporting.
This ensures the test runner correctly detects and displays different test outcomes.
"""
import upytest


class TestDummyResults:
    """Test class with mixed results for testing the test runner"""
    
    def test_pass_1(self):
        """This test should pass"""
        assert True
    
    def test_pass_2(self):
        """Another passing test"""
        assert 1 + 1 == 2
    
    def test_fail_1(self):
        """This test should fail"""
        assert False, "Intentional failure for testing"
    
    def test_fail_2(self):
        """Another failing test"""
        assert 1 + 1 == 3, "Math is broken"
    
    def test_skip_1(self):
        """This test should be skipped"""
        upytest.skip("Intentionally skipped for testing")
    
    def test_skip_2(self):
        """Another skipped test"""
        upytest.skip("Another intentional skip")
    
    def test_pass_3(self):
        """Final passing test"""
        assert "hello" == "hello"


class TestMoreResults:
    """Another test class with different results"""
    
    def test_another_pass(self):
        """This should pass"""
        assert len([1, 2, 3]) == 3
    
    def test_another_fail(self):
        """This should fail"""
        raise ValueError("Intentional error for testing")
        
    def test_another_skip(self):
        """This should be skipped"""
        upytest.skip("Third intentional skip")