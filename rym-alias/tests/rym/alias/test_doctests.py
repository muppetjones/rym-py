#!/usr/bin/env python3
"""Test."""

import doctest
import logging
from typing import Union
from unittest import TestCase, TestLoader, TestSuite

from rym.alias import _alias, _aliasresolver

LOGGER = logging.getLogger(__name__)


def load_tests(
    loader: TestLoader,
    tests: Union[TestCase, TestSuite],
    ignore: str,
) -> TestSuite:
    """Load doctests. For use with the unittest load_tests protocol."""
    tests.addTests(doctest.DocTestSuite(_alias))
    tests.addTests(doctest.DocTestSuite(_aliasresolver))
    return tests


# __END__
