"""Tests for path validity and expected algorithm behavior."""

from __future__ import annotations

import unittest

try:  
    from .maze import Maze
    from .search_algorithms import (
        a_star_search,
        breadth_first_search,
        depth_first_search,
        greedy_best_first_search,
        uniform_cost_search,
    )
except ImportError:
    from maze import Maze
    from search_algorithms import (
        a_star_search,
        breadth_first_search,
        depth_first_search,
        greedy_best_first_search,
        uniform_cost_search,
    )


class MazeSolverTests(unittest.TestCase):
    def test_part1_bfs_and_dfs_find_a_valid_path(self) -> None:
        maze = Maze("small", ("S..", ".#.", "..G"))
        bfs = breadth_first_search(maze)
        dfs = depth_first_search(maze)
        self.assertTrue(bfs.found)
        self.assertEqual(bfs.path_length, 4)
        self.assertEqual(bfs.path_cost, 4)
        self.assertTrue(dfs.found)
        self.assertEqual(dfs.path[0], maze.start)
        self.assertEqual(dfs.path[-1], maze.goal)

    def test_part2_cost_searches_avoid_expensive_short_path(self) -> None:
        maze = Maze("weighted", ("S9G", "111"))
        bfs = breadth_first_search(maze)
        greedy = greedy_best_first_search(maze)
        ucs = uniform_cost_search(maze)
        astar = a_star_search(maze)
        self.assertEqual(bfs.path_cost, 10)
        self.assertEqual(greedy.path_cost, 10)
        self.assertEqual(ucs.path_cost, 4)
        self.assertEqual(astar.path_cost, 4)


if __name__ == "__main__":
    unittest.main()

