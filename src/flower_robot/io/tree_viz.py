from __future__ import annotations

from pathlib import Path
from typing import Any

from pyvis.network import Network

from flower_robot.engine.search_engine import FlowerRobotEngine

DEFAULT_TREE_OUTPUT = Path("output") / "search_tree.html"

_SOLUTION_COLOR = "#4caf50"
_ROOT_COLOR = "#2196f3"
_DEFAULT_COLOR = "#e0e0e0"


def write_search_tree_html(
    engine: FlowerRobotEngine,
    output_path: str | Path,
    *,
    open_browser: bool = False,
) -> Path:
    """Build an interactive Pyvis graph of the generated search tree."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    solution_ids = _solution_node_ids(engine)
    net = Network(
        directed=True,
        height="900px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#111111",
    )
    net.set_options(_hierarchical_options())

    for node_id, record in engine.node_records.items():
        net.add_node(
            node_id,
            label=_node_label(record),
            title=_node_tooltip(record),
            color=_node_color(record, solution_ids),
        )

    for record in engine.node_records.values():
        parent = record.get("parent")
        if parent is not None:
            net.add_edge(parent, record["id"])

    net.write_html(str(path), open_browser=open_browser, notebook=False)
    return path


def _solution_node_ids(engine: FlowerRobotEngine) -> set[int]:
    if engine.solution is None:
        return set()
    return {step["id"] for step in engine.solution["path"]}


def _node_color(record: dict[str, Any], solution_ids: set[int]) -> str:
    node_id = record["id"]
    if node_id in solution_ids:
        return _SOLUTION_COLOR
    if record.get("parent") is None:
        return _ROOT_COLOR
    return _DEFAULT_COLOR


def _node_label(record: dict[str, Any]) -> str:
    action = record.get("action") or "start"
    return f"{record['id']}\n{action}\ng={record['g']} f={record['f']}"


def _node_tooltip(record: dict[str, Any]) -> str:
    lines = [
        f"id: {record['id']}",
        f"parent: {record.get('parent')}",
        f"action: {record.get('action')}",
        f"pos: {record.get('pos')}",
        f"g={record.get('g')} h={record.get('h')} f={record.get('f')}",
        f"status: {record.get('status')}",
    ]
    return "<br>".join(lines)


def _hierarchical_options() -> str:
    return """
{
  "layout": {
    "hierarchical": {
      "enabled": true,
      "direction": "UD",
      "sortMethod": "directed",
      "levelSeparation": 120,
      "nodeSpacing": 140
    }
  },
  "edges": {
    "arrows": { "to": { "enabled": true, "scaleFactor": 0.5 } },
    "smooth": { "type": "cubicBezier", "forceDirection": "vertical" }
  },
  "physics": {
    "enabled": false
  },
  "interaction": {
    "hover": true,
    "tooltipDelay": 100
  }
}
"""
