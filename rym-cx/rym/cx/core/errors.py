#!/usr/bin/env python3
"""Define custom error types."""


class InvalidStateError(RuntimeError):
    """Raise if the registry is in an invalid state.

    NOTE: e.g., some assumption has not been met, data appears corrupted.
    """


class UnregisteredValueError(ValueError):
    """Raise if given value is not associated with a registered item."""


class NonUniqueValueError(ValueError):
    """Raise if value is insufficient to resolve to a single, registered item."""


# __END__
