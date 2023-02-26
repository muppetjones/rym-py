#!/usr/bin/env python3
"""
Set any nested index, item, or attribute
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> from types import SimpleNamespace
>>> from rym import lpath
>>> example = [
...    {"a": list('xyz'), "b": 42},
...    SimpleNamespace(foo={"bar": "baz"}),
... ]
>>> lpath.set(example, '1.foo.bar', 'nope')
>>> example[1].foo['bar']
'nope'

You can also add new keys with mappings:

>>> lpath.set(example, '0.c', 'u l8r')
>>> example[0]['c']
'u l8r'

**Recommended: Just use `lpath.get`**

>>> lpath.get(example, '0.a').append('aa')
>>> lpath.get(example, '0.a.3')
'aa'
>>> setattr(lpath.get(example, '1'), 'baz', 42)
>>> lpath.get(example, '1.baz')
42


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
    """Set value at specified key on the instance.

    Arugments:
        instance: The object to set the value on.
        key: The name or index on the instance.
        value: The value to set.
    Returns:
        None.
    Raises:
        AttributeError, KeyError, or IndexError if key does not exist.
    """
    _ = getattr(instance, key)  # raise if key not available
    setattr(instance, key, value)
    _ = getattr(instance, key)  # raise if key not set


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
