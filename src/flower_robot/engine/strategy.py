from __future__ import annotations

import flower_robot.compat  # noqa: F401
from experta import AS, MATCH, NOT, Rule, TEST

from flower_robot.facts.schema import LowestOpenNodeFact, Node, Solution, StrategyFact


class StrategyRules:
    @Rule(
        StrategyFact(name="dfs"),
        NOT(Node(status="expanding")),
        AS.node << Node(status="open"),
        salience=100,
    )
    def select_depth_first_node(self, node):
        self.modify(node, status="expanding")

    @Rule(
        StrategyFact(name="astar"),
        NOT(Node(status="expanding")),
        NOT(Solution()),
        AS.current << LowestOpenNodeFact(node_id=MATCH.current_id, f=MATCH.current_f),
        AS.node << Node(status="open", id=MATCH.candidate_id, f=MATCH.candidate_f),
        TEST(lambda candidate_f, current_f: candidate_f < current_f),
        salience=350,
    )
    def update_lowest_open_node(self, current, candidate_id, candidate_f):
        self.retract(current)
        self.declare(LowestOpenNodeFact(node_id=candidate_id, f=candidate_f))

    @Rule(
        StrategyFact(name="astar"),
        AS.current << LowestOpenNodeFact(node_id=MATCH.node_id),
        NOT(Node(status="open", id=MATCH.node_id)),
        salience=340,
    )
    def clear_stale_lowest_open_node(self, current):
        self.retract(current)

    @Rule(
        StrategyFact(name="astar"),
        NOT(Node(status="expanding")),
        NOT(Solution()),
        NOT(LowestOpenNodeFact()),
        AS.node << Node(status="open"),
        salience=330,
    )
    def seed_lowest_open_node(self, node):
        self.declare(LowestOpenNodeFact(node_id=node["id"], f=node["f"]))

    @Rule(
        StrategyFact(name="astar"),
        NOT(Node(status="expanding")),
        NOT(Solution()),
        LowestOpenNodeFact(node_id=MATCH.node_id, f=MATCH.f),
        AS.node << Node(status="open", id=MATCH.node_id, f=MATCH.f),
        salience=100,
    )
    def select_astar_node(self, node):
        self.modify(node, status="expanding")

    @Rule(AS.node << Node(status="expanding"), salience=-100)
    def close_expanded_node(self, node):
        self.modify(node, status="closed")
