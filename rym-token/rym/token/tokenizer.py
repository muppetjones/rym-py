#!/usr/bin/env python3
""".

See also:
    https://docs.python.org/3/library/re.html?highlight=re#writing-a-tokenizer
"""

import datetime as dt
import logging
import re
from typing import Callable, Iterable, Tuple

from .regex import combine_regex
from .structures import Token, TokenSpec

try:
    from functools import cache
except ImportError:  # pragma: no cover
    from functools import lru_cache

    cache = lru_cache(maxsize=None)


LOGGER = logging.getLogger(__name__)


@cache
def get_default_specs() -> Tuple[TokenSpec, ...]:
    """Return tuple of (type, pattern, callable)."""
    return (word(), quote(), punctuation())


def tokenize(
    block: str,
    specs: Iterable[Callable[..., TokenSpec]] = None,
) -> Iterable[Token]:
    """Given a string, identify contextual tokens."""
    specs = [*(specs or get_default_specs()), newline()]
    pattern = combine_regex(specs)
    handlers = {k: v for k, _, v in specs if v}

    def _as_is(v: str) -> str:
        return v

    line_num = 0
    line_start = 0
    for match in pattern.finditer(block):
        group_name = match.lastgroup
        if group_name == "NEWLINE":
            line_num += 1
            line_start = match.end()
            continue

        value = match.group()
        column = match.start() - line_start
        handler = handlers.get(group_name, _as_is)
        value = handler(value)
        yield Token(group_name, value, line_num, column)


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
    return TokenSpec(
        "TIMESTAMP",
        "%s%s%s(?:%s)?" % (_DATE, _TS_SEP, _TIME, _TZ),
        _safe_timestamp,
    )


def date() -> TokenSpec:
    return TokenSpec("DATE", _DATE, _safe_date)


def time() -> TokenSpec:
    return TokenSpec("TIME", "%s(?:%s)?" % (_TIME, _TZ), _safe_time)


# numeric
# ----------------------------------


def _safe_float(x: str, *args) -> int:
    return float(x.replace(",", ""))


def _safe_int(x: str, *args) -> int:
    return int(x.replace(",", ""))


@cache
def number() -> TokenSpec:
    return TokenSpec("NUMBER", r"-?\d[\d_]*[e\.]-?\d+", _safe_float)


@cache
def integer() -> TokenSpec:

    return TokenSpec(
        "INTEGER",
        r"(?<![\.\de])(?<!e-)\-?\d(?:[\,_]\d)?\d*(?!\.\d)(?![\d_e])",
        _safe_int,
    )


# text
# ----------------------------------


@cache
def newline() -> TokenSpec:
    return TokenSpec("NEWLINE", r"\r?\n", None)


@cache
def punctuation() -> TokenSpec:
    return TokenSpec("PUNCTUATION", r"[^\w\s]+", None)


@cache
def quote() -> TokenSpec:
    return TokenSpec("QUOTE", r"\"[^\"]*\"")


@cache
def word() -> TokenSpec:
    return TokenSpec("WORD", r"[A-Za-z]+(?:\'[A-Za-z]+)?", None)


# __END__
