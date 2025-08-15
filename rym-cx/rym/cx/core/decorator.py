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
from collections.abc import Callable, Iterable
from functools import partial, wraps
from typing import Optional, TypeVar

from . import _catalog, _inventory

T = TypeVar("T")

# Add to catalog
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


# Retrieve By
# ======================================================================


def retrieve(
    func: Optional[Callable[..., T]] = None, **component_groups: Iterable[T]
) -> Callable:
    """Lookup entities with commonents and pass into wrapped function.

    TODO: Sleep now, then figure out how to describe this more clearly.

    Arguments:
        func: The function being wrapped.
        **kwargs: One or more component classes to match against.
    Returns:
        The wrapped function.
    """
    if func is None:
        return partial(retrieve, **component_groups)

    @wraps(func)
    async def _wrapper(*args, **kwargs) -> T:
        kwargs.update(
            {
                k: await _inventory.retrieve_by_component(*v)
                for k, v in component_groups.items()
            }
        )
        return await func(*args, **kwargs)

    return _wrapper


# __END__
