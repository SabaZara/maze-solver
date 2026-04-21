# Maze Generator & Solver

Generates random mazes and solves them using three different algorithms — animated step by step.

## How it works

Mazes are generated using **recursive backtracking** (iterative DFS). The maze is stored as a binary grid where `0` = wall and `1` = passage.

Three solving algorithms are implemented and compared:

| Algorithm | Guarantees shortest path? | Strategy |
|---|---|---|
| BFS | Yes | Explores level by level (closest cells first) |
| DFS | No | Dives deep before backtracking |
| A* | Yes | BFS guided by Manhattan distance heuristic |

## Project Structure

```
progrmaingfinalproject/
├── app.py              # Streamlit UI (main entry point)
├── maze_generator.py   # Maze generation via recursive backtracking DFS
├── maze_solver.py      # BFS, DFS, A* algorithms with frame-by-frame animation data
├── maze_renderer.py    # matplotlib figure builder and color overlays
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
2. Click **Generate New Maze** to create a fresh random maze
3. Click **Solve Maze** to run all three algorithms
4. Choose **Side by Side** to compare all three at once
5. Choose **Animate: BFS/DFS/A\*** to watch the algorithm explore step by step
6. Switch to the **Statistics** tab to compare path length, cells visited, and solve time

## Dependencies

| Library | Purpose |
|---|---|
| streamlit | Web dashboard UI |
| matplotlib | Maze rendering and visualization |
| numpy | Binary grid representation |
| pandas | Statistics table |
