#!/usr/bin/env python3
"""Test system parameters."""

import logging
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock

import rym.cx.core._inventory as MOD
from rym.cx.core.registrar import Registrar

LOGGER = logging.getLogger(__name__)


class ThisTestCase(IsolatedAsyncioTestCase):
    """Base test case for the module."""

    async def asyncSetUp(self) -> None:
        await MOD.clear_inventory_async(Mock())
        self.addCleanup(MOD.clear_inventory_async, Mock())


class TestClearInventory(ThisTestCase):
    """Test function."""

    async def test_behavior(self) -> None:
        class Foo:
            ...

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


# __END__
