#!/usr/bin/env python3
""".

See also:
    https://docs.python.org/3/library/re.html?highlight=re#writing-a-tokenizer
"""

import logging
from typing import Callable, Iterable, Tuple

from .regex import combine_regex
from .structures import Token, TokenSpec
from .tokenspec import newline, punctuation, word

try:
    from functools import cache
except ImportError:  # pragma: no cover
    from functools import lru_cache

    cache = lru_cache(maxsize=None)


LOGGER = logging.getLogger(__name__)


@cache
def get_default_specs() -> Tuple[TokenSpec, ...]:
    """Return tuple of (type, pattern, callable)."""
    return (word(), punctuation())


def tokenize(
    block: str,
    specs: Iterable[Callable[..., TokenSpec]] = None,
) -> Iterable[Token]:
    """Given a string, identify contextual tokens."""
    specs = [*(specs or get_default_specs()), newline()]
    pattern = combine_regex(specs)
    handlers = {k: v for k, _, v, _ in specs if v}
    subtypes = {k: v for k, _, _, v in specs if v}

    def _as_is(v: str) -> str:
        return v

    def _base_type(v: str, k: str) -> str:
        return k

    line_num = 0
    line_start = 0
    for match in pattern.finditer(block):
        group_name = match.lastgroup
        if group_name == "NEWLINE":
            line_num += 1
            line_start = match.end()
            continue

        value = match.group()
        column = match.start() - line_start
        handler = handlers.get(group_name, _as_is)
        subtype = subtypes.get(group_name, _base_type)
        value = handler(value)
        type_ = subtype(value, group_name)
        yield Token(type_, value, line_num, column)


# __END__
