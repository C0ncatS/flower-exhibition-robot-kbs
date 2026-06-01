from __future__ import annotations

import flower_robot.compat  # noqa: F401
from experta import Fact


class StrategyFact(Fact):
    """Search strategy selector."""


class CostLevelFact(Fact):
    """Current f-cost level considered by A*."""


class CostSuccessorFact(Fact):
    """Precomputed successor relation over integer f-cost levels."""


class GridFact(Fact):
    """Grid dimensions."""


class WarehouseFact(Fact):
    """Warehouse position."""


class PavilionFact(Fact):
    """Static pavilion metadata."""


class MaxLoadFact(Fact):
    """Robot maximum load."""


class LoadOptionFact(Fact):
    """A materialized legal load choice point."""


class UnloadOptionFact(Fact):
    """A materialized unload choice point for a pavilion."""


class Node(Fact):
    """A search-tree node carrying the full world state."""


class Solution(Fact):
    """A found solution path."""
