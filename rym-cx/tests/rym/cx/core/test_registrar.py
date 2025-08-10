#!/usr/bin/env python3
"""Test the registry class."""

import asyncio
import logging
from pprint import pformat
from unittest import IsolatedAsyncioTestCase

import rym.cx.core.registrar as MOD
from rym.cx.core import identifier


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
                logging.critical(pformat(subject.register))


class TestAdd(ThisTestCase):
    """Test function."""

    async def test_raises_if_name_conflict_detected(self) -> None:
        class Foo:
            ...

        class Meh:
            ...

        Meh.__name__ = "Foo"
        subject = MOD.Registrar()
        record = subject.add(value=Foo, namespace="X")

        with self.subTest("igore true duplicates"):
            subject.add(value=Foo, namespace=record.namespace)

        with self.subTest("disallow intra-namespace commonality"):
            with self.assertRaises(ValueError):
                subject.add(value=Meh, namespace=record.namespace)

        with self.subTest("allow inter-namespace commonality"):
            subject.add(value=Meh, namespace="Y")

    async def test_stores_record(self) -> None:
        class Foo:
            ...

        subject = MOD.Registrar()
        subject.add(value=Foo, namespace="X")

        # NOTE: The record uid is auto-generated and must match.
        record = MOD.RegisterRecord.new(value=Foo, namespace="X")
        expected = {record.uid: record}
        found = subject.register
        self.assertEqual(expected, found)

    async def test_sets_cx_reg_property(self) -> None:
        class Foo:
            ...

        subject = MOD.Registrar()
        record = subject.add(value=Foo, namespace="X")

        with self.subTest("sets uid"):
            expected = record.uid
            found = Foo.__cx_reg_uid__
            self.assertEqual(expected, found)

        with self.subTest("sets namespace"):
            expected = record.namespace
            found = Foo.__cx_reg_namespace__
            self.assertEqual(expected, found)


class TestClear(ThisTestCase):
    """Test function."""

    async def test_removes_all_registered_items(self) -> None:
        class Foo:
            ...

        class Bar:
            ...

        subject = MOD.Registrar()
        subject.add(value=Foo, namespace="X")
        subject.add(value=Bar, namespace="Y")

        # control: make sure the items were added
        assert bool(subject.register) is not False
        assert bool(subject.lookup) is not False

        await subject.clear()

        assert bool(subject.register) is False
        assert bool(subject.lookup) is False


class TestGet(ThisTestCase):
    """Test function."""

    async def test_raises_for_unknown_record(self) -> None:
        class Foo:
            ...

        class Bar:
            ...

        subject = MOD.Registrar()
        subject.add(value=Foo, namespace="X")

        tests = [
            # (err, given)
            ("unknown value", {"value": Bar}),
            ("not in namespace", {"value": Foo, "namespace": "Y"}),
        ]
        for err, kwargs in tests:
            with self.subTest(err=err, given=kwargs):
                with self.assertRaisesRegex(ValueError, err):
                    await subject.get(**kwargs)

    async def test_raises_for_invalid_state(self) -> None:
        # NOTE: This test evaluates (what should be) an impossible state
        class Foo:
            ...

        subject = MOD.Registrar()
        record = subject.add(value=Foo, namespace="X")

        with self.subTest("corrupted registry"):
            # MUST test first
            del subject.register[record.uid]
            with self.assertRaisesRegex(RuntimeError, "unknown uid"):
                await subject.get(value=Foo)

        with self.subTest("corrupted lookup"):
            del subject.lookup[Foo][record.namespace]
            with self.assertRaisesRegex(RuntimeError, "orphaned value"):
                await subject.get(value=Foo)

    async def test_behavior_with_namespace(self) -> None:
        class FooA:
            ...

        class FooB:
            ...

        FooA.__name__ = "Foo"
        FooB.__name__ = "Foo"
        subject = MOD.Registrar()
        record_a = subject.add(value=FooA, namespace="A")
        record_b = subject.add(value=FooB, namespace="B")

        with self.subTest("namespace not required if given unique"):
            found = await subject.get(value=FooA)
            expected = record_a
            self.assertEqual(expected, found)

        with self.subTest("raise if no namespace and not unique"):
            with self.assertRaisesRegex(ValueError, "namespace required"):
                _ = await subject.get("foo")

        with self.subTest("namespace resolve name conflict"):
            found = await subject.get("foo", namespace="B")
            expected = record_b
            self.assertEqual(expected, found)

    async def test_returns_record(self) -> None:
        class Foo:
            ...

        subject = MOD.Registrar()
        record = subject.add(value=Foo, namespace="X")

        tests = [
            Foo,
            "Foo",
            "foo",
            record.uid,
        ]
        expected = record
        for given in tests:
            with self.subTest(given):
                found = await subject.get(given)
                self.assertEqual(expected, found)


# __END__
