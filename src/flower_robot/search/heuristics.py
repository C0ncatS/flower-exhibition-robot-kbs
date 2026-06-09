from __future__ import annotations

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
    if not needs:
        return 0

    targets = _remaining_pavilion_positions(needs)
    target_points = list(targets.values())

    if load:
        # Starting from current position, visit all remaining targets
        travel_floor = _compute_mst([position] + target_points)
        load_floor = 0  # Already carrying something
    else:
        # Must travel to warehouse, then visit all remaining targets
        dist_to_wh = manhattan(position, warehouse)
        travel_floor = dist_to_wh + _compute_mst([warehouse] + target_points)
        load_floor = 1  # Must perform at least one load operation

    # Each pavilion that needs items requires at least one unload operation
    operation_floor = len(targets)

    return travel_floor + operation_floor + load_floor


def _compute_mst(points: list[tuple[int, int]]) -> int:
    if not points:
        return 0

    num_points = len(points)
    visited = [False] * num_points
    min_dist = [float("inf")] * num_points
    min_dist[0] = 0
    total_weight = 0

    for _ in range(num_points):
        u = -1
        for i in range(num_points):
            if not visited[i] and (u == -1 or min_dist[i] < min_dist[u]):
                u = i

        if u == -1 or min_dist[u] == float("inf"):
            break

        visited[u] = True
        total_weight += min_dist[u]

        for v in range(num_points):
            if not visited[v]:
                d = manhattan(points[u], points[v])
                if d < min_dist[v]:
                    min_dist[v] = d

    return int(total_weight)


def _remaining_pavilion_positions(needs: NeedsState) -> dict[str, tuple[int, int]]:
    return {pavilion_id: position for pavilion_id, _, position, _, _ in needs}
