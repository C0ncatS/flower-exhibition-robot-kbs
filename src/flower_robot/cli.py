from __future__ import annotations

import argparse

import flower_robot.compat  # noqa: F401
from flower_robot.engine.search_engine import run_engine
from flower_robot.io.reporting import print_run_report
from flower_robot.io.scenario_loader import load_scenario
from flower_robot.search.heuristics import default_heuristic, zero_heuristic


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Flower robot knowledge-based search")
    parser.add_argument("--scenario", help="Path to a scenario JSON file")
    parser.add_argument(
        "--strategy",
        choices=("dfs", "astar", "both"),
        default="astar",
        help="Search strategy to run",
    )
    parser.add_argument(
        "--heuristic",
        choices=("default", "zero"),
        default="default",
        help="Heuristic used by A*",
    )
    parser.add_argument("--max-steps", type=int, help="Maximum experta activations")
    parser.add_argument("--show-tree", action="store_true", help="Print generated search tree")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scenario = load_scenario(args.scenario)
    heuristic = default_heuristic if args.heuristic == "default" else zero_heuristic
    strategies = ("dfs", "astar") if args.strategy == "both" else (args.strategy,)

    for strategy in strategies:
        engine = run_engine(
            scenario=scenario,
            strategy=strategy,
            heuristic=heuristic,
            max_steps=args.max_steps,
        )
        print_run_report(engine, show_tree=args.show_tree or strategy == "dfs")
        print()
