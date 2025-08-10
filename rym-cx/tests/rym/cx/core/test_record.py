#!/usr/bin/env python3
"""Test."""

import logging
from unittest import TestCase

import rym.cx.core.record as MOD

LOGGER = logging.getLogger(__name__)


class ThisTestCase(TestCase):
    """Base test case for the module."""


class TestCatalogRecord(ThisTestCase):
    """Test named tuple."""

    def test_new_generates_consistent_uid_within_namespace(self) -> None:
        a = MOD.CatalogRecord.new("x", "Foo")
        b = MOD.CatalogRecord.new("x", "Foo")
        c = MOD.CatalogRecord.new("x", "Bar")
        d = MOD.CatalogRecord.new("y", "Foo")

        assert a.uid == b.uid
        assert a.uid != c.uid
        assert a.uid != d.uid


class TestInventoryRecord(ThisTestCase):
    """Test named tuple."""

    def test_new_generates_unique_id_on_every_call(self) -> None:
        a = MOD.InventoryRecord.new("x", "Foo")
        b = MOD.InventoryRecord.new("x", "Foo")
        c = MOD.InventoryRecord.new("x", "Bar")
        d = MOD.InventoryRecord.new("y", "Foo")

        assert a.uid != b.uid
        assert a.uid != c.uid
        assert a.uid != d.uid


# __END__
