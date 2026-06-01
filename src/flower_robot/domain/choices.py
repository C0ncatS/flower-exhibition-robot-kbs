from __future__ import annotations

from itertools import combinations

from flower_robot.domain.models import Pavilion
from flower_robot.domain.state import LoadState, NeedsState, load_count, normalize_load


def build_load_options(needs: NeedsState, max_load: int) -> tuple[LoadState, ...]:
    options: set[LoadState] = set()

    for pavilion_id in sorted({pavilion_id for pavilion_id, _, _, _, _ in needs}):
        pavilion_items = tuple(
            (flower_type, color, count)
            for need_pavilion, flower_type, _, color, count in needs
            if need_pavilion == pavilion_id
        )
        options.add(normalize_load(pavilion_items))

    for color in sorted({color for _, _, _, color, _ in needs}):
        same_color = tuple(
            (flower_type, color, count)
            for _, flower_type, _, need_color, count in needs
            if need_color == color
        )
        options.update(_maximal_subsets_within_capacity(same_color, max_load))

    return tuple(
        sorted(option for option in options if 0 < load_count(option) <= max_load)
    )


def build_unload_options(
    pavilions: tuple[Pavilion, ...],
) -> tuple[tuple[str, LoadState], ...]:
    options: list[tuple[str, LoadState]] = []
    for pavilion in pavilions:
        items = tuple(
            (pavilion.flower_type, color, count)
            for color, count in sorted(pavilion.needs.items())
            if count > 0
        )
        for unload in _subsets_within_capacity(
            items,
            max(1, sum(pavilion.needs.values())),
        ):
            options.append((pavilion.pavilion_id, unload))
    return tuple(options)


def _subsets_within_capacity(
    items: tuple[tuple[str, str, int], ...],
    max_load: int,
) -> set[LoadState]:
    options: set[LoadState] = set()
    for size in range(1, len(items) + 1):
        for subset in combinations(items, size):
            normalized = normalize_load(subset)
            if load_count(normalized) <= max_load:
                options.add(normalized)
    return options


def _maximal_subsets_within_capacity(
    items: tuple[tuple[str, str, int], ...],
    max_load: int,
) -> set[LoadState]:
    subsets = _subsets_within_capacity(items, max_load)
    return {
        subset
        for subset in subsets
        if not any(_is_strict_subset(subset, other) for other in subsets)
    }


def _is_strict_subset(left: LoadState, right: LoadState) -> bool:
    left_items = {(flower_type, color) for flower_type, color, _ in left}
    right_items = {(flower_type, color) for flower_type, color, _ in right}
    return left_items < right_items
