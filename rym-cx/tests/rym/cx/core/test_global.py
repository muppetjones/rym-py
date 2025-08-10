#!/usr/bin/env python3
"""Test system parameters."""

import logging
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock

import rym.cx.core._global as MOD
from rym.cx.core.registrar import Registrar

LOGGER = logging.getLogger(__name__)


class ThisTestCase(IsolatedAsyncioTestCase):
    """Base test case for the module."""


class TestClearCatalog(ThisTestCase):
    """Test function."""

    async def test_behavior(self) -> None:
        class Foo:
            ...

        one = MOD.get_catalog()
        one.add("x", Foo)

        await MOD.clear_catalog(logger=Mock())

        with self.subTest("clears current catalog"):
            assert bool(one.lookup) is False
            assert bool(one.register) is False

        with self.subTest("creates new catalog instance"):
            two = MOD.get_catalog()
            assert one is not two

    async def test_repeated_clear(self) -> None:
        _ = MOD.get_catalog()  # make sure we have something to clear
        await MOD.clear_catalog(logger=Mock())
        await MOD.clear_catalog(logger=Mock())  # should not raise
        await MOD.clear_catalog(logger=Mock())  # should not raise


class TestGetCatalog(ThisTestCase):
    """Test function."""

    async def test_returns_singleton_instance(self) -> None:
        subject = MOD.get_catalog()  # type: Registrar
        assert isinstance(subject, Registrar)
        for i in range(5):
            found = MOD.get_catalog()  # type: Registrar
            assert subject is found

    async def test_is_not_true_singleton(self) -> None:
        a = MOD.get_catalog()  # type: Registrar
        b = Registrar()
        assert a is not b


# __END__
