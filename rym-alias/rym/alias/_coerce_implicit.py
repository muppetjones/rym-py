#!/usr/bin/env python3
""".

"""

import logging
import re
from functools import singledispatch
from types import SimpleNamespace
from typing import Any, Optional

from ._aliasresolver import AliasResolver

LOGGER = logging.getLogger(__name__)


RX = None  # type: SimpleNamespace


def build_regex() -> SimpleNamespace:
    global RX
    if not RX:
        RX = SimpleNamespace(
            integer=re.compile(),
        )
    return RX


@singledispatch
def coerce_implicit(value: Any, alias: Optional[AliasResolver] = None) -> Any:
    """Naively detect type and convert.

    Implicit conversion assumes you've provided a string. If not, then
    the given value will be returned as is.

    Arguments:
        value: The thing to convert.
        alias: An AliasResolver
    Returns:
        The converted value.
    Raises:
        InvalidConversionError (ValueError) if unable to convert.
    See also:
        converter_names(...)
    """
    try:
        return alias.identify(value)
    except Exception:
        return value


# __END__
