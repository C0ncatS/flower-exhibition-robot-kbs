from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from flower_robot.domain.models import Pavilion, Scenario

LoadItem = tuple[str, str, int]
LoadState = tuple[LoadItem, ...]
NeedItem = tuple[str, str, tuple[int, int], str, int]
NeedsState = tuple[NeedItem, ...]


def normalize_load(items: Iterable[LoadItem]) -> LoadState:
    totals: dict[tuple[str, str], int] = defaultdict(int)
    for flower_type, color, count in items:
        if count > 0:
            totals[(flower_type, color)] += count
    return tuple(
        (flower_type, color, count)
        for (flower_type, color), count in sorted(totals.items())
        if count > 0
    )


def normalize_needs(items: Iterable[NeedItem]) -> NeedsState:
    return tuple(
        sorted(
            (
                pavilion_id,
                flower_type,
                tuple(position),
                color,
                count,
            )
            for pavilion_id, flower_type, position, color, count in items
            if count > 0
        )
    )


def scenario_needs(scenario: Scenario) -> NeedsState:
    return normalize_needs(
        (
            pavilion.pavilion_id,
            pavilion.flower_type,
            pavilion.position.as_tuple(),
            color,
            count,
        )
        for pavilion in scenario.pavilions
        for color, count in pavilion.needs.items()
    )


def load_count(load: LoadState) -> int:
    return sum(count for _, _, count in load)


def is_valid_load(load: LoadState) -> bool:
    if not load:
        return True
    flower_types = {flower_type for flower_type, _, _ in load}
    colors = {color for _, color, _ in load}
    return len(flower_types) == 1 or len(colors) == 1


def has_needed_bouquets(needs: NeedsState, load: LoadState) -> bool:
    remaining = {
        (flower_type, color): count for _, flower_type, _, color, count in needs
    }
    return all(
        count <= remaining.get((flower_type, color), 0)
        for flower_type, color, count in load
    )


def has_unload_items(needs: NeedsState, pavilion_id: str, unload: LoadState) -> bool:
    remaining = {
        (flower_type, color): count
        for need_pavilion, flower_type, _, color, count in needs
        if need_pavilion == pavilion_id
    }
    return all(
        count == remaining.get((flower_type, color), 0)
        for flower_type, color, count in unload
    )


def load_contains(load: LoadState, unload: LoadState) -> bool:
    carried = {(flower_type, color): count for flower_type, color, count in load}
    return all(
        count <= carried.get((flower_type, color), 0)
        for flower_type, color, count in unload
    )


def subtract_load(load: LoadState, unload: LoadState) -> LoadState:
    totals = {(flower_type, color): count for flower_type, color, count in load}
    for flower_type, color, count in unload:
        totals[(flower_type, color)] = totals.get((flower_type, color), 0) - count
    return normalize_load(
        (flower_type, color, count) for (flower_type, color), count in totals.items()
    )


def subtract_needs(
    needs: NeedsState,
    pavilion_id: str,
    unload: LoadState,
) -> NeedsState:
    delivered = {(flower_type, color): count for flower_type, color, count in unload}
    updated: list[NeedItem] = []
    for need_pavilion, flower_type, position, color, count in needs:
        if need_pavilion == pavilion_id and (flower_type, color) in delivered:
            count -= delivered[(flower_type, color)]
        updated.append((need_pavilion, flower_type, position, color, count))
    return normalize_needs(updated)


def pavilion_facts(scenario: Scenario) -> tuple[tuple[str, str, tuple[int, int]], ...]:
    return tuple(
        (pavilion.pavilion_id, pavilion.flower_type, pavilion.position.as_tuple())
        for pavilion in scenario.pavilions
    )


def needs_by_pavilion(pavilions: Iterable[Pavilion]) -> dict[str, LoadState]:
    return {
        pavilion.pavilion_id: normalize_load(
            (pavilion.flower_type, color, count)
            for color, count in pavilion.needs.items()
        )
        for pavilion in pavilions
    }
