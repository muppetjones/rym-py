#!/usr/bin/env python3
""".

"""

import logging
from functools import singledispatch
from typing import Any, Callable, Iterable, Optional, Tuple, Union

LOGGER = logging.getLogger(__name__)


def get_safekey(key: Optional[Callable]) -> Callable:
    if not key:
        return _safekey

    def wrapper(value: Any) -> Tuple[int, str]:
        try:
            return (0, key(value))
        except Exception:
            return _safekey(value)

    return wrapper


@singledispatch
def _safekey(value: Any) -> Tuple[int, str]:
    return (20, str(value))


@_safekey.register(str)
def _(value: str) -> Tuple[int, str]:
    return (10, value)


@_safekey.register(int)
@_safekey.register(float)
def _(value: Union[int, float]) -> Tuple[int, str]:
    # will break with very large numbers, but not likely an issue
    # - with 64 bits, max int is 19 characters
    return (10, "{:64}".format(value))


def safesorted(iterable: Iterable, *, key=None, **kwargs) -> Iterable:
    """Return a new sorted list from items in iterable."""
    return sorted(iterable, key=get_safekey(key), **kwargs)


# __END__
