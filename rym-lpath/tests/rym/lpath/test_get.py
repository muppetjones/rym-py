#!/usr/bin/env python3
"""Test."""

import itertools
import logging
from types import SimpleNamespace
from typing import Any, Mapping
from unittest import TestCase, skipIf

import rym.lpath as MOD
from rym.lpath.errors import (
    InvalidKeyError,
    KeyFormatError,
    can_use_exception_groups,
    enable_exception_groups,
)

try:
    from exceptiongroup import ExceptionGroup
except ImportError:
    # We don't _need_ exception group as the usage is behind a version check.
    # Exception handling for groups is a pain even with this package, so
    # we don't use it unless we're on 3.11+. However, the linters complain.
    pass

LOGGER = logging.getLogger(__name__)


class ThisTestCase(TestCase):
    """Base test case for the module."""

    def setUp(self) -> None:
        # Ensure test isolation
        initial_state = MOD.do_use_exception_groups()
        self.addCleanup(MOD.set_use_exception_groups, initial_state)


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
            (KeyFormatError, 42),
            # (ValueError, {"foo": "bar"}),
        ]
        for exc_type, key in tests:
            with self.subTest(key=key):
                with self.assertRaisesRegex(exc_type, "invalid key"):
                    MOD.get({}, key, default=None)

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
                with self.assertRaisesRegex(KeyFormatError, exc_type.__name__):
                    MOD.get(example, key)

    def test_raises_if_key_not_found(self) -> None:
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
                with self.assertRaisesRegex(InvalidKeyError, exc_type.__name__):
                    MOD.get(example, key)

    @skipIf(not can_use_exception_groups(), "Requires py3.11+")
    def test_raises_exceptiongroup_if_key_not_found(self) -> None:
        enable_exception_groups()
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
                with self.assertRaises(ExceptionGroup) as eg:
                    MOD.get(example, key)

                self.assertTrue(
                    any(isinstance(e, exc_type) for e in eg.exception.exceptions)
                )

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

    def get_example(self) -> dict[str, Any]:
        return {
            "foo": {"bar": "baz"},
            "meh": ["ugh"],
        }

    def test_returns_default_if_key_not_found(self) -> None:
        example = self.get_example()
        default = None
        tests = itertools.chain(
            [
                # (expected, given)
                (default, ["foo.a", "foo.x"]),
                (default, "x"),
                (default, "meh.3"),
            ]
        )

        for expected, key in tests:
            with self.subTest(key=key):
                found = MOD.get(example, key, default=default)
                self.assertEqual(expected, found)

    def test_default_does_not_need_to_be_keyword_arg(self) -> None:
        # NOTE: 'default' used to be kwarg only
        example = self.get_example()
        found = MOD.get(example, "x", None)
        expected = None
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
                (example["foo"]["bar"], ["meh.ugh", "foo.bar", "foo.x"]),
            ]
        )

        for expected, key in tests:
            with self.subTest(key=key):
                found = MOD.get(example, key)
                self.assertEqual(expected, found)


class TestGetWithAsterisk(ThisTestCase):
    """Test behavior."""

    def test_raises_if_no_match(self) -> None:
        example = {"foo": [{"bar": {"baz": 0}}]}
        with self.assertRaisesRegex(InvalidKeyError, "failure to match"):
            MOD.get(example, "foo.*.bar.meh")

        with self.assertRaisesRegex(KeyError, "ugh"):
            MOD.get(example, "ugh.*")

    def test_raises_single_asterisk_with_empty_array(self) -> None:
        with self.subTest("does not error if path doesn't go past empty array"):
            example = {"foo": [], "baz": "3", "meh": {}}
            MOD.get(example, "foo.*")

        with self.subTest("errors if empty array"):
            example = {"foo": [], "baz": "3", "meh": {}}
            with self.assertRaisesRegex(InvalidKeyError, "failure to match"):
                MOD.get(example, "foo.*.bar")

    def test_behavior_single_asterisk_happy_path(self) -> None:
        example = {
            "foo": [{"bar": 0}, {"bar": 1}, {"bar": 2}],
            "baz": "3",
            "meh": {"a": {"hmm": 4}, "b": {"hmm": 5}, "c": {"hmm": 6}},
        }
        tests = [
            # (expected, key)
            (example["baz"], "baz.*"),
            (example["foo"], "foo.*"),
            (example["meh"], "meh.*"),
            ([0, 1, 2], "foo.*.bar"),
            ([4, 5, 6], "meh.*.hmm"),
            ([{"hmm": 4}], "*.a"),
            ([[0, 1, 2]], "*.*.bar"),
            ([1], "*.1.bar"),
        ]
        for expected, key in tests:
            with self.subTest(key):
                found = MOD.get(example, key)
                self.assertEqual(expected, found)

    def test_behavior_single_asterisk_edge_cases(self) -> None:
        with self.subTest("wild card with root list"):
            example = [{"a": 0}, {"a": 1}, {"a": 2}]
            expected = [0, 1, 2]
            found = MOD.get(example, "*.a")
            self.assertEqual(expected, found)

        with self.subTest("array with namespace"):
            example = [
                {"a": list("xyz"), "b": 42},
                SimpleNamespace(foo={"bar": "baz"}),
            ]
            expected = [["baz"]]  # NOTE: one set of iterables for each asterisk
            found = MOD.get(example, "*.*.bar")
            self.assertEqual(expected, found)

    def test_behavior_with_nested_asterisk(self) -> None:
        example = [
            {"a": list("xyz"), "b": 42},
            SimpleNamespace(foo={"bar": "baz"}),
        ]
        expected = [[["x", "y", "z"], 42], [{"bar": "baz"}]]
        found = MOD.get(example, "*.*.*")
        self.assertEqual(expected, found)

        # __END__
        found = MOD.get(example, "*.*.*")
        self.assertEqual(expected, found)


# __END__
