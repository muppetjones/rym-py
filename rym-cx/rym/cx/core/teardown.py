#!/usr/bin/env python3
"""Cleanup support."""

from rym.cx.core import _catalog, _inventory


def clear_registrar(*args, **kwargs) -> None:
    """Clear catalog and inventory."""
    _catalog.clear_catalog(*args, **kwargs)
    _inventory.clear_inventory(*args, **kwargs)


async def clear_registrar_async(*args, **kwargs) -> None:
    """Clear catalog and inventory."""
    await _catalog.clear_catalog_async(*args, **kwargs)
    await _inventory.clear_inventory_async(*args, **kwargs)


# __END__
