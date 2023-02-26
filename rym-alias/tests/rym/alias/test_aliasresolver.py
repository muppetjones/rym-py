#!/usr/bin/env python3
"""Test."""

import json
import logging
from pathlib import Path
from pprint import pformat
from tempfile import TemporaryDirectory
from typing import Callable
from unittest import TestCase, mock, skipIf

import rym.alias as MOD
from rym.alias import variation
from rym.alias._alias import Alias, _default_transforms
from rym.alias._aliasresolver import toml, yaml  # if installed

LOGGER = logging.getLogger(__name__)


class ThisTestCase(TestCase):
    """Base test case for the module."""

    def get_temporary_directory(self) -> Path:
        tmpdir = TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        return Path(tmpdir.name)

    def pcompare(self, a, b) -> str:
        return f"\n===\n{pformat(a)}\n---\n{pformat(b)}\n"


class TestAddAliases(ThisTestCase):
    """Test method."""

    def test_raises_if_collisions_and_strict(self):
        subject = MOD.AliasResolver([])
        subject.logger = mock.Mock()
        subject.add(foo=["bar"])
        subject.add(foo=["bar"], strict=False)  # should not raise
        with self.assertRaisesRegex(ValueError, "bar"):
            subject.add(foo=["BAR"], strict=True)  # due to transform

    def test_appends_resolved_aliases(self):
        subject = MOD.AliasResolver.build({"foo": ["bar"]})
        subject.add({"hello": ["hola"]})
        expected = [
            Alias("foo", ["bar"]),
            Alias("hello", ["hola"]),
        ]
        found = subject.aliases
        self.assertEqual(expected, found)


class TestBuild(ThisTestCase):
    """Test classmethod."""

    def test_raises_if_collisions_and_strict(self):
        given = [
            {"foo": ["bar"]},
            {"baz": ["bar"]},
        ]
        MOD.AliasResolver.build(
            given,
            strict=False,
            logger=mock.Mock(),
        )  # should not raise
        with self.assertRaisesRegex(ValueError, "bar"):
            MOD.AliasResolver.build(
                given,
                strict=True,
                logger=mock.Mock(),
            )  # should raise

    def test_stores_resolved_aliases(self):
        subject = MOD.AliasResolver.build({"foo": ["bar"]})
        expected = [Alias("foo", ["bar"])]
        found = subject.aliases
        self.assertEqual(expected, found)


class TestBuildLookupIndex(ThisTestCase):
    """Test method."""

    def test_indexes_by_alias(self):
        given = [
            Alias("a", []),
            Alias("b", ["bee"]),
        ]
        expected = {
            "a": 0,  # explicit for example
            "A": 0,
            **{k: 1 for k in given[1].all_names()},  # auto for ease
        }
        subject = MOD.AliasResolver(given)
        subject._lookup = None
        subject._build_lookup_index()
        found = subject._lookup
        self.assertEqual(expected, found)


class TestFindCollisions(ThisTestCase):
    """Test classmethod."""

    def test_returns_iterable(self):
        tests = [
            # (expected, given)
            (["FOO", "foo"], [[Alias("foo", ["bar"])], [Alias("FOO", ["baz"])]]),
            (
                ["BAR", "bar"],
                [Alias("foo", ["Bar", "ick"]), Alias("meh", ["bar"])],
            ),
        ]
        for expected, aliases in tests:
            with self.subTest(expected):
                found = MOD.AliasResolver.find_collisions(aliases)
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
        subject = MOD.AliasResolver.build(**given)
        with self.assertRaisesRegex(KeyError, "foo"):
            subject.identify("foo")

    # section
    # ----------------------------------

    def test_returns_identity_for_alias(self):
        given = [
            {"identity": "foo", "aliases": ["bar"]},
            {"identity": "hello", "aliases": ["hola"]},
        ]
        tests = [
            # (expected, given)
            ("foo", "FOO"),
            ("foo", "bar"),
            ("hello", "HOLA"),
        ]
        subject = MOD.AliasResolver.build(given)
        for expected, value in tests:
            with self.subTest(value):
                found = subject.identify(value)
                self.assertEqual(expected, found)

    def test_tracks_attempts(self):
        given = [
            {"identity": "foo", "aliases": ["bar"]},
            {"identity": "hello", "aliases": ["hola"]},
        ]
        # use transforms=None to avoid enumerating all 0 attempts
        subject = MOD.AliasResolver.build(given, transforms=None)
        expected = {"foo": 2, "bar": 1, "hola": 0, "hello": 6, "bonjour": 3}
        for k, v in expected.items():
            for i in range(v):
                try:
                    subject.identify(k)
                except KeyError:
                    ...
        found = subject._attempts
        self.maxDiff = None
        self.assertEqual(expected, found, self.pcompare(expected, found))


class TestResolveAlias(ThisTestCase):
    """Test function."""

    def test_supports_explicit_aliases(self):
        given = [
            Alias("a", None, None),
            Alias("b", None, None),
        ]
        expected = given[:]
        found = MOD.resolve_aliases(given)
        self.assertEqual(expected, found)

    def test_supports_implicit_aliases(self):
        given = [
            {"identity": "a", "aliases": None, "transforms": [variation.deesser]},
            {"identity": "b", "aliases": ["bee"]},
            {"aliases": [{"identity": "c", "aliases": ["see"]}]},
        ]
        expected = [
            Alias("a", None, [variation.deesser]),
            Alias("b", ["bee"]),
            Alias("c", ["see"]),
        ]
        found = MOD.resolve_aliases(given)
        self.maxDiff = None
        self.assertEqual(expected, found)

    def test_supports_None(self):
        given = None
        expected = []
        found = MOD.resolve_aliases(given)
        self.assertEqual(expected, found)

    def test_supports_mappings(self):
        given = {
            "a": None,
            "b": ["bee"],
        }
        expected = [
            Alias("a", None),  # default transforms
            Alias("b", ["bee"]),  # default transforms
        ]
        found = MOD.resolve_aliases(given)
        self.assertEqual(expected, found)

    def test_supports_kwargs(self):
        kwargs = {
            "a": None,
            "b": ["bee"],
        }
        expected = [
            Alias("a", None),  # default transforms
            Alias("b", ["bee"]),  # default transforms
        ]
        found = MOD.resolve_aliases(**kwargs)
        self.assertEqual(expected, found)

    def test_transform_set_on_all(self):
        args = [
            Alias("a", None, [variation.deesser]),
            Alias("b", ["bee"]),
        ]
        kwargs = {"transforms": [variation.esser]}
        expected = [
            Alias("a", None, [variation.esser]),
            Alias("b", ["bee"], [variation.esser]),
        ]
        found = MOD.resolve_aliases(*args, **kwargs)
        self.assertEqual(expected, found)


class TestResolveAliasEncoding(ThisTestCase):
    """Test function feature."""

    def test_raises_if_unknown_extension(self):
        given = Path("foo.txt")
        with self.assertRaisesRegex(ValueError, "unavailable encoding"):
            MOD.AliasResolver.build(given)

    # section
    # ----------------------------------

    def assert_loads_aliases_from_root(self, suffix: str, encode: Callable):
        data = {
            "aliases": [
                {"identity": "foo", "aliases": ["bar"], "transforms": "deesser"},
                {"identity": "hello", "aliases": ["aloha"]},
            ]
        }
        expected = [
            Alias("foo", ["bar"], [variation.deesser]),
            Alias("hello", ["aloha"], _default_transforms()),
        ]
        tmpdir = self.get_temporary_directory()  # type: Path
        path = Path(tmpdir, "aliases").with_suffix(suffix)
        path.write_text(encode(data))

        subject = MOD.AliasResolver.build(path)
        found = subject.aliases
        self.maxDiff = None
        self.assertEqual(expected, found)

    def test_json(self):
        with self.subTest("load aliases from root"):
            self.assert_loads_aliases_from_root(suffix=".json", encode=json.dumps)

    @skipIf(not toml, "toml not intalled")
    def test_toml(self):
        with self.subTest("load aliases from root"):
            self.assert_loads_aliases_from_root(suffix=".toml", encode=toml.dumps)

    @skipIf(not yaml, "yaml not intalled")
    def test_yaml(self):
        with self.subTest("load aliases from root"):
            self.assert_loads_aliases_from_root(
                suffix=".yaml", encode=yaml.safe_dump
            )

    # section
    # ----------------------------------

    def test_json_as_string(self):
        data = [
            {"identity": "foo", "aliases": ["bar"], "transforms": "deesser"},
            {"identity": "hello", "aliases": ["aloha"]},
        ]
        expected = [
            Alias("foo", ["bar"], [variation.deesser]),
            Alias("hello", ["aloha"], _default_transforms()),
        ]
        given = json.dumps(data)

        subject = MOD.AliasResolver.build(given)
        found = subject.aliases
        self.maxDiff = None
        self.assertEqual(expected, found)

    @skipIf(not toml, "toml not intalled")
    def test_toml_as_string(self):
        data = {
            "aliases": [
                {"identity": "foo", "aliases": ["bar"], "transforms": "deesser"},
                {"identity": "hello", "aliases": ["aloha"]},
            ]
        }
        given = toml.dumps(data)
        with self.assertRaises(ValueError):
            MOD.AliasResolver.build(given)

    @skipIf(not yaml, "yaml not intalled")
    def test_yaml_as_string(self):
        data = [
            {"identity": "foo", "aliases": ["bar"], "transforms": "deesser"},
            {"identity": "hello", "aliases": ["aloha"]},
        ]
        given = yaml.safe_dump(data)
        with self.assertRaises(ValueError):
            MOD.AliasResolver.build(given)


# __END__
