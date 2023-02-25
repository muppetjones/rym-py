#!/usr/bin/env python3
""".

"""

import dataclasses as dcs
import logging
from collections import defaultdict
from typing import Callable, Iterable, Mapping

from . import variation

LOGGER = logging.getLogger(__name__)


class AliasError(KeyError):
    ...


def _default_transforms() -> Iterable[Callable[[str], str]]:
    return [
        variation.upper,
        variation.lower,
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

    identity: str
    aliases: Iterable[str]
    transforms: Iterable[Callable[[str], str]] = dcs.field(
        default_factory=_default_transforms
    )
    logger: logging.Logger = None
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
        self.transforms = self.transforms or []

        # setup alias internal data
        opts = self.names
        self._attempts = defaultdict(int, {k: 0 for k in self.names})
        self._lookup = {
            **{k: 1 for k in opts},
            **{func(name): 1 for name in opts for func in self.transforms},
        }

    @property
    def names(self) -> Iterable[str]:
        return [self.identity, *self.aliases]

    def add_alias(self, value: str) -> None:
        """Add given alias to lookup, including transformed names."""
        if value in self.aliases:
            self.logger.warning("existing alias: %s", value)
            return  # do not add more than once
        lookup = {func(value): 1 for func in self.transforms}
        self._lookup.update(lookup)
        self.aliases.append(value)

    def add_transform(self, func: Callable[[str], str]) -> None:
        """Add given transform and update alias lookup."""
        if func in self.transforms:
            self.logger.warning("existing transform: %s", func)
            return  # do not add more than once
        lookup = {func(k): 1 for k in self.names}
        self._lookup.update(lookup)
        self.transforms.append(func)

    def all_aliases(self) -> Iterable[str]:
        """Return all known aliases and transformations."""
        return sorted(self._lookup.keys())

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


# __END__
