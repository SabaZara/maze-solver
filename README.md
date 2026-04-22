# Maze Generator & Solver

Generates random mazes and solves them using three different algorithms — animated step by step, with side-by-side comparison.

## How it works

Mazes are generated using **recursive backtracking** (iterative DFS). The maze is stored as a binary grid where `0` = wall and `1` = passage.

Three solving algorithms are implemented and compared:

| Algorithm | Guarantees shortest path? | Strategy |
|---|---|---|
| BFS | Yes | Explores level by level (closest cells first) |
| DFS | No | Dives deep before backtracking |
| A* | Yes | BFS guided by Manhattan distance heuristic |

## Perfect vs Imperfect Mazes

A key feature of this project is the **Loop Factor** slider.

- **Loop Factor = 0 (Perfect maze):** Only one path exists between any two cells. All three algorithms find the same path length — the difference is only in *how much they explored*.
- **Loop Factor > 0 (Imperfect maze):** Extra walls are randomly removed after generation, creating loops and shortcuts. Now BFS and A\* find the **true shortest path**, while DFS finds *a* path that is often much longer.

This makes the algorithmic differences concrete and visually dramatic. For example, on a 15×15 maze with loop factor 0.3:

| Algorithm | Path Length | Cells Visited |
|---|---|---|
| BFS | 31 | 225 |
| DFS | **51** | 187 |
| A* | 31 | **167** |

BFS and A\* both find the optimal path (31 steps). DFS finds a path 65% longer (51 steps). A\* visits the fewest cells thanks to its heuristic.

## Project Structure

```
progrmaingfinalproject/
├── app.py              # Streamlit UI (main entry point)
├── maze_generator.py   # Maze generation via recursive backtracking + loop factor
├── maze_solver.py      # BFS, DFS, A* algorithms with frame-by-frame animation data
├── maze_renderer.py    # matplotlib figure builder and colour overlays
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the app

```bash
streamlit run app.py
```

## How to use

1. Adjust **Rows** and **Columns** in the sidebar to set maze size
2. Set **Loop Factor** to 0 for a perfect maze, or increase it (e.g. 0.3) to create loops
3. Click **Generate New Maze**
4. Click **Solve Maze** to run all three algorithms
5. Choose **Side by Side** to watch all three animate simultaneously
6. Choose **Animate: BFS/DFS/A\*** to watch step-by-step
7. Switch to the **Statistics** tab to compare path length, efficiency, overhead, and solve time

## Dependencies

| Library | Purpose |
|---|---|
| streamlit | Web dashboard UI |
| matplotlib | Maze rendering and visualisation |
| numpy | Binary grid representation |
| pandas | Statistics table |

## Links

- **Live app:** https://mazesolverprogrmaingproject.streamlit.app/
- **GitHub:** https://github.com/SabaZara/maze-solver
