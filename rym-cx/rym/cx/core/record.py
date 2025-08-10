#!/usr/bin/env python3
"""Define registrar records."""


from typing import Any, NamedTuple, Protocol
from uuid import UUID, uuid4

from .identifier import generate_uid


class RegisterRecord(Protocol):
    """Define a record protocol."""

    namespace: str
    value: Any
    uid: UUID

    @classmethod
    def new(cls, namespace: str, value: Any) -> "RegisterRecord":
        ...


class CatalogRecord(NamedTuple):
    """Aggregate attributes of a registered item.

    NOTE: KISS. We don't need the overhead of a dataclass for this.
    TODO: Consider using __hash__ instead of __name__.

    Generates unique namespace-based ID for each item.
    """

    namespace: str
    value: Any
    uid: UUID

    @classmethod
    def new(cls, namespace: str, value: Any) -> "CatalogRecord":
        """Create an instance."""
        uid = generate_uid(namespace, value)
        return cls(namespace=namespace, value=value, uid=uid)


class InventoryRecord(NamedTuple):
    """Aggregate attributes of a registered inventory item.

    Generates UUID for each item.
    """

    namespace: str
    value: Any
    uid: UUID

    @classmethod
    def new(cls, namespace: str, value: Any) -> "InventoryRecord":
        """Create an instance."""
        uid = uuid4()
        return cls(namespace=namespace, value=value, uid=uid)


# __END__
