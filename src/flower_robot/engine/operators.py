from __future__ import annotations

import flower_robot.compat  # noqa: F401
from experta import AS, MATCH, P, Rule, TEST

from flower_robot.domain.navigation import is_useful_move
from flower_robot.domain.state import (
    has_needed_bouquets,
    has_unload_items,
    load_contains,
)
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
        AS.node
        << Node(
            status="expanding",
            pos=MATCH.pos,
            load=MATCH.load,
            needs=MATCH.needs,
        ),
        GridFact(width=MATCH.width, height=MATCH.height),
        WarehouseFact(position=MATCH.warehouse),
        TEST(lambda pos, width, height: pos[0] < width),
        TEST(
            lambda pos, load, needs, warehouse: is_useful_move(
                pos,
                load,
                needs,
                warehouse,
                (pos[0] + 1, pos[1]),
            )
        ),
        salience=50,
    )
    def move_right(self, node, pos, width, height):
        self.add_move_child(node, (pos[0] + 1, pos[1]), "right")

    @Rule(
        AS.node
        << Node(
            status="expanding",
            pos=MATCH.pos,
            load=MATCH.load,
            needs=MATCH.needs,
        ),
        GridFact(width=MATCH.width, height=MATCH.height),
        WarehouseFact(position=MATCH.warehouse),
        TEST(lambda pos, width, height: pos[0] > 1),
        TEST(
            lambda pos, load, needs, warehouse: is_useful_move(
                pos,
                load,
                needs,
                warehouse,
                (pos[0] - 1, pos[1]),
            )
        ),
        salience=50,
    )
    def move_left(self, node, pos, width, height):
        self.add_move_child(node, (pos[0] - 1, pos[1]), "left")

    @Rule(
        AS.node
        << Node(
            status="expanding",
            pos=MATCH.pos,
            load=MATCH.load,
            needs=MATCH.needs,
        ),
        GridFact(width=MATCH.width, height=MATCH.height),
        WarehouseFact(position=MATCH.warehouse),
        TEST(lambda pos, width, height: pos[1] > 1),
        TEST(
            lambda pos, load, needs, warehouse: is_useful_move(
                pos,
                load,
                needs,
                warehouse,
                (pos[0], pos[1] - 1),
            )
        ),
        salience=50,
    )
    def move_up(self, node, pos, width, height):
        self.add_move_child(node, (pos[0], pos[1] - 1), "up")

    @Rule(
        AS.node
        << Node(
            status="expanding",
            pos=MATCH.pos,
            load=MATCH.load,
            needs=MATCH.needs,
        ),
        GridFact(width=MATCH.width, height=MATCH.height),
        WarehouseFact(position=MATCH.warehouse),
        TEST(lambda pos, width, height: pos[1] < height),
        TEST(
            lambda pos, load, needs, warehouse: is_useful_move(
                pos,
                load,
                needs,
                warehouse,
                (pos[0], pos[1] + 1),
            )
        ),
        salience=50,
    )
    def move_down(self, node, pos, width, height):
        self.add_move_child(node, (pos[0], pos[1] + 1), "down")

    @Rule(
        AS.node
        << Node(
            status="expanding",
            pos=MATCH.pos,
            load=P(lambda load: len(load) == 0),
            needs=MATCH.needs,
        ),
        WarehouseFact(position=MATCH.pos),
        LoadOptionFact(load=MATCH.option),
        TEST(lambda needs, option: has_needed_bouquets(needs, option)),
        salience=50,
    )
    def load_at_warehouse(self, node, option):
        self.add_load_child(node, option)

    @Rule(
        AS.node
        << Node(
            status="expanding",
            pos=MATCH.pos,
            load=MATCH.load,
            needs=MATCH.needs,
        ),
        PavilionFact(pavilion_id=MATCH.pavilion_id, position=MATCH.pos),
        UnloadOptionFact(pavilion_id=MATCH.pavilion_id, unload=MATCH.option),
        TEST(
            lambda load, needs, pavilion_id, option: (
                load_contains(load, option)
                and has_unload_items(needs, pavilion_id, option)
            )
        ),
        salience=50,
    )
    def unload_at_pavilion(self, node, pavilion_id, option):
        self.add_unload_child(node, pavilion_id, option)
