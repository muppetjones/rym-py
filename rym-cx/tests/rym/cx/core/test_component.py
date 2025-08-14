#!/usr/bin/env python3
"""."""

import dataclasses as dcs
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock
from uuid import UUID

import rym.cx.core.component as MOD
from rym.cx.core import _catalog, _inventory


class ThisTestCase(IsolatedAsyncioTestCase):
    """Base test case for the module."""

    async def asyncSetUp(self) -> None:
        await _catalog.clear_catalog_async(Mock())
        self.addCleanup(_catalog.clear_catalog_async, Mock())
        await _inventory.clear_inventory_async(Mock())
        self.addCleanup(_inventory.clear_inventory_async, Mock())


class TestComponentDecorator(ThisTestCase):
    """Test decorator."""

    async def test_adds_to_catalog_under_namespace(self) -> None:
        @MOD.register_as_component
        class Foo:
            ...

        subject = _catalog.get_catalog()

        with self.subTest("adds to catalog"):
            found = await subject.get_by_namespace("component")
            expected = [Foo]
            self.assertEqual(expected, found)

        with self.subTest("sets cx_cat attribute on the registered object"):
            # NOTE: Technically redundant with catalog and registrar tests
            record = list(subject.register.values())[0]  # only one expected
            expected = (record.namespace, record.uid)
            found = (Foo.__cx_cat_namespace__, Foo.__cx_cat_uid__)
            self.assertEqual(expected, found)

    async def test_instances_of_registered_items_are_tracked_in_inventory(self) -> None:
        @MOD.register_as_component
        class Foo:
            x: int
            y: int

        instance1 = Foo(3, 141592)  # shouldn't matter when we get the inventory
        inventory = _inventory.get_inventory()
        instance2 = Foo(867, 5309)  # before or after -- should be registered

        with self.subTest("adds to inventory"):
            found = await inventory.get_by_namespace(Foo)
            expected = [instance1, instance2]
            self.assertEqual(expected, found)

    async def test_instantiation_behavior_of_decorated_class(self):
        @MOD.register_as_component
        class Foo:
            x: int
            y: int
            z: int = dcs.field(init=False)

            def __post_init__(self) -> None:
                self.z = self.x * 2

        subject = [Foo(867, 5309), Foo(3, 141592)]
        uids = [x.uid for x in subject]

        with self.subTest("sets UID on each instance"):
            assert all(isinstance(x, UUID) for x in uids)

            found = len(uids)
            expected = len(subject)
            self.assertEqual(expected, found)

        with self.subTest("asset added to inventory"):
            inventory = _inventory.get_inventory()
            found = await inventory.get_by_namespace(Foo)
            expected = subject
            self.assertEqual(expected, found)

        with self.subTest("base post init is run"):
            expected = [x.x * 2 for x in subject]
            found = [x.z for x in subject]
            self.assertEqual(expected, found)


# __END__
