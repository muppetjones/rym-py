#!/usr/bin/env python3
""".

"""

import logging

LOGGER = logging.getLogger(__name__)


def get_default_delimiter() -> str:
    return "."


def get_delimiter() -> str:
    global _DELIMITER
    return _DELIMITER


def reset_delimiter() -> None:
    global _DELIMITER
    _DELIMITER = get_default_delimiter()


def set_delimiter(value: str) -> None:
    global _DELIMITER
    _DELIMITER = value


_DELIMITER = get_default_delimiter()

# __END__
