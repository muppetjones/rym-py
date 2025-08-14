#!/usr/bin/env python3
"""Define custom error types."""


class InvalidStateError(RuntimeError):
    """Raise if the registry is in an invalid state.

    NOTE: e.g., some assumption has not been met, data appears corrupted.
    """


class UnregisteredNamespaceError(ValueError):
    """Raise if unknown namespace."""


class InvalidNamespaceError(ValueError):
    """Raise if namespace is not valid."""


class NonUniqueValueError(ValueError):
    """Raise if value is insufficient to resolve to a single, registered item."""


class UnregisteredAssetError(ValueError):
    """Raise for issues related to registrar lookup for unregistered asset."""


# __END__
