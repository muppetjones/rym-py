#!/usr/bin/env python3
"""Test decorators."""

import dataclasses as dcs
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock

import rym.cx.core.decorator as MOD
from rym.cx.core import _catalog, _inventory
from rym.cx.core.record import CatalogRecord, InventoryRecord


class ThisTestCase(IsolatedAsyncioTestCase):
    """Base test case for the module."""

    async def asyncSetUp(self) -> None:
        await _catalog.clear_catalog(Mock())
        self.addCleanup(_catalog.clear_catalog, Mock())


class TestAddToCatalog(ThisTestCase):
    """Test decorator."""

    def test_raises_if_missing_parameters(self) -> None:
        with self.assertRaises(TypeError):

            @MOD.add_to_catalog
            class Foo:
                ...

    def test_preserves_metadata(self) -> None:
        # TODO: Extend this check. The decorator should return the thing wrapped,
        #   so this is really just a sanity check.
        class Foo:
            """Example class."""

        expected = {
            "name": Foo.__name__,
        }

        wrapped = MOD.add_to_catalog(Foo, namespace="example")
        found = {
            "name": wrapped.__name__,
        }
        self.assertEqual(expected, found)

    async def test_adds_to_catalog_catalog(self) -> None:
        @MOD.add_to_catalog(namespace="example")
        class Foo:
            ...

        subject = _catalog.get_catalog()
        found = await subject.get(Foo)
        expected = CatalogRecord.new("example", Foo)
        self.assertEqual(expected, found)

    async def test_applies_dataclass(self) -> None:
        @MOD.add_to_catalog(namespace="example")
        class Foo:
            x: int
            y: bool

        subject = _catalog.get_catalog()
        _ = await subject.get(Foo)
        assert dcs.is_dataclass(Foo)


class TestComponentDecorator(ThisTestCase):
    """Test decorator."""

    async def test_adds_to_catalog_under_namespace(self) -> None:
        @MOD.component
        class Foo:
            ...

        subject = _catalog.get_catalog()
        record = await subject.get(Foo)

        with self.subTest("adds to catalog"):
            found = record
            expected = CatalogRecord.new("component", Foo)
            self.assertEqual(expected, found)

        with self.subTest("sets cx_cat attribute on the registered object"):
            # NOTE: Technically redundant with catalog and registrar tests
            expected = (record.namespace, record.uid)
            found = (Foo.__cx_cat_namespace__, Foo.__cx_cat_uid__)
            self.assertEqual(expected, found)


class TestEntityDecorator(ThisTestCase):
    """Test decorator."""

    async def test_raises_if_wrapped_has_post_init_defined(self) -> None:
        # TODO: Handle this better

        class Foo:
            def __post_init__(cls) -> "Foo":
                ...

        with self.assertRaises(TypeError):
            MOD.entity(Foo)

    async def test_adds_to_catalog_under_namespace(self) -> None:
        @MOD.entity
        class Foo:
            ...

        subject = _catalog.get_catalog()
        record = await subject.get(Foo)

        with self.subTest("adds to catalog"):
            found = record
            expected = CatalogRecord.new("entity", Foo)
            self.assertEqual(expected, found)

        with self.subTest("sets cx_cat attribute on the registered object"):
            # NOTE: Technically redundant with catalog and registrar tests
            expected = (record.namespace, record.uid)
            found = (Foo.__cx_cat_namespace__, Foo.__cx_cat_uid__)
            self.assertEqual(expected, found)

    async def test_instances_of_registered_items_are_tracked_in_inventory(self) -> None:
        @MOD.entity
        class Foo:
            x: int
            y: int

        subject = _inventory.get_inventory()
        instance = Foo(867, 5309)
        record = await subject.get(instance)

        with self.subTest("adds to inventory"):
            found = record
            expected = InventoryRecord(Foo.__name__, instance, uid=record.uid)
            self.assertEqual(expected, found)


# __END__
