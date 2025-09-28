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

Wildcards can be used to access any element. A trailing asterisk will always
return the final value as is; in all other cases, the return value will be
a list of items.

>>> lpath.get(example, '*.*.bar')
[['baz']]
>>> lpath.get(example, '*.*.*')
[[['x', 'y', 'z'], 42], [{'bar': 'baz'}]]

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

    Wildcards:
        A single asterisk may be used as a wildcard to match any value.
        A trailing asterisk will return the final value as is; i.e., it doesn't
        really do much. When used in any other position, the return value will
        always be a list of the matched values.

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


# _get
# ======================================================================
# This set of dispatchers han


@singledispatch
def _get(key: Any, value: Any, delim: str) -> Any:
    """Dispatch based a single key or multiple."""
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


# _get_from
# ======================================================================


def _get_from(value: Any, parts: Deque[str]) -> Any:
    """Dispatch based on value.

    NOTE: Handles any key-specific logic.
    NOTE: The type of parts is handled via _get.
    """
    if not parts:
        return value
    key = parts.popleft()
    if key == "*":
        return _get_from_single_asterisk(value, parts)
    else:
        return _get_from_dispatch(value, parts, key=key)


@singledispatch
def _get_from_dispatch(value: Any, parts: Deque[str], *, key: str) -> Any:
    """Dispatch based on the value.

    NOTE: Should ONLY be called via _get_from. All key-specific logic is
        processed in that function.
    NOTE: Assume value is an object.
    """
    try:
        curr = getattr(value, key)
    except AttributeError as err:
        raise AttributeError(key) from err
    return _get_from(curr, parts)


@_get_from_dispatch.register(abc.Mapping)
def _(value: Mapping, parts: Deque[str], *, key: str) -> Any:
    return _get_from(value[key], parts)


@_get_from_dispatch.register(abc.Iterable)
def _(value: Iterable, parts: Deque[str], *, key: str) -> Any:
    """Dispatch where value is an iterable (and therefore)"""
    try:
        curr = value[int(key)]
    except IndexError:
        raise IndexError(key) from None
    return _get_from(curr, parts)


# _get_from_single_asterisk
# ======================================================================


def _get_from_single_asterisk(value: Any, parts: Deque[str]) -> Any:
    # NOTE: The asterisk has already been removed from "parts"
    if not parts:
        # NOTE: Return value as is if the asterisk was the last item.
        return value
    elif not value:
        # Edge case. We have parts, but no ability to go deeper.
        # NOTE: Stick to ValueError -- we don't know what was expected.
        partial_key = ".".join(parts)
        raise ValueError(f"failure to match after asterisk: *.{partial_key}")
    return list(_yield_from_single_asterisk(value, parts))


def _yield_from_single_asterisk(
    value: Mapping,
    parts: Deque[str],
) -> abc.Generator[Any, None, None]:
    itr = _get_iter(value)  # may raise
    errors = []
    matched_any = False
    for item in itr:
        try:
            yield _get_from(item, parts.copy())
        except (
            AttributeError,
            IndexError,
            KeyError,
            ValueError,
            TypeError,
        ) as err:
            # TODO: Use an exception group
            tb = TracebackException.from_exception(err)
            errors.append(tb)
        else:
            matched_any = True

    if errors and not matched_any:
        # NOTE: Stick to ValueError -- we don't know what was expected.
        partial_key = ".".join(parts)
        raise ValueError(f"failure to match after asterisk: *.{partial_key}")


# _get_iter
# ======================================================================
# Standardize iterable for asterisk feature


@singledispatch
def _get_iter(value: Any) -> Iterable:
    # NOTE: because we support object introspection, don't reject this
    return vars(value).values()  # may raise later


@_get_iter.register(str)
def _get_iter_err(value: Any) -> Iterable:
    raise TypeError("iterable or object with __dict__ expected for asterisk part")


@_get_iter.register(abc.Mapping)
def _(value: Mapping) -> Iterable:
    # NOTE: This ignores the keys, which probably isn't ideal. However, it's a
    #   reasonable concession to make for wild card matching.
    return value.values()


@_get_iter.register(abc.Iterable)
def _(value: Iterable) -> Iterable:
    return value


# __END__
