#!/usr/bin/env python3
""".

"""

from collections import abc, deque
from functools import singledispatch
import logging
from traceback import TracebackException

from typing import Any, Deque, Iterable, Mapping, Optional, Union

from ._delim import get_delimiter

LOGGER = logging.getLogger(__name__)


def get(value: Any, key: str, delim: Optional[str] = None) -> Any:
    delim = delim or get_delimiter()
    return _get(key, value, delim)


@singledispatch
def _get(key: Any, value: Any, delim: str) -> Any:
    raise ValueError(f"invalid key: {key}, ({type(key)}); expected str or list of str")


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
        except (AttributeError, IndexError, KeyError) as err:
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
