#!/usr/bin/env python3
"""
Remove any nested index, item, or attribute
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> from types import SimpleNamespace
>>> from rym import lpath
>>> example = [
...    {"a": list('xyz'), "b": 42},
...    SimpleNamespace(foo={"bar": "baz"}),
... ]
>>> lpath.pop(example, '1.foo.bar')
'baz'
>>> lpath.get(example, '1.foo.bar')
Traceback (most recent call last):
    ...
KeyError: '1.foo.bar'

"""

import logging
from collections import abc
from functools import singledispatch
from typing import Any, Iterable, Mapping, Optional, Tuple, Union

from ._delim import get_delimiter
from ._get import get

LOGGER = logging.getLogger(__name__)


def pop(
    instance: Union[object, Iterable, Mapping],
    key: str,
    *,
    delim: Optional[str] = None,
) -> Any:
    """Remove and return value at given key.

    Arguments:
        instance: An object that supports item retrieval.
        key: Delimited lookup string.
    Returns:
        The removed value.
    Raises:
        AttributeError, KeyError, IndexError: If no item exists at that key.
        TypeError for unsupported input.
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

    return _pop_from(target, name)


@singledispatch
def _pop_from(instance: Any, key: str) -> Any:
    retval = getattr(instance, key)
    delattr(instance, key)
    return retval


@_pop_from.register(abc.Generator)
@_pop_from.register(abc.Iterable)
@_pop_from.register(str)
def _(instance: Union[Tuple, str], key: str) -> Any:
    raise TypeError(f"'pop' not supported for {type(instance)}")


@_pop_from.register(abc.MutableSequence)
def _(instance: Iterable[Any], key: str) -> Any:
    retval = instance.pop(int(key))
    return retval


@_pop_from.register(abc.Mapping)
def _(instance: Mapping[str, Any], key: str) -> Any:
    retval = instance[key]
    del instance[key]
    return retval


# __END__
