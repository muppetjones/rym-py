#!/usr/bin/env python3
""".

"""

import logging
from collections import abc
from functools import singledispatch
from typing import Any, Iterable, Mapping, Optional, Union

from ._delim import get_delimiter
from ._get import get

LOGGER = logging.getLogger(__name__)


def set(
    instance: Union[object, Iterable, Mapping],
    key: str,
    value: Any,
    *,
    delim: Optional[str] = None,
) -> None:
    """Set value of the item at the given path.

    Will add keys to existing mappings, but cannot add attributes to
    objects or elements to lists.

    Args:
        instance: A mutable object, iterable, or mapping.
        key: The delimiter-separated path to the target.
        value: The value to apply.
    Returns:
        None.
    Raises:
        AttributeError, IndexError, or KeyError if the path does not exist.
        TypeError if unable to set the value at the given key.
    """
    delim = delim or get_delimiter()
    try:
        *parts, name = key.split(delim)
    except AttributeError:
        raise TypeError(f"key must be a string, not {type(key)}")

    if parts:
        parent = delim.join(parts)
        target = get(instance, parent, delim=delim)
    else:
        target = instance

    _set_to(target, name, value)


@singledispatch
def _set_to(instance: Any, key: str, value: Any) -> None:
    a = getattr(instance, key)
    setattr(instance, key, value)
    b = getattr(instance, key)


@_set_to.register(str)
def _(instance: str, key: str, value: Any) -> None:
    raise TypeError('"set" does not support item assignment for "str"')


@_set_to.register(abc.Iterable)
def _(instance: Iterable, key: str, value: Any) -> None:
    index = int(key)
    instance[index] = value


@_set_to.register(abc.Mapping)
def _(instance: Mapping, key: str, value: Any) -> None:
    instance[key] = value


# __END__
