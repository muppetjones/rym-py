#!/usr/bin/env python3
"""Test."""

import logging
import re
from unittest import TestCase

import rym.token.regex as MOD

LOGGER = logging.getLogger(__name__)


class ThisTestCase(TestCase):
    """Base test case for the module."""


class TestCombineRegex(ThisTestCase):
    """Test function."""

    def test_raises_for_invalid_source(self):
        with self.assertRaisesRegex(TypeError, "42; expected"):
            MOD.combine_regex([42])

    def test_returns_joined_pattern_from_given_patterns(self):
        given = [r"o", r"e"]
        line = "The quick brown fox jumped over the fence"
        pattern = MOD.combine_regex(given)
        expected = [
            ("", "e"),
            ("o", ""),
            ("o", ""),
            ("", "e"),
            ("o", ""),
            ("", "e"),
            ("", "e"),
            ("", "e"),
            ("", "e"),
        ]
        found = pattern.findall(line)
        self.assertEqual(expected, found)

    def test_caches_if_able(self):
        specs = [
            [r"o", r"e"],
            [re.compile(r"o"), r"e"],
            [r"o", MOD.TokenSpec("P1", r"e", None)],
            [r"o", MOD.TokenSpec("LETTER_E", r"e", None)],
        ]
        a, b, c, d = [MOD.combine_regex(x) for x in specs]
        assert a is b
        assert a is c
        assert a is not d


# __END__
