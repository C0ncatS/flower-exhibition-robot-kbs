from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from flower_robot.domain.models import Pavilion, Scenario
from flower_robot.domain.position import Position

DEFAULT_SCENARIO_PATH = Path(__file__).resolve().parents[3] / "scenarios" / "example.json"


def load_scenario(path: str | Path | None = None) -> Scenario:
    scenario_path = Path(path) if path else DEFAULT_SCENARIO_PATH
    with scenario_path.open("r", encoding="utf-8") as handle:
        return scenario_from_dict(json.load(handle))


def scenario_from_dict(data: dict[str, Any]) -> Scenario:
    return Scenario(
        width=int(data["grid"]["width"]),
        height=int(data["grid"]["height"]),
        warehouse=Position.from_pair(data["warehouse"]),
        robot_start=Position.from_pair(data["robot_start"]),
        pavilions=tuple(_pavilion_from_dict(item) for item in data["pavilions"]),
    )


def _pavilion_from_dict(data: dict[str, Any]) -> Pavilion:
    return Pavilion(
        pavilion_id=str(data["id"]),
        flower_type=str(data["flower_type"]),
        position=Position.from_pair(data["position"]),
        needs={str(color): int(count) for color, count in data["needs"].items()},
    )
