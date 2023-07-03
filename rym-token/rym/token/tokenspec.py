#!/usr/bin/env python3
""".

"""

import calendar
import datetime as dt
import itertools
import logging
import re
from typing import Callable, Iterable, Optional, Tuple

from rym.token.structures import TokenSpec

try:
    from functools import cache
except ImportError:  # pragma: no cover
    from functools import lru_cache

    cache = lru_cache(maxsize=None)


LOGGER = logging.getLogger(__name__)

# support
# ======================================================================


def build_subtype_assignment(
    subtypes: Iterable[Tuple[str, Tuple[str, ...]]]
) -> Callable[[str], str]:
    """Return a callable to assign subtype.

    Arguments:
        subtype: One or more ("type", ("subtype", ...)) definitions
    Returns:
        A callable that takes a value and type string and returns the
        updated type assignment.
    """
    lookup = {str(name).lower(): k.upper() for k, names in subtypes for name in names}

    def assign_subtype(value: str, type_: str) -> str:
        return lookup.get(str(value).lower(), type_)

    return assign_subtype


# specs
# ======================================================================


# datetime
# ----------------------------------
_DATE = r"(?:\d\d)?\d{2}[\-/\.]\d{2}[\-/\.]\d{2}"
_TS_SEP = r"[T\s]"
_TIME = r"\d?\d:\d{2}(?::\d{2}(?:\.\d+)?)?(?:\s?[ZAPap][Mm]?)?"
_TZ = r"(?:Z|[\+\-]\d{2}:\d{2})"
_DATE_SEP = re.compile(r"[\./]")
_TIME_SEP = re.compile(r"[:\sa-z]")


def _safe_date(value: str, *args) -> dt.date:
    value = _DATE_SEP.sub("-", value)
    return dt.date.fromisoformat(value)


def _safe_time(value: str, *args) -> dt.time:
    value = value.lower()
    if "z" == value[-1]:
        # Z support added in 3.11
        value = value[:-1] + "+00:00"
    elif "m" == value[-1]:
        h, m, *_ = _TIME_SEP.split(value)
        adj = 0 if "a" == value[-2] else 12
        h = int(h) + adj
        value = "{:0d}:{}".format(h, m)
    return dt.time.fromisoformat(value)


def _safe_timestamp(value: str, *args) -> dt.datetime:
    if "z" == value[-1].lower():
        # Z support added in 3.11
        value = value[:-1] + "+00:00"
    return dt.datetime.fromisoformat(value)


@cache
def timestamp() -> TokenSpec:
    """Return a spec for ISO-8601 timestamps."""
    return TokenSpec(
        "TIMESTAMP",
        "%s%s%s(?:%s)?" % (_DATE, _TS_SEP, _TIME, _TZ),
        _safe_timestamp,
    )


@cache
def date() -> TokenSpec:
    """Return a spec for ISO-8601 dates, e.g., 2023-10-30."""
    return TokenSpec("DATE", _DATE, _safe_date)


@cache
def time() -> TokenSpec:
    """Return a spec for ISO-8601 time strings, e.g., 24:00.000Z."""
    return TokenSpec("TIME", "%s(?:%s)?" % (_TIME, _TZ), _safe_time)


@cache
def reldate() -> TokenSpec:
    """Return a spec for relative date words, e.g., 'tomorrow'."""
    names = "|".join(
        r"[%s%s]%s" % (x[0].lower(), x[0].upper(), x[1:])
        for x in itertools.chain(
            ("yesterday", "today", "tomorrow", "day"),
            ("weekend", "weekday", "week"),
            ("month", "year"),
            ("winter", "spring", "summer", "fall"),
            ("Q[1-4]",),
        )
    )
    pattern = r"(?<=\b)(?:%s)(?=\b)" % (names,)
    return TokenSpec("RELDATE", pattern)


@cache
def month() -> str:
    """Return a spec for month names and abbreviations. Title case only."""
    names = "|".join(
        itertools.chain.from_iterable(
            zip(calendar.month_name[1:], calendar.month_abbr[1:])
        )
    )
    pattern = r"(?<=\b)(?:%s)(?=\b)" % (names,)
    return TokenSpec("MONTH", pattern)


@cache
def day() -> str:
    """Return a spec for day names and abbreviations. Title case only."""
    names = "|".join(
        itertools.chain.from_iterable(zip(calendar.day_name[1:], calendar.day_abbr[1:]))
    )
    pattern = r"(?<=\b)(?:%s)(?=\b)" % (names,)
    return TokenSpec("DAY", pattern)


# numeric
# ----------------------------------


def _safe_float(x: str, *args) -> int:
    return float(x.replace(",", ""))


def _safe_int(x: str, *args) -> int:
    return int(x.replace(",", ""))


@cache
def number() -> TokenSpec:
    """Return a spec for floating point numbers."""
    return TokenSpec("NUMBER", r"-?\d[\d_]*[e\.]-?\d+", _safe_float)


@cache
def integer() -> TokenSpec:
    """Return a spec for integers."""
    return TokenSpec(
        "INTEGER",
        r"(?<![\.\d\w])(?<!e-)\-?\d(?:[\,_]\d)?\d*(?!\.\d)(?![\d_e])\b",
        _safe_int,
    )


# text
# ----------------------------------


@cache
def alphanum(
    subtype: Optional[Iterable[Tuple[str, Tuple[str, ...]]]] = None
) -> TokenSpec:
    """Return a spec for alphanumeric words. Includes hyphens."""
    if subtype:
        subtype = build_subtype_assignment(subtype)
    return TokenSpec(
        "ALPHANUM",
        r"\b[\w\d\-]+\b",
        None,
        subtype=subtype,
    )


@cache
def newline() -> TokenSpec:
    """Return a spec for newlines."""
    return TokenSpec("NEWLINE", r"\r?\n", None)


@cache
def punctuation() -> TokenSpec:
    """Return a spec for punctuation, e.g., non-word, non-whitespace."""
    return TokenSpec("PUNCTUATION", r"[^\w\s]+", None)


@cache
def quote() -> TokenSpec:
    """Return a spec for returning quoted strings."""
    return TokenSpec("QUOTE", r"\"[^\"]*\"")


@cache
def search_term() -> TokenSpec:
    """Return a spec for search terms in the format 'key=val' or 'key:val'."""
    return TokenSpec(
        "TERM",
        r"(?P<term_key>[\w\-]+)(?P<term_op>[:=><]+)(?P<term_value>[\w\-\.]+\b)(?![:])",
    )


@cache
def uuid_string() -> TokenSpec:
    """Return a spec for UUID v4."""
    return TokenSpec(
        "UUID",
        r"[\da-fA-F]{8}-[\da-fA-F]{4}-[\da-fA-F]{4}-[\da-fA-F]{4}-[\da-fA-F]{12}",
    )


@cache
def word(subtype: Optional[Iterable[Tuple[str, Tuple[str, ...]]]] = None) -> TokenSpec:
    """Return a spec for words.

    NOTE: Matches any consecutive letters.
    """
    if subtype:
        subtype = build_subtype_assignment(subtype)
    return TokenSpec(
        "WORD",
        r"[A-Za-z]+(?:\'[A-Za-z]+)?",
        None,
        subtype=subtype,
    )


# __END__
