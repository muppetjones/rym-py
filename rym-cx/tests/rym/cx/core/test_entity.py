#!/usr/bin/env python3
"""Test."""

import logging
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock

import rym.cx.core.entity as MOD
from rym.cx.core import _catalog, _inventory

LOGGER = logging.getLogger(__name__)


class ThisTestCase(IsolatedAsyncioTestCase):
    """Base test case for the module."""

    async def asyncSetUp(self) -> None:
        await _catalog.clear_catalog_async(Mock())
        self.addCleanup(_catalog.clear_catalog_async, Mock())
        await _inventory.clear_inventory_async(Mock())
        self.addCleanup(_inventory.clear_inventory_async, Mock())


class TestEntity(ThisTestCase):
    """Test dataclass."""

    async def test_registers_in_inventory(self) -> None:
        instance1 = MOD.Entity.new(
            3, 141592
        )  # shouldn't matter when we get the inventory
        inventory = _inventory.get_inventory()
        instance2 = MOD.Entity.new(867, 5309)  # before or after -- should be registered

        with self.subTest("adds to inventory"):
            found = await inventory.get_by_namespace(MOD.Entity)
            expected = [instance1, instance2]
            self.assertEqual(expected, found)

        with self.subTest("sets inventory id"):
            found = [instance1.uid, instance2.uid]
            expected = [
                _inventory.get_inventory_uid(instance1),
                _inventory.get_inventory_uid(instance2),
            ]
            self.assertEqual(expected, found)


# __END__
