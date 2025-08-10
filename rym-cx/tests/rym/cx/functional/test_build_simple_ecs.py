#!/usr/bin/env python3
"""Test."""

import logging
from typing import Iterable, TypeVar
from unittest import TestCase

from rym import cx
from rym.cx.core import _global

T = TypeVar("T")

LOGGER = logging.getLogger(__name__)

# Setup
# ======================================================================
# NOTE: We MUST define the EC instances prior to testing to allow each
#   test access to the entities and compontents. We _could_ make one big
#   test case, but that would be difficult to manage (and smelly).
# tl;dr: Define basic classes here. Test usage below.


def setUpModule() -> None:
    _global.clear_catalog()


def tearDownModule() -> None:
    _global.clear_catalog()


# ----------------------------------
# Kate is designing a simple game.
# She knows she'll need to track location and health of various
# entities. It's a t 2D game, so she'll only need an x and y axis.
# And for now, she'll only track total and current number of HP.
# By default, health should always start at "full"


@cx.component
class Location:
    x: int
    y: int


@cx.component
class Health:
    total: int
    current: int = -1

    def __post_init__(self) -> None:
        self.current = self.current if self.current >= 0 else self.total


# ----------------------------------
# Kate knows she needs two basic archetypes: Animate and Inanimate.
# For now, inanimate objects only have a location while animate objects need
# location and health.

Inanimate = cx.Archetype(Location, without=[Health])
Animate = cx.Archetype(Location, Health)

# ----------------------------------
# Kate knows the player will start in the jungle, navigating around foliage and
# fignting a few enemies, which gives her the first three entities in her game.
# She realizes that Player and Monster have the same components
# and that she accidentally swapped the order, but she does not
# expect that to be a problem.


@cx.entity
class Plant:
    loc: Location


@cx.entity
class Player:
    health: Health
    loc: Location


@cx.entity
class Monster:
    loc: Location
    health: Health


# ----------------------------------
# Kate wants to be able to retrieve injured entites


@cx.get_entities(with_component=[Health])
def get_injured(entities: Iterable[T]) -> Iterable[T]:
    injured = [x for x in entities if x.health.current > x.health.total]
    return injured


# Tests
# ======================================================================


class ThisTestCase(TestCase):
    """Base test case for the module."""


class TestBehavior(ThisTestCase):
    """Test behavior."""

    def test_each_component_registered(self) -> None:
        # Kate checks that the components have been registered
        tests = [Health, Location, Plant, Player, Monster]
        for component in tests:
            with self.subTest(component.__name__):
                expected = cx.core.generate_uid("component", component.__name__)
                found = cx.get_component_id(component)
                self.assertEqual(expected, found)

    def test_each_archetype_registered(self) -> None:
        # Kate checks that the archetypes have been registered
        tests = [Animate, Inanimate]
        for archetype in tests:
            with self.subTest(archetype.__name__):
                expected = cx.core.generate_uid("archetype", archetype.__name__)
                found = cx.get_archetype_id(archetype)
                self.assertEqual(expected, found)

    def test_each_entity_registered(self) -> None:
        # Kate checks that the archetypes have been registered
        tests = [Plant, Player, Monster]
        for entity in tests:
            with self.subTest(entity.__name__):
                expected = cx.core.generate_uid("entity", entity.__name__)
                found = cx.get_entity_id(entity)
                self.assertEqual(expected, found)

    def test_basic_ecs(self) -> None:
        # Kate starts the player at the center of the screen with full health
        player = Player(health=100, loc=(0, 0))

        # She then adds three plants ...
        plants = [
            cx.add_entity(Plant, loc=(1, 2)),
            cx.add_entity("Plant", loc=(0, 3)),
            cx.add_entity("plant", loc=(-1, -3)),
        ]

        # ... and two monsters, one of which is already injured
        monsters = cx.add_entities(
            Monster,
            [
                {"loc": (-1, 2), "health": 40},
                {"loc": (2, -1), "health": (40, 30)},
            ],
        )

        # With everything setup, she starts checking the integrity of the system.
        # First, she looks for the injured monster:
        with self.subTest("retrieve injured monster"):
            expected = [monsters[1]]
            found = get_injured()
            self.assertEqual(expected, found)

        # Second, she checks that Players and Monsters share an Archetype
        with self.subTest("shared archetype"):
            expected = cx.get_archetype(player)
            found = cx.get_archetype(monsters[0])
            self.assertEqual(expected, found)

        # Third, she checks that Plants do not share an archetype with players
        with self.subTest("different archetype"):
            expected = cx.get_archetype(player)  # type: tuple[cx.Archetype]
            found = cx.get_archetype(plants[0])  # type: tuple[cx.Archetype]
            self.assertNotEqual(expected, found)


# __END__
