from __future__ import annotations

import flower_robot.compat  # noqa: F401
from experta import AS, Rule

from flower_robot.facts.schema import Node


class TreeRules:
    @Rule(AS.node << Node(tree_recorded=False), salience=200)
    def record_generated_node(self, node):
        self.record_tree_node(node)
        self.modify(node, tree_recorded=True)
