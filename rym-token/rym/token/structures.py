#!/usr/bin/env python3
""".

"""

import dataclasses as dcs
import logging
from typing import Any, Callable, NamedTuple

LOGGER = logging.getLogger(__name__)


class TokenSpec(NamedTuple):
    type: str
    pattern: str
    handle: Callable[..., Any] = None
    subtype: Callable[[str], str] = None


@dcs.dataclass
class Token:
    type: str
    value: str
    line: int
    column: int


# __END__
