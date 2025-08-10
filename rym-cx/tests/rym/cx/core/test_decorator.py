#!/usr/bin/env python3
"""Test decorators."""

import logging
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock

import rym.cx.core.decorator as MOD
from rym.cx.core import _global
from rym.cx.core.registrar import RegisterRecord

LOGGER = logging.getLogger(__name__)


class ThisTestCase(IsolatedAsyncioTestCase):
    """Base test case for the module."""

    async def asyncSetUp(self) -> None:
        await _global.clear_catalog(Mock())
        self.addCleanup(_global.clear_catalog, Mock())


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

    async def test_adds_to_global_catalog(self) -> None:
        @MOD.add_to_catalog(namespace="example")
        class Foo:
            ...

        subject = _global.get_catalog()
        found = await subject.get(Foo)
        expected = RegisterRecord.new("example", Foo)
        self.assertEqual(expected, found)


class TestComponentDecorator(ThisTestCase):
    """Test decorator."""

    async def test_adds_to_catalog_under_namespace(self) -> None:
        @MOD.component
        class Foo:
            ...

        subject = _global.get_catalog()
        found = await subject.get(Foo)
        expected = RegisterRecord.new("component", Foo)
        self.assertEqual(expected, found)


class TestEntityDecorator(ThisTestCase):
    """Test decorator."""

    async def test_adds_to_catalog_under_namespace(self) -> None:
        @MOD.entity
        class Foo:
            ...

        subject = _global.get_catalog()
        found = await subject.get(Foo)
        expected = RegisterRecord.new("entity", Foo)
        self.assertEqual(expected, found)


# __END__
