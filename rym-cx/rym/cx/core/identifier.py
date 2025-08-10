#!/usr/bin/env python3
"""Generate unique identifiers."""

import hashlib
import logging
from functools import cache
from typing import Any
from uuid import UUID, uuid3

LOGGER = logging.getLogger(__name__)


@cache
def generate_namespace_hash(value: str) -> UUID:
    """Generate constant namespace UUID.

    UUID namespaces should be static, but we want to support modularity.
    In an actual use case, we'll want to require predefined namespaces, but
    for now, this is sufficient.

    Arguments:
        value: String namespace.
    Returns:
        UUID for the namespace.
    """
    try:
        # Use shake to allow custom digest size
        ns_hash = hashlib.shake_128(value.encode())
    except AttributeError:
        raise TypeError(f"expects str, not {type(value)}")
    return UUID(bytes=ns_hash.digest(16))


def generate_uid(namespace: str, value: Any) -> UUID:
    """Generate a UUID3 from the given value within the given namespace.

    Arguments:
        namespace: The registered namespace the item belongs to.
        value: The object or instance to generate a uuid for.
            Should be a class or a string.
    Returns:
        A UUID3.
    Raises:
        None.
        TODO: Better type checking.
    """
    name = getattr(value, "__name__", str(value))
    ns = generate_namespace_hash(namespace)
    return uuid3(ns, name)


# __END__
