#!/usr/bin/env python3
"""
Explicit type coercion suite
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> from rym.alias import safe_bool, safe_int, coerce_explicit
>>> safe_bool('FALSE')
False
>>> safe_int('3.14')
3
>>> coerce_explicit('false', 'bool')
False
>>> coerce_explicit('false', bool, use_safe=False)
True

Messy data is a constant. This module aims to simplify data cleanup and stay
explicit. It is primarily intended for use when loading data from a tabular
format without explicit types, like CSV.

"""

import json
import logging
from collections import abc
from functools import partial, singledispatch
from typing import (
    Any,
    Callable,
    Generator,
    Hashable,
    Iterable,
    Mapping,
    Optional,
    Tuple,
    Union,
)

from ._alias import Alias, AliasError
from ._aliasresolver import AliasResolver
from ._coerce_errors import CoercionError, InvalidConverterError

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

# corerce explicit
# ======================================================================


def coerce_explicit(
    type_: Union[str, Callable],
    value: Any,
    use_safe: bool = True,
    _resolve_type: Optional[Callable] = None,
    **kwargs,
) -> Any:
    """Coerce given value to given type.

    Arguments:
        type_: Name, alias or callable
        value: Thing to coerce
        use_safe: If True, will perform safe coercions where possible.
        **kwargs: Passed to converter
    Returns:
        Coerced value.
    Raises:

    """
    _resolve_type = _resolve_type or resolve_type
    converter = _resolve_type(type_, use_safe=use_safe)
    return converter(value, **kwargs)


# resolve types
# ----------------------------------


@cache
def resolve_type(
    value: Union[str, Callable],
    use_safe: bool = True,
    _resolver: Optional[AliasResolver] = None,
    _safe_resolver: Optional[AliasResolver] = None,
) -> Callable:
    """Return callable for given value.

    Arguments:
        value: Alias or callable
    Returns:
        Callable
        NOTE: If given value is callable, it will be returned as is.
    Raises:
        InvalidConverterError if unknown converter requested.
    """
    type_ = _resolve_type(value, _resolver=_resolver)  # may raise
    if use_safe:
        _safe_resolver = _safe_resolver or get_safe_type_resolver()
        type_ = _safe_resolver.identify(type_, type_)
    return type_


@singledispatch
def _resolve_type(
    value: Any,
    _resolver: Optional[AliasResolver] = None,
) -> Callable:
    """Coerce given value using specified converter."""
    if value is None:
        return None
    raise InvalidConverterError(value)


@_resolve_type.register(abc.Callable)
def _(
    value: Callable,
    _resolver: Optional[AliasResolver] = None,
) -> Callable:
    return value


@_resolve_type.register(str)
def _(
    value: str,
    _resolver: Optional[AliasResolver] = None,
) -> Callable:
    _resolver = _resolver or get_type_resolver()  # type: AliasResolver
    return _resolver.identify(value)


# resolvers
# ======================================================================


def _yield_from(value: Iterable) -> Generator[Any, None, None]:
    yield from value


@cache
def get_alias_bool() -> AliasResolver:
    return AliasResolver.build(
        {True: [True, "true"]},
        {False: [False, "false"]},
    )


@cache
def get_alias_iterable() -> AliasResolver:
    return AliasResolver.build(
        {iter: ["iter"]},
        {_yield_from: ["generator", "yield"]},
        {list: ["list"]},
        {set: ["set"]},
        {tuple: ["tuple"]},
    )


@cache
def get_alias_null() -> Alias:
    return Alias(None, [None, NaN, "n/a", "na", "nil", "none", "null", "", "NaN"])


@cache
def get_type_resolver() -> AliasResolver:
    """Return an AliasResolver for data types (cached)."""
    return AliasResolver.build(
        {None: ["null", "None", None]},
        {bool: ["bool", "boolean"]},
        {int: ["int", "integer"]},
        {float: ["float", "double", "number", "scientific"]},
        {json.loads: ["json.loads"]},
        {json.dumps: ["json.dumps"]},
        {str: ["str", "string"]},
        get_alias_iterable(),
    )


@cache
def get_safe_type_resolver() -> AliasResolver:
    """Return an AliasResolver for safe data types (cached).

    This resolver maps existing types to their safe counterparts where available.
    """
    return AliasResolver.build(
        {safe_int: [int]},
        {safe_bool: [bool]},
        {safe_null: [None]},
        {json.loads: [json.loads]},  # TODO: Make a safe decoder
        {json.dumps: [json.dumps]},  # TODO: Make a safe encoder
        {partial(safe_iterable, itertype=tuple): [tuple]},
        {partial(safe_iterable, itertype=set): [set]},
        {partial(safe_iterable, itertype=list): [list]},
    )


# Safe Types
# ======================================================================
#   These functions are intended to support edge cases from accidental
#   or careless output, e.g., literal "TRUE" or "FALSE" strings
#
# NOTE: The boolean, iterable, and null converters will _not_ raise.

# bool
# ----------------------------------


def safe_bool(value: Any, **kwargs) -> bool:
    """Return a boolean from the given value.

    Arguments:
        value: Value to coerce.
        **kwargs: Ignored.
    Returns:
        Coerced value.
    Raises:
        InvalidConversionError (ValueError) if unsupported type.
    """
    return _safe_bool(value)


@singledispatch
def _safe_bool(
    value: Any,
    _alias: Optional[AliasResolver] = None,
) -> Union[None, Any]:
    return bool(value)


@_safe_bool.register(str)
def _(
    value: str,
    _alias: Optional[AliasResolver] = None,
) -> Union[Any, None]:
    alias = _alias or get_alias_bool()
    try:
        return alias.identify(value)
    except AliasError:
        return bool(value)


# integer
# ----------------------------------


def safe_int(value: Any, **kwargs) -> int:
    """Return integer.

    Arguments:
        value: Value to coerce.
        **kwargs: Ignored.
    Returns:
        Coerced value.
    Raises:
        InvalidConversionError (ValueError) if unsupported type.
    """
    try:
        return int(float(value))
    except (TypeError, ValueError) as err:
        raise CoercionError(f"invalid object: {value}") from err


# iterable
# ----------------------------------


def safe_iterable(
    value: Any,
    itertype: Optional[Callable] = None,
    **kwargs,
) -> Iterable[Any]:
    """Return iterable from given.

    Arguments:
        value: Value to coerce.
        **kwargs: Ignored.
    Returns:
        Iterable of given.
    Raises:
        None.
    """
    itertype = get_alias_iterable().identify(itertype, itertype) or list
    return itertype(_safe_iterable(value))


@singledispatch
def _safe_iterable(value: Any) -> Iterable[Any]:
    return [value]


@_safe_iterable.register(str)
def _(value: str) -> Iterable[str]:
    return [value]


@_safe_iterable.register(abc.Iterable)
def _(value: Iterable[Any]) -> Iterable[Any]:
    return value


@_safe_iterable.register(abc.Mapping)
def _(value: Mapping) -> Iterable[Tuple[Hashable, Any]]:
    return value.items()


# json
# ----------------------------------
# TODO: Add safe json load/dump


# null
# ----------------------------------


def safe_null(
    value: Any,
    _alias: Optional[AliasResolver] = None,
    **kwargs,
) -> Union[None, Any]:
    """Return None if value is acceptable null value. Return given otherwise.

    NOTE: Null-like does not mean false-y.

    Arguments:
        value: Value to coerce.
        **kwargs: Ignored.
    Returns:
        Coerced value.
    Raises:
        None.
    """
    return _safe_null(value, _alias=_alias)


@singledispatch
def _safe_null(
    value: Any,
    _alias: Optional[AliasResolver] = None,
) -> Union[None, Any]:
    return value  # may be None


@_safe_null.register(str)
def _(
    value: str,
    _alias: Optional[AliasResolver] = None,
) -> Union[Any, None]:
    alias = _alias or get_alias_null()
    try:
        return alias.identify(value)
    except AliasError:
        return value


# __END__
