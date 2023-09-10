#!/usr/bin/env python3
"""
Access any nested index, item, or attribute
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> from types import SimpleNamespace
>>> from rym import lpath
>>> example = [
...    {"a": list('xyz'), "b": 42},
...    SimpleNamespace(foo={"bar": "baz"}),
... ]
>>> lpath.get(example, '1.foo.bar')
'baz'

Use a default value if the item doesn't exist


>>> lpath.get(example, 'hello.world', default='oops')
'oops'

Or, specify multiple options and get the first match

>>> lpath.get(example, ['hello.world', '0.a.1'])
'y'

"""

import logging
from collections import abc, deque
from functools import singledispatch
from traceback import TracebackException
from typing import Any, Deque, Iterable, Mapping, Optional, Union

from ._delim import get_delimiter

LOGGER = logging.getLogger(__name__)
__DEFAULT = "any random string that is unlikely to be provided"


class InvalidKey(ValueError):
    """Raise if given an unsupported key type."""


def get(
    value: Any,
    key: Union[str, Iterable[str]],
    default: Optional[Any] = __DEFAULT,
    *,
    delim: Optional[str] = None,
) -> Any:
    """Return the value of the property found at the given key.

    Arguments:
        value: An object, iterable, or mapping
        key: A string indicating the path to the value.
            An itererable of strings may be provided. The first match will be returned.
        delim: Specify the delimiter. Default is '.'.
    Returns:
        The property found.
    Raises:
        AttributeError, IndexError, or KeyError if the requested key could not be found.
        ValueError if an invalid key given.
    """
    delim = delim or get_delimiter()
    try:
        return _get(key, value, delim)
    except InvalidKey:
        raise
    except (AttributeError, KeyError, IndexError, ValueError):
        if __DEFAULT != default:
            return default
        raise


@singledispatch
def _get(key: Any, value: Any, delim: str) -> Any:
    raise InvalidKey(
        f"invalid key: {key}, ({type(key)}); expected str or list of str"
    )


@_get.register(str)
def _(key: str, value: str, delim: str) -> Any:
    parts = key.split(delim)
    try:
        return _get_from(value, deque(parts))
    except (AttributeError, IndexError, KeyError) as err:
        tb = TracebackException.from_exception(err)
        missing = str(err).strip("'\"")
        idx = parts.index(missing) + 1
        raise tb.exc_type(".".join(parts[:idx])) from err
    except ValueError as err:
        raise ValueError(f"{err} (given={key})") from err


@_get.register(abc.Iterable)
def _(key: Iterable[str], value: str, delim: str) -> Any:
    for k in key:
        try:
            parts = k.split(delim)
            return _get_from(value, deque(parts))
        except (AttributeError, IndexError, KeyError, ValueError):
            continue
    raise KeyError(f"no matches: {key}")


@singledispatch
def _get_from(value: Any, parts: Deque[str]) -> Any:
    if not parts:
        return value
    key = parts.popleft()
    try:
        curr = getattr(value, key)
    except AttributeError as err:
        raise AttributeError(key) from err
    return _get_from(curr, parts)


@_get_from.register(abc.Iterable)
def _(value: Iterable, parts: Deque[str]) -> Any:
    if not parts:
        return value
    key = int(parts.popleft())
    try:
        curr = value[key]
    except IndexError:
        raise IndexError(key) from None
    return _get_from(curr, parts)


@_get_from.register(abc.Mapping)
def _(value: Mapping, parts: Deque[str]) -> Any:
    if not parts:
        return value
    key = parts.popleft()
    return _get_from(value[key], parts)


# __END__
