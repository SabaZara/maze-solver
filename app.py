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

    loop_factor = st.slider(
        "Loop Factor",
        min_value=0.0, max_value=0.5, value=0.0, step=0.05,
        help="0 = perfect maze (one unique path — algorithms find same length). "
             "Higher = more walls removed, creating shortcuts and loops. "
             "This makes BFS/A* and DFS find DIFFERENT path lengths."
    )

    if loop_factor == 0.0:
        st.caption("🔒 Perfect maze — all algorithms find the same path length.")
    else:
        st.caption(f"🔀 Imperfect maze — {int(loop_factor*100)}% of walls removed. Algorithms will diverge!")

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
    st.session_state.grid        = generate_maze(rows, cols, loop_factor)
    st.session_state.rows        = rows
    st.session_state.cols        = cols
    st.session_state.loop_factor = loop_factor
    st.session_state.results     = None  # clear previous solutions

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
        min_path   = df["Path Length"].min()
        # Shortest path winner: among algorithms that found the OPTIMAL path only
        optimal_df = df[df["Path Length"] == min_path]
        # Among optimal ones, who visited fewest cells?
        best_search = optimal_df.loc[optimal_df["Cells Visited"].idxmin(), "Algorithm"]
        best_time   = df.loc[df["Solve Time (ms)"].idxmin(), "Algorithm"]
        best_path   = optimal_df["Algorithm"].tolist()

        w1, w2, w3 = st.columns(3)
        if len(best_path) == len(df):
            w1.info(f"All found same path length: **{min_path}** steps")
        else:
            non_optimal = df[df["Path Length"] > min_path]["Algorithm"].tolist()
            w1.success(f"Shortest path: **{', '.join(best_path)}** ({min_path} steps)")
            w1.error(f"Suboptimal: **{', '.join(non_optimal)}** ({df[df['Path Length']>min_path]['Path Length'].values[0]} steps)")
        w2.success(f"Fewest cells visited (among optimal): **{best_search}**")
        w3.success(f"Fastest runtime: **{best_time}**")

        st.divider()

        # ── Charts ────────────────────────────────────────────────────────────
        c1, c2 = st.columns(2)

        with c1:
            st.subheader("Cells Visited — lower is better")
            st.caption("How many cells each algorithm explored. Lower = more focused search. Note: DFS may visit fewer cells but find a longer path.")
            st.bar_chart(df.set_index("Algorithm")["Cells Visited"])

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
        lf = st.session_state.get("loop_factor", 0.0)
        if lf == 0.0:
            st.info(
                f"**Perfect maze** (Loop Factor = 0) — only one path exists between any two cells, "
                f"so all algorithms find the same path length. "
                f"Increase the **Loop Factor** slider to remove walls and create shortcuts: "
                f"BFS and A\\* will find shorter paths than DFS. Total cells: **{total_cells}**."
            )
        else:
            path_lengths = {name: r.path_length for name, r in results.items()}
            if len(set(path_lengths.values())) == 1:
                st.info(
                    f"**Imperfect maze** (Loop Factor = {lf}) — loops exist but all algorithms "
                    f"found the same path length this time. Try regenerating or increasing the loop factor further."
                )
            else:
                best = min(path_lengths, key=path_lengths.get)
                worst = max(path_lengths, key=path_lengths.get)
                st.success(
                    f"**Imperfect maze** (Loop Factor = {lf}) — algorithms found **different** path lengths! "
                    f"**{best}** found the shortest ({path_lengths[best]} steps), "
                    f"**{worst}** found the longest ({path_lengths[worst]} steps). "
                    f"This proves BFS and A\\* are optimal; DFS is not."
                )
        st.markdown(f"""
        **BFS** — explores all cells at distance *d* before *d+1*. Always finds the shortest path.

        **DFS** — dives deep before backtracking. Fast but takes long winding routes when loops exist.

        **A\\*** — uses Manhattan distance heuristic to steer toward the goal. Shortest path with less exploration than BFS.
        """)
