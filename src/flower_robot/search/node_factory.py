from __future__ import annotations

from collections.abc import Callable

from flower_robot.domain.models import Scenario
from flower_robot.domain.state import (
    LoadState,
    NeedsState,
    is_valid_load,
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
        )

    def move(
        self,
        parent: Node,
        node_id: int,
        target: tuple[int, int],
        direction: str,
    ) -> Node:
        return self._node(
            node_id=node_id,
            position=tuple(target),
            load=tuple(parent["load"]),
            needs=tuple(parent["needs"]),
            g=parent["g"] + 1,
            parent=parent["id"],
            action=f"move {direction} to {tuple(target)}",
            action_kind="move",
        )

    def load(self, parent: Node, node_id: int, option: LoadState) -> Node:
        load = normalize_load(option)
        return self._node(
            node_id=node_id,
            position=tuple(parent["pos"]),
            load=load,
            needs=tuple(parent["needs"]),
            g=parent["g"] + 1,
            parent=parent["id"],
            action=f"load {format_items(load)}",
            action_kind="load",
        )

    def unload(
        self,
        parent: Node,
        node_id: int,
        pavilion_id: str,
        option: LoadState,
    ) -> Node:
        unload = normalize_load(option)
        needs = tuple(parent["needs"])
        load = tuple(parent["load"])
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
            tree_recorded=False,
        )


def format_items(items: LoadState) -> str:
    return ", ".join(
        f"{count} {color} {flower_type}" for flower_type, color, count in items
    )
