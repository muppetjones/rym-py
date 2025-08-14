#!/usr/bin/env python3
"""Test."""

import logging
from typing import Iterable, TypeVar
from unittest import IsolatedAsyncioTestCase

from rym import cx
from rym.cx.core import _catalog, _inventory

T = TypeVar("T")

LOGGER = logging.getLogger(__name__)

# Setup
# ======================================================================
# NOTE: We MUST define the EC instances prior to testing to allow each
#   test access to the entities and compontents. We _could_ make one big
#   test case, but that would be difficult to manage (and smelly).
# tl;dr: Define basic classes here. Test usage below.


def setUpModule() -> None:
    # NOTE: Do NOT clear on setup. This function runs _after_ the module is imported.
    # _catalog.clear_catalog()
    # _inventory.clear_inventory()
    pass


def tearDownModule() -> None:
    _catalog.clear_catalog()
    _inventory.clear_inventory()


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
    current: int

    @property
    def percentage(self) -> float:
        return round(100 * (self.current / self.total), 2)


# ----------------------------------
# Kate knows she needs two basic archetypes: Animate and Inanimate.
# For now, inanimate objects only have a location while animate objects need
# location and health.

Inanimate = cx.Archetype(Location, without=[Health])
Animate = cx.Archetype(Location, Health)

# ----------------------------------
# Kate knows the player will start in the jungle, navigating around foliage and
# fignting a few enemies, which gives her three components to track in her game.


@cx.component
class Player:
    ...


@cx.component
class Monster:
    ...


@cx.component
class Plant:
    ...


# section
# ----------------------------------
# Kate creates some initial entities to test with.

# Kate starts the player at the center of the screen with full health
player = cx.spawn(
    (Player(), Health(100, 100), Location(0, 0)),
)

# She then adds three plants ...
plants = cx.spawn(
    (Plant(), Location(1, 2)),
    (Plant(), Location(0, 3)),
    (Plant(), Location(-1, -3)),
)

# ... and two monsters, one of which is already injured
monsters = cx.spawn(
    (Monster(), Location(-1, 2), Health(40, 40)),
    (Monster(), Location(-2, 1), Health(40, 30)),
)


# ----------------------------------
# Kate wants to be able to retrieve injured entites


@cx.retrieve_by(Health)
def get_injured(components: Iterable[T]) -> Iterable[T]:
    injured = [x.entity_id for x in components if x.current > x.total]
    return injured


# Tests
# ======================================================================


class ThisTestCase(IsolatedAsyncioTestCase):
    """Base test case for the module."""


class TestBehavior(ThisTestCase):
    """Test behavior."""

    async def test_each_component_registered_in_catalog(self) -> None:
        # Kate checks that the components types have been registered
        expected = {Health, Location, Plant, Player, Monster}
        catalog = cx.get_catalog()
        assets = await catalog.get_by_namespace("component")
        found = set(assets)
        self.assertEqual(expected, found)

    async def test_each_entity_registered_with_inventory_and_component(self) -> None:
        # Kate checks that each entity is registered in the inventory
        # She knows her systems will need to be able to easily lookup any entity
        # by its id.
        inventory = cx.get_inventory()
        entities = await inventory.get_by_namespace(cx.Entity)

        with self.subTest("matching entities retrieved"):
            found = set(entities)
            expected = set(plants + player + monsters)
            self.assertEqual(expected, found)

    async def test_each_component_added_to_inventory(self) -> None:
        # Kate also wants to make sure that each component is in the inventory
        # _and_ that each component is linked back to its entity.
        inventory = cx.get_inventory()
        entities = await inventory.get_by_namespace(cx.Entity)
        for entity in entities:
            related = inventory.get_related(entity)

            with self.subTest("all components in inventory"):
                found = {x.uid for x in related}
                expected = entity.components
                self.assertEqual(expected, found)

            with self.subTest("each component linked to entity"):
                found = {x.entity_id for x in entity.components}
                expected = set(entity.uid)
                self.assertEqual(expected, found)

    async def test_get_injured(self) -> None:
        # With everything setup, Kate wants to check that her first lookup works.
        # She knows she'll be able to use a lookup expression later, but for now,
        # she's only interested in a small test.
        inventory = cx.get_inventory()
        health = await inventory.get_by_namespace(Health)
        found = get_injured()
        expected = [x.entity_id for x in health if x.percentage < 100]
        self.assertEqual(expected, found)


# __END__
