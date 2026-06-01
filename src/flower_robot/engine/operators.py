from __future__ import annotations

import flower_robot.compat  # noqa: F401
from experta import AS, MATCH, P, Rule, TEST

from flower_robot.facts.schema import (
    GridFact,
    LoadOptionFact,
    Node,
    PavilionFact,
    UnloadOptionFact,
    WarehouseFact,
)


class OperatorRules:
    @Rule(
        AS.node << Node(status="expanding", pos=MATCH.pos),
        GridFact(width=MATCH.width, height=MATCH.height),
        TEST(lambda pos, width, height: pos[0] < width),
        salience=50,
    )
    def move_right(self, node, pos, width, height):
        self.add_move_child(node, (pos[0] + 1, pos[1]), "right")

    @Rule(
        AS.node << Node(status="expanding", pos=MATCH.pos),
        GridFact(width=MATCH.width, height=MATCH.height),
        TEST(lambda pos, width, height: pos[0] > 1),
        salience=50,
    )
    def move_left(self, node, pos, width, height):
        self.add_move_child(node, (pos[0] - 1, pos[1]), "left")

    @Rule(
        AS.node << Node(status="expanding", pos=MATCH.pos),
        GridFact(width=MATCH.width, height=MATCH.height),
        TEST(lambda pos, width, height: pos[1] > 1),
        salience=50,
    )
    def move_up(self, node, pos, width, height):
        self.add_move_child(node, (pos[0], pos[1] - 1), "up")

    @Rule(
        AS.node << Node(status="expanding", pos=MATCH.pos),
        GridFact(width=MATCH.width, height=MATCH.height),
        TEST(lambda pos, width, height: pos[1] < height),
        salience=50,
    )
    def move_down(self, node, pos, width, height):
        self.add_move_child(node, (pos[0], pos[1] + 1), "down")

    @Rule(
        AS.node
        << Node(status="expanding", pos=MATCH.pos, load=P(lambda load: len(load) == 0)),
        WarehouseFact(position=MATCH.pos),
        LoadOptionFact(load=MATCH.option),
        salience=50,
    )
    def load_at_warehouse(self, node, option):
        self.add_load_child(node, option)

    @Rule(
        AS.node << Node(status="expanding", pos=MATCH.pos),
        PavilionFact(pavilion_id=MATCH.pavilion_id, position=MATCH.pos),
        UnloadOptionFact(pavilion_id=MATCH.pavilion_id, unload=MATCH.option),
        salience=50,
    )
    def unload_at_pavilion(self, node, pavilion_id, option):
        self.add_unload_child(node, pavilion_id, option)
