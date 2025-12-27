"""
Test Runner for MicroPython Calculator
Runs all unit tests and displays results
"""

import unittest
import sys

def run_all_tests() -> int:
    """Discover and run all tests"""
    # Create test loader
    loader: unittest.TestLoader = unittest.TestLoader()

    # Discover all tests in current directory
    suite: unittest.TestSuite = loader.discover('.', pattern='test_*.py')

    # Run tests with verbose output
    runner: unittest.TextTestRunner = unittest.TextTestRunner(verbosity=2)
    result: unittest.TestResult = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)

    # Return exit code
    return 0 if result.wasSuccessful() else 1

def run_specific_module(module_name: str) -> int:
    """Run tests from a specific module"""
    loader: unittest.TestLoader = unittest.TestLoader()
    suite: unittest.TestSuite = loader.loadTestsFromName(module_name)
    runner: unittest.TextTestRunner = unittest.TextTestRunner(verbosity=2)
    result: unittest.TestResult = runner.run(suite)
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Run specific test module
        exit_code: int = run_specific_module(sys.argv[1])
    else:
        # Run all tests
        exit_code: int = run_all_tests()

    sys.exit(exit_code)
