#!/usr/bin/env python3
"""Test."""

import logging
from typing import Any
from unittest import TestCase, mock, skipIf

import rym.lpath.errors as MOD

try:
    from exceptiongroup import ExceptionGroup
except ImportError:
    # We don't _need_ exception group as the usage is behind a version check.
    # Exception handling for groups is a pain even with this package, so
    # we don't use it unless we're on 3.11+. However, the linters complain.
    pass

LOGGER = logging.getLogger(__name__)


class ThisTestCase(TestCase):
    """Base test case for the module."""

    def setUp(self) -> None:
        # Ensure test isolation
        initial_state = MOD.do_use_exception_groups()
        self.addCleanup(MOD.set_use_exception_groups, initial_state)


class TestExceptionGroupState(ThisTestCase):
    """Test behavior."""

    @skipIf(not MOD.can_use_exception_groups(), "Requires python 3.11+")
    def test_toggle_behavior(self) -> None:
        # Check repeated disable/enable -- should not impact
        initial_state = MOD.do_use_exception_groups()
        tests = [
            # (retval, expected, function)
            (initial_state, initial_state, MOD.do_use_exception_groups),
            (None, True, MOD.enable_exception_groups),
            (True, True, MOD.do_use_exception_groups),
            (None, False, MOD.disable_exception_groups),
            (False, False, MOD.do_use_exception_groups),
            (None, True, MOD.enable_exception_groups),
            (None, True, MOD.enable_exception_groups),
            (None, True, MOD.enable_exception_groups),
            (True, True, MOD.do_use_exception_groups),
            (None, False, MOD.disable_exception_groups),
            (None, False, MOD.disable_exception_groups),
            (None, False, MOD.disable_exception_groups),
            (False, False, MOD.do_use_exception_groups),
        ]
        for i, (retval, expected, func) in enumerate(tests):
            with self.subTest((i, expected, func.__name__)):
                result = func()
                found = MOD._DO_USE_EXCEPTION_GROUP
                self.assertEqual(retval, result)
                self.assertEqual(expected, found)

    def test_permanently_disabled_if_cannot_use_exception_groups(self) -> None:
        with mock.patch.object(MOD, "can_use_exception_groups") as mcan:
            mcan.return_value = False

            MOD.enable_exception_groups()
            found = MOD.do_use_exception_groups()
            expected = False
            self.assertEqual(expected, found)


class TestUnifiedItemAccessErrorHandler(ThisTestCase):
    """Test decorator."""

    def test_propagates_other_errors(self) -> None:
        tests = [RuntimeError, TypeError]
        mobj = mock.Mock()

        @MOD.unified_item_access_error_handler
        def accessor(instance: Any, key: str) -> Any:
            mobj()

        for exc_type in tests:
            mobj.side_effect = exc_type("test")
            with self.subTest(exc_type.__name__):
                with self.assertRaises(exc_type):
                    accessor({}, "foo")

    def test_unifies_no_groups(self) -> None:
        mobj = mock.Mock()

        @MOD.unified_item_access_error_handler
        def accessor(instance: Any, key: str) -> Any:
            mobj()

        with mock.patch.object(MOD, "can_use_exception_groups") as mcan:
            mcan.return_value = False

            key = "foo.bar"
            tests = [AttributeError, IndexError, KeyError]
            for exc_type in tests:
                mobj.side_effect = exc_type("test")
                with self.subTest(exc_type.__name__):
                    with self.assertRaisesRegex(MOD.InvalidKeyError, key):
                        accessor({}, key)

    @skipIf(not MOD.can_use_exception_groups(), "Requires py3.11+")
    def test_unifies_with_groups(self) -> None:
        MOD.enable_exception_groups()
        mobj = mock.Mock()

        @MOD.unified_item_access_error_handler
        def accessor(instance: Any, key: str) -> Any:
            mobj()

        key = "foo.bar"
        tests = [AttributeError, IndexError, KeyError]
        for exc_type in tests:
            mobj.side_effect = exc_type("test")
            with self.subTest(exc_type.__name__):

                with self.assertRaisesRegex(ExceptionGroup, key) as eg:
                    accessor({}, key)

                found = [isinstance(e, exc_type) for e in eg.exception.exceptions]
                self.assertTrue(any(found))


# __END__
