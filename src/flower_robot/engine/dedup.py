from __future__ import annotations

import flower_robot.compat  # noqa: F401
from experta import AS, MATCH, NOT, Rule, TEST

from flower_robot.facts.schema import CandidateNode, StateBestCostFact


class DedupRules:
    @Rule(
        AS.candidate << CandidateNode(
            pos=MATCH.pos,
            load=MATCH.load,
            needs=MATCH.needs,
            g=MATCH.g,
        ),
        NOT(
            StateBestCostFact(
                pos=MATCH.pos,
                load=MATCH.load,
                needs=MATCH.needs,
            )
        ),
        salience=75,
    )
    def accept_new_state(self, candidate):
        self.declare(
            StateBestCostFact(
                pos=candidate["pos"],
                load=candidate["load"],
                needs=candidate["needs"],
                best_g=candidate["g"],
            )
        )
        self._promote_candidate(candidate)
        self.retract(candidate)

    @Rule(
        AS.candidate << CandidateNode(
            pos=MATCH.pos,
            load=MATCH.load,
            needs=MATCH.needs,
            g=MATCH.g,
        ),
        AS.record << StateBestCostFact(
            pos=MATCH.pos,
            load=MATCH.load,
            needs=MATCH.needs,
            best_g=MATCH.best_g,
        ),
        TEST(lambda g, best_g: g < best_g),
        salience=75,
    )
    def accept_better_path(self, candidate, record):
        self.modify(record, best_g=candidate["g"])
        self._promote_candidate(candidate)
        self.retract(candidate)

    @Rule(
        AS.candidate << CandidateNode(
            pos=MATCH.pos,
            load=MATCH.load,
            needs=MATCH.needs,
            g=MATCH.g,
        ),
        StateBestCostFact(
            pos=MATCH.pos,
            load=MATCH.load,
            needs=MATCH.needs,
            best_g=MATCH.best_g,
        ),
        TEST(lambda g, best_g: g >= best_g),
        salience=75,
    )
    def reject_duplicate_state(self, candidate):
        self.retract(candidate)
