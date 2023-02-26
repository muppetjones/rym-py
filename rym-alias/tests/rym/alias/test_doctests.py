#!/usr/bin/env python3
"""Test."""

import doctest
import logging
import unittest as ut
from typing import Union

from rym.alias import _alias, _aliasresolver

LOGGER = logging.getLogger(__name__)


def load_tests(
    loader: ut.TestLoader,
    tests: Union[ut.TestCase, ut.TestSuite],
    ignore: str,
) -> ut.TestSuite:
    """Load doctests. For use with the unittest load_tests protocol."""
    tests.addTests(doctest.DocTestSuite(_alias))
    tests.addTests(doctest.DocTestSuite(_aliasresolver))
    return tests


# __END__
