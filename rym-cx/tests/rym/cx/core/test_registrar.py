#!/usr/bin/env python3
"""Test the registry class."""

from unittest import TestCase

import rym.cx.core.registrar as MOD


class ThisTestCase(TestCase):
    """Base test case for the module."""


class TestInit(ThisTestCase):
    """Test class init and properties."""

    def test_initializes_with_empty_registrar(self) -> None:
        subject = MOD.Registrar()
        expected = {}
        found = subject.register
        self.assertEqual(expected, found)


class TestAdd(ThisTestCase):
    """Test function."""

    def test_raises_if_name_conflict_detected(self) -> None:
        class Foo:
            ...

        class Meh:
            ...

        Meh.__name__ = "Foo"
        subject = MOD.Registrar()
        record = subject.add(Foo, namespace="X")

        with self.subTest("igore true duplicates"):
            subject.add(Foo, namespace=record.namespace)

        with self.subTest("disallow intra-namespace commonality"):
            with self.assertRaises(ValueError):
                subject.add(Meh, namespace=record.namespace)

        with self.subTest("allow inter-namespace commonality"):
            subject.add(Meh, namespace="Y")

    def test_stores_record(self) -> None:
        class Foo:
            ...

        subject = MOD.Registrar()
        subject.add(Foo, namespace="X")

        # NOTE: The record uid is auto-generated and must match.
        record = MOD.Record.new(item=Foo, namespace="X")
        expected = {record.uid: record}
        found = subject.register
        self.assertEqual(expected, found)

    def test_sets_uid_property(self) -> None:
        class Foo:
            ...

        subject = MOD.Registrar()
        record = subject.add(Foo, namespace="X")

        expected = record.uid
        found = Foo.__uid__
        self.assertEqual(expected, found)


class TestGet(ThisTestCase):
    """Test function."""

    def test_raises_for_unknown_record(self) -> None:
        class Foo:
            ...

        class Bar:
            ...

        subject = MOD.Registrar()
        subject.add(Foo, namespace="X")

        tests = [
            # (err, given)
            ("unknown value", {"value": Bar}),
            ("not in namespace", {"value": Foo, "namespace": "Y"}),
        ]
        for err, kwargs in tests:
            with self.subTest(err=err, given=kwargs):
                with self.assertRaisesRegex(ValueError, err):
                    subject.get(**kwargs)

    def test_raises_for_invalid_state(self) -> None:
        # NOTE: This test evaluates (what should be) an impossible state
        class Foo:
            ...

        subject = MOD.Registrar()
        record = subject.add(Foo, namespace="X")

        with self.subTest("corrupted registry"):
            # MUST test first
            del subject.register[record.uid]
            with self.assertRaisesRegex(RuntimeError, "unknown uid"):
                subject.get(Foo)

        with self.subTest("corrupted lookup"):
            del subject.lookup[Foo][record.namespace]
            with self.assertRaisesRegex(RuntimeError, "orphaned value"):
                subject.get(Foo)

    def test_behavior_with_namespace(self) -> None:
        class FooA:
            ...

        class FooB:
            ...

        FooA.__name__ = "Foo"
        FooB.__name__ = "Foo"
        subject = MOD.Registrar()
        record_a = subject.add(FooA, namespace="A")
        record_b = subject.add(FooB, namespace="B")

        with self.subTest("namespace not required if given unique"):
            found = subject.get(FooA)
            expected = record_a
            self.assertEqual(expected, found)

        with self.subTest("raise if no namespace and not unique"):
            with self.assertRaisesRegex(ValueError, "namespace required"):
                _ = subject.get("foo")

        with self.subTest("namespace resolve name conflict"):
            found = subject.get("foo", namespace="B")
            expected = record_b
            self.assertEqual(expected, found)

    def test_returns_record(self) -> None:
        class Foo:
            ...

        subject = MOD.Registrar()
        record = subject.add(Foo, namespace="X")

        tests = [
            Foo,
            "Foo",
            "foo",
            record.uid,
        ]
        expected = record
        for given in tests:
            with self.subTest(given):
                found = subject.get(given)
                self.assertEqual(expected, found)


# __END__
