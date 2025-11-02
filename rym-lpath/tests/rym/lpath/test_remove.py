#!/usr/bin/env python3
"""Test lpath.delete."""

import copy
import logging
from types import SimpleNamespace
from typing import Mapping
from unittest import TestCase

import rym.lpath as MOD
from rym.lpath.errors import InvalidKeyError, KeyFormatError

LOGGER = logging.getLogger(__name__)


class ThisTestCase(TestCase):
    """Base test case for the module."""


class TestAliasRemove(ThisTestCase):
    """Test alias."""

    def test_alias_exists(self) -> None:
        with self.subTest("alias exists"):
            found = MOD.remove
            expected = MOD.pop
            self.assertEqual(expected, found)

        with self.subTest("alias functionality control"):
            given = {"foo": [0, 1, 2]}
            MOD.remove(given, "foo.1")
            expected = {"foo": [0, 2]}
            found = given  # in place modification!
            self.assertEqual(expected, found)


class TestPop(ThisTestCase):
    """Test function."""

    def get_example(self) -> Mapping:
        data = {
            "a": "a",
            "b": ["b0", "b1", "baz"],
            "c": {"foo": "meh"},
            "d": SimpleNamespace(bar="d"),
            "e": (0, 1, 2),
        }
        return {
            "list": list(data.values()),
            "mapping": data.copy(),
            "namespace": SimpleNamespace(**data),
        }

    def test_raises_if_key_is_not_a_str(self):
        example = self.get_example()
        with self.assertRaisesRegex(TypeError, "must be a string"):
            MOD.pop(example, ["list.0", "mapping.a"])

    def test_raises_if_target_is_immutable(self):
        example = self.get_example()
        tests = [
            "mapping.e.0",
            "mapping.c.foo.0",
        ]
        for key in tests:
            with self.subTest(key=key):
                with self.assertRaisesRegex(TypeError, "not supported"):
                    MOD.pop(example, key)

    def test_raises_if_key_parent_does_not_exist(self):
        example = self.get_example()
        tests = [
            # (exc_type, value, path)
            (IndexError, None, "list.42"),
            (IndexError, None, "list.1.4"),
            (AttributeError, None, "list.3.hehe"),
            (KeyError, None, "mapping.f.missing.nested"),
            (AttributeError, None, "mapping.d.foo"),
            (AttributeError, None, "namespace.f"),
        ]
        for exc_type, value, path in tests:
            with self.subTest(value=value, path=path):
                with self.assertRaisesRegex(InvalidKeyError, exc_type.__name__):
                    MOD.pop(example, path)

    def test_raises_if_key_parent_invalid(self):
        example = self.get_example()
        tests = [
            # (exc_type, value, path)
            (ValueError, None, "mapping.e.missing.nested"),
        ]
        for exc_type, value, path in tests:
            with self.subTest(value=value, path=path):
                with self.assertRaisesRegex(KeyFormatError, exc_type.__name__):
                    MOD.pop(example, path)

    def test_returns_value_for_given_path(self):
        example = self.get_example()
        tests = [
            # (key, lookup lambda)
            ("list.0", lambda x: x["list"][0]),
            ("list.1.1", lambda x: x["list"][1][1]),
            ("list.2.foo", lambda x: x["list"][2]["foo"]),
            ("list.3.bar", lambda x: x["list"][3].bar),
            ("mapping.b.2", lambda x: x["mapping"]["b"][2]),
            ("namespace.b", lambda x: x["namespace"].b),
        ]
        for path, retrieve in tests:
            instance = copy.deepcopy(example)
            with self.subTest(path=path):
                expected = retrieve(instance)
                found = MOD.pop(instance, path)
                self.assertEqual(expected, found)


class TestPopIntegratedExamples(ThisTestCase):
    """Test behavior."""

    def test_removes_from_iterable(self):
        example = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        removed = [
            MOD.pop(example, "0.0"),
            MOD.pop(example, "2.2"),
            MOD.pop(example, "1"),
            MOD.pop(example, "1.0"),
            MOD.pop(example, "1.0"),
        ]
        self.assertEqual([[2, 3], []], example)
        self.assertEqual([1, 9, [4, 5, 6], 7, 8], removed)

        with self.assertRaisesRegex(InvalidKeyError, "IndexError"):
            MOD.pop(example, "1.0")

    def test_removes_from_mapping(self):
        example = {"a": [1, 2, 3], "b": {"x": 4, "y": 5}, "c": {"z": 42}}
        removed = [
            MOD.pop(example, "a.2"),
            MOD.pop(example, "b.y"),
            MOD.pop(example, "c"),
        ]
        self.assertEqual({"a": [1, 2], "b": {"x": 4}}, example)
        self.assertEqual([3, 5, {"z": 42}], removed)

        with self.assertRaisesRegex(InvalidKeyError, "KeyError"):
            MOD.pop(example, "b.y")

    def test_removes_from_namespace(self):
        example = SimpleNamespace(
            a=[1, 2, 3],
            b=SimpleNamespace(x=4, y=5),
            c={"z": 42},
        )
        removed = [
            MOD.pop(example, "a.2"),
            MOD.pop(example, "b.y"),
            MOD.pop(example, "c"),
        ]
        expected = SimpleNamespace(
            a=[1, 2],
            b=SimpleNamespace(x=4),
        )
        self.assertEqual(expected, example)
        self.assertEqual([3, 5, {"z": 42}], removed)

        with self.assertRaises(InvalidKeyError):
            MOD.pop(example, "b.y")


class TestPopWithDelim(ThisTestCase):
    """Test feature."""

    def get_example(self):
        return {
            "foo": {"bar": "baz"},
            "meh": ["ugh", "ack"],
            "ick": SimpleNamespace(tsk=0, heh=1),
        }

    def test_honors_given_delim(self):
        example = self.get_example()
        key = "foo/bar"
        MOD.pop(example, key, delim="/")

        found = example["foo"]
        expected = {}
        self.assertEqual(expected, found)

    def test_honors_set_delim(self):
        MOD.set_delimiter("@")
        self.addCleanup(MOD.reset_delimiter)

        example = self.get_example()
        key = "ick@tsk"
        MOD.pop(example, key)

        found = example["ick"]
        expected = SimpleNamespace(heh=1)
        self.assertEqual(expected, found)


# __END__
