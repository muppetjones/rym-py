# NOTE: Init files should be empty. Imports in this file simplify usage.
#   BE MINDFUL OF WHAT YOU PUT IN HERE.

from . import core
from .core import _inventory as inventory

"""Easy access to common decorators, classes, functions, etc.

See also:
    rym.cx.core._catalog
    rym.cx.core._inventory
    rym.cx.core.component
    rym.cx.core.entity
    rym.cx.core.spawn
"""
from .core.component import Component, register_as_component
from .core.entity import Entity
from .core._inventory import get_inventory, get_inventory_uid
from .core._catalog import get_catalog
from .core.spawn import spawn_entity
from .core.teardown import clear_registrar, clear_registrar_async
from .core.decorator import retrieve


"""Aliases.

Define aliases for easier use.
"""
component = register_as_component


"""Placeholders for functional tests.

The functional tests fail outside of test cases b/c objects are not defined.
Define a set of placeholders to allow tests to run (and fail) more accurately.
"""

from unittest.mock import MagicMock


Archetype = MagicMock()

get_archetype_id = MagicMock()
