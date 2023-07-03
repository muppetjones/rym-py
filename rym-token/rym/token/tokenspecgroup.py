#!/usr/bin/env python3
""".

"""

import logging
from typing import Tuple

from . import tokenspec
from .structures import TokenSpec

LOGGER = logging.getLogger(__name__)

TokenSubtypeSpec = Tuple[str, Tuple[str, ...]]


def grammar_word_subtypes() -> Tuple[TokenSubtypeSpec, ...]:
    # NOTE: Many words play multiple roles
    return (
        ("article", ("a", "an", "the")),
        (
            "conjunction",
            ("and", "nor", "but", "or", "yet", "so", "since", "because"),
        ),  # 'for'
        ("preposition", ("at", "by", "for", "from", "in", "of", "on", "with")),
    )


def grammar() -> Tuple[TokenSpec, ...]:
    return (
        tokenspec.punctuation(),
        tokenspec.word(grammar_word_subtypes()),
    )


def numeric() -> Tuple[TokenSpec, ...]:
    return (
        tokenspec.integer(),
        tokenspec.number(),
    )


def search() -> Tuple[TokenSpec, ...]:
    return (
        tokenspec.search_term(),
        tokenspec.uuid_string(),
        *temporal(),
        *numeric(),
        tokenspec.alphanum(
            (
                ("qualifier", ("before", "after", "since", "between")),
                ("quantifier", ("some", "all", "any")),
            )
        ),
    )


def temporal() -> Tuple[TokenSpec, ...]:
    return (
        tokenspec.timestamp(),  # ORDER MATTERS!
        tokenspec.date(),
        tokenspec.time(),
        tokenspec.day(),
        tokenspec.month(),
        tokenspec.reldate(),
    )


# __END__
