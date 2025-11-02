#!/usr/bin/env python3
"""Backwards compatible error handling with python 3.11 support.

PEP 654 outlines ExceptionGroups and except* added in 3.11. While the former
is available via the exceptiongroup package, the latter is not -- and it
requires a significant work around. Worse still, the asterisk is necessary
to catch targeted errors; i.e., there is no way to make ExceptionGroups
backwards compatible.

In lpath v1.0.0, a single error type was added to encapsulate all of the lookup
errors: AttributeError for objects, IndexError for sequences, and KeyError for
dictionaries. With ExceptionGroups, each of these errors may be individually
handled; however, we would either require 3.11 as the minimum py version or
we fragment the user interface, which I am loathe to do.

Instead, we'll allow users to enable or disable ExceptionGroups at their
discretion, and we'll add a decorator to handle the error unification.
"""


import functools
import logging
from sys import version_info
from typing import Any, Callable, TypeVar

try:
    from exceptiongroup import ExceptionGroup
except ImportError:
    # We don't _need_ exception group as the usage is behind a version check.
    # Exception handling for groups is a pain even with this package, so
    # we don't use it unless we're on 3.11+. However, the linters complain.
    pass


LOGGER = logging.getLogger(__name__)


# ExceptionGroup State
# ======================================================================

_CAN_USE_EXCEPTION_GROUP = version_info.major == 3 and version_info.minor >= 11
_DO_USE_EXCEPTION_GROUP = False  # DISABLED by default


def can_use_exception_groups() -> bool:
    """Return True if ExceptionGroup is available, i.e., py3.11+."""
    return _CAN_USE_EXCEPTION_GROUP


def do_use_exception_groups() -> bool:
    """Return True if ExceptionGroup is enabled; requires py3.11+."""
    return can_use_exception_groups() and _DO_USE_EXCEPTION_GROUP


def disable_exception_groups() -> None:
    """Disable ExceptionGroup usage (default)."""
    set_use_exception_groups(False)


def enable_exception_groups() -> None:
    """Enable ExceptionGroup usage; requires py3.11+"""
    set_use_exception_groups(True)


def set_use_exception_groups(value: bool) -> None:
    """Enable or disable ExceptionGroup usage; requires py3.11+."""
    global _DO_USE_EXCEPTION_GROUP
    if not value:
        _DO_USE_EXCEPTION_GROUP = False
    elif can_use_exception_groups():
        # Technically, we don't _need_ this thanks to the func abstraction
        # (i.e., b/c "do_use" also checks if we can)
        # but, it prevents someone from accidentally setting it.
        _DO_USE_EXCEPTION_GROUP = True
    else:
        LOGGER.debug("Cannot enable exception groups; requires py3.11+")


# Errors
# ======================================================================


class KeyFormatError(ValueError):
    """Raise if given an unsupported key type."""


class InvalidKeyError(KeyError):
    """Raise if given an invalid key, regardless of the object type.

    This error simplifies the user interface so that the user does not need to care
    what kind of error is raised.
    """


class InvalidWildcardError(ValueError):
    """Raise if given a key with a wildcard (asterisk8) that cannot be completed.

    e.g., "foo.*.bar" given a mapping {"foo": []}
    """


# Unified Error Handler
# ======================================================================

T = TypeVar("T")


def unified_item_access_error_handler(func: Callable[..., T]) -> Callable[..., T]:
    """Catch item access errors and raise as unified error.

    NOTE: If enabled, will raise an ExceptionGroup with all relevant groups.
        Otherwise, will raise InvalidKeyError.
    """

    def _wrapper_no_group(instance: Any, key: Any, *args, **kwargs) -> T:
        # Use a single error type; add a note if we can
        try:
            return func(instance, key, *args, **kwargs)
        except (KeyFormatError, InvalidKeyError):
            raise
        except (AttributeError, KeyError, IndexError, InvalidWildcardError) as err:
            emsg = str(err).strip('"')
            msg = f"{emsg} ({err.__class__.__name__})"
            raise InvalidKeyError(f"{key}; {msg}") from err
        except ValueError as err:
            emsg = str(err).strip('"')
            msg = f"{emsg} ({err.__class__.__name__})"
            raise KeyFormatError(f"{key}; {msg}") from err

    def _wrapper_with_group(instance: Any, key: Any, *args, **kwargs) -> T:
        # Use exception groups
        try:
            return func(instance, key, *args, **kwargs)
        except (
            AttributeError,
            KeyError,
            IndexError,
            InvalidWildcardError,
            ExceptionGroup,
        ) as err:
            raise ExceptionGroup(key, [InvalidKeyError(key), err])
        except ValueError as err:
            raise ExceptionGroup(key, [KeyFormatError(key), err])

    @functools.wraps(func)
    def _wrapper(*args, **kwargs) -> T:
        # NOTE: Do _not_ make this static or we'll have import order concerns.
        #   i.e., we'd need to enable or disable BEFORE we import any wrapped funcs.
        if do_use_exception_groups():
            return _wrapper_with_group(*args, **kwargs)
        else:
            return _wrapper_no_group(*args, **kwargs)

    return _wrapper


# __END__
