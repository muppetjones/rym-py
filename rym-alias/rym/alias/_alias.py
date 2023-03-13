#!/usr/bin/env python3
"""
Create an Alias
^^^^^^^^^^^^^^^

>>> from rym.alias import Alias
>>> x = Alias('prd', aliases=['prod', 'production'])
>>> x.identify('prod')
'prd'
>>> x.identify('PROD')
'prd'
>>> x.identity
'prd'
>>> x.all_names()
['PRD', 'PROD', 'PRODUCTION', 'prd', 'prod', 'production']


Specify Transformations
^^^^^^^^^^^^^^^^^^^^^^^

Upper and lower case transformations are performed by default, but additional
transformations may be provided, too.

> Note: A `lambda` isn't needed in this example as `snakecase` matches the
> expected `Callable[[str], str]` signature already.

>>> from rym.alias import Alias
>>> import stringcase as sc
>>> x = Alias('fooBar', [], transforms=[lambda x: sc.snakecase(x)])
>>> x.identify('fooBar')
'fooBar'
>>> x.identify('foo_bar')
'fooBar'
>>> x.all_names()
['fooBar', 'foo_bar']

"""

import dataclasses as dcs
import logging
from collections import abc, defaultdict
from functools import singledispatch
from typing import (
    Any,
    Callable,
    Generator,
    Hashable,
    Iterable,
    Mapping,
    Optional,
    Tuple,
)

from . import variation
from .safesort import safesorted

LOGGER = logging.getLogger(__name__)


class AliasError(KeyError):
    ...


def _default_transforms() -> Iterable[Callable[[str], str]]:
    return [
        variation.upper,
        variation.lower,
        variation.capitalize,
    ]


@dcs.dataclass
class Alias:
    """Simple name lookup.

    - Provides basic name lookup.
    - Support for enumerating common (or custom) variations, including
        upper and lower case or (de)essing.

    Attributes:
        identity: The "true name" of the alias.
        aliases: An iterable of names to alias.
        transforms: An iterable of functions to apply to each alias.
            Each function should take one string and return one string.
            Default: Upper and lower case of each alias.
    """

    identity: Hashable
    aliases: Iterable[Hashable]
    transforms: Iterable[Callable[[Hashable], Hashable]] = dcs.field(
        default_factory=_default_transforms
    )
    strict: bool = False
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
        # allow users to explicitly provide 'None"
        self.aliases = self.aliases or []
        self.logger = self.logger or LOGGER
        self.transforms = resolve_variations(self.transforms)

        # support single alias
        if isinstance(self.aliases, str):
            self.aliases = [self.aliases]

        # setup alias internal data
        opts = self.names
        self._attempts = defaultdict(int, {k: 0 for k in self.names})
        self._lookup = {
            **{k: 1 for k in opts},
            **dict(self._yield_lookup(opts, self.transforms, strict=self.strict)),
        }

    @property
    def names(self) -> Iterable[str]:
        return [self.identity, *self.aliases]

    @staticmethod
    def _yield_lookup(
        opts: Iterable[Hashable],
        transforms: Iterable[Callable],
        strict: bool,
    ) -> Tuple[Hashable, int]:
        """Yield (name, 1) tuples for lookup.

        Arguments:
            opts: One or more lookup names.
            transforms: One or more transforms to apply to each name.
            strict: If true, will raise if unable to apply transform.
        """
        for name in opts:
            for func in transforms:
                try:
                    yield (func(name), 1)
                except Exception:
                    if strict:
                        raise RuntimeError(
                            f"unable to create lookup via {func} while strict: {name}"
                        )
                    yield (name, 1)

    def add_alias(self, value: str) -> None:
        """Add given alias to lookup, including transformed names."""
        if value in self.aliases:
            self.logger.warning("existing alias: %s", value)
            return  # do not add more than once
        lookup = self._yield_lookup([value], self.transforms, strict=self.strict)
        self._lookup.update(lookup)
        self.aliases.append(value)

    def all_names(
        self,
        _sorted: Optional[Callable] = None,
        **kwargs,
    ) -> Iterable[str]:
        """Return all known aliases and transformations.

        Arguments:
            _sorted: Inject sorting function. Uses rym.alias.safesorted by default.
            **kwargs: Keywords for "sorted".
        """
        _sorted = _sorted or safesorted
        return _sorted(self._lookup.keys(), **kwargs)

    def add_transform(self, value: Callable[[str], str]) -> None:
        """Add given transform and update alias lookup."""
        for func in resolve_variations(value):
            if func in self.transforms:
                self.logger.warning("existing transform: %s", func)
                return  # do not add more than once
            lookup = self._yield_lookup(self.names, [func], strict=self.strict)
            self._lookup.update(lookup)
            self.transforms.append(func)

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
        match = self._lookup.get(value)  # faster than itrable and try:except
        if not match:
            raise AliasError(value)
        return self.identity

    def set_transforms(self, value: Iterable[Callable[[str], str]]) -> None:
        """Replace current transforms and update lookup.

        Arguments:
            value: Iterable of callables. None to clear  current.
        Returns:
            None
        """
        value = resolve_variations(value)
        opts = self.names
        lookup_gen = self._yield_lookup(self.names, value, strict=self.strict)
        lookup = {
            **{k: 1 for k in opts},
            **dict(lookup_gen),
        }
        self._lookup = lookup
        self.transforms = value[:]


# resolve variation
# ----------------------------------


def resolve_variations(value: Any) -> Callable[[str], str]:
    """Resolve given value into callables.

    Supported:
        - string names (see rym.alias.variation)
        - callables (should take and return a single string)
        - iterables of either of the others

    Arguments:
        value: One of the supported input.
    Returns:
        An iterable of resolved variation callables.
    Raises:
        TypeError for invalid input.
    """
    return list(_resolve_variations(value))


@singledispatch
def _resolve_variations(value: Any) -> Generator[Callable[[str], str], None, None]:
    if value is not None:
        raise TypeError(f"invalid variation: {value}")
    yield from []


@_resolve_variations.register(str)
def _(value: str) -> Generator[Callable[[str], str], None, None]:
    yield getattr(variation, value)


@_resolve_variations.register(abc.Callable)
def _(value: Callable) -> Generator[Callable[[str], str], None, None]:
    yield value


@_resolve_variations.register(abc.Iterable)
def _(value: Iterable) -> Generator[Callable[[str], str], None, None]:
    for item in value:
        yield from _resolve_variations(item)


# __END__
