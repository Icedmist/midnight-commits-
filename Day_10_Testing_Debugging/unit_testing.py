"""
Unit Testing Framework
Build comprehensive unit tests with fixtures, mocks, and coverage reporting
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Callable, Any
import logging
from functools import wraps
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def timer_decorator(func):
    """Decorator to measure function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        logger.info(f"⏱️  {func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper


class TestCase(unittest.TestCase):
    """Extended TestCase with helpers"""

    def setUp(self):
        """Setup before each test"""
        self.test_start = time.time()
        logger.info(f"🧪 Starting: {self._testMethodName}")

    def tearDown(self):
        """Teardown after each test"""
        elapsed = time.time() - self.test_start
        logger.info(f"✅ Completed: {self._testMethodName} ({elapsed:.4f}s)")

    def assert_raises_with_message(self, exception: Exception, message: str, func: Callable, *args):
        """Assert exception with specific message"""
        with self.assertRaises(exception) as context:
            func(*args)
        self.assertIn(message, str(context.exception))

    def assert_in_range(self, value: float, min_val: float, max_val: float):
        """Assert value is in range"""
        self.assertTrue(min_val <= value <= max_val,
                       f"{value} not in range [{min_val}, {max_val}]")


class MockDatabase:
    """Mock database for testing"""

    def __init__(self):
        """Initialize mock database"""
        self.data = {}
        self.call_count = 0

    def insert(self, key: str, value: Any) -> bool:
        """Insert data"""
        self.call_count += 1
        self.data[key] = value
        return True

    def get(self, key: str) -> Any:
        """Retrieve data"""
        self.call_count += 1
        return self.data.get(key)

    def delete(self, key: str) -> bool:
        """Delete data"""
        self.call_count += 1
        return key in self.data and bool(self.data.pop(key, False))

    def clear(self) -> None:
        """Clear all data"""
        self.data.clear()


class BasicTests(TestCase):
    """Example tests"""

    def setUp(self):
        super().setUp()
        self.mock_db = MockDatabase()

    def test_database_insert(self):
        """Test database insert"""
        result = self.mock_db.insert("user:1", {"name": "Alice"})
        self.assertTrue(result)
        self.assertEqual(self.mock_db.call_count, 1)

    def test_database_get(self):
        """Test database retrieval"""
        self.mock_db.insert("user:1", {"name": "Alice"})
        user = self.mock_db.get("user:1")
        self.assertIsNotNone(user)
        self.assertEqual(user["name"], "Alice")

    def test_database_delete(self):
        """Test database deletion"""
        self.mock_db.insert("user:1", {"name": "Alice"})
        result = self.mock_db.delete("user:1")
        self.assertTrue(result)
        self.assertIsNone(self.mock_db.get("user:1"))

    def test_exception_handling(self):
        """Test exception handling"""
        def divide_by_zero():
            return 1 / 0

        self.assertRaises(ZeroDivisionError, divide_by_zero)

    @patch('requests.get')
    def test_api_call(self, mock_get):
        """Test API call with mock"""
        mock_get.return_value.json.return_value = {"status": "ok"}
        mock_get.return_value.status_code = 200

        # Simulated API call
        import requests
        response = requests.get("https://api.example.com")

        self.assertEqual(response.status_code, 200)
        mock_get.assert_called_once()


class ParameterizedTests(TestCase):
    """Parametrized tests"""

    def test_string_operations(self):
        """Test various string operations"""
        test_cases = [
            ("hello", 5),
            ("world", 5),
            ("python", 6),
            ("", 0)
        ]

        for string, expected_length in test_cases:
            with self.subTest(string=string):
                self.assertEqual(len(string), expected_length)

    def test_math_operations(self):
        """Test math operations"""
        test_cases = [
            (2, 3, 5),
            (10, 5, 15),
            (0, 0, 0),
            (-5, 5, 0)
        ]

        for a, b, expected in test_cases:
            with self.subTest(a=a, b=b):
                self.assertEqual(a + b, expected)


class TestRunner:
    """Enhanced test runner"""

    def __init__(self):
        """Initialize test runner"""
        self.results = None

    def run_tests(self, test_module=None, verbosity=2):
        """Run tests"""
        loader = unittest.TestLoader()
        
        if test_module:
            suite = loader.loadTestsFromModule(test_module)
        else:
            suite = loader.discover('.', pattern='test_*.py')

        runner = unittest.TextTestRunner(verbosity=verbosity)
        self.results = runner.run(suite)

        return self.get_summary()

    def run_single_test(self, test_class: str, test_method: str):
        """Run single test"""
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Add specific test
        test = globals()[test_class](test_method)
        suite.addTest(test)

        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        return result.wasSuccessful()

    def get_summary(self) -> dict:
        """Get test summary"""
        if not self.results:
            return {}

        return {
            'tests_run': self.results.testsRun,
            'successes': self.results.testsRun - len(self.results.failures) - len(self.results.errors),
            'failures': len(self.results.failures),
            'errors': len(self.results.errors),
            'skipped': len(self.results.skipped)
        }


if __name__ == "__main__":
    print("🧪 Unit Testing Framework\n")
    
    print("Features:")
    print("✓ Test cases with fixtures")
    print("✓ Mock objects")
    print("✓ Parametrized tests")
    print("✓ Exception testing")
    print("✓ Test runner")
    print("✓ Coverage reporting")
    
    print("\nRun tests with:")
    print("  python -m unittest discover")
    print("  coverage run -m unittest discover")
    print("  coverage report")
