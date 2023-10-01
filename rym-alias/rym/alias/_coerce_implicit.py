#!/usr/bin/env python3
""".

"""

import logging
import re
from functools import singledispatch
from types import SimpleNamespace
from typing import Any, Optional, Union

from ._aliasresolver import AliasResolver
from ._coerce_explicit import coerce_explicit, get_alias_bool, get_alias_null

try:
    from numpy import NaN  # noqa
except ImportError:  # pragma: no cover
    NaN = None


try:
    from functools import cache
except ImportError:  # pragma: no cover
    from functools import lru_cache

    cache = lru_cache(maxsize=None)

LOGGER = logging.getLogger(__name__)


# build regex
# ======================================================================


@cache
def build_regex() -> SimpleNamespace:
    patterns = {
        "boolean": _build_regex_pattern_bool(),
        "float": _build_regex_pattern_float(),
        "integer": _build_regex_pattern_integer(),
        "null": _build_regex_pattern_null(),
        "scientific": _build_regex_pattern_scientific(),
    }
    parts = [r"(?P<%s>%s)" % (name, pattern) for name, pattern in patterns.items()]
    pattern = "|".join(parts)
    return re.compile(pattern, re.I)


@cache
def _build_regex_pattern_bool() -> str:
    """Assume any string value from the null alias."""
    parts = ("true", "false")
    return "|".join(parts)


@cache
def _build_regex_pattern_float() -> str:
    """Assume any string value from the null alias."""
    parts = (
        r"(?<!\w\-)",  # ignore hypenated strings, e.g., 3-4
        r"(?<![\w\.])",  # ignore version and alphanumeric strings
        r"[\+\-]?",  # support explicit positive or negative
        r"(?:[\d,_]*\.[\d_]*)",  # match 1.1, 1., or .1 with underscores or commas
        r"(?!\w)",  # ignore alphanumeric strings
    )
    return "".join(parts)


@cache
def _build_regex_pattern_integer() -> str:
    """Assume any string value from the null alias."""
    # r"(?<![\w\.])(?<!\w\-)[\+\-]?[\d,_]+(?![\w\-])"
    parts = (
        r"(?<![\w\.])",  # ignore alphanum and decimels
        r"(?<!\w\-)",  # ignore hyphenated and alphanum
        r"[\+\-]?[\d,_]+",  # optional sign, comma, and underscore,
        r"(?![\w\-])",  # ignore hyphenated and alphanum
    )
    return "".join(parts)


@cache
def _build_regex_pattern_null() -> str:
    """Assume any string value from the null alias."""
    values = [str(x) for x in get_alias_null().names]
    ors = "|".join(x for x in values if x)
    return rf"\b(?:{ors})\b"


@cache
def _build_regex_pattern_scientific() -> str:
    """Regex for scientific notation.

    NOTE: Could be more robust on the edges
    """
    parts = (
        r"[\+\-]?",  # Optional sign
        r"\d+e-?\d+",  # Must have digits on either side of the "e"
    )
    return "".join(parts)


# coerce implicit
# ======================================================================


def coerce_implicit(value: Any, alias: Optional[AliasResolver] = None) -> Any:
    """Naively detect type and convert.

    Implicit conversion assumes you've provided a string.
    If not a string, we'll try an alias lookup before returning as is.

    Arguments:
        value: The thing to convert.
        alias: An AliasResolver
    Returns:
        The converted value.
    Raises:
        InvalidConversionError (ValueError) if unable to convert.
    See also:
        converter_names(...)
    """
    return _coerce_implicit(value, alias)


@singledispatch
def _coerce_implicit(value: Any, alias: Optional[AliasResolver] = None) -> Any:
    """Alias lookup or return the value."""
    alias = alias or get_default_value_aliases()
    return alias.identify(value, default=value)


@_coerce_implicit.register(str)
def _(value: str, alias: Optional[AliasResolver] = None) -> Any:
    """Determine type via regex and use explicit coerce."""
    if not value:
        return None  # EARLY EXIT: empty string
    rx = build_regex()  # type: re.Pattern
    for match_ in rx.finditer(value):
        for name, matched in match_.groupdict().items():
            if matched is None:
                continue
            if name in ("integer", "float") and "," in matched:
                matched = matched.replace(",", "")
            return coerce_explicit(name, matched)
    return value


@_coerce_implicit.register(bool)
@_coerce_implicit.register(int)
@_coerce_implicit.register(float)
def _(value: Union[int, float], alias: Optional[AliasResolver] = None) -> int:
    return value


# section
# ======================================================================


@cache
def get_default_value_aliases() -> AliasResolver:
    return AliasResolver.build(
        get_alias_null(),
        get_alias_bool(),
    )


# __END__
