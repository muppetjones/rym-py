#!/usr/bin/env python3
"""Coerce values.

"""

import dataclasses as dcs
import logging
from typing import Any, Callable, Optional

from ._aliasresolver import AliasResolver

LOGGER = logging.getLogger(__name__)


@dcs.dataclass
class Coercer:
    converter_resolver: AliasResolver

    def __call__(self, value: Any, converter: Optional[Callable] = None) -> Any:
        return self.coerce(value, converter=converter)

    def coerce(self, value: Any, converter: Optional[Callable] = None) -> Any:
        """Coerce the given value to a data type.

        Implicit conversion assumes you've provided a string. If not, then
        the given value will be returned as is.

        Arguments:
            value: The thing to convert.
            converter: The method used for conversion. If not given, will
                use implicit conversion IFF given value is a string.
                May be a string value.
        Returns:
            The converted value.
        Raises:
            InvalidConversionError (ValueError) if unable to convert.
        See also:
            converter_names(...)
        """


def get_default_converter_resolver() -> AliasResolver:
    return AliasResolver.build()


def get_default_coercer() -> Coercer:
    return Coercer(converter_resolver=get_default_converter_resolver())


# __END__
