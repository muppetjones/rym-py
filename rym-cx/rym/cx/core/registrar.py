#!/usr/bin/env python3
"""Define a registrar to track object definitions."""

import asyncio
import dataclasses as dcs
from collections import defaultdict
from collections.abc import Hashable
from functools import partial
from typing import Any, ClassVar, NamedTuple, Optional
from uuid import UUID

from .errors import InvalidStateError, NonUniqueValueError, UnregisteredValueError
from .identifier import generate_uid


class Record(NamedTuple):
    """Aggregate attributes of a registered item.

    NOTE: KISS. We don't need the overhead of a dataclass for this.
    TODO: Consider using __hash__ instead of __name__.
    """

    namespace: str
    value: Any
    uid: UUID

    @classmethod
    def new(cls, namespace: str, value: Any) -> "Record":
        """Create an instance."""
        uid = generate_uid(namespace, value)
        return cls(value=value, namespace=namespace, uid=uid)


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
        HOWEVER, if this is really meant to be used, we _need_ async. Define an async
        wrapper around add() and make the other methods async.

    Attributes:
        register: Store registered items. Mapping of {UID: record}.
        lookup: Store aliases of registered items. Provides a mapping from
            the alias and namespace to the UID.
        _lock: Class lock for async features. Do not use directly.
    """

    # NOTE: We could use more efficient data types for storage, e.g., deque,
    #   at the cost of additional lookup complexity. KISS for now.
    register: dict[UUID, Record] = dcs.field(default_factory=dict)
    lookup: dict[Any, dict[str, UUID]] = dcs.field(
        default_factory=partial(defaultdict, dict)
    )

    _lock: ClassVar[asyncio.Lock] = asyncio.Lock()

    async def add_async(self, namespace: str, value: Any) -> Record:
        """Add given item to the register.

        Same functionality as add(), but async. Locks the object.

        See also:
            add()
        """
        async with self._lock:
            # Lock to prevent race condition between checking and adding the item.
            self.add(namespace, value)

    def add(self, namespace: str, value: Any) -> Record:
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
        record = Record.new(namespace, value)

        # Prevent addition of items with name conflicts but ignore known items.
        existing = self.register.get(record.uid)
        if not existing:
            pass  # new addition; no action
        elif existing == record:
            pass  # duplicate; no action
        else:
            raise NonUniqueValueError(f"value exists in namespace: {record}")

        # Generate aliases for easier lookup
        # TODO: Consider using a singledispatch generator to build this.
        keys = [record.uid]
        if isinstance(value, Hashable):
            keys.append(value)
        if name := getattr(value, "__name__", str(value)):
            keys.extend([name, name.lower()])

        # Add the item to the register
        for key in keys:
            self.lookup[key][namespace] = record.uid
        self.register[record.uid] = record
        setattr(value, "__cx_uid__", record.uid)

        return record

    async def clear(self) -> None:
        """Clear registered items."""
        # NOTE: Use default_factory for safety.
        async with self._lock:
            self.lookup = Registrar.__dataclass_fields__["lookup"].default_factory()
            self.register = Registrar.__dataclass_fields__["register"].default_factory()

    async def get(self, value: Any, namespace: Optional[str] = None) -> Record:
        """Retrieve registered record associated with given input.

        Arguments:
            value: Used to lookup the record.
            namespace: The namespace to look in.
        Returns:
            Registered record.
        Raises:
            UnregisteredValueError(ValueError) if no matching record found.
            NonUniqueValueError(ValueError) if no unique match (namespace required).
        """
        matched = self.lookup.get(value)  # keep default as None
        uid = (matched or {}).get(namespace)

        # Rather than a complex set of try:except or nested conditionals,
        # order the conditionals to allow a sort of fall through.
        # NOTE: Ideally, a unique match w/o namespace would not be the last conditional,
        #   but we have to be sure we actually have matches first. Any other order
        #   would check something twice.
        msg = None
        error = None
        if uid:
            pass  # got what we need
        elif matched is None:
            msg = "unknown value"
            error = UnregisteredValueError
        elif not matched:
            msg = "orphaned value; rebuild lookup"
            error = InvalidStateError
        elif namespace:
            # i.e., given namespace, but no match
            msg = "value not in namespace"
            error = UnregisteredValueError
        elif len(matched) != 1:
            # i.e., no namespace, cannot differentiate
            msg = "multiple matches; namespace required"
            error = NonUniqueValueError
        else:
            # i.e., no namespace given but only one match
            uid = list(matched.values())[0]

        if not uid:
            # NOTE: Could check error or msg instead, but we only care if we have a uid.
            raise error(f"{msg} ({namespace}, {value})")  # EARLY EXIT: no match!

        try:
            return self.register[uid]
        except KeyError:
            msg = "unknown uid; rebuild lookup"
            raise InvalidStateError(f"{msg} ({namespace}, {value})")


# __END__
