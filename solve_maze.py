"""Run one selected search method and print its path."""

from __future__ import annotations

import argparse

try:  
    from .search_algorithms import run_algorithm
except ImportError:
    from maze import load_maze
    from search_algorithms import run_algorithm


def main() -> None:
    parser = argparse.ArgumentParser(description="Solve one maze with one search method.")
    parser.add_argument("maze_file", help="Path to a maze JSON file")
    parser.add_argument("algorithm", help="bfs, dfs, ucs, greedy, or astar")
    arguments = parser.parse_args()
    maze = load_maze(arguments.maze_file)
    result = run_algorithm(arguments.algorithm, maze)
    print(f"Maze: {maze.name}")
    print(f"Algorithm: {result.algorithm}")
    print(f"Path found: {result.found}")
    print(f"Path length: {result.path_length}")
    print(f"Path cost: {result.path_cost}")
    print(f"States expanded: {result.states_expanded}")
    print(f"Runtime (ms): {result.runtime_ms:.6f}")
    if result.found:
        print("\nPath:")
        print(maze.render_path(result.path))


if __name__ == "__main__":
    main()

