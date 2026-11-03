"""Maze loading, checking, and display helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


Position = tuple[int, int]
ALLOWED_CELLS = set("#SG.123456789")


@dataclass(frozen=True)
class Maze:
    """A rectangular maze where the cost is paid when entering a cell"""

    name: str
    rows: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.rows:
            raise ValueError("A maze needs at least one row.")
        width = len(self.rows[0])
        if width == 0 or any(len(row) != width for row in self.rows):
            raise ValueError("All maze rows must have the same nonzero length.")
        if any(cell not in ALLOWED_CELLS for row in self.rows for cell in row):
            raise ValueError("Maze contains a cell symbol that is not allowed.")
        if sum(row.count("S") for row in self.rows) != 1:
            raise ValueError("Maze must have exactly one start cell.")
        if sum(row.count("G") for row in self.rows) != 1:
            raise ValueError("Maze must have exactly one goal cell.")

    @property
    def height(self) -> int:
        return len(self.rows)

    @property
    def width(self) -> int:
        return len(self.rows[0])

    def find(self, symbol: str) -> Position:
        for row_index, row in enumerate(self.rows):
            column_index = row.find(symbol)
            if column_index >= 0:
                return row_index, column_index
        raise ValueError(f"Maze does not contain {symbol}.")

    @property
    def start(self) -> Position:
        return self.find("S")

    @property
    def goal(self) -> Position:
        return self.find("G")

    def cell_cost(self, position: Position) -> int:
        cell = self.rows[position[0]][position[1]]
        return int(cell) if cell.isdigit() else 1

    def neighbors(self, position: Position) -> Iterable[tuple[Position, int]]:
        row, column = position
        for next_row, next_column in (
            (row - 1, column),
            (row, column - 1),
            (row, column + 1),
            (row + 1, column),
        ):
            if 0 <= next_row < self.height and 0 <= next_column < self.width:
                if self.rows[next_row][next_column] != "#":
                    next_position = (next_row, next_column)
                    yield next_position, self.cell_cost(next_position)

    def path_cost(self, path: tuple[Position, ...]) -> int:
        if not path:
            return 0
        return sum(self.cell_cost(position) for position in path[1:])

    def render_path(self, path: tuple[Position, ...]) -> str:
        path_cells = set(path[1:-1])
        rendered = []
        for row_index, row in enumerate(self.rows):
            line = "".join(
                "*" if (row_index, column_index) in path_cells else cell
                for column_index, cell in enumerate(row)
            )
            rendered.append(line)
        return "\n".join(rendered)


def load_maze(path: str | Path) -> Maze:
    """Load one maze from a JSON file."""
    maze_path = Path(path)
    with maze_path.open(encoding="utf-8") as file:
        data = json.load(file)
    return Maze(name=data["name"], rows=tuple(data["rows"]))

