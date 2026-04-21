"""
app.py
------
Streamlit UI for the Maze Generator & Solver.

Run with:
    streamlit run app.py

Features:
  - Generate random mazes of any size using recursive backtracking DFS
  - Solve with BFS, DFS, and A* — shown side by side or animated step-by-step
  - Statistics tab comparing the three algorithms
"""

import time
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from maze_generator import generate_maze
from maze_solver import solve_bfs, solve_dfs, solve_astar
from maze_renderer import render_frame, render_comparison


# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Maze Solver",
    page_icon="🧩",
    layout="wide",
)

st.title("🧩 Maze Generator & Solver")
st.markdown("Generate a random maze and watch **BFS**, **DFS**, and **A\*** solve it.")
st.divider()


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("⚙️ Controls")

    rows = st.slider("Rows", 5, 40, 15)
    cols = st.slider("Columns", 5, 40, 15)

    st.divider()

    view_mode = st.radio(
        "View Mode",
        ["Side by Side", "Animate: BFS", "Animate: DFS", "Animate: A*"],
        help="Side by Side shows all three algorithms at once. Animate shows a chosen algorithm step by step."
    )

    anim_speed = st.slider(
        "Animation Speed",
        min_value=1, max_value=10, value=5,
        help="Higher = faster animation"
    )
    sleep_time = max(0.01, 0.15 - anim_speed * 0.013)

    st.divider()

    gen_btn   = st.button("🔀 Generate New Maze", use_container_width=True)
    solve_btn = st.button("▶️ Solve Maze",         use_container_width=True, type="primary")


# ─── SESSION STATE INIT ──────────────────────────────────────────────────────

if "grid" not in st.session_state or gen_btn:
    st.session_state.grid    = generate_maze(rows, cols)
    st.session_state.rows    = rows
    st.session_state.cols    = cols
    st.session_state.results = None  # clear previous solutions

grid = st.session_state.grid
s_rows = st.session_state.rows
s_cols = st.session_state.cols


# ─── SOLVE ───────────────────────────────────────────────────────────────────

if solve_btn:
    with st.spinner("Solving with all three algorithms..."):
        st.session_state.results = {
            "BFS": solve_bfs(grid, s_rows, s_cols),
            "DFS": solve_dfs(grid, s_rows, s_cols),
            "A*":  solve_astar(grid, s_rows, s_cols),
        }


# ─── TABS ────────────────────────────────────────────────────────────────────

tab_viz, tab_stats = st.tabs(["Visualization", "Statistics"])


# ── Visualization tab ────────────────────────────────────────────────────────

with tab_viz:

    results = st.session_state.get("results")

    if results is None:
        # Show the unsolved maze
        fig = render_frame(grid, s_rows, s_cols, visited=set(), path=[], title="Generated Maze")
        st.pyplot(fig)
        plt.close(fig)
        st.info("Click **Solve Maze** in the sidebar to run the algorithms.")

    elif view_mode == "Side by Side":
        # Animate all three algorithms simultaneously, frame by frame
        max_frames = max(len(r.frames) for r in results.values())
        col1, col2, col3 = st.columns(3)
        placeholders = {
            "BFS": col1.empty(),
            "DFS": col2.empty(),
            "A*":  col3.empty(),
        }

        for i in range(max_frames):
            for algo, ph in placeholders.items():
                result = results[algo]
                # Use the last available frame once an algorithm finishes
                frame_idx = min(i, len(result.frames) - 1)
                frame = result.frames[frame_idx]
                # Show path only on the final frame
                show_path = (frame_idx == len(result.frames) - 1)
                fig = render_frame(
                    grid, s_rows, s_cols,
                    visited=set(frame),
                    path=result.path if show_path else [],
                    title=f"{algo}" + (" ✓" if show_path else f" — frame {i+1}")
                )
                with ph:
                    st.pyplot(fig)
                plt.close(fig)
            time.sleep(sleep_time)

    else:
        # Animated mode — map radio label to algorithm key
        algo_map = {"Animate: BFS": "BFS", "Animate: DFS": "DFS", "Animate: A*": "A*"}
        algo = algo_map[view_mode]
        result = results[algo]

        placeholder = st.empty()

        # Play through exploration frames
        for i, frame in enumerate(result.frames):
            fig = render_frame(
                grid, s_rows, s_cols,
                visited=set(frame),
                path=[],
                title=f"{algo} — Exploring... (frame {i+1}/{len(result.frames)})"
            )
            with placeholder:
                st.pyplot(fig)
            plt.close(fig)
            time.sleep(sleep_time)

        # Final frame: show solution path
        fig = render_frame(
            grid, s_rows, s_cols,
            visited=set(result.frames[-1]),
            path=result.path,
            title=f"{algo} — Solved! Path length: {result.path_length}"
        )
        with placeholder:
            st.pyplot(fig)
        plt.close(fig)


# ── Statistics tab ───────────────────────────────────────────────────────────

with tab_stats:

    results = st.session_state.get("results")

    if results is None:
        st.info("Solve the maze first to see statistics.")
    else:
        total_cells = s_rows * s_cols

        # Build enriched stats table
        rows_data = []
        for name, r in results.items():
            wasted = r.cells_visited - r.path_length  # cells explored but not on path
            efficiency = round(r.path_length / r.cells_visited * 100, 1) if r.cells_visited else 0
            overhead   = round(r.cells_visited / r.path_length, 2) if r.path_length else 0
            coverage   = round(r.cells_visited / total_cells * 100, 1)
            rows_data.append({
                "Algorithm":             name,
                "Path Length":           r.path_length,
                "Cells Visited":         r.cells_visited,
                "Wasted Exploration":    wasted,
                "Efficiency (%)":        efficiency,   # path / visited × 100
                "Search Overhead":       overhead,     # visited / path  (1.0 = perfect)
                "Maze Coverage (%)":     coverage,     # % of maze cells touched
                "Solve Time (ms)":       r.solve_time_ms,
            })

        df = pd.DataFrame(rows_data)

        # ── Headline metrics ──────────────────────────────────────────────────
        st.subheader("Algorithm Comparison")
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()

        # ── Winner callouts ───────────────────────────────────────────────────
        best_eff   = df.loc[df["Efficiency (%)"].idxmax(), "Algorithm"]
        best_time  = df.loc[df["Solve Time (ms)"].idxmin(), "Algorithm"]
        best_waste = df.loc[df["Wasted Exploration"].idxmin(), "Algorithm"]

        w1, w2, w3 = st.columns(3)
        w1.success(f"Most efficient path: **{best_eff}**")
        w2.success(f"Fastest runtime: **{best_time}**")
        w3.success(f"Least wasted exploration: **{best_waste}**")

        st.divider()

        # ── Charts ────────────────────────────────────────────────────────────
        c1, c2 = st.columns(2)

        with c1:
            st.subheader("Efficiency (%) — higher is better")
            st.caption("Path length ÷ cells visited × 100. 100% = explored nothing wasted.")
            st.bar_chart(df.set_index("Algorithm")["Efficiency (%)"])

        with c2:
            st.subheader("Search Overhead — lower is better")
            st.caption("Cells visited ÷ path length. 1.0 = perfect (only visited cells on the solution).")
            st.bar_chart(df.set_index("Algorithm")["Search Overhead"])

        st.divider()
        c3, c4 = st.columns(2)

        with c3:
            st.subheader("Wasted Exploration — lower is better")
            st.caption("Cells visited that are NOT on the final path.")
            st.bar_chart(df.set_index("Algorithm")["Wasted Exploration"])

        with c4:
            st.subheader("Maze Coverage (%) — lower = more focused")
            st.caption("What percentage of the entire maze was touched.")
            st.bar_chart(df.set_index("Algorithm")["Maze Coverage (%)"])

        st.divider()
        st.subheader("Solve Time (ms)")
        st.bar_chart(df.set_index("Algorithm")["Solve Time (ms)"])

        st.divider()
        st.markdown(f"""
        **Note — why all path lengths are equal here:**
        This is a *perfect maze* (single unique path between any two cells), so every
        algorithm finds the same one path. The differences that matter are **efficiency**:
        how much of the maze each algorithm had to explore before finding it.

        **BFS** explores all cells at distance *d* before moving to *d+1* — systematic but
        visits many cells it doesn't need. Total cells in this maze: **{total_cells}**.

        **DFS** dives straight down one branch — often stumbles onto the goal quickly with
        less wasted exploration, but gives no guarantees on non-perfect mazes.

        **A\\*** uses Manhattan distance to bias toward the goal — in open mazes it skips
        dead-end branches early, making it the most focused searcher.
        """)
