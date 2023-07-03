#!/usr/bin/env python3
"""Regex handling for rym-token.

"""

import logging
import re
from collections import abc
from functools import singledispatch
from re import Pattern
from typing import Any, Iterable, Tuple, Union

from .structures import TokenSpec

LOGGER = logging.getLogger(__name__)

try:
    from functools import cache
except ImportError:  # pragma: no cover
    from functools import lru_cache

    cache = lru_cache(maxsize=None)


def combine_regex(sources: Iterable[Union[str, Pattern, TokenSpec]]) -> Pattern:
    """Compile sources into single, compiled regex pattern.

    Accepted sources:
        -   String
        -   re.Pattern
        -   rym.token.TokenSpec

    All string and pattern sources will be captured as 'PX' where 'X' is the
    index within the given list. All TokenSpec sources will be captured with
    their 'type'.

    Sources are deduplicated based on capture name and pattern, i.e., only
    token spec sources are deduplicated. Group index is based on the
    pre-deduplication order, i.e., count based on your input.

    This function is indirectly memoized for (name, regex) sources.

    Arguments:
        sources: Iterable with one or more regex sources.
    Returns:
        Compiled regex with named capture group for each source.
    Raises:
        TypeError for invalid source.
    )
    """
    patterns = tuple(_yield_patterns(sources, i=None))
    return combine_regex_memoized(patterns)


@cache
def combine_regex_memoized(specs: Tuple[Tuple[str, str], ...]) -> Pattern:
    """Memoized version of combine_regex.

    See also:
        combine_regex
    """
    idx = {k: i for i, (k, _) in reversed(list(enumerate(specs)))}
    ordered = [specs[i] for i in sorted(idx.values())]
    regexp = "|".join("(?P<%s>%s)" % (name, pattern) for name, pattern in ordered)
    return re.compile(regexp)


@singledispatch
def _yield_patterns(value: Any, i: int) -> Tuple[str, str]:
    """Return (name, pattern) for every source.

    Arguments:
        value: Regex pattern source
        i: Index for naming (if needed)
    Returns:
        A tuple of the name and pattern.
    Raises:
        TypeError for unsupported sources.
    """
    raise TypeError(f"{value}; expected string, re.Pattern, or TokenSpec")


@_yield_patterns.register(str)
def _(value: str, i: int) -> Tuple[str, str]:
    yield f"P{i or 0}", value


@_yield_patterns.register(Pattern)
def _(value: Pattern, i: int) -> Tuple[str, str]:
    yield f"P{i or 0}", value.pattern


@_yield_patterns.register(TokenSpec)
def _(value: TokenSpec, i: int) -> Tuple[str, str]:
    yield value.type, value.pattern


@_yield_patterns.register(abc.Iterable)
def _(value: Iterable, i: int) -> Tuple[str, str]:
    prefix = f"{i}_" if i else ""
    for j, x in enumerate(value):
        yield from _yield_patterns(x, f"{prefix}{j}")


# __END__
