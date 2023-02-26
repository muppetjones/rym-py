#!/usr/bin/env python3
"""Test."""

import logging
from unittest import TestCase, mock

import stringcase as sc

import rym.alias as MOD
from rym.alias import variation

LOGGER = logging.getLogger(__name__)


class ThisTestCase(TestCase):
    """Base test case for the module."""


class TestInit(ThisTestCase):
    """Test initialization."""

    def test_creates_default_transform_aliases(self):
        given = {
            "identity": "fooBar",
            "aliases": ["FOO_bar"],
        }
        expected = sorted(
            [
                *["fooBar", "FOO_bar"],  # given
                *["FOOBAR", "FOO_BAR"],  # upper
                *["foobar", "foo_bar"],  # lower
            ]
        )
        subject = MOD.Alias(**given)
        found = subject.all_names()
        self.assertEqual(expected, found)

    def test_creates_transform_aliases(self):
        given = {
            "identity": "fooBar",
            "aliases": ["FOO_bar"],
            "transforms": [sc.camelcase, lambda x: x.lower()],
        }
        expected = sorted(
            [
                *["fooBar", "FOO_bar"],  # given
                *["fOOBar"],  # camel doesn't really play nice with screaming snake
                *["foobar", "foo_bar"],  # lower
            ]
        )
        subject = MOD.Alias(**given)
        found = subject.all_names()
        self.assertEqual(expected, found)

    def test_disable_transform(self):
        given = {
            "identity": "fooBar",
            "aliases": ["FOO_bar"],
            "transforms": None,
        }
        subject = MOD.Alias(**given)
        assert "fooBar" == subject.identify("FOO_bar")
        with self.assertRaises(KeyError):
            subject.identify("FOO_BAR")

    def test_no_aliases(self):
        given = {
            "identity": "fooBar",
            "aliases": None,
        }
        subject = MOD.Alias(**given)
        assert "fooBar" == subject.identify("FOOBAR")
        with self.assertRaises(KeyError):
            subject.identify("FOO_BAR")

    def test_single_alias(self):
        given = {
            "identity": "fooBar",
            "aliases": "meh",
        }
        subject = MOD.Alias(**given)
        expected = "fooBar"
        found = subject.identify("MEH")
        self.assertEqual(expected, found)

    def test_transform_by_name(self):
        given = {
            "identity": "fooBar",
            "aliases": None,
            "transforms": ["deesser"],
        }
        subject = MOD.Alias(**given)
        expected = [variation.deesser]
        found = subject.transforms
        self.assertEqual(expected, found)


class TestAddAlias(ThisTestCase):
    """Test function."""

    def get_subject(self, **kwargs) -> MOD.Alias:
        given = {
            "identity": "fooBar",
            "aliases": None,
            **kwargs,
        }
        subject = MOD.Alias(**given)
        return subject

    def test_added_to_attribute_once(self):
        subject = self.get_subject()
        given = "foo_bar"
        expected = [*subject.aliases, given]

        subject.logger = mock.Mock()
        subject.add_alias("foo_bar")
        subject.add_alias("foo_bar")
        subject.add_alias("foo_bar")

        found = subject.aliases
        self.assertEqual(expected, found)

    def test_identifiable(self):
        subject = self.get_subject()
        given = "foo_bar"
        expected = subject.identity

        subject.add_alias("foo_bar")
        found = subject.identify(given)
        self.assertEqual(expected, found)

    def test_transformed(self):
        subject = self.get_subject()
        given = "foo_bar"
        expected = subject.identity

        subject.add_alias("foo_bar")
        found = subject.identify(given.upper())  # default transform
        self.assertEqual(expected, found)


class TestAddTransform(ThisTestCase):
    """Test function."""

    def get_subject(self, **kwargs) -> MOD.Alias:
        given = {
            "identity": "fooBar",
            "aliases": None,
            **kwargs,
        }
        subject = MOD.Alias(**given)
        return subject

    def test_added_to_attribute_once(self):
        subject = self.get_subject()
        given = sc.spinalcase
        expected = [*subject.transforms, given]

        subject.logger = mock.Mock()
        subject.add_transform(given)
        subject.add_transform(given)
        subject.add_transform(given)

        found = subject.transforms
        self.assertEqual(expected, found)

    def test_updates_lookup(self):
        subject = self.get_subject()
        given = sc.spinalcase
        expected = subject.identity

        subject.add_transform(given)
        found = subject.identify("foo-bar")
        self.assertEqual(expected, found)


class TestIdentify(ThisTestCase):
    """Test function."""

    # error path
    # ----------------------------------

    def test_raises_if_unknown_alias(self):
        given = {
            "identity": "fooBar",
            "aliases": ["FOO_bar"],
        }
        subject = MOD.Alias(**given)
        with self.assertRaisesRegex(KeyError, "foo"):
            subject.identify("foo")

    # section
    # ----------------------------------

    def test_returns_identity_for_alias(self):
        given = {
            "identity": "fooBar",
            "aliases": ["FOO_bar"],
        }
        tests = [
            *["fooBar", "FOO_bar"],  # given
            *["FOOBAR", "FOO_BAR"],  # upper
            *["foobar", "foo_bar"],  # lower
        ]
        expected = given["identity"]
        subject = MOD.Alias(**given)
        for value in tests:
            with self.subTest(value):
                found = subject.identify(value)
                self.assertEqual(expected, found)

    def test_tracks_attempts(self):
        given = {
            "identity": "a",
            "aliases": list("abc"),
        }
        subject = MOD.Alias(**given)

        expected = {"a": 2, "b": 1, "c": 0, "d": 6, "foo": 3}
        for k, v in expected.items():
            for i in range(v):
                try:
                    subject.identify(k)
                except KeyError:
                    ...
        found = subject._attempts
        self.assertEqual(expected, found)


class TestSetTransforms(ThisTestCase):
    """Test method."""

    def get_subject(self, **kwargs) -> MOD.Alias:
        given = {
            "identity": "fooBar",
            "aliases": None,
            **kwargs,
        }
        subject = MOD.Alias(**given)
        return subject

    def test_attribute_set(self):
        subject = self.get_subject()
        given = [sc.spinalcase]
        initial = subject.transforms[:]
        expected = given[:]

        assert initial != expected, "invalid assumption; cannot test"
        subject.set_transforms(given)
        found = subject.transforms
        self.assertEqual(expected, found)

    def test_disable_transforms(self):
        subject = self.get_subject()
        subject.set_transforms(None)
        assert subject.names == list(subject._lookup.keys()), "lookup not erased"

    def test_updates_lookup(self):
        subject = self.get_subject()

        with self.subTest("initial identify"):
            subject.identify("FOOBAR")  # should not raise; default transform

        with self.subTest("new identity"):
            given = [sc.spinalcase]
            expected = subject.identity
            subject.set_transforms(given)
            found = subject.identify("foo-bar")
            self.assertEqual(expected, found)

        with self.subTest("old erased"):
            with self.assertRaises(KeyError):
                subject.identify("FOOBAR")  # default transform


class TestResolveVariations(ThisTestCase):
    """Test function."""

    def test_raises_for_invalid_type(self):
        with self.assertRaises(TypeError):
            MOD.resolve_variations(42)

    def test_raises_for_unknown(self):
        with self.assertRaisesRegex(AttributeError, "alias.variation"):
            MOD.resolve_variations("uppercrust")

    def test_returns_named_variation(self):
        expected = [variation.deesser]
        found = MOD.resolve_variations("deesser")
        self.assertEqual(expected, found)

    def test_returns_callable_pass_through(self):
        given = list
        expected = [given]
        found = MOD.resolve_variations(given)
        self.assertEqual(expected, found)

    def test_returns_None_as_empty_list(self):
        given = None
        expected = []
        found = MOD.resolve_variations(given)
        self.assertEqual(expected, found)


# __END__
