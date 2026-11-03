"""A simple window for viewing a maze and the path found by a search method"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

try:
    from .maze import Maze, load_maze
    from .search_algorithms import run_algorithm
except ImportError:
    from maze import Maze, load_maze
    from search_algorithms import run_algorithm


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAZE_FOLDER = PROJECT_ROOT / "data" / "mazes"
ALGORITHM_LABELS = {
    "Breadth-First Search": "bfs",
    "Depth-First Search": "dfs",
    "Uniform-Cost Search": "ucs",
    "Greedy Best-First Search": "greedy",
    "A-star Search": "astar",
}


class MazeViewer:
    """Shows one maze at a readable size and solves it when asked"""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Maze Solver: Comparing Search Algorithms")
        self.root.minsize(980, 730)
        self.maze_files = sorted(MAZE_FOLDER.glob("*.json"))
        if not self.maze_files:
            raise FileNotFoundError("No maze files were found; run generate_mazes.py first")

        self.maze_name = tk.StringVar(value=self.maze_files[0].name)
        self.algorithm_name = tk.StringVar(value="A-star Search")
        self.status = tk.StringVar(value="Choose a maze and an algorithm, then press Solve")
        self.metrics = {
            "Path found": tk.StringVar(value="-"),
            "Path length": tk.StringVar(value="-"),
            "Path cost": tk.StringVar(value="-"),
            "States expanded": tk.StringVar(value="-"),
            "Runtime": tk.StringVar(value="-"),
        }
        self.current_maze: Maze | None = None
        self.current_path: tuple[tuple[int, int], ...] = ()

        self._build_window()
        self.solve_selected_maze()

    def _build_window(self) -> None:
        main = ttk.Frame(self.root, padding=16)
        main.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=1)

        heading = ttk.Label(
            main,
            text="Maze Solver: Comparing Search Algorithms",
            font=("Helvetica", 18, "bold"),
        )
        heading.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        board_frame = ttk.LabelFrame(main, text="Maze and selected path", padding=10)
        board_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 14))
        board_frame.columnconfigure(0, weight=1)
        board_frame.rowconfigure(0, weight=1)
        self.canvas = tk.Canvas(
            board_frame,
            width=650,
            height=650,
            background="white",
            highlightthickness=1,
            highlightbackground="#999999",
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        controls = ttk.Frame(main)
        controls.grid(row=1, column=1, sticky="ns")
        ttk.Label(controls, text="Maze", font=("Helvetica", 11, "bold")).grid(row=0, column=0, sticky="w")
        self.maze_picker = ttk.Combobox(
            controls,
            textvariable=self.maze_name,
            values=[path.name for path in self.maze_files],
            state="readonly",
            width=25,
        )
        self.maze_picker.grid(row=1, column=0, sticky="ew", pady=(3, 12))

        ttk.Label(controls, text="Search method", font=("Helvetica", 11, "bold")).grid(row=2, column=0, sticky="w")
        self.algorithm_picker = ttk.Combobox(
            controls,
            textvariable=self.algorithm_name,
            values=list(ALGORITHM_LABELS),
            state="readonly",
            width=25,
        )
        self.algorithm_picker.grid(row=3, column=0, sticky="ew", pady=(3, 12))

        ttk.Button(controls, text="Solve", command=self.solve_selected_maze).grid(row=4, column=0, sticky="ew", pady=(0, 12))
        ttk.Label(controls, textvariable=self.status, wraplength=230, justify="left").grid(row=5, column=0, sticky="w", pady=(0, 14))

        metrics_frame = ttk.LabelFrame(controls, text="Run results", padding=10)
        metrics_frame.grid(row=6, column=0, sticky="ew")
        for row, (label, value) in enumerate(self.metrics.items()):
            ttk.Label(metrics_frame, text=f"{label}:", font=("Helvetica", 10, "bold")).grid(row=row, column=0, sticky="w", pady=2)
            ttk.Label(metrics_frame, textvariable=value).grid(row=row, column=1, sticky="e", padx=(12, 0), pady=2)

        legend = ttk.LabelFrame(controls, text="Legend", padding=10)
        legend.grid(row=7, column=0, sticky="ew", pady=(14, 0))
        for row, text in enumerate((
            "Black: wall",
            "Green: start",
            "Red: goal",
            "Blue: chosen path",
            "Yellow: higher-cost cell",
        )):
            ttk.Label(legend, text=text).grid(row=row, column=0, sticky="w", pady=1)

    def solve_selected_maze(self) -> None:
        try:
            maze_path = MAZE_FOLDER / self.maze_name.get()
            maze = load_maze(maze_path)
            algorithm_key = ALGORITHM_LABELS[self.algorithm_name.get()]
            result = run_algorithm(algorithm_key, maze)
        except (OSError, ValueError, KeyError) as error:
            messagebox.showerror("Could not solve maze", str(error))
            return

        self.current_maze = maze
        self.current_path = result.path
        self.metrics["Path found"].set("Yes" if result.found else "No")
        self.metrics["Path length"].set(str(result.path_length) if result.found else "-")
        self.metrics["Path cost"].set(str(result.path_cost) if result.found else "-")
        self.metrics["States expanded"].set(str(result.states_expanded))
        self.metrics["Runtime"].set(f"{result.runtime_ms:.3f} ms")
        self.status.set(f"{result.algorithm} solved {maze.name}.")
        self.draw_maze()

    def draw_maze(self) -> None:
        if self.current_maze is None:
            return
        maze = self.current_maze
        self.canvas.delete("all")
        board_size = 630
        cell_size = max(14, min(32, board_size // max(maze.width, maze.height)))
        grid_width = maze.width * cell_size
        grid_height = maze.height * cell_size
        left = (650 - grid_width) // 2
        top = (650 - grid_height) // 2
        path_cells = set(self.current_path[1:-1])

        for row in range(maze.height):
            for column in range(maze.width):
                cell = maze.rows[row][column]
                position = (row, column)
                fill = "#202020" if cell == "#" else "#F7F7F7"
                if cell.isdigit() and cell != "1":
                    fill = "#FFE59A"
                if position in path_cells:
                    fill = "#8ECDF4"
                if cell == "S":
                    fill = "#53A853"
                elif cell == "G":
                    fill = "#E55555"
                x1 = left + column * cell_size
                y1 = top + row * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="#B0B0B0")
                if cell in "SG" or (cell.isdigit() and cell != "1"):
                    text_color = "white" if cell in "SG" else "black"
                    self.canvas.create_text(
                        (x1 + x2) // 2,
                        (y1 + y2) // 2,
                        text=cell,
                        fill=text_color,
                        font=("Helvetica", max(9, cell_size // 2), "bold"),
                    )


def main() -> None:
    root = tk.Tk()
    MazeViewer(root)
    root.mainloop()


if __name__ == "__main__":
    main()

