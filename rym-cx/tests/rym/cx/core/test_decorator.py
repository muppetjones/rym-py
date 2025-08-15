#!/usr/bin/env python3
"""Test decorators."""

import dataclasses as dcs
from unittest import IsolatedAsyncioTestCase, mock
from unittest.mock import Mock

import rym.cx.core.decorator as MOD
from rym.cx.core import _catalog


class ThisTestCase(IsolatedAsyncioTestCase):
    """Base test case for the module."""

    async def asyncSetUp(self) -> None:
        await _catalog.clear_catalog_async(Mock())
        self.addCleanup(_catalog.clear_catalog_async, Mock())


class TestAddToCatalog(ThisTestCase):
    """Test decorator."""

    def test_raises_if_missing_parameters(self) -> None:
        with self.assertRaises(TypeError):

            @MOD.add_to_catalog
            class Foo: ...

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
        class Foo: ...

        subject = _catalog.get_catalog()
        found = await subject.get_by_namespace("example")
        expected = [Foo]
        self.assertEqual(expected, found)

    async def test_applies_dataclass(self) -> None:
        @MOD.add_to_catalog(namespace="example")
        class Foo:
            x: int
            y: bool

        expected = True
        found = dcs.is_dataclass(Foo)
        self.assertEqual(expected, found)


class TestRetrieve(ThisTestCase):
    """Test decorator."""

    async def test_passes_results_from_inventory_into_kwargs(self) -> None:
        with mock.patch.object(MOD._inventory, "retrieve_by_component") as mock_dec:
            mock_dec.return_value = [[1, 2], [3, 4]]

            inner_mock = Mock()

            @MOD.retrieve(foo=["A", "B"])
            async def bar(*args, **kwargs):
                inner_mock(*args, **kwargs)

            await bar()

        with self.subTest("asks inventory retrieve expected components"):
            found = mock_dec.mock_calls
            expected = [mock.call("A", "B")]
            self.assertEqual(expected, found)

        with self.subTest("passed retrieved components into wrapped function"):
            found = inner_mock.mock_calls
            expected = [mock.call(foo=[[1, 2], [3, 4]])]
            self.assertEqual(expected, found)


# __END__
