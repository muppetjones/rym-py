#!/usr/bin/env python3
"""
Coerce values.
^^^^^^^^^^^^^^

Implicit type conversion from strings.

>>> from rym.alias import coerce
>>> coerce('null')
None
>>> coerce('1.24')
1.24
>>> coerce('["a", false]')
["a", False]
>>> coerce('true')
True
>>> coerce('1985-10-26T09:22:01.234567Z')
datetime()

"""

import dataclasses as dcs
import json
import logging
from collections import abc
from functools import singledispatch
from typing import Any, Callable, Optional, Union

from ._alias import Alias, AliasError

# from ._aliasfrozen import FrozenAlias
from ._aliasresolver import AliasResolver
from ._coerce_implicit import coerce_implicit

try:
    from numpy import NaN  # noqa
except ImportError:  # pragma: no cover
    NaN = None

LOGGER = logging.getLogger(__name__)


class InvalidConversionError(ValueError):
    ...


class InvalidConverter(ValueError):
    ...


@dcs.dataclass
class Coercer:
    """Data type converter."""

    converter_resolver: AliasResolver = None
    value_alias: AliasResolver = None
    logger: logging.Logger = None

    def __post_init__(self):
        self.logger = self.logger or LOGGER
        # self.logger.critical(self.converter_resolver._lookup)
        if not self.converter_resolver:
            self.converter_resolver = AliasResolver([])
        if not self.value_alias:
            self.value_alias = AliasResolver([])

    def __call__(self, value: Any, converter: Optional[Callable] = None) -> Any:
        return self.coerce(value, converter=converter)

    def coerce(self, value: Any, converter: Optional[Callable] = None) -> Any:
        """Coerce the given value to a data type.

        Implicit conversion assumes you've provided a string. If not, then
        the given value will be returned as is.

        NOTE: Explicit conversion starts with an implicit conversion to properly
            catch special edge cases, such as "2.2" to int or "None" to None.

        Arguments:
            value: The thing to convert.
            converter: The method used for conversion. If not given, will
                use implicit conversion IFF given value is a string.
                May be a string value.
        Returns:
            The converted value.
        Raises:
            InvalidConversionError (ValueError) if unable to convert.
            AliasError (KeyError) if unknown converter alias given.
        See also:
            converter_names(...)
        """
        coerced = self.coerce_implicit(value)
        try:
            if converter:
                coerced = self.coerce_explicit(coerced, converter=converter)
        except Exception:
            raise InvalidConversionError(
                f"unable to coerce using {converter}: {value}"
            )
        return coerced

    def coerce_implicit(self, value: Any) -> Any:
        return coerce_implicit(value, alias=self.value_alias)

    def coerce_explicit(self, value: Any, converter: Union[str, Callable]) -> Any:
        converter = self.resolve_converter(converter)
        return _coerce_explicit(converter, value)

    def resolve_converter(self, converter: Union[str, Callable]) -> Any:
        """Attempt to resolve converter from given value.

        Args:
            converter: Name or callable for converting.
        Returns:
            The aliased converter if found; given converter otherwise.
        """
        try:
            converter = self.converter_resolver.identify(converter)
        except AliasError:
            self.logger.warning("Unknown converter: %s", converter)
        return converter


# section
# ======================================================================


@singledispatch
def _coerce_explicit(converter: Any, value: Any) -> Any:
    """Coerce given value using specified converter."""
    raise InvalidConverter(converter)


@_coerce_explicit.register(abc.Callable)
def _(converter: Callable, value: Any) -> Any:
    return converter(value)


@_coerce_explicit.register(str)
def _(converter: str, value: Any) -> Any:
    if "null" == converter:
        return value if value else None
    elif "bool" == converter:
        return bool(value)
    raise InvalidConverter(converter)


# section
# ======================================================================


def get_alias_null() -> Alias:
    return Alias(None, [None, NaN, "n/a", "na", "nil", "none", "null"])


def get_alias_bool() -> AliasResolver:
    return AliasResolver.build(
        {True: [True, "true"]},
        {False: [False, "false"]},
    )


def get_default_coercer() -> Coercer:
    return Coercer(
        converter_resolver=get_default_converter_resolver(),
        value_alias=get_default_value_aliases(),
    )


def get_default_converter_resolver() -> AliasResolver:
    resolver = AliasResolver.build(
        {"null": ["null", "None"]},
        {"bool": ["bool", "boolean"]},
        {int: ["int", "integer"]},
        {float: ["float", "double", "number"]},
        {json.loads: ["json"]},
    )
    return resolver


def get_default_value_aliases() -> AliasResolver:
    return AliasResolver.build(
        get_alias_null(),
        get_alias_bool(),
    )


# __END__
