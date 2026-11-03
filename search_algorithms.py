"""Five search methods used by the maze."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import count
from time import perf_counter_ns
from typing import Callable

try: 
    from .maze import Maze, Position
except ImportError:
    from maze import Maze, Position


@dataclass(frozen=True)
class SearchResult:
    algorithm: str
    found: bool
    path: tuple[Position, ...]
    path_cost: int | None
    path_length: int | None
    states_expanded: int
    runtime_ms: float


def manhattan_distance(first: Position, second: Position) -> int:
    return abs(first[0] - second[0]) + abs(first[1] - second[1])


def _finish(
    algorithm: str,
    maze: Maze,
    parents: dict[Position, Position | None],
    found: bool,
    states_expanded: int,
    start_time: int,
) -> SearchResult:
    runtime_ms = (perf_counter_ns() - start_time) / 1_000_000
    if not found:
        return SearchResult(algorithm, False, (), None, None, states_expanded, runtime_ms)
    path_nodes: list[Position] = []
    current: Position | None = maze.goal
    while current is not None:
        path_nodes.append(current)
        current = parents[current]
    path = tuple(reversed(path_nodes))
    return SearchResult(
        algorithm=algorithm,
        found=True,
        path=path,
        path_cost=maze.path_cost(path),
        path_length=len(path) - 1,
        states_expanded=states_expanded,
        runtime_ms=runtime_ms,
    )


def breadth_first_search(maze: Maze) -> SearchResult:
    start_time = perf_counter_ns()
    frontier = deque([maze.start])
    parents: dict[Position, Position | None] = {maze.start: None}
    states_expanded = 0
    while frontier:
        current = frontier.popleft()
        states_expanded += 1
        if current == maze.goal:
            return _finish("BFS", maze, parents, True, states_expanded, start_time)
        for neighbor, _ in maze.neighbors(current):
            if neighbor not in parents:
                parents[neighbor] = current
                frontier.append(neighbor)
    return _finish("BFS", maze, parents, False, states_expanded, start_time)


def depth_first_search(maze: Maze) -> SearchResult:
    start_time = perf_counter_ns()
    frontier = [maze.start]
    parents: dict[Position, Position | None] = {maze.start: None}
    states_expanded = 0
    while frontier:
        current = frontier.pop()
        states_expanded += 1
        if current == maze.goal:
            return _finish("DFS", maze, parents, True, states_expanded, start_time)
        neighbors = list(maze.neighbors(current))
        for neighbor, _ in reversed(neighbors):
            if neighbor not in parents:
                parents[neighbor] = current
                frontier.append(neighbor)
    return _finish("DFS", maze, parents, False, states_expanded, start_time)


def uniform_cost_search(maze: Maze) -> SearchResult:
    start_time = perf_counter_ns()
    order = count()
    frontier: list[tuple[int, int, Position]] = [(0, next(order), maze.start)]
    costs = {maze.start: 0}
    parents: dict[Position, Position | None] = {maze.start: None}
    states_expanded = 0
    while frontier:
        current_cost, _, current = heappop(frontier)
        if current_cost != costs[current]:
            continue
        states_expanded += 1
        if current == maze.goal:
            return _finish("UCS", maze, parents, True, states_expanded, start_time)
        for neighbor, move_cost in maze.neighbors(current):
            next_cost = current_cost + move_cost
            if next_cost < costs.get(neighbor, float("inf")):
                costs[neighbor] = next_cost
                parents[neighbor] = current
                heappush(frontier, (next_cost, next(order), neighbor))
    return _finish("UCS", maze, parents, False, states_expanded, start_time)


def greedy_best_first_search(maze: Maze) -> SearchResult:
    start_time = perf_counter_ns()
    order = count()
    frontier: list[tuple[int, int, Position]] = [(manhattan_distance(maze.start, maze.goal), next(order), maze.start)]
    parents: dict[Position, Position | None] = {maze.start: None}
    closed: set[Position] = set()
    states_expanded = 0
    while frontier:
        _, _, current = heappop(frontier)
        if current in closed:
            continue
        closed.add(current)
        states_expanded += 1
        if current == maze.goal:
            return _finish("Greedy", maze, parents, True, states_expanded, start_time)
        for neighbor, _ in maze.neighbors(current):
            if neighbor not in closed and neighbor not in parents:
                parents[neighbor] = current
                priority = manhattan_distance(neighbor, maze.goal)
                heappush(frontier, (priority, next(order), neighbor))
    return _finish("Greedy", maze, parents, False, states_expanded, start_time)


def a_star_search(maze: Maze) -> SearchResult:
    start_time = perf_counter_ns()
    order = count()
    frontier: list[tuple[int, int, int, Position]] = [
        (manhattan_distance(maze.start, maze.goal), 0, next(order), maze.start)
    ]
    costs = {maze.start: 0}
    parents: dict[Position, Position | None] = {maze.start: None}
    states_expanded = 0
    while frontier:
        _, current_cost, _, current = heappop(frontier)
        if current_cost != costs[current]:
            continue
        states_expanded += 1
        if current == maze.goal:
            return _finish("A*", maze, parents, True, states_expanded, start_time)
        for neighbor, move_cost in maze.neighbors(current):
            next_cost = current_cost + move_cost
            if next_cost < costs.get(neighbor, float("inf")):
                costs[neighbor] = next_cost
                parents[neighbor] = current
                priority = next_cost + manhattan_distance(neighbor, maze.goal)
                heappush(frontier, (priority, next_cost, next(order), neighbor))
    return _finish("A*", maze, parents, False, states_expanded, start_time)


ALGORITHMS: dict[str, Callable[[Maze], SearchResult]] = {
    "bfs": breadth_first_search,
    "dfs": depth_first_search,
    "ucs": uniform_cost_search,
    "greedy": greedy_best_first_search,
    "astar": a_star_search,
}


def run_algorithm(name: str, maze: Maze) -> SearchResult:
    normalized_name = name.lower().replace("-", "")
    if normalized_name not in ALGORITHMS:
        choices = ", ".join(ALGORITHMS)
        raise ValueError(f"Unknown algorithm: {name}. Choose one of: {choices}")
    return ALGORITHMS[normalized_name](maze)

