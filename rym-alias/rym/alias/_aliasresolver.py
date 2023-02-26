#!/usr/bin/env python3
"""
Use an AliasResolver to Manage Multiple Aliases
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> from rym.alias import AliasResolver
>>> import stringcase as sc
>>> x = AliasResolver.build(
...   prd=['prod'],
...   dev=['develop'],
... ).add(
...   alp=['alpha'],
...   transforms=[sc.titlecase],
... )
>>> x.identify('PROD')
'prd'
>>> x.identify('develop')
'dev'
>>> x.identify('Alpha')
'alp'

You can specify transforms that apply to all aliases
And if you need to provide an alias to a keyword, just use a dictionary.

>>> x.add({'transforms': 'etl'}) # doctest: +ELLIPSIS
AliasResolver(aliases=[...])
>>> x.identify('etl')
'transforms'

"""

import dataclasses as dcs
import itertools
import json
import logging
from collections import ChainMap, abc, defaultdict
from functools import singledispatch
from pathlib import Path
from pprint import pformat
from typing import Any, Callable, Generator, Iterable, Mapping, Optional

from ._alias import Alias, AliasError


def _load_pkg(names: Iterable[str]):
    """Safe import. Allow variable feature set based on available packages.

    Arguments:
        names: List of acceptable package names (with compatible interfaces).
    Returns:
        The loaded module or None.
    """
    import importlib

    for name in names:
        try:
            return importlib.import_module(name)
        except ImportError:
            continue
    return None


toml = _load_pkg(
    [
        "tomllib",  # py 3.11+
        "tomlkit",  # style-preserving
        "toml",
    ]
)
yaml = _load_pkg(["yaml"])

LOGGER = logging.getLogger(__name__)
_DEFAULT = __file__


class CollisionError(ValueError):
    """Raise for an alias collision."""


@dcs.dataclass
class AliasResolver:
    """Group of aliases."""

    aliases: Iterable[Alias]
    logger: logging.Logger = dcs.field(
        default=None, repr=False, hash=False, compare=False
    )
    _lookup: Mapping[str, int] = dcs.field(init=False, repr=False)
    _attempts: Mapping[str, int] = dcs.field(
        init=False,
        repr=False,
        hash=False,
        compare=False,
    )

    def __post_init__(self):
        self.logger = self.logger or LOGGER

        # setup alias internal data
        self._build_lookup_index()

    @classmethod
    def build(
        cls,
        *args,
        strict: bool = True,
        transforms: Optional[Iterable[Callable[[str], str]]] = _DEFAULT,
        logger: logging.Logger = None,
        _resolver: Callable = None,
        **kwargs,
    ) -> "AliasResolver":
        """Build aliases to resolve.

        Arguments:
            *args: Supported formats as positional arguments
            strict: If true, will raise if collisions detected.
            transforms: Optional transforms to apply to all aliases.
                If given, will replace existing transforms on each alias.
                Use 'None' to disable all transformations
            _resolver: Inject an alias factory.
            **kwargs: Supported formats as keyword arguments
        Returns:
            An AliasResolver instance.
        See also:
            alias_factory
        """
        _resolver = _resolver or resolve_aliases
        aliases = _resolver(*args, transforms=transforms, **kwargs)
        instance = cls(aliases=[], logger=logger)
        instance.add(aliases, strict=strict)
        return instance

    def _build_lookup_index(self) -> None:
        """Index alias lookup."""
        self._lookup = {k: i for i, x in enumerate(self.aliases) for k in x.all_names()}
        self._attempts = defaultdict(int, {k: 0 for k in self._lookup.keys()})

    def add(
        self,
        *args,
        strict: bool = True,
        transforms: Optional[Iterable[Callable[[str], str]]] = _DEFAULT,
        _resolver: Callable = None,
        **kwargs,
    ) -> "AliasResolver":
        """Add aliases to self."""
        _resolver = _resolver or resolve_aliases
        aliases = _resolver(*args, transforms=transforms, **kwargs)
        collisions = self.find_collisions(self.aliases, aliases)
        if not collisions:
            ...
        elif strict:
            raise CollisionError(collisions)
        else:
            self.logger.warning("Collisions detected: %s", collisions)

        self.aliases.extend(aliases)
        self._build_lookup_index()
        return self  # support chaining

    @classmethod
    def find_collisions(
        cls,
        *aliases: Iterable[Alias],
        logger: logging.Logger = None,
    ) -> Iterable[str]:
        """Check for alias collisions."""
        logger = logger or LOGGER
        lookup = ChainMap(*[x._lookup for x in resolve_aliases(aliases)])
        keys = set()
        lost = defaultdict(list)
        collisions = set()
        for child in lookup.maps:
            both = keys & child.keys()
            for k in both:
                lost[k].append(child[k])
            keys |= child.keys()
            collisions |= both
        logger.debug("Lost aliases due to collisions: %s", pformat(lost))
        return sorted(collisions)

    def identify(self, value: str) -> str:
        """Return identity for the given alias value.

        Arguments:
            value: Alias to match.
        Returns:
            Identity for the given alias.
        Raises:
            AliasError (KeyError) if unknown alias given.
        """
        self._attempts[value] += 1  # know which aliases are used / needed
        idx = self._lookup.get(value)  # faster than itrable and try:except
        if idx is None:
            raise AliasError(value)
        return self.aliases[idx].identity


def resolve_aliases(
    *args,
    transforms: Optional[Iterable[Callable[[str], str]]] = _DEFAULT,
    **kwargs,
) -> Iterable[Alias]:
    """Build aliases from multiple supported formats.

    Supported Formats:
        - Alias instances
        - Alias keywords
            e.g., {'identity': 'foo', 'aliases': 'bar', 'transform': 'upper'}
        - Alias mapping (does not support transform definition)
            e.g., {'foo': ['bar']}
        - None
        - Iterable of supported format
        - Encoding of supported format
            - May be string (json only)
            - May be file path (json, toml, yaml)

    NOTE: TOML requires a root object (not an array)

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
    if value is not None:
        raise TypeError(f"invalid alias: {value}")
    yield from []


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
            if identity == "aliases":
                yield from _yield_aliases(aliases)
            else:
                yield Alias(identity, aliases)


@_yield_aliases.register(Path)
def _(value: Path) -> Generator[Alias, None, None]:
    cases = {
        ".json": json.loads,
        ".toml": getattr(toml, "loads", None),
        ".yaml": getattr(yaml, "safe_load", None),
        ".yml": getattr(yaml, "safe_load", None),
    }

    func = cases.get(value.suffix)
    if not func:
        raise ValueError(f"unavailable encoding: {value.suffix} ({value})") from None

    content = value.read_text()
    data = func(content)
    yield from _yield_aliases(data)


# __END__
