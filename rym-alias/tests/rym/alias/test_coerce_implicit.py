#!/usr/bin/env python3
"""Test."""

import logging
from unittest import TestCase

import rym.alias._coerce_implicit as MOD
from rym.alias._coerce_explicit import get_alias_null

LOGGER = logging.getLogger(__name__)


class ThisTestCase(TestCase):
    """Base test case for the module."""


class TestCoerceImplicit(ThisTestCase):
    """Test function."""

    def test_implicit_bool(self) -> None:
        tests = [
            # (expected, given)
            (True, "TRUE"),
            (True, "True"),
            (True, "true"),
            (False, "FALSE"),
            (False, "False"),
            (False, "false"),
        ]
        for expected, given in tests:
            with self.subTest(given):
                found = MOD.coerce_implicit(given)
                assert isinstance(found, bool), type(found)
                self.assertEqual(expected, found)

    def test_implicit_float(self) -> None:
        tests = [
            # (expected, given)
            (1.0, 1.0),
            (2.0, "2."),
            (4000.1, "4_000.1"),
            (5000.2, "5,000.2"),
            (-6001.0006, "-6,001.000_6"),
            (7000, "7e3"),
            (0.007, "7e-3"),
        ]
        for expected, given in tests:
            with self.subTest(given):
                found = MOD.coerce_implicit(given)
                assert isinstance(found, float), type(found)
                self.assertEqual(expected, found)

    def test_implicit_integer(self) -> None:
        tests = [
            # (expected, given)
            (1, 1),
            (2, "2"),
            (4000, "4_000"),
            (5000, "5,000"),
            (-6001, "-6,001"),
            (7000, "7000"),
        ]
        for expected, given in tests:
            with self.subTest(given):
                found = MOD.coerce_implicit(given)
                assert isinstance(found, int), type(found)
                self.assertEqual(expected, found)

    def test_implicit_null(self) -> None:
        expected = None
        tests = get_alias_null().names
        for given in tests:
            with self.subTest(given):
                found = MOD.coerce_implicit(given)
                self.assertEqual(expected, found)


# __END__
