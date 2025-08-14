#!/usr/bin/env python3
"""."""


from collections.abc import Callable
from typing import Optional, Protocol, TypeVar
from uuid import UUID

from rym.cx.core import _inventory

from .decorator import add_to_catalog

T = TypeVar("T")


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

    attr = [
        ("__post_init__", call_each(*setup_func)),
        ("uid", property(attr_uid)),
    ]
    for name, asset in attr:
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


def attr_uid(self) -> UUID:
    return _inventory.get_inventory_uid(self)


def add_to_inventory(self) -> None:
    """Replacement for __post_init__."""
    # track this instance!
    inventory = _inventory.get_inventory()
    inventory.add(self.__class__.__name__, self)


# __END__
