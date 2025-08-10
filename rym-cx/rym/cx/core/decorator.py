#!/usr/bin/env python3
"""Define core decorators.

Who hates long names and imports in libraries?
Probably everyone.
That's why you never see "pandas.DataFrame".

This module defines class decorators for "component" and "entity". These are imported
into the top module to make usage easy -- and short.

NOTE: This module imports _system, which imports registrar. Be mindful of import chaos.

NOTE: Archetype doesn't have a decorator. It _could_, but that would limit
    features and subvert expectations.
"""


from functools import partial
from typing import Optional, TypeVar

from . import _system

T = TypeVar("T")

# High-level decorators
# ======================================================================


def component(klass: Optional[T] = None) -> T:
    """Decorate a component class.

    Example:
        >>> from rym import cx
        >>> @cx.component
        ... class Health:
        ...     max_hp: int
        ...     current: int

    """
    return add_to_registry(klass, namespace="component")


def entity(klass: Optional[T] = None) -> T:
    """Decorate a entity class.

    Example:
        >>> from rym import cx
        >>> @cx.entity
        ... class Monster:
        ...     health: Health

    """
    return add_to_registry(klass, namespace="entity")


# Low-level decorators
# ======================================================================


def add_to_registry(
    klass: Optional[T] = None,
    *,
    namespace: Optional[str] = None,
) -> T:
    """Decorator used to add given klass to the global registry.

    NOTE: Registering an object adds __cx_reg_uid__ property to the object.

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
        return partial(add_to_registry, namespace=namespace)

    if not (namespace and klass):
        raise TypeError("namespace is required; provide as kwarg via decorator")

    registry = _system.get_registry()
    registry.add(namespace, klass)

    return klass


# __END__
