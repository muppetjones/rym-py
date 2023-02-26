#!/usr/bin/env python3
"""Test."""

import doctest
import logging
from typing import Union
from unittest import TestCase, TestLoader, TestSuite

from rym.lpath import _delim, _get, _remove, _set

LOGGER = logging.getLogger(__name__)


def load_tests(
    loader: TestLoader,
    tests: Union[TestCase, TestSuite],
    ignore: str,
) -> TestSuite:
    """Load doctests. For use with the unittest load_tests protocol."""
    mods = (_get, _set, _remove, _delim)
    for mod in mods:
        tests.addTests(doctest.DocTestSuite(mod))
    return tests


# __END__
