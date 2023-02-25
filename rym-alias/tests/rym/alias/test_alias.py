#!/usr/bin/env python3
"""Test."""

import logging
from unittest import TestCase, mock

import rym.alias as MOD
import stringcase as sc

LOGGER = logging.getLogger(__name__)


class ThisTestCase(TestCase):
    """Base test case for the module."""


class TestInit(ThisTestCase):
    """Test initialization."""

    def test_creates_default_aliases(self):
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
        found = subject.all_aliases()
        self.assertEqual(expected, found)

    def test_creates_requested_aliases(self):
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
        found = subject.all_aliases()
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


# __END__
