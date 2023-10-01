#!/usr/bin/env python3
"""
Coerce values.
^^^^^^^^^^^^^^

Implicit type conversion from strings.

>>> from rym.alias import coerce
>>> coerce('null')
None
>>> coerce('1.24')
1.24
>>> coerce('["a", false]')
["a", False]
>>> coerce('true')
True
>>> coerce('1985-10-26T09:22:01.234567Z')
datetime()

"""

import dataclasses as dcs
import logging
from typing import Any, Callable, Optional, Union

from ._coerce_explicit import coerce_explicit
from ._coerce_implicit import coerce_implicit

try:
    from functools import cache
except ImportError:  # pragma: no cover
    from functools import lru_cache

    cache = lru_cache(maxsize=None)


LOGGER = logging.getLogger(__name__)
_DEFAULT = __file__


@dcs.dataclass
class Coercer:
    """Data type converter."""

    explicit: Callable = coerce_explicit
    implicit: Callable = coerce_implicit
    logger: logging.Logger = None

    def __post_init__(self):
        self.logger = self.logger or logging.getLogger(__name__)

    def __call__(
        self,
        value: Any,
        type_: Optional[Union[str, Callable]] = _DEFAULT,
        **kwargs,
    ) -> Any:
        return self.coerce(value, type_=type_, **kwargs)

    def coerce(
        self,
        value: Any,
        type_: Optional[Union[str, Callable]] = _DEFAULT,
        **kwargs,
    ) -> Any:
        """Coerce given value

        Args:
            value: Thing to coerce.
            type_: Optional coercion type if known
            logger: Optional logger (easier for testing)
            **kwargs: Passed to coercion functions
        Returns:
            Any: _description_
        See Also:
            coerce_explicit
            coerce_implicit
        """
        if _DEFAULT != type_:
            return self.explicit(type_, value, **kwargs)
        else:
            return self.implicit(value, **kwargs)


# # section
# # ======================================================================


def get_default_coercer() -> Coercer:
    """Return an instance of the default coercer."""
    return Coercer()


# __END__
