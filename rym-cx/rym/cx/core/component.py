#!/usr/bin/env python3
"""."""


import itertools
from collections.abc import Callable
from typing import Optional, Protocol, TypeVar
from uuid import UUID

from rym.cx.core import _inventory

from .decorator import add_to_catalog

T = TypeVar("T")
_ENTITY_UID_TAG = "__cx_entity_uid__"


class Component(Protocol):
    entity_id: UUID


def register_as_component(klass: Optional[T] = None) -> T:
    """Decorate a component class.

    Example:
        >>> from rym import cx
        >>> @cx.component
        ... class Health:
        ...     max_hp: int
        ...     current: int

    """

    setup_func = [
        # NOTE: MUST call base post-init FIRST to resolve user defs, e.g., init=False
        getattr(klass, "__post_init__", None),
        add_to_inventory,
    ]

    attrs = [
        (_ENTITY_UID_TAG, None),
    ]
    methods = [
        ("__post_init__", call_each(*setup_func)),
        ("uid", property(attr_uid)),
        ("entity_uid", property(attr_entity_uid)),
    ]
    for name, asset in itertools.chain(attrs, methods):
        setattr(klass, name, asset)

    return add_to_catalog(klass, namespace="component")


# Post-init Setup
# ======================================================================


def call_each(*args: Callable[..., None]) -> Callable[..., None]:
    """Return a wrapper to call each given function."""

    def __post_init__(self) -> None:
        for func in args:
            if not func:
                continue  # in case of null
            func(self)

    return __post_init__


# Unbound methods
# ----------------------------------


def attr_entity_uid(self) -> UUID:
    return getattr(self, _ENTITY_UID_TAG)


def attr_uid(self) -> UUID:
    return _inventory.get_inventory_uid(self)


def add_to_inventory(self) -> None:
    """Replacement for __post_init__."""
    # track this instance!
    inventory = _inventory.get_inventory()
    inventory.add(self.__class__.__name__, self)


# __END__
