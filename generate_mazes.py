"""Create the 10 unweighted and 10 weighted maze files"""

from __future__ import annotations

import json
import random
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAZE_FOLDER = PROJECT_ROOT / "data" / "mazes"


def _carve_maze(width: int, height: int, seed: int) -> list[list[str]]:
    """Make a connected maze with some extra openings for alternate routes"""
    randomizer = random.Random(seed)
    grid = [["#" for _ in range(width)] for _ in range(height)]
    start = (1, 1)
    grid[start[0]][start[1]] = "."
    stack = [start]
    visited = {start}
    directions = [(-2, 0), (0, -2), (0, 2), (2, 0)]

    while stack:
        row, column = stack[-1]
        choices = []
        for row_change, column_change in directions:
            next_row = row + row_change
            next_column = column + column_change
            if 1 <= next_row < height - 1 and 1 <= next_column < width - 1:
                if (next_row, next_column) not in visited:
                    choices.append((next_row, next_column, row + row_change // 2, column + column_change // 2))
        if not choices:
            stack.pop()
            continue
        next_row, next_column, wall_row, wall_column = randomizer.choice(choices)
        visited.add((next_row, next_column))
        grid[wall_row][wall_column] = "."
        grid[next_row][next_column] = "."
        stack.append((next_row, next_column))

    possible_openings = []
    for row in range(1, height - 1):
        for column in range(1, width - 1):
            if grid[row][column] != "#":
                continue
            horizontal = grid[row][column - 1] != "#" and grid[row][column + 1] != "#"
            vertical = grid[row - 1][column] != "#" and grid[row + 1][column] != "#"
            if horizontal or vertical:
                possible_openings.append((row, column))
    randomizer.shuffle(possible_openings)
    for row, column in possible_openings[: max(5, width // 3)]:
        grid[row][column] = "."

    grid[1][1] = "S"
    grid[height - 2][width - 2] = "G"
    return grid


def _add_weights(grid: list[list[str]], seed: int) -> list[list[str]]:
    randomizer = random.Random(seed)
    weighted = [row[:] for row in grid]
    for row_index, row in enumerate(weighted):
        for column_index, cell in enumerate(row):
            if cell == "." and randomizer.random() < 0.32:
                weighted[row_index][column_index] = str(randomizer.randint(2, 9))
    return weighted


def _write_maze(name: str, grid: list[list[str]]) -> None:
    path = MAZE_FOLDER / f"{name}.json"
    data = {"name": name, "rows": ["".join(row) for row in grid]}
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
        file.write("\n")


def generate_all_mazes() -> None:
    MAZE_FOLDER.mkdir(parents=True, exist_ok=True)
    for index in range(1, 11):
        size = 21 + 2 * ((index - 1) % 3)
        base = _carve_maze(size, size, seed=1000 + index)
        _write_maze(f"unweighted_{index:02}", base)
        _write_maze(f"weighted_{index:02}", _add_weights(base, seed=2000 + index))


if __name__ == "__main__":
    generate_all_mazes()
    print(f"Created 20 maze files in {MAZE_FOLDER}")

