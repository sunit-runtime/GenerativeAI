"""
Runs the provided code and test cases, then executes the tests and calculates the coverage.
Args:
    code (str): The code to be tested.
    test_cases (str): The test cases to run against the code.
Returns:
    tuple: A tuple containing:
        - result (unittest.result.TestResult): The result of the test run.
        - coverage (float): The percentage of tests that passed.
        - code (str): The original code that was tested.
Raises:
    Exception: If there is an error executing the code or test cases.
"""

import unittest


def run_tests(code, test_cases):
    try:
        exec(code, globals())
    except Exception as e:
        return f"Error executing code: {e}", 0

    try:
        exec(test_cases, globals())
    except Exception as e:
        return f"Error executing test cases: {e}", 0

    suite = unittest.TestLoader().discover(".")

    for name, obj in globals().items():
        if isinstance(obj, type) and issubclass(obj, unittest.TestCase):
            suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(obj))

    runner = unittest.TextTestRunner()
    result = runner.run(suite)

    coverage = (result.testsRun - len(result.failures)) / result.testsRun * 100

    return result, coverage, code
