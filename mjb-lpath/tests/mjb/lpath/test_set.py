#!/usr/bin/env python3
"""Test."""

import copy
import logging
from types import SimpleNamespace
from typing import Mapping
from unittest import TestCase, mock

import mjb.lpath as MOD

LOGGER = logging.getLogger(__name__)


class ThisTestCase(TestCase):
    """Base test case for the module."""


class TestSet(ThisTestCase):
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
            MOD.set(example, ["list.0", "mapping.a"], "str required")

    def test_raises_if_target_is_immutable(self):
        example = self.get_example()
        with self.assertRaisesRegex(TypeError, "not support item assignment"):
            MOD.set(example, "mapping.e.0", "err")

        with self.assertRaisesRegex(TypeError, "not support item assignment"):
            MOD.set(example, "mapping.c.foo.0", "err")

    def test_raises_if_key_parent_does_not_exist_or_invalid(self):
        example = self.get_example()
        tests = [
            # (exc_type, value, path)
            (IndexError, None, "list.42"),
            (IndexError, None, "list.1.4"),
            (AttributeError, None, "list.3.hehe"),
            (ValueError, None, "mapping.e.missing.nested"),
            (KeyError, None, "mapping.f.missing.nested"),
            (AttributeError, None, "mapping.d.foo"),
            (AttributeError, None, "namespace.f"),
        ]
        for exc_type, value, path in tests:
            with self.subTest(value=value, path=path):
                with self.assertRaises(exc_type):
                    MOD.set(example, path, value)

    def test_sets_value_for_given_path(self):
        example = self.get_example()
        value = 42
        tests = [
            # (key, lookup lambda)
            ("other", lambda x: x["other"]),
            ("list.0", lambda x: x["list"][0]),
            ("list.1.1", lambda x: x["list"][1][1]),
            ("list.2.foo", lambda x: x["list"][2]["foo"]),
            ("list.3.bar", lambda x: x["list"][3].bar),
            ("mapping.b.2", lambda x: x["mapping"]["b"][2]),
            ("namespace.b", lambda x: x["namespace"].b),
        ]
        for path, retrieve in tests:
            instance = copy.deepcopy(example)
            with self.subTest(value=value, path=path):
                MOD.set(instance, path, value)
                found = retrieve(instance)
                expected = value
                self.assertEqual(expected, found)

    def test_adds_item_if_parent_is_mapping(self):
        example = self.get_example()
        value = 42
        tests = [
            # (path, lookup lambda)
            ("list.2.b", lambda x: x["list"][2]["b"]),
            ("mapping.f", lambda x: x["mapping"]["f"]),
            ("mapping.c.u", lambda x: x["mapping"]["c"]["u"]),
            ("namespace.c.u", lambda x: x["namespace"].c["u"]),
        ]
        for path, retrieve in tests:
            instance = copy.deepcopy(example)
            with self.subTest(value=value, path=path):
                MOD.set(instance, path, value)
                found = retrieve(instance)
                expected = value
                self.assertEqual(expected, found)


class TestSetWithDelim(ThisTestCase):
    """Test feature."""

    def get_example(self):
        return {
            "foo": {"bar": "baz"},
            "meh": ["ugh"],
        }

    def test_honors_given_delim(self):
        example = self.get_example()
        key = "foo/bar"
        value = (0, 1, 42)
        MOD.set(example, key, value, delim="/")

        found = example["foo"]["bar"]
        expected = value
        self.assertEqual(expected, found)

    def test_honors_set_delim(self):
        MOD.set_delimiter("@")
        self.addCleanup(MOD.reset_delimiter)

        example = self.get_example()
        key = "foo@bar"
        value = {"a": "mapping"}
        MOD.set(example, key, value)

        found = example["foo"]["bar"]
        expected = value
        self.assertEqual(expected, found)


# __END__
