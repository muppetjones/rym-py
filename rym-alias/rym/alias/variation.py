#!/usr/bin/env python3
"""Common variations for aliasing.

"""

import logging

LOGGER = logging.getLogger(__name__)


def deesser(value: str) -> str:
    """Remove any trailing 's' characters.

    NOTE: This transform is not recommended for forcing singular form.
        In English, too many plural words do not end in 's', e.g., 'moose';
        to many plural words have alternate spellings, e.g., 'remedies';
        and too many singular words end in 's', e.g., 'news'.
    """
    return value.rstrip("s")


def esser(value: str) -> str:
    """Add an 's' to the end of a word -- if there isn't one.

    NOTE: This transform is not recommended for forcing plural form.
        In English, too many plural words do not end in 's', e.g., 'moose';
        to many plural words have alternate spellings, e.g., 'remedies';
        and too many singular words end in 's', e.g., 'news'.
    """
    if value.endswith("s"):
        return value
    return f"{value}s"


def lower(value: str) -> str:
    """Convert to lowercase.

    NOTE: Compatible signature for alias transforms.
    """
    return value.lower()


def upper(value: str) -> str:
    """Convert to uppercase.

    NOTE: Compatible signature for alias transforms.
    """
    return value.upper()


# __END__
