#!/usr/bin/env python3
""".

"""

import logging

LOGGER = logging.getLogger(__name__)


def get_default_delimiter() -> str:
    """Return the default delimiter.

    Returns:
        The default delimiter.
    """
    return "."


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


_DELIMITER = get_default_delimiter()

# __END__
