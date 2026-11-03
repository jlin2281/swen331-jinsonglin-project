# Maze Solver: Comparing Search Algorithms

Developer: Add your name before publishing.

## Abstract

This project compares five search methods on grid mazes: Breadth-First Search, Depth-First Search, Uniform-Cost Search, Greedy Best-First Search, and A-star Search. The project uses ten unweighted mazes and ten weighted mazes. Each run records whether a path was found, path length, path cost, states expanded, and run time.

This is a search project, not a machine-learning training project. Training data, model training, and train-test splits do not apply. The maze files are checked before each run to make sure they have one start, one goal, valid rows, and allowed cell symbols.

## Folder layout

- `code/`: search methods, maze tools, tests, and experiment scripts.
- `data/mazes/`: the 20 generated maze files.
- `resources/`: plan and check-in notes.
- `results/`: CSV files and a short summary from the experiment runs.

## Run the project

```bash
python3 code/generate_mazes.py
python3 code/test_maze_solver.py
python3 code/run_experiments.py
python3 code/solve_maze.py data/mazes/weighted_01.json astar
python3 code/maze_viewer.py
```

`maze_viewer.py` opens a window with larger maze cells, maze and algorithm pickers, a Solve button, and the result numbers for the selected run.

## Maze format

Each JSON file contains a maze name and a list of equal-length text rows.

- `#` is a wall.
- `S` is the start.
- `G` is the goal.
- `.` and `1` cost 1 to enter.
- `2` through `9` cost that number to enter.

The solver can move up, down, left, or right. It cannot move through a wall

