"""
maze_generator.py
-----------------
Generates mazes using iterative Depth-First Search (recursive backtracking).

The maze is stored as a binary grid of shape (2*rows+1, 2*cols+1):
  - 0 = wall (black)
  - 1 = passage (white)

Each maze cell (r, c) occupies pixel (2r+1, 2c+1) in the grid.
The wall between two adjacent cells sits at the pixel between them.

A "perfect maze" has exactly one path between any two cells — no loops.
An "imperfect maze" has extra walls removed, creating loops and multiple paths.
This means BFS/A* and DFS can now find DIFFERENT path lengths, making comparisons meaningful.
"""

import numpy as np
import random


def generate_maze(rows: int, cols: int, loop_factor: float = 0.0) -> np.ndarray:
    """
    Generates a maze and returns the binary grid.

    Parameters:
        rows, cols   — maze dimensions
        loop_factor  — fraction of remaining walls to remove after generation (0.0 to 1.0).
                       0.0 = perfect maze (one unique path).
                       0.3 = ~30% of internal walls removed, creating many shortcuts/loops.
                       Higher values = more open maze = bigger difference between algorithms.

    Algorithm: iterative DFS with backtracking (recursive backtracking).
      1. Start at cell (0, 0), mark it visited.
      2. While the stack is non-empty:
         a. Look at the current cell's unvisited neighbors.
         b. If any exist, pick one at random, carve the wall between them, push neighbor.
         c. If none exist, backtrack (pop the stack).
      3. After generation, randomly remove extra walls based on loop_factor.
         This creates cycles — multiple paths between cells — so algorithms diverge.
    """
    # Binary grid: all walls up initially (everything is 0)
    grid = np.zeros((2 * rows + 1, 2 * cols + 1), dtype=np.uint8)

    # Open the cell pixels (passages exist, walls still closed)
    for r in range(rows):
        for c in range(cols):
            grid[2 * r + 1][2 * c + 1] = 1

    visited = np.zeros((rows, cols), dtype=bool)

    start_r, start_c = 0, 0
    visited[start_r][start_c] = True
    stack = [(start_r, start_c)]

    # Directions: (row_delta, col_delta)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while stack:
        r, c = stack[-1]

        # Find unvisited neighbors
        neighbors = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                neighbors.append((nr, nc, dr, dc))

        if neighbors:
            # Choose a random unvisited neighbor
            nr, nc, dr, dc = random.choice(neighbors)

            # Carve the wall between current cell and chosen neighbor
            # Wall pixel is halfway between the two cell pixels
            grid[2 * r + 1 + dr][2 * c + 1 + dc] = 1

            visited[nr][nc] = True
            stack.append((nr, nc))
        else:
            # Dead end — backtrack
            stack.pop()

    # ── Add loops by removing extra internal walls ────────────────────────────
    if loop_factor > 0.0:
        # Collect all internal wall pixels that are still closed (value == 0)
        # and sit between two valid cells (not on the border)
        walls = []
        for r in range(rows):
            for c in range(cols):
                for dr, dc in [(0, 1), (1, 0)]:  # only right and down to avoid duplicates
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        wr = 2 * r + 1 + dr
                        wc = 2 * c + 1 + dc
                        if grid[wr][wc] == 0:  # wall still up
                            walls.append((wr, wc))

        # Randomly remove a fraction of these walls
        n_remove = int(len(walls) * loop_factor)
        random.shuffle(walls)
        for wr, wc in walls[:n_remove]:
            grid[wr][wc] = 1  # carve the wall — creates a loop

    return grid
