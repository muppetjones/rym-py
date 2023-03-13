#!/usr/bin/env python3

import dataclasses as dcs
import logging
from typing import Callable, Hashable, Iterable, Optional

from rym.alias.safesort import safesorted

from ._alias import Alias, AliasError

LOGGER = logging.getLogger(__name__)


@dcs.dataclass(frozen=True, eq=True)
class FrozenAlias:
    """Hashable Alias."""

    identity: Hashable
    _lookup: Iterable[Hashable] = dcs.field(repr=False)

    @classmethod
    def build(cls, *args, **kwargs) -> "FrozenAlias":
        alias = Alias(*args, **kwargs)
        return cls.clone(alias)

    @classmethod
    def clone(cls, alias: Alias) -> "FrozenAlias":
        return cls(identity=alias.identity, _lookup=tuple(alias.all_names()))

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
        return _sorted(self._lookup, **kwargs)

    def identify(self, value: Hashable) -> Hashable:
        if value in self._lookup:
            return self.identity
        raise AliasError(value)


# __END__
