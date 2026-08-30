#!/usr/bin/env python
import sys
import unittest
from pathlib import Path

if __name__ == '__main__':
    loader = unittest.TestLoader()
    tests_directory = Path(__file__).resolve().parent / "tests"
    suite = loader.discover(str(tests_directory), pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
