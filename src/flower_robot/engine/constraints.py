from __future__ import annotations

import flower_robot.compat  # noqa: F401
from experta import AS, MATCH, TEST, Rule

from flower_robot.facts.schema import GridFact, MaxLoadFact, Node


class ConstraintRules:
    @Rule(
        AS.node << Node(status="open", load_count=MATCH.load_count),
        MaxLoadFact(value=MATCH.max_load),
        TEST(lambda load_count, max_load: load_count > max_load),
        salience=85,
    )
    def reject_overloaded_node(self, node):
        self.retract(node)

    @Rule(AS.node << Node(status="open", load_valid=False), salience=85)
    def reject_illegal_load_mix(self, node):
        self.retract(node)

    @Rule(AS.node << Node(status="open", action_valid=False), salience=85)
    def reject_invalid_operator_result(self, node):
        self.retract(node)

    @Rule(
        AS.node << Node(status="open", pos=MATCH.pos),
        GridFact(width=MATCH.width, height=MATCH.height),
        TEST(lambda pos, width, height: not (1 <= pos[0] <= width and 1 <= pos[1] <= height)),
        salience=85,
    )
    def reject_out_of_bounds_node(self, node):
        self.retract(node)
