#!/usr/bin/env python3
"""Test."""

import logging
from unittest import TestCase

import rym.lpath._delim as MOD

LOGGER = logging.getLogger(__name__)


class ThisTestCase(TestCase):
    """Base test case for the module."""

    def setUp(self) -> None:
        MOD.reset_delimiter()
        self.addCleanup(MOD.reset_delimiter)
        return super().setUp()


class TestGetDelimiter(ThisTestCase):
    """Test function."""

    def test_returns_default(self):
        expected = "."
        found = MOD.get_delimiter()
        self.assertEqual(expected, found)

    def test_returns_current(self):
        MOD._DELIMITER = "/"
        expected = "/"
        found = MOD.get_delimiter()
        self.assertEqual(expected, found)


class TestResetDelimiter(ThisTestCase):
    """Test function."""

    def test_sets_to_default(self):
        MOD._DELIMITER = "/"
        MOD.reset_delimiter()
        expected = "."
        found = MOD._DELIMITER
        self.assertEqual(expected, found)


class TestSetDelimiter(ThisTestCase):
    """Test function."""

    def test_sets_to_given(self):
        MOD.set_delimiter("@")
        expected = "@"
        found = MOD._DELIMITER
        self.assertEqual(expected, found)


# __END__
