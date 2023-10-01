#!/usr/bin/env python3
"""Test."""

import json
import logging
from unittest import TestCase, mock
from unittest.mock import Mock

import rym.alias._coerce_explicit as MOD

LOGGER = logging.getLogger(__name__)


class ThisTestCase(TestCase):
    """Base test case for the module."""


class TestCoerceExplicit(ThisTestCase):
    """Test function."""

    def test_disable_use_safe(self) -> None:
        # NOTE: int will default to safe_int if use_safe=True
        with self.assertRaises(ValueError):
            MOD.coerce_explicit(int, "3.14", use_safe=False)

    def test_returns_expected(self) -> None:
        # NOTE: Minimal test cases as covered below in 'safe' tests
        tests = [
            # (expected, value, type_)
            (True, "true", bool),
            (False, "", "bool"),
            (("a", "b", "c"), list("abc"), "tuple"),
            (None, "nil", "null"),
            (1, "1.1", int),
        ]
        for expected, value, type_ in tests:
            with self.subTest(given=[value, type_]):
                found = MOD.coerce_explicit(type_, value)
                self.assertEqual(expected, found)

    def test_passes_given_kwargs(self):
        mobj = Mock()
        _ = MOD.coerce_explicit(mobj, "value", a=0, b=2)
        expected = [mock.call("value", a=0, b=2)]
        found = mobj.mock_calls
        self.assertEqual(expected, found)


class TestResolveType(ThisTestCase):
    """Test function."""

    def test_returns_safe_type_by_default(self) -> None:
        tests = [
            # (expected, given)
            (MOD.safe_bool, bool),
            (MOD.safe_int, int),
            (MOD.safe_int, "integer"),
            (MOD.safe_null, "null"),
            (float, "float"),  # no safe type exists
            (json.dumps, "json.dumps"),
            (json.loads, "json.loads"),
            (Mock, Mock),
        ]
        for expected, given in tests:
            with self.subTest(given):
                found = MOD.resolve_type(given)
                self.assertEqual(expected, found)


class TestSafeBool(ThisTestCase):
    """Test function."""

    def test_ignores_kwargs(self) -> None:
        given = "true"
        expected = True
        found = MOD.safe_bool(given, a=0)
        self.assertEqual(expected, found)

    def test_behavior_bool_like(self) -> None:
        tests = [
            # (expected, given)
            (True, True),
            (False, False),
            (True, "true"),
            (True, "True"),
            (True, "TRUE"),
            (False, "false"),
            (False, "False"),
            (False, "FALSE"),
        ]
        for expected, given in tests:
            with self.subTest(given):
                found = MOD.safe_bool(given)
                self.assertEqual(expected, found)

    def test_behavior_non_bool_like(self) -> None:
        tests = [
            # (expected, given)
            (True, 1),
            (False, 0),
            (True, -1),
            (True, [False]),
            (True, "foo"),
            (False, ""),
            (False, []),
            (False, None),
        ]
        for expected, given in tests:
            with self.subTest(given):
                found = MOD.safe_bool(given)
                self.assertEqual(expected, found)


class TestSafeInt(ThisTestCase):
    """Test function."""

    def test_ignores_kwargs(self) -> None:
        given = "4"
        expected = 4
        found = MOD.safe_int(given, a=0)
        self.assertEqual(expected, found)

    def test_raises_for_invalid_input(self) -> None:
        tests = [
            "foo",
            ["bar"],
            {"bar": 0},
        ]
        for given in tests:
            with self.subTest(given):
                with self.assertRaisesRegex(ValueError, "invalid"):
                    MOD.safe_int(given)

    def test_returns_expected(self) -> None:
        tests = [
            # (expected, given)
            (1, 1),
            (2, "2"),
            (3, "3.14"),
            (1, True),
            (0, False),
        ]
        for expected, given in tests:
            with self.subTest(given):
                found = MOD.safe_int(given)
                self.assertEqual(expected, found)


class TestSafeIterable(ThisTestCase):
    """Test function."""

    def test_ignores_kwargs(self) -> None:
        given = "foo"
        expected = ["foo"]
        found = MOD.safe_iterable(given, a=0)
        self.assertEqual(expected, found)

    def test_returns_expected(self) -> None:
        tests = [
            # (expected, given)
            ([1], 1),
            (["23"], "23"),
            (list("abc"), list("abc")),
            ([True], True),
            ([None], None),
            ([("a", 0), ("b", 1)], {"a": 0, "b": 1}),
        ]
        for expected, given in tests:
            with self.subTest(given):
                found = MOD.safe_iterable(given)
                self.assertEqual(expected, found)

    def test_returns_coerced(self) -> None:
        given = list("aabc")
        tests = [
            # (expected, itertype)
            (list(given), None),  # default
            (tuple(given), tuple),
            (tuple(given), "tuple"),
            (set(given), set),
            (set(given), "set"),
        ]
        for expected, itertype in tests:
            with self.subTest(itertype):
                found = MOD.safe_iterable(given, itertype=itertype)
                self.assertEqual(expected, found)

    def test_generators(self) -> None:
        given = list("aabc")
        tests = [
            # (expected, itertype)
            (given, iter),
            (given, "iter"),
            (given, "generator"),
            (given, "yield"),
        ]
        for expected, itertype in tests:
            with self.subTest(itertype):
                result = MOD.safe_iterable(given, itertype=itertype)
                assert expected != result
                found = list(result)
                self.assertEqual(expected, found)


class TestSafeNull(ThisTestCase):
    """Test function."""

    def test_ignores_kwargs(self) -> None:
        given = "n/a"
        expected = None
        found = MOD.safe_null(given, a=0)
        self.assertEqual(expected, found)

    def test_returns_given_if_non_null(self) -> None:
        tests = [
            "foo",
            ["bar"],
            {"bar": 0},
            0,
            False,
        ]
        for given in tests:
            with self.subTest(given):
                expected = given
                found = MOD.safe_null(given)
                self.assertEqual(expected, found)

    def test_returns_expected(self) -> None:
        tests = [
            # (expected, given)
            (None, None),
            (None, ""),
            (None, "none"),
            (None, "NULL"),
            (None, "null"),
            (None, "nil"),
            (None, "na"),
            (None, "NaN"),
            (None, MOD.NaN),
        ]
        for expected, given in tests:
            with self.subTest(given):
                found = MOD.safe_null(given)
                self.assertEqual(expected, found)


# __END__
