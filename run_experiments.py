"""Run every algorithm on every project maze and save comparison files."""

from __future__ import annotations

import csv
import statistics
from pathlib import Path

try:  
    from .maze import load_maze
    from .search_algorithms import ALGORITHMS
except ImportError:
    from maze import load_maze
    from search_algorithms import ALGORITHMS


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAZE_FOLDER = PROJECT_ROOT / "data" / "mazes"
RESULTS_FOLDER = PROJECT_ROOT / "results"


def run_experiments() -> None:
    if not list(MAZE_FOLDER.glob("*.json")):
        raise FileNotFoundError("No maze files found. Run generate_mazes.py first.")
    RESULTS_FOLDER.mkdir(exist_ok=True)
    records: list[dict[str, object]] = []
    for maze_path in sorted(MAZE_FOLDER.glob("*.json")):
        maze = load_maze(maze_path)
        maze_type = "weighted" if maze.name.startswith("weighted") else "unweighted"
        for algorithm_name, algorithm in ALGORITHMS.items():
            result = algorithm(maze)
            records.append({
                "maze": maze.name,
                "maze_type": maze_type,
                "algorithm": result.algorithm,
                "found": result.found,
                "path_length": result.path_length,
                "path_cost": result.path_cost,
                "states_expanded": result.states_expanded,
                "runtime_ms": f"{result.runtime_ms:.6f}",
            })

    results_path = RESULTS_FOLDER / "experiment_results.csv"
    with results_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

    summary_rows = []
    for algorithm_name in ["BFS", "DFS", "UCS", "Greedy", "A*"]:
        for maze_type in ["unweighted", "weighted"]:
            group = [record for record in records if record["algorithm"] == algorithm_name and record["maze_type"] == maze_type]
            summary_rows.append({
                "algorithm": algorithm_name,
                "maze_type": maze_type,
                "mazes_solved": f"{sum(bool(record['found']) for record in group)}/{len(group)}",
                "average_path_cost": f"{statistics.mean(record['path_cost'] for record in group):.2f}",
                "average_path_length": f"{statistics.mean(record['path_length'] for record in group):.2f}",
                "average_states_expanded": f"{statistics.mean(record['states_expanded'] for record in group):.2f}",
                "average_runtime_ms": f"{statistics.mean(float(record['runtime_ms']) for record in group):.6f}",
            })
    summary_path = RESULTS_FOLDER / "summary_results.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=summary_rows[0].keys())
        writer.writeheader()
        writer.writerows(summary_rows)

    notes = [
        "Experiment summary",
        "",
        "The result files compare five search methods on 10 unweighted and 10 weighted mazes.",
        "BFS should be judged by path length on unweighted mazes.",
        "UCS and A-star should be judged by path cost on weighted mazes.",
        "DFS and Greedy may find a path quickly but do not promise the lowest-cost path.",
        "Runtime values are small and can change between runs, so states expanded is also important.",
    ]
    (RESULTS_FOLDER / "analysis_notes.txt").write_text("\n".join(notes) + "\n", encoding="utf-8")
    print(f"Saved {len(records)} runs to {results_path}")
    print(f"Saved summary to {summary_path}")


if __name__ == "__main__":
    run_experiments()

