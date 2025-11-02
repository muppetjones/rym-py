#!/usr/bin/env python3
"""Test coercion functionality.

NOTE: Tests the interface of rym.alias.coerce.
"""

import json
import logging
from datetime import datetime, timezone
from unittest import TestCase, skip

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
            ((bool, True), {"value": 1, "type_": "boolean"}),
            ((bool, False), {"value": 0, "type_": "bool"}),
            ((bool, True), {"value": "true", "type_": "bool"}),
            ((bool, False), {"value": "false", "type_": "boolean"}),
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
            ((bool, True), {"value": 1, "type_": bool}),
            ((bool, False), {"value": 0, "type_": bool}),
            ((bool, True), {"value": "1", "type_": bool}),
            ((bool, True), {"value": "0", "type_": bool}),
            ((bool, False), {"value": "", "type_": bool}),
            ((bool, True), {"value": [0], "type_": bool}),
            ((bool, False), {"value": [], "type_": bool}),
            ((bool, True), {"value": "None", "type_": bool}),
            ((bool, False), {"value": None, "type_": bool}),
        ]
        for expected, kwargs in tests:
            with self.subTest(kwargs):
                value = MOD.coerce(**kwargs)
                found = (type(value), value)
                self.assertEqual(expected, found)

    def test_returns_value_from_implicit_type(self):
        tests = [
            # (expected, given)
            *[((bool, True), {"value": x}) for x in (True, "true", "TRUE", "True")],
            *[
                ((bool, False), {"value": x})
                for x in (False, "false", "FALSE", "False")
            ],
        ]
        for expected, kwargs in tests:
            with self.subTest(kwargs):
                value = MOD.coerce(**kwargs)
                found = (type(value), value)
                self.assertEqual(expected, found)


@skip("not implemented")
class TestCoerceDatetime(ThisTestCase):
    """Test feature."""

    @skip("not implemented")
    def test_returns_isoformat_given_datetime_objects(self) -> None:
        now = datetime.now(timezone.utc)
        tests = [
            # (expected, given)
            ((str, now.isoformat()), {"value": now, "type_": str}),
            ((str, now.date.isoformat()), {"value": now.date, "type_": str}),
            ((str, now.time.isoformat()), {"value": now.time, "type_": str}),
        ]
        for expected, kwargs in tests:
            with self.subTest(kwargs):
                value = MOD.coerce(**kwargs)
                found = (type(value), value)
                self.assertEqual(expected, found)


@skip("not implemented")
class TestCoerceJsonLoads(ThisTestCase):
    """Test feature."""

    def test_raises_for_invalid_explicit_type(self):
        tests = [
            # given
            {"value": "1,", "type_": json.loads},
            {"value": True, "type_": "json.loads"},
            {"value": ["x"], "type_": "json.loads"},
            {"value": "foo", "type_": "json.loads"},
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
                {"value": '["a", false, null, 42.4]', "type_": "json"},
            ),
            ({"a": None}, {"value": '{"a": null}', "type_": "json"}),
            ({"a": True}, {"value": '{"a": true}', "type_": "json"}),
            ({"a": 1}, {"value": '{"a": 1}', "type_": "json"}),
            ({"a": 42}, {"value": '{"a": "42"}', "type_": "json"}),
            ({"a": ["x"]}, {"value": '{"a": ["x"]}', "type_": "json"}),
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

    def test_returns_given_if_not_null_like(self):
        tests = [
            # given
            {"value": "1", "type_": "null"},
            {"value": True, "type_": "null"},
            {"value": ["x"], "type_": "null"},
            {"value": "foo", "type_": "null"},
            {"value": [], "type_": "null"},
            {"value": 0, "type_": "null"},
            {"value": False, "type_": None},
        ]
        for kwargs in tests:
            with self.subTest(kwargs):
                expected = kwargs["value"]
                found = MOD.coerce(**kwargs)
                self.assertEqual(expected, found)

    def test_returns_value_from_explicit_named_type(self):
        _ = type(None)
        tests = [
            # (expected, given)
            ((_, None), {"value": None, "type_": None}),
            ((_, None), {"value": "n/a", "type_": "null"}),
            ((_, None), {"value": "NULL", "type_": "null"}),
            ((_, None), {"value": "NaN", "type_": "null"}),
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
            {"value": "42.4", "type_": int, "use_safe": False},
            {"value": "one", "type_": int},
            {"value": "[1]", "type_": int},
            {"value": "two", "type_": float},
        ]
        for kwargs in tests:
            with self.subTest(kwargs):
                with self.assertRaises(ValueError):
                    MOD.coerce(**kwargs)

    def test_returns_value_from_explicit_named_type(self):
        tests = [
            # (expected, given)
            ((float, 42.4), {"value": "42.4", "type_": "float"}),
            ((float, 1.0), {"value": 1, "type_": "number"}),
            ((int, 42), {"value": 42.4, "type_": "int"}),
            ((int, 42), {"value": 42.4, "type_": "integer"}),
        ]
        for expected, kwargs in tests:
            with self.subTest(kwargs):
                value = MOD.coerce(**kwargs)
                found = (type(value), value)
                self.assertEqual(expected, found)

    def test_returns_value_from_explicit_type(self):
        tests = [
            # (expected, given)
            ((float, 42.4), {"value": "42.4", "type_": float}),
            ((float, 1.0), {"value": 1, "type_": float}),
            ((int, 42), {"value": 42.4, "type_": int}),
            ((int, 42), {"value": 42.4, "type_": int}),
            ((float, 1.0), {"value": "1.0", "type_": float}),
            ((int, 2), {"value": "2", "type_": int}),
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
            ((float, 4200.4), {"value": "4_200.4"}),
            ((float, 4200.4), {"value": "4,200.4"}),
            ((float, 42.4), {"value": 42.4}),
            ((int, 1), {"value": 1}),
            ((float, 1), {"value": "1."}),
            ((int, 1000), {"value": "1_000"}),
            ((int, 1000), {"value": "1,000"}),
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
        class Foo: ...

        instance = Foo()
        tests = [
            # (expected, given)
            ((str, "42.4"), {"value": "42.4", "type_": str}),
            ((str, "1.0"), {"value": 1.0, "type_": "str"}),
            (
                (str, "['a', 'b', None]"),
                {"value": ["a", "b", None], "type_": "str"},
            ),
            ((str, str(Foo)), {"value": Foo, "type_": "str"}),  # "<class Foo>"
            ((str, str(instance)), {"value": instance, "type_": "str"}),  # "Foo()"
        ]
        for expected, kwargs in tests:
            with self.subTest(kwargs):
                value = MOD.coerce(**kwargs)
                found = (type(value), value)
                self.assertEqual(expected, found, f"\n{expected}\n{found}")


# __END__
