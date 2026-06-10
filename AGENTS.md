# AGENTS.md - Flower Robot KBS

## Execution & Commands
- **Run CLI:** `uv run flower-robot [ARGS]` or `uv run python main.py [ARGS]`
- **Install Deps:** `uv sync`
- **Key CLI Args:**
  - `--scenario PATH`: JSON scenario file (default: `scenarios/example.json`).
  - `--strategy dfs | astar | both`: Search algorithm.
  - `--heuristic default | zero`: A* heuristic.
  - `--show-tree`: Print search tree to console.
  - `--tree-html [PATH]`: Generate Pyvis HTML (default: `output/search_tree.html`).
  - `--open-tree`: Open HTML tree in browser.
  - `--max-steps N`: Limit experta activations.

## Architecture & Workflow
- **`src/flower_robot/domain/`**: Pure Python logic, problem constraints, and precomputed choice points.
- **`src/flower_robot/facts/`**: `experta` fact definitions (schema).
- **`src/flower_robot/engine/`**: Forward-chaining rules.
  - `operators.py`: Move/load/unload actions.
  - `dedup.py`: Duplicate state pruning.
  - `constraints.py`: State validation and retraction.
  - `strategy.py`: Node selection (DFS vs A*).
  - `goal.py`: Goal check and solution path.
- **`src/flower_robot/search/`**: Node creation and A* cost (g, h, f) calculation.
- **`src/flower_robot/io/`**: Scenario loading and Pyvis visualization.

## Development Conventions
- **Experta Rules**:
  - **Avoid loops** inside `@Rule` bodies. Use patterns and facts on the LHS.
  - Loops are permitted in `domain/` and `search/` (non-rule code).
- **Python 3.14 Compatibility**:
  - MUST import `flower_robot.compat` before `experta` in any new module using `experta` to avoid `collections.Mapping` errors.
- **A* Implementation**:
  - Uses `LowestOpenNodeFact` to track the best node without using `min()` inside rules.
  - Heuristics are located in `src/flower_robot/search/heuristics.py`.
- **Scenarios**:
  - JSON files in `scenarios/`. Positions are **1-based** `(x, y)`.
