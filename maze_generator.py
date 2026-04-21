"""
maze_generator.py
-----------------
Generates a perfect maze using iterative Depth-First Search (recursive backtracking).

The maze is stored as a binary grid of shape (2*rows+1, 2*cols+1):
  - 0 = wall (black)
  - 1 = passage (white)

Each maze cell (r, c) occupies pixel (2r+1, 2c+1) in the grid.
The wall between two adjacent cells sits at the pixel between them.

A "perfect maze" has exactly one path between any two cells — no loops, no isolated areas.
"""

import numpy as np
import random


def generate_maze(rows: int, cols: int) -> np.ndarray:
    """
    Generates a perfect maze and returns the binary grid.

    Algorithm: iterative DFS with backtracking.
      1. Start at cell (0, 0), mark it visited.
      2. While the stack is non-empty:
         a. Look at the current cell's unvisited neighbors.
         b. If any exist, pick one at random, carve the wall between them, push neighbor.
         c. If none exist, backtrack (pop the stack).
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

    return grid
