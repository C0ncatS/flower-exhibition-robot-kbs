from __future__ import annotations

import flower_robot.compat  # noqa: F401
from experta import AS, P, Rule

from flower_robot.facts.schema import Node


class GoalRules:
    @Rule(
        AS.node << Node(
            status="expanding",
            load=P(lambda load: len(load) == 0),
            needs=P(lambda needs: len(needs) == 0),
        ),
        salience=90,
    )
    def found_goal(self, node):
        self.record_solution(node)
