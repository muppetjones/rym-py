#!/usr/bin/env python3
"""Test system parameters."""

from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock

import rym.cx.core._inventory as MOD
from rym import cx
from rym.cx.core.registrar import Registrar


class ThisTestCase(IsolatedAsyncioTestCase):
    """Base test case for the module."""

    async def asyncSetUp(self) -> None:
        await cx.clear_registrar_async(Mock())
        self.addCleanup(cx.clear_registrar_async, Mock())


class TestClearInventory(ThisTestCase):
    """Test function."""

    async def test_behavior(self) -> None:
        class Foo: ...

        one = MOD.get_inventory()
        one.add("x", Foo)

        await MOD.clear_inventory_async(logger=Mock())

        with self.subTest("clears current inventory"):
            assert bool(one.lookup) is False
            assert bool(one.register) is False

        with self.subTest("creates new inventory instance"):
            two = MOD.get_inventory()
            assert one is not two

    async def test_repeated_clear(self) -> None:
        logger = Mock()
        _ = MOD.get_inventory()  # make sure we have something to clear
        await MOD.clear_inventory_async(logger=logger)
        await MOD.clear_inventory_async(logger=logger)  # should not raise
        MOD.clear_inventory(logger=logger)  # should not raise
        await MOD.clear_inventory_async(logger=logger)  # should not raise


class TestGetInventory(ThisTestCase):
    """Test function."""

    async def test_returns_singleton_instance(self) -> None:
        subject = MOD.get_inventory()  # type: Registrar
        assert isinstance(subject, Registrar)
        for i in range(5):
            found = MOD.get_inventory()  # type: Registrar
            assert subject is found

    async def test_is_not_true_singleton(self) -> None:
        a = MOD.get_inventory()  # type: Registrar
        b = Registrar()
        assert a is not b

    async def test_sets_label(self) -> None:
        subject = MOD.get_inventory()
        expected = "inv"
        found = subject.label
        self.assertEqual(expected, found)


class TestGetInventoryId(ThisTestCase):
    """Test function."""

    async def test_raises_if_object_not_registerd(self) -> None:
        with self.assertRaisesRegex(ValueError, "unregistered"):
            MOD.get_inventory_uid("foo")

    async def test_returns_expected_value(self) -> None:
        class Foo: ...

        subject = MOD.get_inventory()
        instance = Foo()
        subject.add(Foo, instance)

        expected = instance.__cx_inv_uid__
        found = MOD.get_inventory_uid(instance)
        self.assertEqual(expected, found)


class TestGetRelatedComponent(ThisTestCase):
    """Test function.

    NOTE: Requires entity and component to be imported for singledispatch register.
    """

    async def test_raises_if_object_not_registerd(self) -> None:
        with self.assertRaisesRegex(ValueError, "unregistered"):
            await MOD.get_related_component("foo")

    async def test_returns_components_given_entity(self) -> None:
        # NOTE: Relies too heavily on other patterns. Mocking works but only
        #   with significant setup, which diultes the test.
        # tl;dr: Relies in entity_uid and inventory lookup. The entities
        #   and components are automatically added to the inventory
        @cx.component
        class Foo:
            x: int

        @cx.component
        class Bar:
            y: int

        subject = [
            [Foo(0), Bar(1)],
            [Foo(3), Bar(4)],
            [Bar(5)],
        ]
        entities = cx.spawn_entity(*subject)

        tests = [
            # (expected, given)
            (subject[1], entities[1]),
            (subject[1], subject[1][0]),
            (subject[1], subject[1][1]),
        ]
        for expected, given in tests:
            with self.subTest(given):
                found = await MOD.get_related_component(given)
                self.assertEqual(expected, found)


class TestRetrieveByComponent(ThisTestCase):
    """Test function."""

    async def test_returns_matching_components_by_entity(self) -> None:
        @cx.component
        class Foo:
            x: int

        @cx.component
        class Bar:
            y: int

        @cx.component
        class Baz:
            z: int

        subject = [
            [Foo(6)],
            [Foo(0), Bar(1), Baz(8)],
            [Foo(3), Bar(4)],
            [Bar(5)],
        ]
        _ = cx.spawn_entity(*subject)

        found = await MOD.retrieve_by_component(Bar, Foo)
        expected = sorted(
            [
                [subject[1][1], subject[1][0]],
                [subject[2][1], subject[2][0]],
            ],
            key=lambda x: x[0].entity_uid,
        )
        self.assertEqual(expected, found)


# __END__
