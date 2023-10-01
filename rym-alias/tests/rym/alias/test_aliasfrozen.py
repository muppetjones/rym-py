#!/usr/bin/env python3
"""Test."""

import logging
from unittest import TestCase

import rym.alias._aliasfrozen as MOD
from rym.alias._alias import Alias

LOGGER = logging.getLogger(__name__)


class ThisTestCase(TestCase):
    """Base test case for the module."""


class TestFrozenAlias(ThisTestCase):
    """Test class."""

    def test_build(self):
        subject = MOD.FrozenAlias.build("a", list("xyz"))
        expected = "a"
        found = subject.identify("x")
        self.assertEqual(expected, found)

    def test_clone(self):
        given = Alias("a", list("xyz"))

        with self.subTest("from alias"):
            subject = MOD.FrozenAlias.clone(given)
            expected = "a"
            found = subject.identify("x")
            self.assertEqual(expected, found)

        with self.subTest("from frozen"):
            subject = MOD.FrozenAlias.clone(subject)
            expected = "a"
            found = subject.identify("x")
            self.assertEqual(expected, found)

    def test_is_hashable(self):
        subject = MOD.FrozenAlias("a", tuple("xyz"))
        _ = {subject: True}  # should not raise

    def test_identity(self):
        subject = MOD.FrozenAlias("a", tuple("xyz"))
        with self.subTest("found"):
            expected = "a"
            found = subject.identify("x")
            self.assertEqual(expected, found)
        with self.subTest("missing"):
            with self.assertRaises(KeyError):
                subject.identify("b")


# __END__
