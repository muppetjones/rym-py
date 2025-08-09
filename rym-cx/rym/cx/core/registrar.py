#!/usr/bin/env python3
"""Define a registrar to track object definitions."""

import dataclasses as dcs
import hashlib
from collections import defaultdict
from collections.abc import Hashable
from functools import cache, partial
from typing import Any, NamedTuple, Optional
from uuid import UUID, uuid3

from .errors import InvalidStateError, NonUniqueValueError, UnregisteredValueError


@cache
def generate_namespace_hash(value: str) -> UUID:
    """Generate constant namespace UUID.

    UUID namespaces should be static, but we want to support modularity.
    In an actual use case, we'll want to require predefined namespaces, but
    for now, this is sufficient.
    """
    # Use shake to allow custom digest size
    ns_hash = hashlib.shake_128(value.encode())
    return UUID(bytes=ns_hash.digest(16))


class Record(NamedTuple):
    """Aggregate attributes of a registered item.

    NOTE: KISS. We don't need the overhead of a dataclass for this.
    TODO: Consider using __hash__ instead of __name__.
    """

    item: Any
    namespace: str
    uid: UUID

    @classmethod
    def new(cls, item: Any, namespace: str) -> "Record":
        """Create an instance."""
        uid = cls.generate_uid(namespace, item)
        return cls(item=item, namespace=namespace, uid=uid)

    @staticmethod
    def generate_uid(namespace: str, value: Any) -> UUID:
        """Return a UUID3 from the given values.

        Arguments:
            item: A class or name of a class.
            namespace: The registered namespace the item belongs to.
        Returns:
            A UUID3.
        Raises:
            None.
            TODO: Better type checking.
        """
        name = getattr(value, "__name__", str(value))
        ns = generate_namespace_hash(namespace)
        return uuid3(ns, name)


@dcs.dataclass
class Registrar:
    """Store and index an item registry.

    TODO: Add more here.
    """

    # NOTE: We could use more efficient data types for storage, e.g., deque,
    #   at the cost of additional lookup complexity. KISS for now.
    register: dict[UUID, Record] = dcs.field(default_factory=dict)
    lookup: dict[Any, dict[str, UUID]] = dcs.field(
        default_factory=partial(defaultdict, dict)
    )

    def add(self, value: Any, namespace: str) -> Record:
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
        record = Record.new(value, namespace)

        # Prevent addition of items with name conflicts but ignore known items.
        existing = self.register.get(record.uid)
        if not existing:
            pass  # new addition; no action
        elif existing == record:
            pass  # duplicate; no action
        else:
            raise NonUniqueValueError(f"Value already exists in namespace: {record}")

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
        value.__uid__ = record.uid

        return record

    def get(self, value: Any, namespace: Optional[str] = None) -> Record:
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
        #   but we have to be sure we actually have matches first. Any other order,
        #   and we'd be checking something twice.
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
            raise error(f"{msg} ({value}, {namespace})")  # EARLY EXIT: no match!

        try:
            return self.register[uid]
        except KeyError:
            msg = "unknown uid; rebuild lookup"
            raise InvalidStateError(f"{msg} ({value}, {namespace})")


# __END__
