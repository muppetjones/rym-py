#!/usr/bin/env python3
"""Tooling to spawn entities."""

from rym.cx.core.component import Component
from rym.cx.core.entity import Entity


def spawn_entity(*args: Component) -> list[Entity]:
    """Create an entity from one or more component sets and link them.

    Given tuples of components, create a new entity -- only providing the
    component ids to the new entity. Then, add the entity ID to each component.

    Arguments:
        *args: Iterables of component instances.
    Returns:
        List of entity objects.
    """
    spawned = []
    for components in args:
        component_ids = [x.uid for x in components]
        entity = Entity(component_ids)

        # Link components back to entity
        for component in components:
            setattr(component, "__cx_entity_uid__", entity.uid)

        spawned.append(entity)

    return spawned


# __END__
