#!/usr/bin/env python3
"""Test."""

import logging
from unittest import TestCase
from unittest.mock import Mock

import rym.alias._coerce as MOD

LOGGER = logging.getLogger(__name__)


class ThisTestCase(TestCase):
    """Base test case for the module."""


class TestAsBool(ThisTestCase):
    """Test method."""

    def test_returns_True_if_truthy(self):
        subject = MOD.get_default_coercer()
        tests = ["a", 1, True, ["x"]]
        expected = [True] * len(tests)
        found = [subject.coerce(x, converter="bool") for x in tests]
        self.assertEqual(expected, found)

    def test_returns_False_if_falsy(self):
        subject = MOD.get_default_coercer()
        tests = ["", False, 0, []]
        expected = [False] * len(tests)
        found = [subject.coerce(x, converter="bool") for x in tests]
        self.assertEqual(expected, found)

    def test_returns_True_if_true_alias(self):
        subject = MOD.get_default_coercer()
        tests = ["true", "True", "TRUE"]
        expected = [True] * len(tests)
        found = [subject.coerce(x, converter="bool") for x in tests]
        self.assertEqual(expected, found)

    def test_returns_False_if_false_alias(self):
        subject = MOD.get_default_coercer()
        tests = ["false", "False", "FALSE"]
        expected = [False] * len(tests)
        found = [subject.coerce(x, converter="bool") for x in tests]
        self.assertEqual(expected, found)

    def test_no_converter_aliases(self):
        subject = MOD.Coercer(logger=Mock())
        tests = ["", "a", "false"]
        expected = [False, True, True]
        found = [subject.coerce(x, converter="bool") for x in tests]
        self.assertEqual(expected, found)


class TestAsNull(ThisTestCase):
    """Test method."""

    def test_returns_value_if_truthy(self):
        subject = MOD.get_default_coercer()
        tests = ["a", 1, True, ["x"]]
        expected = tests[:]
        found = [subject.coerce(x, converter="null") for x in tests]
        self.assertEqual(expected, found)

    def test_returns_None_if_falsy(self):
        subject = MOD.get_default_coercer()
        tests = ["", False, 0, []]
        expected = [None] * len(tests)
        found = [subject.coerce(x, converter="null") for x in tests]
        self.assertEqual(expected, found)

    def test_returns_None_if_null_alias(self):
        subject = MOD.get_default_coercer()
        tests = ["null", "NIL", "n/a", None]
        expected = [None] * len(tests)
        found = [subject.coerce(x, converter="null") for x in tests]
        self.assertEqual(expected, found)

    def test_no_converter_aliases(self):
        subject = MOD.Coercer(logger=Mock())
        tests = ["", "a", "nil"]
        expected = [None, "a", "nil"]
        found = [subject.coerce(x, converter="null") for x in tests]
        self.assertEqual(expected, found)


# __END__
