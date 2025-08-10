#!/usr/bin/env python3
"""Define core decorators."""


from functools import partial
from typing import Optional, TypeVar

from . import _system

T = TypeVar("T")


def add_to_registry(
    klass: Optional[T] = None,
    *,
    namespace: Optional[str] = None,
) -> T:
    """Decorator used to add given klass to the global registry.

    NOTE: Registering an object adds __cx_uid__ property to the object.

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
