"""
maze_solver.py
--------------
Three maze-solving algorithms, each returning a step-by-step animation frame list.

Algorithms:
  - BFS   (Breadth-First Search)   — guaranteed shortest path
  - DFS   (Depth-First Search)     — fast but not shortest
  - A*    (A-star)                 — shortest path, guided by heuristic (faster than BFS)

All solvers work on maze cell coordinates (row, col), not grid pixels.
They use the binary grid to check whether a wall between two cells is open.

Returns a SolveResult containing:
  - path         : list of (row, col) cells from start to end
  - frames       : list of visited-cell snapshots for animation
  - cells_visited: how many unique cells were explored
  - steps        : number of animation frames
  - solve_time_ms: wall-clock time in milliseconds
"""

import time
import heapq
from collections import deque
from dataclasses import dataclass, field


@dataclass
class SolveResult:
    path: list
    frames: list
    cells_visited: int
    steps: int
    solve_time_ms: float
    path_length: int


def _neighbors(grid, r, c, rows, cols):
    """Returns maze-cell neighbors reachable from (r, c) — i.e. no wall between them."""
    result = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            # Check if the wall pixel between (r,c) and (nr,nc) is open
            wall_r = 2 * r + 1 + dr
            wall_c = 2 * c + 1 + dc
            if grid[wall_r][wall_c] == 1:
                result.append((nr, nc))
    return result


def _reconstruct_path(parent, end):
    """Walks the parent map backwards from end to start to build the path."""
    path = []
    node = end
    while node is not None:
        path.append(node)
        node = parent[node]
    return list(reversed(path))


def _snapshot_interval(total_cells):
    """Record a frame every N steps so animation stays ~200 frames regardless of maze size."""
    return max(1, total_cells // 200)


def solve_bfs(grid, rows, cols, start=(0, 0), end=None):
    """
    Breadth-First Search: explores cells level by level.
    Always finds the shortest path (fewest cells).
    """
    if end is None:
        end = (rows - 1, cols - 1)

    t0 = time.perf_counter()

    queue = deque([start])
    parent = {start: None}
    visited_set = {start}
    frames = []
    interval = _snapshot_interval(rows * cols)
    step = 0

    while queue:
        r, c = queue.popleft()
        step += 1

        if step % interval == 0:
            frames.append(frozenset(visited_set))

        if (r, c) == end:
            break

        for nr, nc in _neighbors(grid, r, c, rows, cols):
            if (nr, nc) not in visited_set:
                visited_set.add((nr, nc))
                parent[(nr, nc)] = (r, c)
                queue.append((nr, nc))

    path = _reconstruct_path(parent, end) if end in parent else []
    frames.append(frozenset(visited_set))  # final frame

    elapsed = (time.perf_counter() - t0) * 1000
    return SolveResult(
        path=path,
        frames=frames,
        cells_visited=len(visited_set),
        steps=len(frames),
        solve_time_ms=round(elapsed, 3),
        path_length=len(path),
    )


def solve_dfs(grid, rows, cols, start=(0, 0), end=None):
    """
    Depth-First Search: dives deep before backtracking.
    Finds A path but not necessarily the shortest one.
    """
    if end is None:
        end = (rows - 1, cols - 1)

    t0 = time.perf_counter()

    stack = [start]
    parent = {start: None}
    visited_set = {start}
    frames = []
    interval = _snapshot_interval(rows * cols)
    step = 0
    found = False

    while stack:
        r, c = stack.pop()
        step += 1

        if step % interval == 0:
            frames.append(frozenset(visited_set))

        if (r, c) == end:
            found = True
            break

        for nr, nc in _neighbors(grid, r, c, rows, cols):
            if (nr, nc) not in visited_set:
                visited_set.add((nr, nc))
                parent[(nr, nc)] = (r, c)
                stack.append((nr, nc))

    path = _reconstruct_path(parent, end) if found else []
    frames.append(frozenset(visited_set))

    elapsed = (time.perf_counter() - t0) * 1000
    return SolveResult(
        path=path,
        frames=frames,
        cells_visited=len(visited_set),
        steps=len(frames),
        solve_time_ms=round(elapsed, 3),
        path_length=len(path),
    )


def _manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def solve_astar(grid, rows, cols, start=(0, 0), end=None):
    """
    A* Search: like BFS but guided by a heuristic (Manhattan distance to goal).
    Finds the shortest path and typically visits fewer cells than BFS.
    """
    if end is None:
        end = (rows - 1, cols - 1)

    t0 = time.perf_counter()

    # Priority queue entries: (f_score, g_score, cell)
    open_set = [(0, 0, start)]
    parent = {start: None}
    g_score = {start: 0}
    visited_set = set()
    frames = []
    interval = _snapshot_interval(rows * cols)
    step = 0

    while open_set:
        _, g, (r, c) = heapq.heappop(open_set)

        if (r, c) in visited_set:
            continue
        visited_set.add((r, c))
        step += 1

        if step % interval == 0:
            frames.append(frozenset(visited_set))

        if (r, c) == end:
            break

        for nr, nc in _neighbors(grid, r, c, rows, cols):
            new_g = g + 1
            if new_g < g_score.get((nr, nc), float("inf")):
                g_score[(nr, nc)] = new_g
                f = new_g + _manhattan((nr, nc), end)
                heapq.heappush(open_set, (f, new_g, (nr, nc)))
                parent[(nr, nc)] = (r, c)

    path = _reconstruct_path(parent, end) if end in parent else []
    frames.append(frozenset(visited_set))

    elapsed = (time.perf_counter() - t0) * 1000
    return SolveResult(
        path=path,
        frames=frames,
        cells_visited=len(visited_set),
        steps=len(frames),
        solve_time_ms=round(elapsed, 3),
        path_length=len(path),
    )
