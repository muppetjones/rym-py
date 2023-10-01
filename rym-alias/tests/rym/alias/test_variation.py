#!/usr/bin/env python3
"""Test."""

import logging
from unittest import TestCase

import rym.alias.variation as MOD

LOGGER = logging.getLogger(__name__)


class ThisTestCase(TestCase):
    """Base test case for the module."""


class TestDeesser(ThisTestCase):
    """Test function."""

    def test_returns_expected(self):
        tests = [
            # (expected, given)
            ("foo", "foosss"),
            ("foo", "foos"),
            ("foo", "foo"),
            ("foso", "foso"),
            ("sfoo", "sfoo"),
        ]
        for expected, given in tests:
            with self.subTest(given):
                found = MOD.deesser(given)
                self.assertEqual(expected, found)


class TestEsser(ThisTestCase):
    """Test function."""

    def test_returns_expected(self):
        tests = [
            # (expected, given)
            ("foosss", "foosss"),
            ("foos", "foo"),
            ("fosos", "foso"),
            ("sfoos", "sfoo"),
        ]
        for expected, given in tests:
            with self.subTest(given):
                found = MOD.esser(given)
                self.assertEqual(expected, found)


class TestCapitalize(ThisTestCase):
    """Test function."""

    def test_returns_expected(self):
        given = "foo"
        expected = "Foo"
        found = MOD.capitalize(given)
        self.assertEqual(expected, found)


class TestLower(ThisTestCase):
    """Test function."""

    def test_returns_expected(self):
        given = "FOO"
        expected = "foo"
        found = MOD.lower(given)
        self.assertEqual(expected, found)


class TestUpper(ThisTestCase):
    """Test function."""

    def test_returns_expected(self):
        given = "foo"
        expected = "FOO"
        found = MOD.upper(given)
        self.assertEqual(expected, found)


# __END__
