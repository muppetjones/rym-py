#!/usr/bin/env python3
"""Test."""

import json
import logging
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable
from unittest import TestCase, mock, skipIf

import rym.alias as MOD
from rym.alias import variation
from rym.alias._alias import Alias, _default_transforms

try:
    import toml
except ImportError:
    toml = None

try:
    import yaml
except ImportError:
    yaml = None

LOGGER = logging.getLogger(__name__)


class ThisTestCase(TestCase):
    """Base test case for the module."""

    def get_temporary_directory(self) -> Path:
        tmpdir = TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        return Path(tmpdir.name)


class TestBuild(ThisTestCase):
    """Test initialization classmethod."""

    def test_supports_explicit_aliases(self):
        given = [
            Alias("a", None, None),
            Alias("b", None, None),
        ]
        expected = given[:]
        subject = MOD.AliasResolver.build(given)
        found = subject.aliases
        self.assertEqual(expected, found)

    def test_supports_implicit_aliases(self):
        given = [
            {"identity": "a", "aliases": None, "transforms": [variation.deesser]},
            {"identity": "b", "aliases": ["bee"]},
        ]
        expected = [
            Alias("a", None, [variation.deesser]),
            Alias("b", ["bee"]),
        ]
        subject = MOD.AliasResolver.build(given)
        found = subject.aliases
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
        subject = MOD.AliasResolver.build(given)
        found = subject.aliases
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
        subject = MOD.AliasResolver.build(**kwargs)
        found = subject.aliases
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
        subject = MOD.AliasResolver.build(*args, **kwargs)
        found = subject.aliases
        self.assertEqual(expected, found)


class TestEncoding(ThisTestCase):
    """Test feature."""

    def test_raises_if_unknown_extension(self):
        given = Path("foo.txt")
        with self.assertRaisesRegex(ValueError, "unavailable encoding"):
            MOD.AliasResolver.build(given)

    # section
    # ----------------------------------

    def assert_loads_aliases_from_root(self, suffix: str, encode: Callable):
        data = [
            {"identity": "foo", "aliases": ["bar"], "transforms": "deesser"},
            {"identity": "hello", "aliases": ["aloha"]},
        ]
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
        data = [
            {"identity": "foo", "aliases": ["bar"], "transforms": "deesser"},
            {"identity": "hello", "aliases": ["aloha"]},
        ]
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
