# NOTE: Init files should be empty. Imports in this file simplify usage.
#   BE MINDFUL OF WHAT YOU PUT IN HERE.

from . import core

"""Easy access to decorators.

See also:
    rym.cx.core.catalog
    rym.cx.core._global
    rym.cx.core.decorators
"""
from .core.decorator import component, entity


"""Placeholders for functional tests.

The functional tests fail outside of test cases b/c objects are not defined.
Define a set of placeholders to allow tests to run (and fail) more accurately.
"""

from unittest.mock import MagicMock


Archetype = MagicMock()
get_entities = MagicMock()
clear_all = MagicMock()

get_archetype_id = MagicMock()
get_component_id = MagicMock()
get_entity_id = MagicMock()
