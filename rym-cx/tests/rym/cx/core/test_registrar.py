#!/usr/bin/env python3
"""Test the registry class."""

import asyncio
import dataclasses as dcs
from unittest import IsolatedAsyncioTestCase

import rym.cx.core.registrar as MOD
from rym.cx.core import identifier
from rym.cx.core.record import InventoryRecord


class ThisTestCase(IsolatedAsyncioTestCase):
    """Base test case for the module."""


class TestInit(ThisTestCase):
    """Test class init and properties."""

    async def test_initializes_with_empty_registrar(self) -> None:
        subject = MOD.Registrar()
        expected = {}
        found = subject.register
        self.assertEqual(expected, found)


class TestAddAsync(ThisTestCase):
    """Test coroutine."""

    async def test_behavior(self) -> None:
        class Foo:
            ...

        class Bar:
            ...

        class Meh:
            ...

        subject = MOD.Registrar()

        with self.subTest("async adds each item"):
            coro = [
                subject.add_async(value=Foo, namespace="x"),
                subject.add_async(value=Foo, namespace="y"),
            ]
            await asyncio.gather(*coro)
            expected = {
                identifier.generate_uid("x", Foo),
                identifier.generate_uid("y", Foo),
            }
            found = set(subject.register.keys())
            self.assertEqual(expected, found)

        with self.subTest("raises for collision"):
            Meh.__name__ = "Bar"
            with self.assertRaisesRegex(ValueError, "value exists in namespace"):
                coro = [
                    subject.add_async(value=Bar, namespace="x"),
                    subject.add_async(value=Meh, namespace="x"),
                ]
                await asyncio.gather(*coro)


class TestAdd(ThisTestCase):
    """Test function."""

    async def test_raises_if_name_conflict_detected(self) -> None:
        class Foo:
            ...

        class Meh:
            ...

        Meh.__name__ = "Foo"
        subject = MOD.Registrar()
        record = subject.add("X", Foo)

        with self.subTest("igore true duplicates"):
            subject.add(record.namespace, Foo)

        with self.subTest("disallow intra-namespace commonality"):
            with self.assertRaises(ValueError):
                subject.add(record.namespace, Meh)

        with self.subTest("allow inter-namespace commonality"):
            subject.add("Y", Meh)

    async def test_raises_if_invalid_namespace(self) -> None:
        class Foo:
            ...

        subject = MOD.Registrar()
        with self.assertRaisesRegex(ValueError, "must be hashable"):
            subject.add({"foo"}, Foo)

    async def test_returns_and_stores_record(self) -> None:
        class Foo:
            ...

        subject = MOD.Registrar()
        result = subject.add("X", Foo)

        with self.subTest("returns record"):
            expected = subject._Record.new("X", Foo)
            found = result
            self.assertEqual(expected, found)

        with self.subTest("stores record"):
            expected = {result.uid: result}
            found = subject.register
            self.assertEqual(expected, found)

        with self.subTest("indexed by namespace"):
            expected = {"X": [result.uid]}
            found = subject.lookup
            self.assertEqual(expected, found)

    async def test_sets_cx_property(self) -> None:
        class Foo:
            ...

        subject = MOD.Registrar()
        record = subject.add("X", Foo)

        with self.subTest("sets uid"):
            expected = record.uid
            attr = f"__cx_{subject.label}_uid__"
            found = getattr(Foo, attr)
            self.assertEqual(expected, found)

        with self.subTest("sets namespace"):
            expected = record.namespace
            attr = f"__cx_{subject.label}_namespace__"
            found = getattr(Foo, attr)
            self.assertEqual(expected, found)

    async def test_uses_given_record_class(self) -> None:
        class Foo:
            ...

        subject = MOD.Registrar(_Record=InventoryRecord)
        record = subject.add("X", Foo)
        assert isinstance(record, InventoryRecord)

    async def test_supports_namespace_by_class(self):
        # NOTE: Intended for use with InventoryRecord
        @dcs.dataclass
        class Foo:
            x: int

        subject = MOD.Registrar(_Record=InventoryRecord)
        record = subject.add(Foo, Foo(0))

        with self.subTest("record by class name"):
            expected = Foo.__name__
            found = record.namespace
            self.assertEqual(expected, found)

        with self.subTest("lookup by class name"):
            expected = {Foo.__name__: [record.uid]}
            found = subject.lookup
            self.assertEqual(expected, found)


class TestClearAsync(ThisTestCase):
    """Test coroutine."""

    async def test_removes_all_registered_items(self) -> None:
        class Foo:
            ...

        class Bar:
            ...

        subject = MOD.Registrar()
        subject.add("X", Foo)
        subject.add("Y", Bar)

        # control: make sure the items were added
        assert bool(subject.register) is not False
        assert bool(subject.lookup) is not False

        await subject.clear_async()

        assert bool(subject.register) is False
        assert bool(subject.lookup) is False


class TestClear(ThisTestCase):
    """Test function."""

    async def test_removes_all_registered_items(self) -> None:
        class Foo:
            ...

        class Bar:
            ...

        subject = MOD.Registrar()
        subject.add("X", Foo)
        subject.add("Y", Bar)

        # control: make sure the items were added
        assert bool(subject.register) is not False
        assert bool(subject.lookup) is not False

        subject.clear()

        assert bool(subject.register) is False
        assert bool(subject.lookup) is False


class TestGetByNamespace(ThisTestCase):
    """Test function."""

    async def test_raises_for_unknown_namespace(self) -> None:
        class Foo:
            ...

        class Bar:
            ...

        subject = MOD.Registrar()
        subject.add("X", Foo)

        with self.subTest("control"):
            expected = [Foo]
            found = await subject.get_by_namespace("X")
            self.assertEqual(expected, found)

        tests = ["Y", None]
        for given in tests:
            with self.subTest(given):
                with self.assertRaisesRegex(ValueError, "register items first"):
                    await subject.get_by_namespace(given)

    async def test_raises_for_invalid_namespace(self) -> None:
        subject = MOD.Registrar()
        with self.assertRaisesRegex(ValueError, "must be hashable"):
            await subject.get_by_namespace({"foo"})

    async def test_returns_list_of_items_in_namespace(self) -> None:
        class FooA:
            ...

        class FooB:
            ...

        class Bar:
            ...

        FooA.__name__ = "Foo"  # must be able to pull same name out independently
        FooB.__name__ = "Foo"

        subject = MOD.Registrar()
        _ = subject.add("A", FooA)
        _ = subject.add("B", FooB)
        _ = subject.add("A", Bar)

        tests = [
            # (expected, given)
            ([FooA, Bar], "A"),
            ([FooB], "B"),
        ]

        for expected, given in tests:
            with self.subTest(given):
                found = await subject.get_by_namespace(given)
                self.assertEqual(expected, found)

    async def test_supports_lookup_by_class(self):
        # NOTE: Intended for use with InventoryRecord

        @dcs.dataclass
        class Foo:
            x: int

        @dcs.dataclass
        class Bar:
            y: int

        subject = MOD.Registrar(_Record=InventoryRecord)
        instances = [Foo(0), Foo(1), Bar(3)]
        for instance in instances:
            subject.add(instance.__class__.__name__, instance)

        tests = [
            # (expected, given)
            (instances[:2], Foo),
            (instances[2:], Bar),
        ]
        for expected, given in tests:
            with self.subTest(given):
                found = await subject.get_by_namespace(given)
                self.assertEqual(expected, found)


# __END__
