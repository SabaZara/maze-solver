"""
maze_renderer.py
----------------
Converts the binary maze grid into matplotlib figures for display in Streamlit.

Color scheme:
  - Black  : walls
  - White  : passages
  - Blue   : cells visited during solving (exploration)
  - Gold   : the final solution path
  - Green  : start cell
  - Red    : end cell
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend — required for Streamlit
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


# RGB colors (0.0–1.0 scale)
COLOR_WALL    = (0.10, 0.10, 0.10)
COLOR_PASSAGE = (0.97, 0.97, 0.97)
COLOR_VISITED = (0.53, 0.81, 0.98)
COLOR_PATH    = (1.00, 0.84, 0.00)
COLOR_START   = (0.18, 0.80, 0.44)
COLOR_END     = (0.91, 0.30, 0.24)


def _build_color_grid(grid, rows, cols, visited, path):
    """
    Builds an RGB image array from the maze grid + overlay data.
    visited and path are sets of maze-cell (row, col) tuples.
    """
    h, w = grid.shape
    rgb = np.zeros((h, w, 3), dtype=float)

    # Base layer: walls and passages
    for gy in range(h):
        for gx in range(w):
            rgb[gy, gx] = COLOR_PASSAGE if grid[gy, gx] == 1 else COLOR_WALL

    # Visited overlay
    for r, c in visited:
        rgb[2 * r + 1, 2 * c + 1] = COLOR_VISITED
        # Also color the passage pixels adjacent to visited cells
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            wr, wc = 2 * r + 1 + dr, 2 * c + 1 + dc
            if 0 <= wr < h and 0 <= wc < w and grid[wr, wc] == 1:
                nr, nc = r + dr, c + dc
                if (nr, nc) in visited:
                    rgb[wr, wc] = COLOR_VISITED

    # Path overlay
    path_set = set(path)
    for r, c in path:
        rgb[2 * r + 1, 2 * c + 1] = COLOR_PATH
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            wr, wc = 2 * r + 1 + dr, 2 * c + 1 + dc
            if 0 <= wr < h and 0 <= wc < w and grid[wr, wc] == 1:
                nr, nc = r + dr, c + dc
                if (nr, nc) in path_set:
                    rgb[wr, wc] = COLOR_PATH

    # Start and end cells
    rgb[1, 1] = COLOR_START
    rgb[2 * rows - 1, 2 * cols - 1] = COLOR_END

    return rgb


def render_frame(grid, rows, cols, visited, path, title=""):
    """
    Renders a single maze frame as a matplotlib Figure.
    Call plt.close(fig) after st.pyplot(fig) to free memory.
    """
    rgb = _build_color_grid(grid, rows, cols, visited, path)

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.imshow(rgb, interpolation="nearest")
    ax.set_title(title, fontsize=13, fontweight="bold", color="#f0f0f0")
    ax.axis("off")

    fig.patch.set_facecolor("#0e1117")
    ax.set_facecolor("#0e1117")

    # Legend
    legend_elements = [
        mpatches.Patch(color=COLOR_START,   label="Start"),
        mpatches.Patch(color=COLOR_END,     label="End"),
        mpatches.Patch(color=COLOR_VISITED, label="Explored"),
        mpatches.Patch(color=COLOR_PATH,    label="Solution"),
    ]
    ax.legend(
        handles=legend_elements,
        loc="upper right",
        fontsize=7,
        framealpha=0.4,
        labelcolor="white",
        facecolor="#1e1e1e",
    )

    plt.tight_layout(pad=0.5)
    return fig


def render_comparison(grid, rows, cols, results):
    """
    Renders a 1x3 figure showing the final solved state of BFS, DFS, and A* side by side.
    results is a dict: {"BFS": SolveResult, "DFS": SolveResult, "A*": SolveResult}
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.patch.set_facecolor("#0e1117")

    for ax, (name, result) in zip(axes, results.items()):
        rgb = _build_color_grid(
            grid, rows, cols,
            visited=set(result.frames[-1]) if result.frames else set(),
            path=result.path,
        )
        ax.imshow(rgb, interpolation="nearest")
        ax.set_title(
            f"{name}\n{result.path_length} steps · {result.cells_visited} visited",
            fontsize=11, fontweight="bold", color="#f0f0f0"
        )
        ax.axis("off")
        ax.set_facecolor("#0e1117")

    plt.tight_layout(pad=1.0)
    return fig
