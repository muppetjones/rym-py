#!/usr/bin/env python3
"""Test."""

import logging
from datetime import date, datetime, time, timedelta, timezone
from typing import Iterable
from unittest import TestCase

import rym.token.tokenspecgroup as MOD
from rym.token.structures import Token
from rym.token.tokenizer import tokenize

LOGGER = logging.getLogger(__name__)


class ThisTestCase(TestCase):
    """Base test case for the module."""

    maxDiff = None

    def add_buffer(
        self,
        tokens: Iterable[Token],
        buffer: int,
    ) -> Iterable[Token]:
        for tobj in tokens:
            tobj.column += buffer
        return tokens


class TestNumeric(ThisTestCase):
    """Test functionality."""

    def test_matches_numbers(self) -> None:
        #   0         1         2         3         4         5         6
        #   0123456789012345678901234567890123456789012345678901234567890123456789
        text = """
            Some numbers are floating point, such as 2_000.0, 3.14, and 1e-3,
            and others that are integers, such as -4, 1, 42, and 1,005.
        """
        spec = MOD.numeric()
        expected = [
            Token(type="NUMBER", value=2000.0, line=1, column=41),
            Token(type="NUMBER", value=3.14, line=1, column=50),
            Token(type="NUMBER", value=0.001, line=1, column=60),
            Token(type="INTEGER", value=-4, line=2, column=38),
            Token(type="INTEGER", value=1, line=2, column=42),
            Token(type="INTEGER", value=42, line=2, column=45),
            Token(type="INTEGER", value=1005, line=2, column=53),
        ]
        expected = self.add_buffer(expected, buffer=12)
        result = tokenize(text, spec)
        found = list(result)
        self.assertEqual(expected, found)


class TestSearch(ThisTestCase):
    """Test functionality."""

    def test_matches_expected(self) -> None:
        #   0         1         2         3         4         5         6
        #   0123456789012345678901234567890123456789012345678901234567890123456789
        text = """
            assay=xt.v4 analyte=rna since Aug 2008
            23abcde workflow:run_this
            before 2022/12/31 01234567-0123-0123-0123-0123456789ab
            2008-07-25T02:45:00.000000Z
        """
        spec = MOD.search()
        expected = [
            Token(type="TERM", value="assay=xt.v4", line=1, column=0),
            Token(type="TERM", value="analyte=rna", line=1, column=12),
            Token(type="QUALIFIER", value="since", line=1, column=24),
            Token(type="MONTH", value="Aug", line=1, column=30),
            Token(type="INTEGER", value=2008, line=1, column=34),
            Token(type="ALPHANUM", value="23abcde", line=2, column=0),
            Token(type="TERM", value="workflow:run_this", line=2, column=8),
            Token(type="QUALIFIER", value="before", line=3, column=0),
            Token(type="DATE", value=date(2022, 12, 31), line=3, column=7),
            Token(
                type="UUID",
                value="01234567-0123-0123-0123-0123456789ab",
                line=3,
                column=18,
            ),
            Token(
                type="TIMESTAMP",
                value=datetime(2008, 7, 25, 2, 45, tzinfo=timezone.utc),
                line=4,
                column=0,
            ),
        ]
        expected = self.add_buffer(expected, buffer=12)
        result = tokenize(text, spec)
        found = list(result)
        self.assertEqual(expected, found)


class TestTemporal(ThisTestCase):
    """Test functionality."""

    def test_matches_dates(self) -> None:
        # NOTE: Test all dates together to ensure each can be detected.
        #   0         1         2         3         4         5         6
        #   0123456789012345678901234567890123456789012345678901234567890123456789
        text = """
            Dates are often expressed as timestamps: 2008-07-25T02:45:00.000000-05:00
            But there are quite a few variations:
                2008-07-25T02:45:00.000000-05:00
                2008-07-25T02:45:00.000
                2008-07-25 02:45
                2008-07-25T02:45:00.000000Z
            But you can also only specify the date: 1985-10-26, 1955.11.05, 2015/10/21
            Or just the time: 21:00 in 24-hour or 9:00 PM in 12-hour formats.
            Time can also include a timezone: 04:20Z, 16:20-05:00
        """
        spec = MOD.temporal()
        LOGGER.critical(spec)
        est = {"tzinfo": timezone(timedelta(hours=-5))}
        utc = {"tzinfo": timezone.utc}
        TS = "TIMESTAMP"
        arg = (2008, 7, 25, 2, 45)
        expected = [
            Token(type=TS, value=datetime(*arg, **est), line=1, column=41),
            Token(type=TS, value=datetime(*arg, **est), line=3, column=4),
            Token(type=TS, value=datetime(*arg), line=4, column=4),
            Token(type=TS, value=datetime(*arg), line=5, column=4),
            Token(type=TS, value=datetime(*arg, **utc), line=6, column=4),
            Token(type="DATE", value=date(1985, 10, 26), line=7, column=40),
            Token(type="DATE", value=date(1955, 11, 5), line=7, column=52),
            Token(type="DATE", value=date(2015, 10, 21), line=7, column=64),
            Token(type="TIME", value=time(21, 0, 0), line=8, column=18),
            Token(type="TIME", value=time(21, 0, 0), line=8, column=38),
            Token(type="TIME", value=time(4, 20, 0, **utc), line=9, column=34),
            Token(type="TIME", value=time(16, 20, 0, **est), line=9, column=42),
        ]
        buf = 12
        for tobj in expected:
            tobj.column += buf
        result = tokenize(text, spec)
        found = list(result)
        self.assertEqual(expected, found)

    def test_matches_relative_date(self):
        # NOTE: Test all dates together to ensure each can be detected.
        #   0         1         2         3         4         5         6
        #   0123456789012345678901234567890123456789012345678901234567890123456789
        text = """
            Been around since April of last year, or was it last June?
            Worked on that last summer
            Happenend between Jan and Feb
            Completed in Q2
            Today is Friday, which means tomorrow is Sat, and yesterday was Thursday
            It'll be done by Wed of this week
            We have until the end of September
        """
        spec = MOD.temporal()
        LOGGER.critical(spec)
        expected = [
            Token(type="MONTH", value="April", line=1, column=30),
            Token(type="RELDATE", value="year", line=1, column=44),
            Token(type="MONTH", value="June", line=1, column=65),
            Token(type="RELDATE", value="summer", line=2, column=32),
            Token(type="MONTH", value="Jan", line=3, column=30),
            Token(type="MONTH", value="Feb", line=3, column=38),
            Token(type="RELDATE", value="Q2", line=4, column=25),
            Token(type="RELDATE", value="Today", line=5, column=12),
            Token(type="DAY", value="Friday", line=5, column=21),
            Token(type="RELDATE", value="tomorrow", line=5, column=41),
            Token(type="DAY", value="Sat", line=5, column=53),
            Token(type="RELDATE", value="yesterday", line=5, column=62),
            Token(type="DAY", value="Thursday", line=5, column=76),
            Token(type="DAY", value="Wed", line=6, column=29),
            Token(type="RELDATE", value="week", line=6, column=41),
            Token(type="MONTH", value="September", line=7, column=37),
        ]
        result = tokenize(text, spec)
        found = list(result)
        self.assertEqual(expected, found)


# __END__
