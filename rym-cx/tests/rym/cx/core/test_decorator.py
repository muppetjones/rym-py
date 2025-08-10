#!/usr/bin/env python3
"""Test decorators."""

import logging
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock

import rym.cx.core.decorator as MOD
from rym.cx.core import _system, registrar

LOGGER = logging.getLogger(__name__)


class ThisTestCase(IsolatedAsyncioTestCase):
    """Base test case for the module."""

    async def asyncSetUp(self) -> None:
        await _system.clear_registry(Mock())
        self.addCleanup(_system.clear_registry, Mock())


class TestAddToRegistry(ThisTestCase):
    """Test decorator."""

    def test_raises_if_missing_parameters(self) -> None:
        with self.assertRaises(TypeError):

            @MOD.add_to_registry
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

        wrapped = MOD.add_to_registry(Foo, namespace="example")
        found = {
            "name": wrapped.__name__,
        }
        self.assertEqual(expected, found)

    async def test_adds_to_global_registry(self) -> None:
        @MOD.add_to_registry(namespace="example")
        class Foo:
            ...

        subject = _system.get_registry()
        found = await subject.get(Foo)
        expected = registrar.Record.new("example", Foo)
        self.assertEqual(expected, found)


# __END__
