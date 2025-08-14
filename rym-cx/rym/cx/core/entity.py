#!/usr/bin/env python3
"""."""

import dataclasses as dcs
import logging
from typing import TypeVar
from uuid import UUID

from . import _inventory
from .component import Component

LOGGER = logging.getLogger(__name__)

T = TypeVar("T")


@dcs.dataclass
class Entity:
    """Define entity object."""

    component: tuple[Component]

    @classmethod
    def new(cls, *args) -> "Entity":
        """Create new instance."""
        return cls(component=args)

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
