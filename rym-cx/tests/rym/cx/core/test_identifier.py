#!/usr/bin/env python3
"""Test."""

import logging
from unittest import TestCase
from uuid import uuid4

import rym.cx.core.identifier as MOD

LOGGER = logging.getLogger(__name__)


class ThisTestCase(TestCase):
    """Base test case for the module."""


class TestGenerateNamespaceHash(ThisTestCase):
    """Test function."""

    def test_raises_if_given_non_string(self) -> None:
        tests = [0, ["x"], uuid4()]
        for given in tests:
            with self.subTest(given):
                with self.assertRaises(TypeError):
                    MOD.generate_namespace_hash(given)

    def test_returns_same_value_given_same_value(self) -> None:
        a = MOD.generate_namespace_hash("foo")
        b = MOD.generate_namespace_hash("bar")
        c = MOD.generate_namespace_hash("foo")

        self.assertEqual(a, c)
        self.assertNotEqual(b, c)


class TestGenerateUid(ThisTestCase):
    """Test function."""

    def test_behavior(self) -> None:
        class Foo:
            ...

        class Bar:
            ...

        a = MOD.generate_uid("x", Foo)
        b = MOD.generate_uid("y", Foo)
        c = MOD.generate_uid("x", Bar)
        d = MOD.generate_uid("x", Foo)
        e = MOD.generate_uid("x", "Foo")

        self.assertEqual(a, d)
        self.assertEqual(a, e)  # same name! let catalog handle collisions
        self.assertNotEqual(a, b)
        self.assertNotEqual(b, c)


# __END__
