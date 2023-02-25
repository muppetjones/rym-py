#!/usr/bin/env python3
""".

"""

import dataclasses as dcs
import itertools
import json
import logging
from collections import abc
from functools import singledispatch
from pathlib import Path
from typing import Any, Callable, Generator, Iterable, Mapping, Optional

from ._alias import Alias

try:
    import toml
except ImportError:
    toml = None

try:
    import yaml
except ImportError:
    yaml = None

LOGGER = logging.getLogger(__name__)
_DEFAULT = __file__


@dcs.dataclass
class AliasResolver:
    """Group of aliases."""

    aliases: Iterable[Alias]

    @classmethod
    def build(
        cls,
        *args,
        transforms: Optional[Iterable[Callable[[str], str]]] = _DEFAULT,
        **kwargs,
    ) -> "AliasResolver":
        """Build aliases to resolve.

        Arguments:
            *args: Supported formats as positional arguments
            transforms: Optional transforms to apply to all aliases.
                If given, will replace existing transforms on each alias.
                Use 'None' to disable all transformations
            **kwargs: Supported formats as keyword arguments
        See also:
            alias_factory
        """
        aliases = alias_factory(*args, transforms=transforms, **kwargs)
        return cls(aliases=aliases)


def alias_factory(
    *args, transforms: Optional[Iterable[Callable[[str], str]]] = None, **kwargs
) -> Iterable[Alias]:
    """Build aliases from multiple supported formats.

    Supported Formats:
        - Alias instances
        - Alias keywords
            e.g., {'identity': 'foo', 'aliases': 'bar', 'transform': 'upper'}
        - Alias mapping (does not support transform definition)
            e.g., {'foo': ['bar']}
        - Iterable of supported format
        - Encoding of supported format
            - May be string (json only)
            - May be file path (json, toml, yaml)

    Arguments:
            *args: Supported formats as positional arguments
            transforms: Optional transforms to apply to all aliases.
                Use 'None' to disable.
            **kwargs: Supported formats as keyword arguments
    Returns:
        Iterable of Alias instances.
    """
    aliases = list(
        itertools.chain(
            _yield_aliases(args),
            _yield_aliases(kwargs),
        )
    )
    if transforms != _DEFAULT:
        for alias in aliases:
            alias.set_transforms(transforms)
    return aliases


@singledispatch
def _yield_aliases(value: Any) -> Generator[Alias, None, None]:
    raise TypeError(f"invalid alias: {value}")


@_yield_aliases.register(str)
def _(value: str) -> Generator[Alias, None, None]:
    yield from _yield_aliases(json.loads(value))


@_yield_aliases.register(Alias)
def _(value: Alias) -> Generator[Alias, None, None]:
    yield value


@_yield_aliases.register(abc.Iterable)
def _(value: Iterable) -> Generator[Alias, None, None]:
    for item in value:
        yield from _yield_aliases(item)


@_yield_aliases.register(abc.Mapping)
def _(value: Mapping) -> Generator[Alias, None, None]:
    try:
        yield Alias(**value)
    except TypeError:
        for identity, aliases in value.items():
            yield Alias(identity, aliases)


@_yield_aliases.register(Path)
def _(value: Path) -> Generator[Alias, None, None]:
    cases = {
        ".json": json.dumps,
        ".toml": getattr(toml, "dumps", None),
        ".yaml": getattr(yaml, "safe_load", None),
        ".yml": getattr(yaml, "safe_load", None),
    }

    func = cases.get(value.suffix)
    if not func:
        raise ValueError(
            f"unavailable encoding: {value.suffix} ({value})"
        ) from None

    content = value.read_text()
    data = func(content)
    yield from _yield_aliases(data)


# __END__
