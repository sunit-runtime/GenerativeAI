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
