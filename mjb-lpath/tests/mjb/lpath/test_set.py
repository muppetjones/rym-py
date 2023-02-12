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
        }
        return {
            "list": list(data.values()),
            "mapping": data.copy(),
            "namespace": SimpleNamespace(**data),
        }

    def test_raises_if_key_is_not_a_str(self):
        example = self.get_example()
        with self.assertRaisesRegex(TypeError, "invalid"):
            MOD.set(example, ["list.0", "mapping.a"])

    def test_raises_if_key_parent_does_not_exist(self):
        example = self.get_example()
        tests = [
            # (exc_type, value, path)
            (IndexError, None, "list.4"),
            (IndexError, None, "list.1.4"),
            (IndexError, None, "list.d.hehe"),
            (KeyError, None, "mapping.e.missing.nested"),
            (AttributeError, None, "mapping.d.foo"),
            (AttributeError, None, "namespace.f"),
        ]
        for exc_type, value, path in tests:
            with self.subTest(value=value, path=path):
                with self.assertRaises(exc_type):
                    MOD.set(example, path, value)

    def test_sets_value_for_given_path(self):
        example = self.get_example()
        tests = [
            # (value, path)
        ]
        for value, path in tests:
            instance = copy.deepcopy(example)
            with self.subTest(value=value, path=path):
                MOD.set(instance, path, value)
                found = MOD.get(instance, path)
                expected = value
                self.assertEqual(expected, found)

    def test_adds_item_if_parent_is_mapping(self):
        example = self.get_example()
        tests = [
            # (value, path)
            (0, "list.c.missing"),
            (1, "mapping.e"),
            (2, "mapping.c.missing"),
            (3, "namespace.c.missing"),
        ]
        for value, path in tests:
            instance = copy.deepcopy(example)
            with self.subTest(value=value, path=path):
                MOD.set(instance, path, value)
                found = MOD.get(instance, path)
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
        value = 42

        MOD.get(example, key, value, delim="/")

        found = example["foo"]["bar"]
        expected = value
        self.assertEqual(expected, found)

    def test_honors_set_delim(self):
        MOD.set_delimiter("@")
        self.addCleanup(MOD.reset_delimiter)

        example = self.get_example()
        key = "foo@bar"
        expected = example["foo"]["bar"]
        found = MOD.get(example, key)
        self.assertEqual(expected, found)


# __END__
