from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Position:
    x: int
    y: int

    @classmethod
    def from_pair(cls, pair: list[int] | tuple[int, int]) -> "Position":
        return cls(int(pair[0]), int(pair[1]))

    def as_tuple(self) -> tuple[int, int]:
        return (self.x, self.y)


DIRECTIONS: dict[str, tuple[int, int]] = {
    "right": (1, 0),
    "left": (-1, 0),
    "up": (0, -1),
    "down": (0, 1),
}


def manhattan(
    left: tuple[int, int] | Position,
    right: tuple[int, int] | Position,
) -> int:
    left_pair = left.as_tuple() if isinstance(left, Position) else left
    right_pair = right.as_tuple() if isinstance(right, Position) else right
    return abs(left_pair[0] - right_pair[0]) + abs(left_pair[1] - right_pair[1])
