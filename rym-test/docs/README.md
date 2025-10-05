# Purpose

The `rym-test` package is intended to be an adapter or wrapper around your testing framework of choice. It is not itself a testing framework. The goal of rym-test is to:

1. Ensure test visibility. Most python namespaces are defined by `__init__.py` files, and test suites often rely on these files to accurately discover tests. If these files are missing -- either intentionally as with implicit namespaces or accidentally -- the test suite may not function as intended.

2. Ensure test suite accessibility. While most test frameworks support the builtin `unittest` patterns, there are differences in how certain features are accessed:
    1. Identify tests at the command line using either a dot path, e.g., `unittest`, or file and colon-delimited path, e.g., `pytest`.
    2. Auto-discover regardless of the path.

3. Ensure test flexibility. The primary goal is to provide a unified interface without requiring a specific test framework. This pattern should make it easier to ensure a consistent pattern and interface regardless of which test framework is used.
    1. Allow users to define and configure the testing framework independently of this library.
    2. Auto-set coverage parameters based on the test path. In other words, don't rely on hard-coded, configuration-based coverage settings.

# General Test Patterns

1. **One** assert per test.
2. Prefer equality checks where possible as this can reduce complexity and improve consistency.
3. Use a common format:
    1. Always clearly identify test setup, e.g., mocks.
    2. Clearly define the input variables (and constants).
    3. Clearly indicate the subject under test.
    4. Clearly indicate the expected outcome.
    5. Clearly indicate the found value.


# Aside on `pytest`

Personally, I don't like `pytest`, and I strongly prefer `unittest`. 

1. All python testing frameworks support `unittest`, so all tests should be written in `unittest` to allow developers the freedom of choice to execute tests with their preferred framework. 
    1. _This does not preclude use of a common framework for automated CI/CD._
2. The `unittest` pattern provides a structure that helps organize tests.
3. It is very easy to write unmaintainable tests in `pytest`:
    1. Use of `assert` statements without ensuring feedback about the result; compare against `self.assertEqual`.
    2. Hidden `pytest` fixtures. `pytest` fixtures can get out of hand very easily and result in implicit, poorly defined behaviors and spaghetti code.
    3. Large, unorganized tests.
