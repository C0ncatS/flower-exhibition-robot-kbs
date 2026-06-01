from __future__ import annotations

import flower_robot.compat  # noqa: F401
from experta import AS, MATCH, NOT, Rule

from flower_robot.facts.schema import CostLevelFact, CostSuccessorFact, Node, StrategyFact


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
        AS.cost << CostLevelFact(value=MATCH.current_f),
        NOT(Node(status="open", f=MATCH.current_f)),
        CostSuccessorFact(value=MATCH.current_f, next_value=MATCH.next_f),
        salience=120,
    )
    def advance_astar_cost_level(self, cost, next_f):
        self.modify(cost, value=next_f)

    @Rule(
        StrategyFact(name="astar"),
        NOT(Node(status="expanding")),
        CostLevelFact(value=MATCH.f),
        AS.node << Node(status="open", f=MATCH.f),
        salience=100,
    )
    def select_lowest_f_node(self, node):
        self.modify(node, status="expanding")

    @Rule(AS.node << Node(status="expanding"), salience=-100)
    def close_expanded_node(self, node):
        self.modify(node, status="closed")
