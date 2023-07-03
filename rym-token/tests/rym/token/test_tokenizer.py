#!/usr/bin/env python3
"""Test."""

import logging
from unittest import TestCase

import rym.token.tokenizer as MOD
import rym.token.tokenspec as specs
import rym.token.tokenspecgroup as groups
from rym.token.structures import Token

LOGGER = logging.getLogger(__name__)


class ThisTestCase(TestCase):
    """Base test case for the module."""


class TestTokenize(ThisTestCase):
    """Test function."""

    maxDiff = None

    def test_words_and_punctuation_from_block_of_text(self) -> None:
        # NOTE: Intentionally did not used dedent.
        text = """
            Find all the words -- and punctuation. But we'll treat
            contractions as words: The meaning
            is lost if you split 'em up.
        """
        #   012345678901234567890123456789012345678901234567890123456789
        #   0         1         2         3         4         5
        expected = [
            Token(type="WORD", value="Find", line=1, column=12),
            Token(type="WORD", value="all", line=1, column=17),
            Token(type="WORD", value="the", line=1, column=21),
            Token(type="WORD", value="words", line=1, column=25),
            Token(type="PUNCTUATION", value="--", line=1, column=31),
            Token(type="WORD", value="and", line=1, column=34),
            Token(type="WORD", value="punctuation", line=1, column=38),
            Token(type="PUNCTUATION", value=".", line=1, column=49),
            Token(type="WORD", value="But", line=1, column=51),
            Token(type="WORD", value="we'll", line=1, column=55),
            Token(type="WORD", value="treat", line=1, column=61),
            Token(type="WORD", value="contractions", line=2, column=12),
            Token(type="WORD", value="as", line=2, column=25),
            Token(type="WORD", value="words", line=2, column=28),
            Token(type="PUNCTUATION", value=":", line=2, column=33),
            Token(type="WORD", value="The", line=2, column=35),
            Token(type="WORD", value="meaning", line=2, column=39),
            Token(type="WORD", value="is", line=3, column=12),
            Token(type="WORD", value="lost", line=3, column=15),
            Token(type="WORD", value="if", line=3, column=20),
            Token(type="WORD", value="you", line=3, column=23),
            Token(type="WORD", value="split", line=3, column=27),
            Token(type="PUNCTUATION", value="'", line=3, column=33),
            Token(type="WORD", value="em", line=3, column=34),
            Token(type="WORD", value="up", line=3, column=37),
            Token(type="PUNCTUATION", value=".", line=3, column=39),
        ]
        result = MOD.tokenize(text)
        found = list(result)
        self.assertEqual(expected, found)

    def test_matches_quotation(self) -> None:
        # NOTE: Intentionally did not used dedent.
        #   0         1         2         3         4         5
        #   012345678901234567890123456789012345678901234567890123456789
        text = """
            "Well", he said, "I hadn't really thought about it".
        """
        spec = [specs.quote(), specs.punctuation(), specs.word()]
        expected = [
            Token(type="QUOTE", value='"Well"', line=1, column=12),
            Token(type="PUNCTUATION", value=",", line=1, column=18),
            Token(type="WORD", value="he", line=1, column=20),
            Token(type="WORD", value="said", line=1, column=23),
            Token(type="PUNCTUATION", value=",", line=1, column=27),
            Token(
                type="QUOTE",
                value='"I hadn\'t really thought about it"',
                line=1,
                column=29,
            ),
            Token(type="PUNCTUATION", value=".", line=1, column=63),
        ]
        result = MOD.tokenize(text, spec)
        found = list(result)
        self.assertEqual(expected, found)

    def test_given_subtype_match(self) -> None:
        # NOTE: Test all dates together to ensure each can be detected.
        #   0         1         2         3         4         5         6
        #   0123456789012345678901234567890123456789012345678901234567890123456789
        text = """
            Some words are qualifiers. Between coding sessions, try it out, and
            before you know it, you'll have it done.
            After all, practice makes perfect.
        """
        subtypes = (
            ("qualifier", ("before", "after", "since", "between")),
            ("quantifier", ("some", "all", "any")),
        )
        spec = [MOD.word(subtypes)]  # ORDER MATTERS!
        expected = [
            Token(type="QUANTIFIER", value="Some", line=1, column=12),
            Token(type="WORD", value="words", line=1, column=17),
            Token(type="WORD", value="are", line=1, column=23),
            Token(type="WORD", value="qualifiers", line=1, column=27),
            Token(type="QUALIFIER", value="Between", line=1, column=39),
            Token(type="WORD", value="coding", line=1, column=47),
            Token(type="WORD", value="sessions", line=1, column=54),
            Token(type="WORD", value="try", line=1, column=64),
            Token(type="WORD", value="it", line=1, column=68),
            Token(type="WORD", value="out", line=1, column=71),
            Token(type="WORD", value="and", line=1, column=76),
            Token(type="QUALIFIER", value="before", line=2, column=12),
            Token(type="WORD", value="you", line=2, column=19),
            Token(type="WORD", value="know", line=2, column=23),
            Token(type="WORD", value="it", line=2, column=28),
            Token(type="WORD", value="you'll", line=2, column=32),
            Token(type="WORD", value="have", line=2, column=39),
            Token(type="WORD", value="it", line=2, column=44),
            Token(type="WORD", value="done", line=2, column=47),
            Token(type="QUALIFIER", value="After", line=3, column=12),
            Token(type="QUANTIFIER", value="all", line=3, column=18),
            Token(type="WORD", value="practice", line=3, column=23),
            Token(type="WORD", value="makes", line=3, column=32),
            Token(type="WORD", value="perfect", line=3, column=38),
        ]
        result = MOD.tokenize(text, spec)
        found = list(result)
        self.assertEqual(expected, found)

    def test_relative_date_and_grammar(self) -> None:
        # NOTE: Test all dates together to ensure each can be detected.
        #   0         1         2         3         4         5         6
        #   0123456789012345678901234567890123456789012345678901234567890123456789
        text = """
            Been around since April of last year, or was it last March?
            Worked on that last summer
            Happenend between Jan and Feb
            Completed in Q2
            We have until the end of September
            It'll be done by Thu of this week
        """
        spec = [*groups.temporal(), *groups.grammar()]
        expected = [
            Token(type="WORD", value="Been", line=1, column=12),
            Token(type="WORD", value="around", line=1, column=17),
            Token(type="CONJUNCTION", value="since", line=1, column=24),
            Token(type="MONTH", value="April", line=1, column=30),
            Token(type="PREPOSITION", value="of", line=1, column=36),
            Token(type="WORD", value="last", line=1, column=39),
            Token(type="RELDATE", value="year", line=1, column=44),
            Token(type="PUNCTUATION", value=",", line=1, column=48),
            Token(type="CONJUNCTION", value="or", line=1, column=50),
            Token(type="WORD", value="was", line=1, column=53),
            Token(type="WORD", value="it", line=1, column=57),
            Token(type="WORD", value="last", line=1, column=60),
            Token(type="MONTH", value="March", line=1, column=65),
            Token(type="PUNCTUATION", value="?", line=1, column=70),
            Token(type="WORD", value="Worked", line=2, column=12),
            Token(type="PREPOSITION", value="on", line=2, column=19),
            Token(type="WORD", value="that", line=2, column=22),
            Token(type="WORD", value="last", line=2, column=27),
            Token(type="RELDATE", value="summer", line=2, column=32),
            Token(type="WORD", value="Happenend", line=3, column=12),
            Token(type="WORD", value="between", line=3, column=22),
            Token(type="MONTH", value="Jan", line=3, column=30),
            Token(type="CONJUNCTION", value="and", line=3, column=34),
            Token(type="MONTH", value="Feb", line=3, column=38),
            Token(type="WORD", value="Completed", line=4, column=12),
            Token(type="PREPOSITION", value="in", line=4, column=22),
            Token(type="RELDATE", value="Q2", line=4, column=25),
            Token(type="WORD", value="We", line=5, column=12),
            Token(type="WORD", value="have", line=5, column=15),
            Token(type="WORD", value="until", line=5, column=20),
            Token(type="ARTICLE", value="the", line=5, column=26),
            Token(type="WORD", value="end", line=5, column=30),
            Token(type="PREPOSITION", value="of", line=5, column=34),
            Token(type="MONTH", value="September", line=5, column=37),
            Token(type="WORD", value="It'll", line=6, column=12),
            Token(type="WORD", value="be", line=6, column=18),
            Token(type="WORD", value="done", line=6, column=21),
            Token(type="PREPOSITION", value="by", line=6, column=26),
            Token(type="DAY", value="Thu", line=6, column=29),
            Token(type="PREPOSITION", value="of", line=6, column=33),
            Token(type="WORD", value="this", line=6, column=36),
            Token(type="RELDATE", value="week", line=6, column=41),
        ]
        result = MOD.tokenize(text, spec)
        found = list(result)
        self.assertEqual(expected, found)


# __END__
