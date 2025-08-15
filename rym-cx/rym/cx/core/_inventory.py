#!/usr/bin/env python3
"""Define global system parameters.

NOTE: The contents of this module are intended for use within rym.cx modules.

NOTE: This module is a bit of a smell. Globals and singletons can get messy
    and should be avoided. However, we want some functionality provided behind
    the scenes, and we can't reliably do that without having a single registry
    and index to track entities and instances, etc. The best we can do (for now)
    is make sure it's at least safe.

NOTE: Not a big fan of "_global" as a name, but it is apt.
    Conversely, "app" may imply that this is the entrypoint or driver,
    and "system" is part of ECS.
    Most users shouldn't need to use this directly.
"""

import logging
from typing import Any, Generator, Optional, Protocol
from uuid import UUID

from rym.cx.core.record import InventoryRecord

from .errors import UnregisteredAssetError
from .registrar import Registrar

_INVENTORY = None  # type: Registrar


class Asset(Protocol):
    """Generic protocol for Entity or Component."""

    uid: UUID
    entity_id: Optional[UUID]


async def clear_inventory_async(logger: Optional[logging.Logger] = None) -> None:
    """Clear the current global inventory and inventory instance.

    See also:
        clear_inventory.
    """
    global _INVENTORY
    if not _INVENTORY:
        return  # EARLY EXIT: no inventory -- ignore
    logger = logger or logging.getLogger(__name__)

    logger.warning("Clearing cx inventory")
    await _INVENTORY.clear_async()
    _INVENTORY = None


def clear_inventory(logger: Optional[logging.Logger] = None) -> None:
    """Clear the current global inventory and inventory instance.

    In case someone is storing a reference to the inventory, clear the instance.
    In case someone is using the global variable directly, clear the variable, too.

    NOTE: This pattern is technically fragile. We could just use the same one
        or create a new global instance; however, that could lead to undefined
        behavior is someone is doing something bad. By clearing both, any offending
        code should fail more directly.

    NOTE: Even more technically, this pattern is not thread safe or multiproc safe.
        Creating a new instance in the middle of execution will result in the
        shared instance being unavailable to child threads or procesesses.
        While reusing the same inventory wouldn't guarantee safety, if the instance
        is created early enough, it _may_ be shared automatically, though likely
        it would be a separate instance, which would be bad anyway.

    NOTE: More technically still, it's a moot point. This function is largely
        intended for testing, and the inventory should not be modified at runtime.
        (The index will be a separate matter). In a worst case scenario, we'd
        use this to reset and then rebuild the inventory, but at that point we
        need much more sophisticated error handling anyway.

    TODO: Make this thread and multiprocess safe.

    Arguments:
        None
    Returns:
        None
    """
    global _INVENTORY
    if not _INVENTORY:
        return  # EARLY EXIT: no inventory -- ignore
    logger = logger or logging.getLogger(__name__)

    logger.warning("Clearing cx inventory")
    _INVENTORY.clear()
    _INVENTORY = None


def get_inventory() -> Registrar:
    """Return a static inventory.

    This function will return the same registrar every time,
    i.e., the _global_ inventory. Multiple registrar instances may exist at any
    given time, but only one is the global inventory.

    Arguments:
        None
    Returns:
        A static inventory instance.
    """
    global _INVENTORY
    if not _INVENTORY:
        _INVENTORY = Registrar(label="inv", _Record=InventoryRecord)
    return _INVENTORY


def get_inventory_uid(obj: Any) -> None:
    """Return inventory UID of an item.

    The attribute name is determined by the registrar, so provide an easy lookup.

    NOTE: While this _could_ be on the registrar, it would require access to the
        registrar instance. This function assumes we want the global inventory.
    """
    inventory = get_inventory()
    try:
        return getattr(obj, inventory.uid_tag)
    except AttributeError:
        raise UnregisteredAssetError(f"No uid for unregistered asset: {obj}")


async def get_related_component(asset: Asset) -> Generator[Asset, None, None]:
    """Given an asset, return related components.

    Arguments:
        asset: A component or entity.
    Returns:
        The components associated with the entity the asset is a part of.
    """
    # NOTE: Avoid singledispatch.
    #   - It's fast, but it has an overhead, and this function can't afford it.
    #   - Also, entity and component both use inventory, so there's a diamond
    #       pattern; however, we can solve that by defining the registration
    #       functions in the respective modules.
    #   - We can't register "Component" -- it isnt' a class, so the base
    #       function would have to handle components.
    inventory = get_inventory()
    if entity_uid := getattr(asset, "entity_uid", None):
        entity, *_ = await inventory.get_by_uid(entity_uid)
    else:
        entity = asset

    try:
        components = entity.component
    except AttributeError as err:
        # It's not a component (no entity uid attr)
        # It's a component, but not part of an entity (entity uid is None)
        # It's not an entity (no component attr)
        raise UnregisteredAssetError(f"unregistered asset: {asset}") from err

    return await inventory.get_by_uid(*components)


async def retrieve_by_component(*args: Asset) -> list[list[Asset]]:
    """Retrieve partial entities based on given component types.

    CRITICAL: Assumes each component type is unique per entity.
        Fine for now, but probably not ideal.

    Arguments:
        *args: One or more component types.
    Returns:
        Matching components by entity.
    """
    inventory = get_inventory()

    # this will be lossy if an entity has multiple of a component type
    matched_components = [
        {y.entity_uid: y for y in await inventory.get_by_namespace(x)} for x in args
    ]

    components = await inventory.get_by_namespace(args[0])

    # find common entities
    entity_ids = set(matched_components[0].keys())
    for components in matched_components[1:]:
        entity_ids &= set(components.keys())

    matches = [[x[uid] for x in matched_components] for uid in sorted(entity_ids)]
    return matches


# __END__
