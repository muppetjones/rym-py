#!/usr/bin/env python3
""".

"""

from collections import abc, deque
from functools import singledispatch
import logging
from traceback import TracebackException

from typing import Any, Deque, Iterable, Mapping, Union

LOGGER = logging.getLogger(__name__)


def get(value: Any, key: str) -> Any:
    parts = key.split(".")
    try:
        return _get(value, deque(parts))
    except (AttributeError, IndexError, KeyError) as err:
        tb = TracebackException.from_exception(err)
        missing = str(err).strip("'\"")
        idx = parts.index(missing) + 1
        raise tb.exc_type(".".join(parts[:idx])) from err
    except ValueError as err:
        raise ValueError(f"{err} (given={key})") from err


@singledispatch
def _get(value: Any, parts: Deque[str]) -> Any:
    if not parts:
        return value
    key = parts.popleft()
    try:
        curr = getattr(value, key)
    except AttributeError as err:
        raise AttributeError(key) from err
    return _get(curr, parts)


@_get.register(abc.Iterable)
def _(value: Iterable, parts: Deque[str]) -> Any:
    if not parts:
        return value
    key = int(parts.popleft())
    try:
        curr = value[key]
    except IndexError:
        raise IndexError(key) from None
    return _get(curr, parts)


@_get.register(abc.Mapping)
def _(value: Mapping, parts: Deque[str]) -> Any:
    if not parts:
        return value
    key = parts.popleft()
    return _get(value[key], parts)


# __END__
