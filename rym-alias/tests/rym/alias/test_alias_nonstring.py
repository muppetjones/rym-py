#!/usr/bin/env python3
"""Test rym.alias with non-string aliases."""

import logging
from unittest import TestCase

import rym.alias as MOD

LOGGER = logging.getLogger(__name__)


class ThisTestCase(TestCase):
    """Base test case for the module."""


class TestIfStrict(ThisTestCase):
    """Test feature."""

    def test_fails_on_init(self):
        with self.assertRaisesRegex(RuntimeError, "strict"):
            MOD.Alias(None, ["null"], strict=True)

    def test_fails_on_add_alias(self):
        subject = MOD.Alias("a", "b", strict=True)
        with self.assertRaisesRegex(RuntimeError, "strict"):
            subject.add_alias(None)


class TestIfNotStrict(ThisTestCase):
    """Test feature (default)."""

    def test_fails_if_not_hashable(self):
        with self.subTest("identity"):
            with self.assertRaisesRegex(TypeError, "unhashable"):
                MOD.Alias(["a"], ["b"])
        with self.subTest("alias"):
            with self.assertRaisesRegex(TypeError, "unhashable"):
                MOD.Alias("a", [["b"]])

    def test_default(self):
        subject = MOD.Alias("a", "b")
        expected = False
        found = subject.strict
        self.assertEqual(expected, found)

    def test_no_err_on_init(self):
        MOD.Alias(None, ["null"], strict=False)  # should not raise

    def test_no_err_on_add_alias(self):
        subject = MOD.Alias("a", "b", strict=False)
        subject.add_alias(None)  # should not raise

    def test_no_err_on_add_transform(self):
        subject = MOD.Alias(None, "b", strict=False)
        subject.add_transform(lambda x: x.capitalize())  # should not raise

    def test_no_err_on_set_transform(self):
        subject = MOD.Alias(None, "b", strict=False)
        subject.set_transforms(lambda x: x.capitalize())  # should not raise

    def test_all_names(self):
        subject = MOD.Alias(None, ["b", 0, False, (1,)], strict=False)
        expected = [0, "B", "b", (1,), None]
        found = subject.all_names()
        self.assertEqual(expected, found)

    def test_identify(self):
        subject = MOD.Alias(None, "b", strict=False)
        expected = [None, None]
        found = [subject.identify(None), subject.identify("b")]
        self.assertEqual(expected, found)

    def test_with_callable(self):
        subject = MOD.Alias(int, ["int", "integer"], strict=False)
        expected = [int, int]
        found = [subject.identify(int), subject.identify("integer")]
        self.assertEqual(expected, found)


# __END__
