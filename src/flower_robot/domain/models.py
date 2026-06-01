from __future__ import annotations

from dataclasses import dataclass

from flower_robot.domain.position import Position


@dataclass(frozen=True)
class Pavilion:
    pavilion_id: str
    flower_type: str
    position: Position
    needs: dict[str, int]

    @property
    def total_need(self) -> int:
        return sum(self.needs.values())


@dataclass(frozen=True)
class Scenario:
    width: int
    height: int
    warehouse: Position
    robot_start: Position
    pavilions: tuple[Pavilion, ...]

    @property
    def max_load(self) -> int:
        return max((pavilion.total_need for pavilion in self.pavilions), default=0)
