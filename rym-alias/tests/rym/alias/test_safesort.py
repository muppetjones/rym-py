#!/usr/bin/env python3
"""Test."""

import logging
from unittest import TestCase

import rym.alias.safesort as MOD

LOGGER = logging.getLogger(__name__)


class ThisTestCase(TestCase):
    """Base test case for the module."""


class TestSafeSort(ThisTestCase):
    """Test function."""

    maxDiff = None

    def test_returns_expected(self):
        class Foo:
            ...

        obj = Foo()
        given = ["a", 10, 1, 2, "A", Foo, obj]
        expected = [1, 2, 10, "A", "a", Foo, obj]
        found = MOD.safesorted(given)
        self.assertEqual(expected, found, found)

    def test_supports_key(self) -> None:
        class Foo:
            ...

        obj = Foo()
        given = ["B", 10, 1, 2, "a", Foo, obj]
        # upper will sort 'a' before 'B'
        # values supported by 'key' will be first
        expected = ["a", "B", 1, 2, 10, Foo, obj]
        found = MOD.safesorted(given, key=lambda x: x.upper())
        self.assertEqual(expected, found)

    def test_supports_reverse(self):
        class Foo:
            ...

        obj = Foo()
        given = ["a", 10, 1, 2, "A", Foo, obj]
        expected = [obj, Foo, "a", "A", 10, 2, 1]
        found = MOD.safesorted(given, reverse=True)
        self.assertEqual(expected, found, found)


# __END__
