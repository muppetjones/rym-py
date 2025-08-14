#!/usr/bin/env python3
"""Test."""

import itertools
import logging
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock

import rym.cx.core.spawn as MOD
from rym import cx
from rym.cx.core import _inventory, teardown

LOGGER = logging.getLogger(__name__)


class ThisTestCase(IsolatedAsyncioTestCase):
    """Base test case for the module."""

    async def asyncSetUp(self) -> None:
        await teardown.clear_registrar_async(logger=Mock())
        self.addCleanup(teardown.clear_registrar_async, logger=Mock())


class TestSpawnEntity(ThisTestCase):
    """Test function."""

    def test_returns_entity_instances(self) -> None:
        @cx.component
        class Foo:
            ...

        @cx.component
        class Bar:
            ...

        given = [
            (Foo(), Foo()),
            (Foo(), Bar()),
        ]

        entities = MOD.spawn_entity(*given)

        with self.subTest("returns entities"):
            assert all(isinstance(x, cx.Entity) for x in entities)

        with self.subTest("stores component ids"):
            for entity, component in zip(entities, given):
                found = entity.component
                expected = tuple(x.uid for x in component)
                self.assertEqual(expected, found)

    async def test_behavior(self) -> None:
        @cx.component
        class Foo:
            ...

        @cx.component
        class Bar:
            ...

        given = [
            (Foo(), Foo()),
            (Foo(), Bar()),
        ]

        components = list(itertools.chain.from_iterable(given))
        entities = MOD.spawn_entity(*given)

        inventory = _inventory.get_inventory()

        with self.subTest("entity registered with inventory"):
            found = await inventory.get_by_namespace(cx.Entity)
            expected = entities
            self.assertEqual(expected, found)

        with self.subTest("components registered with inventory"):
            found = [
                *await inventory.get_by_namespace(Foo),
                *await inventory.get_by_namespace(Bar),
            ]
            expected = components
            self.assertEqual(expected, found)

        with self.subTest("components reference entity"):
            for entity, component in zip(entities, given):
                found = {x.entity_uid for x in component}
                expected = {entity.uid}
                self.assertEqual(expected, found)


# __END__
