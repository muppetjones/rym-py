#!/usr/bin/env python3
"""Test."""

import copy
import itertools
from typing import Iterable, TypeVar
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock

from rym import cx
from rym.cx.core import _catalog, _inventory

T = TypeVar("T")


# Setup
# ======================================================================
# NOTE: We MUST define the EC instances prior to testing to allow each
#   test access to the entities and compontents. We _could_ make one big
#   test case, but that would be difficult to manage (and smelly).
# CRITICAL: We MUST store the state and reload it during class setup.
# tl;dr: Define basic classes here. Test usage below.


# ----------------------------------
# Kate is designing a simple dungeon crawler.
# She knows she'll need to track location and health of various
# entities. It's a 2D game, so she'll only need an x and y axis.
# And for now, she'll only track total and current number of HP.
# She wants to support poison damage, too.


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


@cx.component
class Poison:
    damage: int
    duration: int


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
class Plant:
    name: str = "ficus"


@cx.component
class Player: ...


@cx.component
class Monster:
    name: str = "monster"


# section
# ----------------------------------
# Kate creates some initial entities to test with.

# Kate starts the player at the center of the screen with full health
player = cx.spawn_entity(
    (Player(), Health(100, 100), Location(0, 0)),
)

# She then adds three plants ...
plants = cx.spawn_entity(
    (Plant(), Location(1, 2)),
    (Plant(), Location(0, 3)),
    (Plant(), Location(-1, -3)),
)

# ... and two monsters, one of which is already injured
monsters = cx.spawn_entity(
    (Monster(), Location(-1, 2), Health(40, 40)),
    (Monster(), Location(-2, 1), Health(40, 30), Poison(5, 3)),
)

# ----------------------------------
# Kate wants a system that can periodically apply poison damage to any
# poisoned entity.


@cx.retrieve(poisoned=(Health, Poison))
async def tick_poison_damage(poisoned: Iterable[tuple[Health, Poison]]) -> None:
    """Reduce health by poison amount on each tick.

    TODO: Remove Poisoned component once duration is complete once component
        removal is supported,
    """
    for health, poison in poisoned:
        if health.current > 0 and poison.duration > 0:
            health.current = max(0, health.current - poison.damage)
            poison.duration -= 1


# Save inventory and catalog
# ======================================================================
# CRITICAL: Both are setup when the module is loaded. The state is NOT
#   persistent for the test suite

_INVENTORY = copy.deepcopy(_inventory._INVENTORY)
_CATALOG = copy.deepcopy(_catalog._CATALOG)

# Tests
# ======================================================================


class ThisTestCase(IsolatedAsyncioTestCase):
    """Base test case for the module."""

    @classmethod
    def setUpClass(cls) -> None:
        # NOTE: Restore the module state
        cx.clear_registrar(logger=Mock())
        _inventory._INVENTORY = _INVENTORY
        _catalog._CATALOG = _CATALOG
        cls.addClassCleanup(cx.clear_registrar, logger=Mock())


class TestBehavior(ThisTestCase):
    """Test behavior."""

    async def test_each_component_registered_in_catalog(self) -> None:
        # Kate checks that the components types have been registered
        expected = {Health, Location, Poison, Plant, Player, Monster}
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
            # NOTE: Entity is not safely hashable.
            found = sorted([x.uid for x in entities])
            expected = sorted(
                [x.uid for x in itertools.chain(player, plants, monsters)]
            )
            self.assertEqual(expected, found)

    async def test_each_component_added_to_inventory(self) -> None:
        # Kate also wants to make sure that each component is in the inventory
        # _and_ that each component is linked back to its entity.
        inventory = cx.get_inventory()
        entities = await inventory.get_by_namespace(cx.Entity)
        for entity in entities:
            related = await _inventory.get_related_component(entity)

            with self.subTest("all components in inventory"):
                found = {x.uid for x in related}
                expected = set(entity.component)
                self.assertEqual(expected, found)

            with self.subTest(f"each component linked to entity: {related}"):
                found = set(x.entity_uid for x in related)
                expected = {entity.uid}
                self.assertEqual(expected, found, f"{expected} != {found}")

    async def test_poison_damage(self) -> None:
        # Kate wants to have a system that will periodically deal damage to any
        # poisoned entities. The system shouldn't take entity below 0 health,
        # and the person should not continue to take damage once the poison
        # duration has ended.
        health, poison = (await _inventory.retrieve_by_component(Health, Poison))[0]
        status = [(health.current, poison.duration)]
        for _ in range(4):
            await tick_poison_damage()
            status.append((health.current, poison.duration))

        found = status
        expected = [(30, 3), (25, 2), (20, 1), (15, 0), (15, 0)]
        self.assertEqual(expected, found)


# __END__
