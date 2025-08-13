#!/usr/bin/env python3
"""Define global system parameters.

NOTE: The contents of this module are intended for use within rym.cx modules.

NOTE: This module is a bit of a smell. Globals and singletons can get messy
    and should be avoided. However, we want some functionality provided behind
    the scenes, and we can't reliably do that without having a single registry
    and index to track entities and instances, etc. The best we can do (for now)
    is make sure it's at least safe.

NOTE: Not a big fan of "_global" as a name, but it is apt.
    Conversely, "app" may imply that this is the entrypoint or driver,
    and "system" is part of ECS.
    Most users shouldn't need to use this directly.
"""

import logging
from typing import Optional

from .registrar import Registrar

_CATALOG = None  # type: Registrar


async def clear_catalog_async(logger: Optional[logging.Logger] = None) -> None:
    """Clear the current global catalog and catalog instance.

    See also:
        clear_catalog
    """
    global _CATALOG
    if not _CATALOG:
        return  # EARLY EXIT: no catalog -- ignore
    logger = logger or logging.getLogger(__name__)

    logger.warning("Clearing cx catalog")
    await _CATALOG.clear_async()
    _CATALOG = None


def clear_catalog(logger: Optional[logging.Logger] = None) -> None:
    """Clear the current global catalog and catalog instance.

    In case someone is storing a reference to the catalog, clear the instance.
    In case someone is using the global variable directly, clear the variable, too.

    NOTE: This pattern is technically fragile. We could just use the same one
        or create a new global instance; however, that could lead to undefined
        behavior is someone is doing something bad. By clearing both, any offending
        code should fail more directly.

    NOTE: Even more technically, this pattern is not thread safe or multiproc safe.
        Creating a new instance in the middle of execution will result in the
        shared instance being unavailable to child threads or procesesses.
        While reusing the same catalog wouldn't guarantee safety, if the instance
        is created early enough, it _may_ be shared automatically, though likely
        it would be a separate instance, which would be bad anyway.

    NOTE: More technically still, it's a moot point. This function is largely
        intended for testing, and the catalog should not be modified at runtime.
        (The index will be a separate matter). In a worst case scenario, we'd
        use this to reset and then rebuild the catalog, but at that point we
        need much more sophisticated error handling anyway.

    TODO: Make this thread and multiprocess safe.

    Arguments:
        None
    Returns:
        None
    """
    global _CATALOG
    if not _CATALOG:
        return  # EARLY EXIT: no catalog -- ignore
    logger = logger or logging.getLogger(__name__)

    logger.warning("Clearing cx catalog")
    _CATALOG.clear()
    _CATALOG = None


def get_catalog() -> Registrar:
    """Return a static catalog.

    This function will return the same registrar every time,
    i.e., the _global_ catalog. Multiple registrar instances may exist at any
    given time, but only one is the global catalog.

    Arguments:
        None
    Returns:
        A static catalog instance.
    """
    global _CATALOG
    if not _CATALOG:
        _CATALOG = Registrar(label="cat")
    return _CATALOG


# __END__
