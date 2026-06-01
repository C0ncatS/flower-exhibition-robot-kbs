from __future__ import annotations

from collections.abc import Callable

from flower_robot.domain.models import Scenario
from flower_robot.domain.position import manhattan
from flower_robot.domain.state import (
    LoadState,
    NeedsState,
    has_needed_bouquets,
    has_unload_items,
    is_valid_load,
    load_contains,
    load_count,
    normalize_load,
    scenario_needs,
    subtract_load,
    subtract_needs,
)
from flower_robot.facts.schema import Node

Heuristic = Callable[[tuple[int, int], LoadState, NeedsState, tuple[int, int]], int]


class NodeFactory:
    def __init__(self, scenario: Scenario, heuristic: Heuristic) -> None:
        self._scenario = scenario
        self._heuristic = heuristic

    def root(self, node_id: int) -> Node:
        needs = scenario_needs(self._scenario)
        position = self._scenario.robot_start.as_tuple()
        return self._node(
            node_id=node_id,
            position=position,
            load=(),
            needs=needs,
            g=0,
            parent=None,
            action="start",
            action_kind="start",
            action_valid=True,
        )

    def move(
        self,
        parent: Node,
        node_id: int,
        target: tuple[int, int],
        direction: str,
    ) -> Node | None:
        if not self._is_useful_move(parent, tuple(target)):
            return None
        return self._node(
            node_id=node_id,
            position=tuple(target),
            load=tuple(parent["load"]),
            needs=tuple(parent["needs"]),
            g=parent["g"] + 1,
            parent=parent["id"],
            action=f"move {direction} to {tuple(target)}",
            action_kind="move",
            action_valid=True,
        )

    def load(self, parent: Node, node_id: int, option: LoadState) -> Node | None:
        load = normalize_load(option)
        valid = (
            len(parent["load"]) == 0
            and is_valid_load(load)
            and load_count(load) <= self._scenario.max_load
            and has_needed_bouquets(tuple(parent["needs"]), load)
        )
        if not valid:
            return None
        return self._node(
            node_id=node_id,
            position=tuple(parent["pos"]),
            load=load,
            needs=tuple(parent["needs"]),
            g=parent["g"] + 1,
            parent=parent["id"],
            action=f"load {format_items(load)}",
            action_kind="load",
            action_valid=True,
        )

    def _is_useful_move(self, parent: Node, target: tuple[int, int]) -> bool:
        current = tuple(parent["pos"])
        targets = self._movement_targets(parent)
        return any(
            manhattan(target, destination) < manhattan(current, destination)
            for destination in targets
        )

    def _movement_targets(self, parent: Node) -> tuple[tuple[int, int], ...]:
        load = tuple(parent["load"])
        needs = tuple(parent["needs"])
        if not load:
            return (self._scenario.warehouse.as_tuple(),) if needs else ()
        carried = {(flower_type, color) for flower_type, color, _ in load}
        return tuple(
            sorted(
                {
                    position
                    for _, flower_type, position, color, _ in needs
                    if (flower_type, color) in carried
                }
            )
        )

    def unload(
        self,
        parent: Node,
        node_id: int,
        pavilion_id: str,
        option: LoadState,
    ) -> Node | None:
        unload = normalize_load(option)
        needs = tuple(parent["needs"])
        load = tuple(parent["load"])
        valid = load_contains(load, unload) and has_unload_items(
            needs, pavilion_id, unload
        )
        if not valid:
            return None
        next_load = subtract_load(load, unload)
        next_needs = subtract_needs(needs, pavilion_id, unload)
        return self._node(
            node_id=node_id,
            position=tuple(parent["pos"]),
            load=next_load,
            needs=next_needs,
            g=parent["g"] + 1,
            parent=parent["id"],
            action=f"unload at {pavilion_id}: {format_items(unload)}",
            action_kind="unload",
            action_valid=True,
        )

    def _node(
        self,
        *,
        node_id: int,
        position: tuple[int, int],
        load: LoadState,
        needs: NeedsState,
        g: int,
        parent: int | None,
        action: str,
        action_kind: str,
        action_valid: bool,
    ) -> Node:
        h = self._heuristic(position, load, needs, self._scenario.warehouse.as_tuple())
        return Node(
            id=node_id,
            pos=position,
            load=load,
            load_count=load_count(load),
            load_valid=is_valid_load(load),
            needs=needs,
            g=g,
            h=h,
            f=g + h,
            status="open",
            parent=parent,
            action=action,
            action_kind=action_kind,
            action_valid=action_valid,
            tree_recorded=False,
        )


def format_items(items: LoadState) -> str:
    return ", ".join(
        f"{count} {color} {flower_type}" for flower_type, color, count in items
    )
