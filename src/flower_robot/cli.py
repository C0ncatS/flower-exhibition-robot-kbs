from __future__ import annotations

import argparse
from pathlib import Path

import flower_robot.compat  # noqa: F401
from flower_robot.engine.search_engine import run_engine
from flower_robot.io.reporting import print_run_report
from flower_robot.io.tree_viz import DEFAULT_TREE_OUTPUT, write_search_tree_html
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
    parser.add_argument(
        "--tree-html",
        metavar="PATH",
        nargs="?",
        const=str(DEFAULT_TREE_OUTPUT),
        help=f"Write interactive search tree (Pyvis HTML); default: {DEFAULT_TREE_OUTPUT}",
    )
    parser.add_argument(
        "--open-tree",
        action="store_true",
        help="Open the generated tree HTML in the default browser",
    )
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
        if args.tree_html is not None:
            html_path = args.tree_html
            if len(strategies) > 1:
                stem = Path(html_path).stem
                suffix = Path(html_path).suffix or ".html"
                html_path = f"{stem}_{strategy}{suffix}"
            written = write_search_tree_html(
                engine,
                html_path,
                open_browser=args.open_tree,
            )
            print(f"Search tree visualization: {written.resolve()}")
        print()
