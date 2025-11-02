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

**Recommended: Just use `lpath.get` for nested objects.**

>>> lpath.get(example, '0.a').append('aa')
>>> lpath.get(example, '0.a.3')
'aa'
>>> setattr(lpath.get(example, '1'), 'baz', 42)
>>> lpath.get(example, '1.baz')
42

**Backwards Compatability**

The `lpath` module is expected to be used directly rather than importing individual
functions, e.g., `lpath.set`. This convention avoids any name collisions while
being explicit. To minimize risk if the function is imported directly, the function
name was changed to `set_value` in v1.0.0. The alias `lpath.set` is maintained
and will not be removed.
"""

import logging
import warnings
from collections import abc
from functools import singledispatch
from typing import Any, Iterable, Mapping, Optional, Union

from ._delim import get_delimiter
from ._get import get_value
from .errors import unified_item_access_error_handler

LOGGER = logging.getLogger(__name__)

# Backwards compatibility
# ======================================================================


def set(
    instance: Union[object, Iterable, Mapping],
    key: str,
    value: Any,
    *,
    delim: Optional[str] = None,
) -> None:
    """DEPRECATED: Use set_value.

    NOTE: This function name causes a collision with the builtin "set".
        Because lpath is intended to be used directly as a module, e.g., lpath.set,
        this collision should not be relevant, but it's safer to do rename it this
        way.

    See also:
        set_value.
    """
    msg = (
        "rympy.lpath._set.set is deprecated and is not indended to be used directly",
        "Please use via 'lpath.set' or use 'set_value' directly.",
    )
    warnings.warn(" ".join(msg))
    return set_value(instance, key, value, delim=delim)


# Set value
# ======================================================================


@unified_item_access_error_handler
def set_value(
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
        target = get_value(instance, parent, delim=delim)
    else:
        target = instance

    return _set_to(target, name, value)


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
