from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

import flower_robot.compat  # noqa: F401
from experta import DefFacts, KnowledgeEngine

from flower_robot.domain.choices import build_load_options, build_unload_options
from flower_robot.domain.models import Scenario
from flower_robot.domain.state import LoadState, NeedsState, scenario_needs
from flower_robot.engine.constraints import ConstraintRules
from flower_robot.engine.dedup import DedupRules
from flower_robot.engine.goal import GoalRules
from flower_robot.engine.operators import OperatorRules
from flower_robot.engine.strategy import StrategyRules
from flower_robot.engine.tree import TreeRules
from flower_robot.facts.schema import (
    CandidateNode,
    GridFact,
    LoadOptionFact,
    LowestOpenNodeFact,
    MaxLoadFact,
    Node,
    PavilionFact,
    Solution,
    StateBestCostFact,
    StrategyFact,
    UnloadOptionFact,
    WarehouseFact,
)
from flower_robot.search.heuristics import default_heuristic
from flower_robot.search.node_factory import Heuristic, NodeFactory


class FlowerRobotEngine(
    TreeRules,
    GoalRules,
    ConstraintRules,
    DedupRules,
    OperatorRules,
    StrategyRules,
    KnowledgeEngine,
):
    def __init__(
        self,
        scenario: Scenario,
        strategy: str = "astar",
        heuristic: Heuristic = default_heuristic,
    ) -> None:
        self.scenario = scenario
        self.strategy_name = strategy
        self.node_factory = NodeFactory(scenario, heuristic)
        self.node_records: dict[int, dict[str, Any]] = {}
        self.tree_order: list[int] = []
        self.solution: dict[str, Any] | None = None
        self.elapsed_seconds: float | None = None
        self._next_node_id = 0
        super().__init__()

    def reset(self, **kwargs: Any) -> None:
        self.node_records = {}
        self.tree_order = []
        self.solution = None
        self.elapsed_seconds = None
        self._next_node_id = 0
        super().reset(**kwargs)

    @DefFacts()
    def scenario_facts(self):
        root = self.node_factory.root(self._allocate_node_id())
        self._remember_node(root)

        yield StrategyFact(name=self.strategy_name)
        yield StateBestCostFact(
            pos=root["pos"],
            load=root["load"],
            needs=root["needs"],
            best_g=root["g"],
        )
        yield GridFact(width=self.scenario.width, height=self.scenario.height)
        yield WarehouseFact(position=self.scenario.warehouse.as_tuple())
        yield MaxLoadFact(value=self.scenario.max_load)

        if self.strategy_name == "astar":
            yield LowestOpenNodeFact(node_id=root["id"], f=root["f"])

        for pavilion in self.scenario.pavilions:
            yield PavilionFact(
                pavilion_id=pavilion.pavilion_id,
                flower_type=pavilion.flower_type,
                position=pavilion.position.as_tuple(),
                needs=tuple(sorted(pavilion.needs.items())),
            )

        for index, option in enumerate(
            build_load_options(scenario_needs(self.scenario), self.scenario.max_load),
            start=1,
        ):
            yield LoadOptionFact(option_id=index, load=option)

        for index, (pavilion_id, option) in enumerate(
            build_unload_options(self.scenario.pavilions),
            start=1,
        ):
            yield UnloadOptionFact(
                option_id=index,
                pavilion_id=pavilion_id,
                unload=option,
            )

        yield root

    def add_move_child(
        self,
        parent: Node,
        target: tuple[int, int],
        direction: str,
    ) -> None:
        child = self.node_factory.move(
            parent,
            self._allocate_node_id(),
            target,
            direction,
        )
        self._queue_candidate(child)

    def add_load_child(self, parent: Node, option: LoadState) -> None:
        child = self.node_factory.load(parent, self._allocate_node_id(), option)
        self._queue_candidate(child)

    def add_unload_child(
        self,
        parent: Node,
        pavilion_id: str,
        option: LoadState,
    ) -> None:
        child = self.node_factory.unload(
            parent,
            self._allocate_node_id(),
            pavilion_id,
            option,
        )
        self._queue_candidate(child)

    def record_tree_node(self, node: Node) -> None:
        self.tree_order.append(node["id"])

    def record_solution(self, node: Node) -> None:
        path = self._path_to(node["id"])
        self.solution = {
            "node_id": node["id"],
            "cost": node["g"],
            "path": path,
            "generated": len(self.node_records),
        }
        self.declare(
            Solution(
                node_id=node["id"],
                cost=node["g"],
                path=tuple(step["action"] for step in path),
            )
        )
        self.halt()

    def _queue_candidate(self, node: Node) -> None:
        self.declare(
            CandidateNode(
                id=node["id"],
                pos=node["pos"],
                load=node["load"],
                load_count=node["load_count"],
                load_valid=node["load_valid"],
                needs=node["needs"],
                g=node["g"],
                h=node["h"],
                f=node["f"],
                parent=node["parent"],
                action=node["action"],
                action_kind=node["action_kind"],
                action_valid=node["action_valid"],
            )
        )

    def _promote_candidate(self, candidate: CandidateNode) -> None:
        node = Node(
            id=candidate["id"],
            pos=candidate["pos"],
            load=candidate["load"],
            load_count=candidate["load_count"],
            load_valid=candidate["load_valid"],
            needs=candidate["needs"],
            g=candidate["g"],
            h=candidate["h"],
            f=candidate["f"],
            status="open",
            parent=candidate["parent"],
            action=candidate["action"],
            action_kind=candidate["action_kind"],
            action_valid=candidate["action_valid"],
            tree_recorded=False,
        )
        self._remember_node(node)
        self.declare(node)

    def _remember_node(self, node: Node) -> None:
        self.node_records[node["id"]] = node.as_dict()

    def _allocate_node_id(self) -> int:
        self._next_node_id += 1
        return self._next_node_id

    def _path_to(self, node_id: int) -> list[dict[str, Any]]:
        path: list[dict[str, Any]] = []
        current: int | None = node_id
        while current is not None:
            record = self.node_records[current]
            path.append(record)
            current = record["parent"]
        return list(reversed(path))


def run_engine(
    scenario: Scenario,
    strategy: str = "astar",
    heuristic: Callable[
        [tuple[int, int], LoadState, NeedsState, tuple[int, int]], int
    ] = default_heuristic,
    max_steps: int | None = None,
) -> FlowerRobotEngine:
    engine = FlowerRobotEngine(
        scenario=scenario,
        strategy=strategy,
        heuristic=heuristic,
    )
    engine.reset()
    start = time.perf_counter()
    engine.run(max_steps or float("inf"))
    engine.elapsed_seconds = time.perf_counter() - start
    return engine
