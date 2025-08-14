#!/usr/bin/env python3
"""Define core decorators.

Who hates long names and imports in libraries?
Probably everyone.
That's why you never see "pandas.DataFrame".

This module defines class decorators for "component" and "entity". These are imported
into the top module to make usage easy -- and short.

NOTE: This module imports _global, which imports catalog. Be mindful of import chaos.

NOTE: Archetype doesn't have a decorator. It _could_, but that would limit
    features and subvert expectations.
"""


import dataclasses as dcs
from functools import partial
from typing import Optional, TypeVar

from . import _catalog

T = TypeVar("T")

# High-level decorators
# ======================================================================
# See also:
#   .component.component


# Low-level decorator support
# ======================================================================


def add_to_catalog(
    klass: Optional[T] = None,
    *,
    namespace: Optional[str] = None,
) -> T:
    """Decorator used to add given klass to the global registry.

    NOTE: Registering an object adds __cx_cat_uid__ property to the object.

    NOTE: Both parameters are required. They are optional to allow decorator kwargs.

    NOTE: Do NOT use async here.

    Arguments:
        klass: The class to add (and modify)
        namespace: The namespace to register the klass with.
    Returns:
        The modified class.
    Raises:
        TypeError if both parameters are not provided.
    """
    if namespace and not klass:
        return partial(add_to_catalog, namespace=namespace)

    if not (namespace and klass):
        raise TypeError("namespace is required; provide as kwarg via decorator")

    registry = _catalog.get_catalog()
    registry.add(namespace, klass)

    # also apply dataclass
    # -- we want everything that this provides, even if this is a little too magic
    dklass = dcs.dataclass(klass)
    return dklass


# Supporting functions
# ======================================================================


# __END__
