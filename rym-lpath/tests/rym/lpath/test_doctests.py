#!/usr/bin/env python3
"""Test."""

import doctest
import logging
import unittest as ut
from typing import Union

from rym.lpath import _delim, _get, _remove, _set

LOGGER = logging.getLogger(__name__)


def load_tests(
    loader: ut.TestLoader,
    tests: Union[ut.TestCase, ut.TestSuite],
    ignore: str,
) -> ut.TestSuite:
    """Load doctests. For use with the unittest load_tests protocol."""
    mods = (_get, _set, _remove, _delim)
    for mod in mods:
        tests.addTests(doctest.DocTestSuite(mod))
    return tests


# __END__
