#!/usr/bin/env python3
"""
Spawn an Entity
^^^^^^^^^^^^^^^^

Never use cx.Entity directly. It's provided only for type hints. Instead, use
`cx.spawn_entity`

>>> from rym import cx
>>> @cx.component
... class Foo: ...
...
>>> cx.spawn_entity((Foo(), ))
[Entity(component=(UUID('4e818f68-299c-4807-bd2b-5d36bd17cc1d'),))]

"""

import dataclasses as dcs
import logging
from typing import ClassVar, TypeVar
from uuid import UUID

from . import _inventory
from .component import _ENTITY_UID_TAG, Component

LOGGER = logging.getLogger(__name__)

T = TypeVar("T")


@dcs.dataclass
class Entity:
    """Define an entity object.

    NOTE: Entity is little more than a struct. Prefer a functional paradigm over OO.

    Attributes:
        component: A tuple of component UIDs.
    """

    component: tuple[Component]

    reference_tag: ClassVar[str] = _ENTITY_UID_TAG

    def __post_init__(self) -> None:
        """Initialize and link."""
        inventory = _inventory.get_inventory()
        inventory.add(self.__class__, self)
        self.component = tuple(self.component)  # ensure it's a tuple

    @property
    def uid(self) -> UUID:
        """Return inventory UID."""
        # NOTE: using the name explicitly is a litte smelly
        return _inventory.get_inventory_uid(self)


# __END__
