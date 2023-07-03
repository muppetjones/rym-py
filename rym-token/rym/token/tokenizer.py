#!/usr/bin/env python3
"""
Tokenize Strings
^^^^^^^^^^^^^^^^

The `tokenize` function is a generator that scans a string for certain
patterns and returns matched substrings with their location.

>>> from rym.token import tokenize
>>> text = "42 is an integer; 2023-10-30T21:30:00Z is a date string"
>>> list(tokenize(text))
[Token(type='INTEGER', value=42, line=0, column=0), Token(type='WORD', value='is', line=0, column=3), Token(type='WORD', value='an', line=0, column=6), Token(type='WORD', value='integer', line=0, column=9), Token(type='PUNCTUATION', value=';', line=0, column=16), Token(type='TIMESTAMP', value=datetime.datetime(2023, 10, 30, 21, 30, tzinfo=datetime.timezone.utc), line=0, column=18), Token(type='WORD', value='is', line=0, column=39), Token(type='WORD', value='a', line=0, column=42), Token(type='WORD', value='date', line=0, column=44), Token(type='WORD', value='string', line=0, column=49)]

While `rym.token` provides several token specifications, you may also
provide your own. Patterns are regex strings, and matching is case sensitive.

>>> from rym.token import TokenSpec
>>> spec = TokenSpec("BOOL", r"True|False")
>>> text = "I prefer True/False over multiple choice"
>>> list(tokenize(text, [spec]))
[Token(type='BOOL', value='True', line=0, column=9), Token(type='BOOL', value='False', line=0, column=14)]

Type Handlers
-------------

You may also provide a type handler to customize the final value. This
feature should be used with care as it may prevent recreation of the
input text from the tokens. Type handlers are included in a few of the
included spec: `integer`, `number`, `timestamp`, `date`, and `time`.

>>> spec = TokenSpec(
...     "BOOL", r"True|False",
...     lambda x: True if x.lower() == 'true' else False)
>>> list(tokenize(text, [spec]))
[Token(type='BOOL', value=True, line=0, column=9), Token(type='BOOL', value=False, line=0, column=14)]


Subtypes
--------

You may also define subtypes for a type specification. These are evaluated prior
to execution of a type handler and are case-insensitive.

>>> from rym.token.tokenspec import build_subtype_assignment
>>> subtypes = (
...     ('TRUE', ('true', )),
...     ('FALSE', ('false',)),
... )
>>> subtype = build_subtype_assignment(subtypes)
>>> spec = TokenSpec(
...     "BOOL",
...     r"True|False",
...     lambda x: True if x.lower() == 'true' else False,
...     subtype=subtype)
>>> list(tokenize(text, [spec]))
[Token(type='TRUE', value=True, line=0, column=9), Token(type='FALSE', value=False, line=0, column=14)]

See Also
^^^^^^^^
- https://docs.python.org/3/library/re.html?highlight=re#writing-a-tokenizer
"""  # noqa

import logging
from typing import Callable, Iterable, Tuple

from .regex import combine_regex
from .structures import Token, TokenSpec
from .tokenspec import newline, punctuation, word
from .tokenspecgroup import numeric, temporal

try:
    from functools import cache
except ImportError:  # pragma: no cover
    from functools import lru_cache

    cache = lru_cache(maxsize=None)


LOGGER = logging.getLogger(__name__)


@cache
def get_default_specs() -> Tuple[TokenSpec, ...]:
    """Return tuple of (type, pattern, callable)."""
    return (*temporal(), *numeric(), word(), punctuation())


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
        type_ = subtype(value, group_name)
        value = handler(value)
        yield Token(type_, value, line_num, column)


# __END__
