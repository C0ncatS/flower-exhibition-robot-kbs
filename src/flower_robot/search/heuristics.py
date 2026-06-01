from __future__ import annotations

from collections import defaultdict

from flower_robot.domain.position import manhattan
from flower_robot.domain.state import LoadState, NeedsState


def zero_heuristic(
    position: tuple[int, int],
    load: LoadState,
    needs: NeedsState,
    warehouse: tuple[int, int],
) -> int:
    return 0


def default_heuristic(
    position: tuple[int, int],
    load: LoadState,
    needs: NeedsState,
    warehouse: tuple[int, int],
) -> int:
    if not needs and not load:
        return 0

    unload_targets = _remaining_pavilion_positions(needs)
    operation_floor = len(unload_targets)
    load_floor = 0 if load else int(bool(needs))

    if load:
        travel_floor = _nearest_loaded_target_distance(position, load, needs)
    else:
        travel_floor = manhattan(position, warehouse) + _nearest_need_from_warehouse(warehouse, needs)

    return operation_floor + load_floor + travel_floor


def _remaining_pavilion_positions(needs: NeedsState) -> dict[str, tuple[int, int]]:
    return {pavilion_id: position for pavilion_id, _, position, _, _ in needs}


def _nearest_need_from_warehouse(warehouse: tuple[int, int], needs: NeedsState) -> int:
    distances = [manhattan(warehouse, position) for _, _, position, _, _ in needs]
    return min(distances, default=0)


def _nearest_loaded_target_distance(
    position: tuple[int, int],
    load: LoadState,
    needs: NeedsState,
) -> int:
    carried = {(flower_type, color) for flower_type, color, _ in load}
    targets: dict[str, tuple[int, int]] = {}
    for pavilion_id, flower_type, target, color, _ in needs:
        if (flower_type, color) in carried:
            targets[pavilion_id] = target
    return min((manhattan(position, target) for target in targets.values()), default=0)
