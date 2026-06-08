from __future__ import annotations

from flower_robot.domain.position import manhattan
from flower_robot.domain.state import LoadState, NeedsState


def movement_targets(
    load: LoadState,
    needs: NeedsState,
    warehouse: tuple[int, int],
) -> tuple[tuple[int, int], ...]:
    if not load:
        return (warehouse,) if needs else ()
    carried = {(flower_type, color) for flower_type, color, _ in load}
    return tuple(
        sorted(
            {
                position
                for _, flower_type, position, color, _ in needs
                if (flower_type, color) in carried
            }
        )
    )


def is_useful_move(
    position: tuple[int, int],
    load: LoadState,
    needs: NeedsState,
    warehouse: tuple[int, int],
    target: tuple[int, int],
) -> bool:
    targets = movement_targets(load, needs, warehouse)
    return any(
        manhattan(target, destination) < manhattan(position, destination)
        for destination in targets
    )
