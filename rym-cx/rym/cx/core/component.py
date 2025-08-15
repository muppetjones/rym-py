#!/usr/bin/env python3
"""
Declare Components via Decorator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This decorator is aliased in the root package as `cx.component`.

Features
^^^^^^^^

- Catalogs the class as a component.
- Adds "uid" and "entity_uid" properties.
- Converts to a dataclass.
- Auto-registers instances in the inventory.

Example
^^^^^^^

>>> from rym import cx
>>> @cx.component
... class Health:
...     max_hp: int
...     current: int

"""


from collections.abc import Callable
from typing import Any, Iterable, Optional, Protocol, TypeVar
from uuid import UUID

from rym.cx.core import _inventory

from .decorator import add_to_catalog

T = TypeVar("T")
_ENTITY_UID_TAG = "__cx_entity_uid__"


class Component(Protocol):
    entity_id: UUID


def register_as_component(klass: Optional[T] = None) -> T:
    """Decorate a component class.

    - Integrates with ECS inventory, including attribuets and post-init updates.
    - Converts to dataclass

    Arguments:
        klass: The class to decorate.
    Returns:
        The modified class as a dataclass.
    See also:
        rym.cx.core.decorators.add_to_catalog
    """
    inventory = _inventory.get_inventory()

    setup_func = [
        # NOTE: MUST call base post-init FIRST to resolve user defs, e.g., init=False
        getattr(klass, "__post_init__", None),
        add_to_inventory,
    ]

    attrs = [
        (_ENTITY_UID_TAG, str, None),
        (inventory.uid_tag, UUID, None),
    ]
    set_attr_safely(klass, attrs)

    methods = [
        ("__post_init__", call_each(*setup_func)),
        ("uid", property(attr_uid)),
        ("entity_uid", property(attr_entity_uid)),
    ]
    for name, asset in methods:
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


# Python Quirks
# ======================================================================


def set_attr_safely(
    klass: Callable,
    attrs: Iterable[tuple[str, str, Any]],
) -> None:
    """Set attributes on a future dataclass.

    Dataclasses use __annotations__ to define fields. If we want these fields
    to be included in the dataclass definition(we do), then we must provide
    annotations. Unfortunately, this is a bit trickier in python 3.9.

    See also:
        https://docs.python.org/3/howto/annotations.html
    """

    if isinstance(klass, type):
        ann = klass.__dict__.get("__annotations__", None)
    else:
        ann = getattr(klass, "__annotations__", None)

    if ann is None:
        # Starting annotations is the same for both
        ann = {}
        setattr(klass, "__annotations__", ann)

    for name, annotation, default in attrs:
        # NOTE: MUST update annotations to allow dataclass to track the field
        ann[name] = annotation
        setattr(klass, name, default)


# __END__
