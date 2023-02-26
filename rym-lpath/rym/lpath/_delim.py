#!/usr/bin/env python3
"""
Use a different delimiter
^^^^^^^^^^^^^^^^^^^^^^^^^

>>> from types import SimpleNamespace
>>> from rym import lpath
>>> example = [
...    {"a": list('xyz'), "b": 42},
...    SimpleNamespace(foo={"bar": "baz"}),
... ]
>>> lpath.get(example, '1/foo/bar', delim='/')
'baz'

Or set it globally

>>> lpath.set_delimiter('/')
>>> lpath.get_delimiter()
'/'
>>> lpath.get(example, '1/foo/bar')
'baz'

If you change your mind, it's easy enough to go back to the default

>>> lpath.get_default_delimiter()
'.'
>>> lpath.reset_delimiter()
>>> lpath.get(example, '1.foo.bar')
'baz'


"""

import logging

LOGGER = logging.getLogger(__name__)
__DEFAULT_DELIMITER = "."
_DELIMITER = __DEFAULT_DELIMITER


def get_default_delimiter() -> str:
    """Return the default delimiter.

    Returns:
        The default delimiter.
    """
    return __DEFAULT_DELIMITER


def get_delimiter() -> str:
    """Return the current delimiter."""
    global _DELIMITER
    return _DELIMITER


def reset_delimiter() -> None:
    """Reset to the default delimiter."""
    global _DELIMITER
    _DELIMITER = get_default_delimiter()


def set_delimiter(value: str) -> None:
    """Set the lpath delimeter.

    Args:
        value (str): The delimiter to use.
    Returns:
        None.
    """
    global _DELIMITER
    _DELIMITER = value


# __END__
