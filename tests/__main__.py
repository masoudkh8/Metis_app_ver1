"""
Test suite for the Flask application.
Run all tests with: python -m unittest discover tests -v
"""

import unittest


def create_test_suite():
    """Create a test suite with all test cases."""
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir='tests', pattern='test_*.py')
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    suite = create_test_suite()
    runner.run(suite)
