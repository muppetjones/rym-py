#!/usr/bin/env python3
"""Test."""

import itertools
import logging
from types import SimpleNamespace
from typing import Mapping
from unittest import TestCase, mock

import rym.lpath as MOD

LOGGER = logging.getLogger(__name__)


class ThisTestCase(TestCase):
    """Base test case for the module."""


class TestGet(ThisTestCase):
    """Test function."""

    def get_example(self) -> Mapping:
        """Return complex nested structure."""
        data = {
            "a": "a",
            "b": ["b0", "b1", "baz"],
            "c": {"foo": "meh"},
            "d": SimpleNamespace(bar="d"),
        }
        return {
            "list": list(data.values()),
            "mapping": data.copy(),
            "namespace": SimpleNamespace(**data),
        }

    def test_raises_if_invalid_key(self):
        tests = [
            (ValueError, 42),
            # (ValueError, {"foo": "bar"}),
        ]
        for exc_type, key in tests:
            with self.subTest(key=key):
                with self.assertRaisesRegex(exc_type, "invalid key"):
                    MOD.get({}, key)

    def test_raises_if_invalid_path(self):
        # i.e., given key is invalid for the object type
        example = self.get_example()
        tests = [
            # (error, msg, key)
            (ValueError, None, "list.a.other"),
            (ValueError, None, "mapping.a.other"),
            (ValueError, None, "mapping.b.other"),
            (ValueError, None, "namespace.a.other"),
        ]
        for exc_type, msg, key in tests:
            msg = msg or key
            with self.subTest(key=key):
                with self.assertRaisesRegex(exc_type, msg):
                    MOD.get(example, key)

    def test_raises_if_key_not_found(self):
        example = self.get_example()
        tests = [
            # (error, msg, key)
            (KeyError, None, "other"),
            (KeyError, None, "list.2.other"),
            (KeyError, None, "mapping.other"),
            (KeyError, None, "mapping.c.other"),
            (IndexError, None, "mapping.b.4"),
            (AttributeError, None, "mapping.d.meh"),
            (AttributeError, None, "namespace.other"),
        ]
        for exc_type, msg, key in tests:
            msg = msg or key
            with self.subTest(key=key):
                with self.assertRaisesRegex(exc_type, msg):
                    MOD.get(example, key)

    def test_returns_expected(self):
        example = self.get_example()
        tests = itertools.chain(
            [
                # (expected, given)
                (example["list"][0], "list.0"),
                (example["list"][1], "list.1"),
                (example["list"][1][1], "list.1.1"),
                (example["list"][2], "list.2"),
                (example["list"][2]["foo"], "list.2.foo"),
                (example["list"][3], "list.3"),
                (example["list"][3].bar, "list.3.bar"),
                (example["mapping"]["a"], "mapping.a"),
                (example["mapping"]["b"], "mapping.b"),
                (example["mapping"]["b"][1], "mapping.b.1"),
                (example["mapping"]["c"], "mapping.c"),
                (example["mapping"]["c"]["foo"], "mapping.c.foo"),
                (example["mapping"]["c"]["foo"][2], "mapping.c.foo.2"),
                (example["mapping"]["d"], "mapping.d"),
                (example["mapping"]["d"].bar, "mapping.d.bar"),
                (example["namespace"].a, "namespace.a"),
                (example["namespace"].b, "namespace.b"),
                (example["namespace"].b[1], "namespace.b.1"),
                (example["namespace"].c, "namespace.c"),
                (example["namespace"].c["foo"], "namespace.c.foo"),
                (example["namespace"].d, "namespace.d"),
                (example["namespace"].d.bar, "namespace.d.bar"),
            ]
        )

        for expected, key in tests:
            with self.subTest(key=key):
                found = MOD.get(example, key)
                self.assertEqual(expected, found)


class TestGetWithDefault(ThisTestCase):
    """Test feature."""

    def get_example(self):
        return {
            "foo": {"bar": "baz"},
            "meh": ["ugh"],
        }

    def test_returns_default_if_key_not_found(self):
        example = self.get_example()
        default = None
        tests = itertools.chain(
            [
                # (expected, given)
                (default, ["foo.a", "foo.x"]),
                (default, "x"),
            ]
        )

        for expected, key in tests:
            with self.subTest(key=key):
                found = MOD.get(example, key, default=default)
                self.assertEqual(expected, found)


class TestGetWithDelim(ThisTestCase):
    """Test feature."""

    def get_example(self):
        return {
            "foo": {"bar": "baz"},
            "meh": ["ugh"],
        }

    def test_honors_given_delim(self):
        example = self.get_example()
        key = "foo/bar"
        expected = example["foo"]["bar"]
        found = MOD.get(example, key, delim="/")
        self.assertEqual(expected, found)

    def test_honors_set_delim(self):
        MOD.set_delimiter("@")
        self.addCleanup(MOD.reset_delimiter)

        example = self.get_example()
        key = "foo@bar"
        expected = example["foo"]["bar"]
        found = MOD.get(example, key)
        self.assertEqual(expected, found)


class TestGetWithMultiKey(ThisTestCase):
    """Test feature."""

    def get_example(self):
        return {
            "foo": {"bar": "baz"},
            "meh": ["ugh"],
        }

    def test_raises_if_no_match(self):
        example = self.get_example()
        with self.assertRaisesRegex(KeyError, "no matches"):
            MOD.get(example, ["foo.ick", "b"])

    def test_returns_first_match(self):
        example = self.get_example()
        tests = itertools.chain(
            [
                # (expected, given)
                (example["foo"]["bar"], ["foo.bar", "foo.x"]),
                (example["foo"]["bar"], ["foo.x", "foo.bar"]),
                (example["foo"]["bar"], ["a", "foo.bar", "foo.x"]),
            ]
        )

        for expected, key in tests:
            with self.subTest(key=key):
                found = MOD.get(example, key)
                self.assertEqual(expected, found)


# __END__
