#!/usr/bin/env python3
"""Define a registrar to track object definitions."""

import asyncio
import dataclasses as dcs
from collections import defaultdict
from collections.abc import Callable, Hashable
from functools import partial, singledispatchmethod
from typing import Any, ClassVar, Generator, Optional, TypeVar
from uuid import UUID

from .errors import (
    InvalidNamespaceError,
    NonUniqueValueError,
    UnregisteredAssetError,
    UnregisteredNamespaceError,
)
from .record import CatalogRecord, RegisterRecord

T = TypeVar("T")


@dcs.dataclass
class Registrar:
    """Store and index an item registry.

    NOTE: Registered items _should_ be classes.
    TODO: Add "remove" function. Removing from lookup adds complexity.
    NOTE: At first glance, this class seems like a good target for async functionality:
        Just lock when adding or clearing, and you're good go. However, the registrar
        tracks the creation of classes not instances. Classes are registered during
        import, and should be fully loaded prior to execution of the main program. As
        such, the added complexity likely isn't worth it -- at least for add().
        Unfortunately, one of the lightest ways to allow auto registration of new
        inventory instances is to use __post_init__, which isn't async.
        HOWEVER, if this is really meant to be usable, we'll need async for some cases.
        For now, define an asyncwrapper around add() and make the other methods async.

    Attributes:
        register: Store registered items. Mapping of {UID: record}.
        lookup: Namespace lookup. Nothing too fancy.
        label: String used to differentiate between different registrars.
            Recommendation: Do not touch.
        _lock: Class lock for async features. Do not use directly.
    """

    # NOTE: We could use more efficient data types for storage, e.g., deque,
    #   at the cost of additional lookup complexity. KISS for now.
    register: dict[UUID, RegisterRecord[T]] = dcs.field(default_factory=dict)
    lookup: dict[Any, dict[str, UUID]] = dcs.field(
        default_factory=partial(defaultdict, list)
    )
    label: str = "reg"
    _Record: Callable = CatalogRecord

    _lock: ClassVar[asyncio.Lock] = asyncio.Lock()

    # property
    # ----------------------------------

    @property
    def namespace_tag(self) -> str:
        return f"__cx_{self.label}_namespace__"

    @property
    def uid_tag(self) -> str:
        return f"__cx_{self.label}_uid__"

    # add
    # ----------------------------------

    async def add_async(self, namespace: str, value: Any) -> RegisterRecord:
        """Add given item to the register.

        Same functionality as add(), but async. Locks the object.

        See also:
            add()
        """
        async with self._lock:
            # Lock to prevent race condition between checking and adding the item.
            self.add(namespace, value)

    @singledispatchmethod
    def add(self, namespace: str, value: T) -> RegisterRecord:
        """Add given item to the register.

        TODO: Use rym.alias.AliasResolver.
        TODO: Add support for default namespace.

        Arguments:
            value: The item to add.
            namespace: The namspace the value is associated with.
        Returns:
            A record of the item.
        Raises:
            NonUniqueValueError (ValueError) if the (value, namespace) are
            already registered.
        """
        raise InvalidNamespaceError(f"must be hashable or class: {namespace}")

    @add.register
    def _(self, namespace: Callable, value: T) -> RegisterRecord:
        """Dispatch for callable namespace lookup."""
        return self._add_hashable(namespace.__name__, value)

    @add.register
    def _add_hashable(self, namespace: Hashable, value: T) -> list[T]:
        """Dispatch for callable hashable lookup."""
        record = (self._Record).new(namespace, value)

        # Prevent addition of items with name conflicts but ignore known items.
        existing = self.register.get(record.uid)
        if not existing:
            pass  # new addition; no action
        elif existing == record:
            return  # EARLY EXIT: duplicate
        else:
            raise NonUniqueValueError(f"value exists in namespace: {record}")

        # Add the item to the register
        self.register[record.uid] = record
        self.lookup[namespace].append(record.uid)

        # Tag the item
        setattr(value, self.uid_tag, record.uid)
        setattr(value, self.namespace_tag, record.namespace)

        return record

    # clear
    # ----------------------------------

    async def clear_async(self) -> None:
        """Clear registered items."""
        async with self._lock:
            self.clear()

    def clear(self) -> None:
        """Clear registered items."""
        # NOTE: Use default_factory for safety.
        self.lookup = Registrar.__dataclass_fields__["lookup"].default_factory()
        self.register = Registrar.__dataclass_fields__["register"].default_factory()

    # yield_by_id
    # ----------------------------------

    async def get_by_uid(self, *args: UUID) -> Generator[T, None, None]:
        """Return asset registered with givien uid.

        Arguments:
            *args: One or more UUIDs
        Returns:
            A tuple of the registered assets.
        Raises:
            UnregisteredAssetError if unknown ID given.
        """
        record = [(x, self.register.get(x)) for x in args]
        unknown = [x for x, y in record if not y]
        if unknown:
            raise UnregisteredAssetError(f"unknown uid: {unknown}")
        return [y.value for _, y in record if y]

    # get_by_namespace
    # ----------------------------------

    @singledispatchmethod
    async def get_by_namespace(self, namespace: Optional[str] = None) -> list[T]:
        """Retrieve registered record associated with given input.

        Arguments:
            namespace: The namespace to retrieve items from
        Returns:
            Registered record.
        Raises:
            UnregisteredNamespaceError(ValueError) if no matching namespace
            InvalidNamespaceError(ValueError) if namespace is invalid
        """
        raise InvalidNamespaceError(f"must be hashable or class: {namespace}")

    @get_by_namespace.register
    async def _(self, namespace: Callable) -> list[T]:
        """Dispatch for callable namespace lookup."""
        return await self._get_by_namespace_hashable(namespace.__name__)

    @get_by_namespace.register
    async def _get_by_namespace_hashable(self, namespace: Hashable) -> list[T]:
        """Dispatch for hashable namespace lookup."""
        if namespace not in self.lookup:
            raise UnregisteredNamespaceError(f"{namespace}; register items first")

        ids = self.lookup[namespace]
        items = [self.register[id_].value for id_ in ids]
        return items


# __END__
