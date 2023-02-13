#!/usr/bin/env python3
"""Test."""

import logging
from unittest import TestCase

import mjb.alias as MOD

LOGGER = logging.getLogger(__name__)


class ThisTestCase(TestCase):
    """Base test case for the module."""


class TestAlias(ThisTestCase):
    """Test function."""

    def test_something(self):
        self.fail()

    # def test_something_else(self):
    #     self.fail()


# __END__
