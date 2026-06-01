from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from flower_robot.domain.flowers import color_label, flower_label
from flower_robot.domain.state import LoadState, NeedsState
from flower_robot.engine.search_engine import FlowerRobotEngine


def print_run_report(engine: FlowerRobotEngine, show_tree: bool = False) -> None:
    print(f"Strategy: {engine.strategy_name}")
    print(f"Generated nodes: {len(engine.node_records)}")
    if engine.solution is None:
        print("No solution found.")
        return

    print(f"Solution cost: {engine.solution['cost']}")
    print("Solution path:")
    for index, step in enumerate(engine.solution["path"]):
        print(_format_path_step(index, step))

    if show_tree:
        print()
        print("Generated search tree:")
        for node_id in engine.tree_order:
            print(_format_tree_node(engine.node_records[node_id]))


def _format_path_step(index: int, step: dict[str, Any]) -> str:
    return (
        f"  {index:02d}. {step['action']} | "
        f"pos={step['pos']} load=[{_format_items(step['load'])}] "
        f"remaining={_remaining_count(step['needs'])} g={step['g']} h={step['h']} f={step['f']}"
    )


def _format_tree_node(step: dict[str, Any]) -> str:
    return (
        f"  node {step['id']:03d} parent={step['parent']} "
        f"g={step['g']} h={step['h']} f={step['f']} "
        f"pos={step['pos']} action={step['action']}"
    )


def _format_items(items: LoadState | Iterable[tuple[str, str, int]]) -> str:
    parts = [
        f"{count} {color_label(color)} {flower_label(flower_type)}"
        for flower_type, color, count in items
    ]
    return ", ".join(parts) if parts else "empty"


def _remaining_count(needs: NeedsState) -> int:
    return sum(count for _, _, _, _, count in needs)
