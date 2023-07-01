#!/usr/bin/env python3
"""Test coercion functionality.

NOTE: Tests the interface of rym.alias.coerce.
"""

import json
import logging
from datetime import date, datetime, time, timezone
from unittest import TestCase

import rym.alias as MOD

try:
    from numpy import NaN  # flake8: noqa
except ImportError:  # noqa
    NaN = None

LOGGER = logging.getLogger(__name__)


class ThisTestCase(TestCase):
    """Base test case for the module."""


class TestBoolean(TestCase):
    """Test feature."""

    def test_returns_value_from_explicit_named_type(self):
        # NOTE: Behaves like standard bool.
        tests = [
            # (expected, given)
            ((bool, True), {"value": 1, "converter": "boolean"}),
            ((bool, False), {"value": 0, "converter": "bool"}),
        ]
        for expected, kwargs in tests:
            with self.subTest(kwargs):
                value = MOD.coerce(**kwargs)
                found = (type(value), value)
                self.assertEqual(expected, found)

    def test_returns_value_from_explicit_type(self):
        # NOTE: Behaves like standard bool.
        tests = [
            # (expected, given)
            ((bool, True), {"value": 1, "converter": bool}),
            ((bool, False), {"value": 0, "converter": bool}),
            ((bool, True), {"value": "1", "converter": bool}),
            ((bool, True), {"value": "0", "converter": bool}),
            ((bool, False), {"value": "", "converter": bool}),
            ((bool, True), {"value": [0], "converter": bool}),
            ((bool, False), {"value": [], "converter": bool}),
            ((bool, True), {"value": "None", "converter": bool}),
            ((bool, False), {"value": None, "converter": bool}),
        ]
        for expected, kwargs in tests:
            with self.subTest(kwargs):
                value = MOD.coerce(**kwargs)
                found = (type(value), value)
                self.assertEqual(expected, found)

    def test_returns_value_from_implicit_type(self):
        tests = [
            # (expected, given)
            *[(True, {"value": x}) for x in (True, "true", "TRUE", "True")],
            *[(False, {"value": x}) for x in (False, "false", "FALSE", "False")],
        ]
        for expected, kwargs in tests:
            with self.subTest(kwargs):
                value = MOD.coerce(**kwargs)
                found = (type(value), value)
                self.assertEqual(expected, found)


class TestCoerceEncodedJSON(ThisTestCase):
    """Test feature."""

    def test_raises_for_invalid_explicit_type(self):
        tests = [
            # given
            {"value": "1,", "converter": json.loads},
            {"value": True, "converter": "json"},
            {"value": ["x"], "converter": "json"},
            {"value": "foo", "converter": "json "},
        ]
        for kwargs in tests:
            with self.subTest(kwargs):
                with self.assertRaises(ValueError):
                    MOD.coerce(**kwargs)

    def test_returns_value_from_explicit_named_type(self):
        tests = [
            # (expected, given)
            (
                ["a", False, None, 42.4],
                {"value": '["a", false, null, 42.4]', "converter": "json"},
            ),
            ({"a": None}, {"value": '{"a": null}', "converter": "json"}),
            ({"a": True}, {"value": '{"a": true}', "converter": "json"}),
            ({"a": 1}, {"value": '{"a": 1}', "converter": "json"}),
            ({"a": 42}, {"value": '{"a": "42"}', "converter": "json"}),
            ({"a": ["x"]}, {"value": '{"a": ["x"]}', "converter": "json"}),
        ]
        for expected, kwargs in tests:
            with self.subTest(kwargs):
                value = MOD.coerce(**kwargs)
                found = value
                self.assertEqual(expected, found)

    def test_returns_value_from_implicit_type(self):
        tests = [
            # (expected, given)
            (
                ["a", False, None, 42.4],
                {"value": '["a", false, null, 42.4]'},
            ),
            ({"a": None}, {"value": '{"a": null}'}),
            ({"a": True}, {"value": '{"a": true}'}),
            ({"a": 1}, {"value": '{"a": 1}'}),
            ({"a": 42}, {"value": '{"a": "42"}'}),
            ({"a": ["x"]}, {"value": '{"a": ["x"]}'}),
        ]
        for expected, kwargs in tests:
            with self.subTest(kwargs):
                value = MOD.coerce(**kwargs)
                found = value
                self.assertEqual(expected, found)


class TestCoerceNull(ThisTestCase):
    """Test feature."""

    def test_raises_for_invalid_explicit_type(self):
        tests = [
            # given
            {"value": "1", "converter": "null"},
            {"value": True, "converter": "null"},
            {"value": ["x"], "converter": "null"},
            {"value": "foo", "converter": "null"},
        ]
        for kwargs in tests:
            with self.subTest(kwargs):
                with self.assertRaises(ValueError):
                    MOD.coerce(**kwargs)

    def test_returns_value_from_explicit_named_type(self):
        _ = None
        tests = [
            # (expected, given)
            ((_, None), {"value": None, "converter": "null"}),
            ((_, None), {"value": "n/a", "converter": "null"}),
            ((_, None), {"value": [], "converter": "null"}),
            ((_, None), {"value": 0, "converter": "null"}),
            ((_, None), {"value": False, "converter": "null"}),
        ]
        for expected, kwargs in tests:
            with self.subTest(kwargs):
                value = MOD.coerce(**kwargs)
                found = (type(value), value)
                self.assertEqual(expected, found)

    def test_returns_value_from_implicit_type(self):
        tests = [
            *["null", "NULL"],
            *[NaN, "nan", "NaN"],
            *[None, "none", "None", "NONE"],
            *["na", "NA", "n/a", "N/A"],
            *["nil", "NIL"],
        ]
        expected = None
        for given in tests:
            with self.subTest(given):
                found = MOD.coerce(given)
                self.assertEqual(expected, found)


class TestCoerceNumber(ThisTestCase):
    """Test feature."""

    def test_raises_for_invalid_explicit_type(self):
        tests = [
            # given
            {"value": "42.4", "converter": int},
            {"value": "42.4", "converter": "number"},
            {"value": "one", "converter": int},
            {"value": "[1]", "converter": int},
            {"value": "two", "converter": float},
        ]
        for kwargs in tests:
            with self.subTest(kwargs):
                with self.assertRaises(ValueError):
                    MOD.coerce(**kwargs)

    def test_returns_value_from_explicit_named_type(self):
        tests = [
            # (expected, given)
            ((float, 42.4), {"value": "42.4", "converter": "float"}),
            ((float, 1.0), {"value": 1, "converter": "number"}),
            ((int, 42), {"value": 42.4, "converter": "int"}),
            ((int, 42), {"value": 42.4, "converter": "integer"}),
        ]
        for expected, kwargs in tests:
            with self.subTest(kwargs):
                value = MOD.coerce(**kwargs)
                found = (type(value), value)
                self.assertEqual(expected, found)

    def test_returns_value_from_explicit_type(self):
        tests = [
            # (expected, given)
            ((float, 42.4), {"value": "42.4", "converter": float}),
            ((float, 1.0), {"value": 1, "converter": float}),
            ((int, 42), {"value": 42.4, "converter": int}),
            ((int, 42), {"value": 42.4, "converter": int}),
            ((int, 1), {"value": "1.0", "converter": int}),
            ((int, 2), {"value": "2", "converter": int}),
        ]
        for expected, kwargs in tests:
            with self.subTest(kwargs):
                value = MOD.coerce(**kwargs)
                found = (type(value), value)
                self.assertEqual(expected, found)

    def test_returns_value_from_implicit_type(self):
        tests = [
            # (expected, given)
            ((float, 42.4), {"value": "42.4"}),
            ((float, 42.4), {"value": "4_200.4"}),
            ((float, 42.4), {"value": "4,200.4"}),
            ((float, 42.4), {"value": 42.4}),
            ((int, 1), {"value": 1}),
            ((int, 1), {"value": "1.0"}),
            ((int, 1), {"value": "1_000"}),
            ((int, 1), {"value": "1,000"}),
            ((int, 2), {"value": "2"}),
        ]
        for expected, kwargs in tests:
            with self.subTest(kwargs):
                value = MOD.coerce(**kwargs)
                found = (type(value), value)
                self.assertEqual(expected, found)


class TestString(ThisTestCase):
    """Test feature."""

    def test_returns_value_from_explicit_type(self):
        class Foo:
            ...

        now = datetime.now(timezone.utc)
        tests = [
            # (expected, given)
            ((str, "42.4"), {"value": "42.4", "converter": str}),
            ((str, "1.0"), {"value": 1, "converter": "str"}),
            (
                (str, '["a", "b", null]'),
                {"value": ["a", "b", None], "converter": "str"},
            ),
            ((str, "<class Foo>"), {"value": Foo, "converter": "str"}),
            ((str, "Foo()"), {"value": Foo(), "converter": "str"}),
            ((str, now.isoformat()), {"value": now, "converter": str}),
        ]
        for expected, kwargs in tests:
            with self.subTest(kwargs):
                value = MOD.coerce(**kwargs)
                found = (type(value), value)
                self.assertEqual(expected, found)

    def test_returns_isoformat_given_datetime_objects(self):

        now = datetime.now(timezone.utc)
        tests = [
            # (expected, given)
            ((str, now.isoformat()), {"value": now, "converter": str}),
            ((str, now.date.isoformat()), {"value": now.date, "converter": str}),
            ((str, now.time.isoformat()), {"value": now.time, "converter": str}),
        ]
        for expected, kwargs in tests:
            with self.subTest(kwargs):
                value = MOD.coerce(**kwargs)
                found = (type(value), value)
                self.assertEqual(expected, found)


# __END__
