from . import core


"""Placeholders for functional tests.

The functional tests fail outside of test cases b/c objects are not defined.
Define a set of placeholders to allow tests to run (and fail) more accurately.
"""

from unittest.mock import MagicMock


def placeholder_decorator(klass):
    return klass


component = placeholder_decorator
entity = placeholder_decorator
archetype = placeholder_decorator

Archetype = MagicMock()
get_entities = MagicMock()
clear_all = MagicMock()

get_archetype_id = MagicMock()
get_component_id = MagicMock()
get_entity_id = MagicMock()
