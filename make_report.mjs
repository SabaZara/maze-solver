import {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, PageNumber, ExternalHyperlink, LevelFormat, ImageRun
} from "docx";
import fs from "fs";

const NAVY   = "1A1A2E";
const DARK   = "2C3E50";
const GRAY   = "555555";
const WHITE  = "FFFFFF";
const LIGHT  = "EBF0F7";
const BORDER = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const BORDERS = { top: BORDER, bottom: BORDER, left: BORDER, right: BORDER };

// Page content width A4 with 2.5cm margins each side: 11906 - 2*1417 = 9072 DXA
const CONTENT_W = 9072;

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 280, after: 120 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: NAVY, space: 4 } },
    children: [new TextRun({ text, bold: true, size: 28, color: NAVY, font: "Arial" })]
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 200, after: 80 },
    children: [new TextRun({ text, bold: true, size: 24, color: DARK, font: "Arial" })]
  });
}

function body(text, opts = {}) {
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { before: 60, after: 60, line: 276 },
    children: [new TextRun({ text, size: 20, font: "Arial", color: "222222", ...opts })]
  });
}

function bullet(text) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { before: 40, after: 40, line: 260 },
    children: [new TextRun({ text, size: 20, font: "Arial", color: "222222" })]
  });
}

function numbered(text) {
  return new Paragraph({
    numbering: { reference: "numbers", level: 0 },
    spacing: { before: 40, after: 40, line: 260 },
    children: [new TextRun({ text, size: 20, font: "Arial", color: "222222" })]
  });
}

function sp(n = 1) {
  return new Paragraph({ children: [new TextRun({ text: "", size: n * 12 })] });
}

function img(path, w, h, caption) {
  return [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 120, after: 60 },
      children: [new ImageRun({
        type: "png",
        data: fs.readFileSync(path),
        transformation: { width: w, height: h },
        altText: { title: caption, description: caption, name: caption }
      })]
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 0, after: 120 },
      children: [new TextRun({ text: caption, size: 16, font: "Arial", color: GRAY, italics: true })]
    })
  ];
}

function link(label, url) {
  return new ExternalHyperlink({
    link: url,
    children: [new TextRun({ text: label, size: 20, font: "Arial", color: "1155CC", underline: {} })]
  });
}

function cell(text, w, bold = false, bg = null, center = false) {
  return new TableCell({
    borders: BORDERS,
    width: { size: w, type: WidthType.DXA },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    shading: bg ? { fill: bg, type: ShadingType.CLEAR } : undefined,
    verticalAlign: "center",
    children: [new Paragraph({
      alignment: center ? AlignmentType.CENTER : AlignmentType.LEFT,
      children: [new TextRun({ text, size: 18, font: "Arial", bold, color: bold && bg === NAVY ? WHITE : "222222" })]
    })]
  });
}

// Perfect maze table (loop=0)
const tableDataPerfect = [
  ["Algorithm", "Path Length", "Cells Visited", "Efficiency (%)", "Overhead", "Time (ms)"],
  ["BFS",  "79", "109", "72.5", "1.38", "0.169"],
  ["DFS",  "79", "83",  "95.2", "1.05", "0.111"],
  ["A*",   "79", "95",  "83.2", "1.20", "0.196"],
];

// Imperfect maze table (loop=0.3)
const tableDataImperfect = [
  ["Algorithm", "Path Length", "Cells Visited", "Efficiency (%)", "Overhead", "Time (ms)"],
  ["BFS",  "31", "225", "13.8", "7.26", "1.125"],
  ["DFS",  "51", "187", "27.3", "3.67", "0.335"],
  ["A*",   "31", "167", "18.6", "5.39", "0.381"],
];
const colW = [1400, 1300, 1500, 1500, 1200, 1172]; // sums to 8072 (slightly narrower than content)

function makeTable(data) {
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: colW,
    rows: data.map((row, i) =>
      new TableRow({
        tableHeader: i === 0,
        children: row.map((text, j) =>
          cell(text, colW[j], i === 0, i === 0 ? NAVY : (i % 2 === 0 ? LIGHT : null), i > 0)
        )
      })
    )
  });
}

const resultsTablePerfect   = makeTable(tableDataPerfect);
const resultsTableImperfect = makeTable(tableDataImperfect);

const doc = new Document({
  numbering: {
    config: [
      { reference: "bullets",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 600, hanging: 300 } } } }] },
      { reference: "numbers",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 600, hanging: 300 } } } }] },
    ]
  },
  styles: {
    default: {
      document: { run: { font: "Arial", size: 20, color: "222222" } }
    },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: NAVY },
        paragraph: { spacing: { before: 280, after: 120 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "Arial", color: DARK },
        paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 1 } },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1417, right: 1417, bottom: 1417, left: 1417 }
      }
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: NAVY, space: 4 } },
          children: [new TextRun({ text: "Maze Generator & Solver — Principles of Programming", size: 16, font: "Arial", color: GRAY, italics: true })]
        })]
      })
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          border: { top: { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC", space: 4 } },
          children: [
            new TextRun({ text: "Page ", size: 16, font: "Arial", color: GRAY }),
            new TextRun({ children: [PageNumber.CURRENT], size: 16, font: "Arial", color: GRAY }),
            new TextRun({ text: " | SabaZara | April 2026", size: 16, font: "Arial", color: GRAY }),
          ]
        })]
      })
    },
    children: [

      // ── TITLE PAGE ──────────────────────────────────────────────────────────
      sp(8),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 80 },
        children: [new TextRun({ text: "Maze Generator & Solver", size: 52, bold: true, font: "Arial", color: NAVY })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 200 },
        children: [new TextRun({ text: "Visualising BFS, DFS, and A* Search Algorithms", size: 28, font: "Arial", color: DARK, italics: true })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        border: { top: { style: BorderStyle.SINGLE, size: 12, color: NAVY, space: 8 }, bottom: { style: BorderStyle.SINGLE, size: 4, color: NAVY, space: 8 } },
        spacing: { before: 80, after: 80 },
        children: [new TextRun({ text: "", size: 4 })]
      }),
      sp(2),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Author: SabaZara", size: 22, font: "Arial", color: GRAY })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Course: Principles of Programming", size: 22, font: "Arial", color: GRAY })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Date: April 2026", size: 22, font: "Arial", color: GRAY })] }),
      sp(2),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [
          new TextRun({ text: "Live app: ", size: 20, font: "Arial", color: GRAY }),
          link("mazesolverprogrmaingproject.streamlit.app", "https://mazesolverprogrmaingproject.streamlit.app/"),
        ]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [
          new TextRun({ text: "GitHub: ", size: 20, font: "Arial", color: GRAY }),
          link("github.com/SabaZara/maze-solver", "https://github.com/SabaZara/maze-solver"),
        ]
      }),

      // ── SECTION 1 ───────────────────────────────────────────────────────────
      new Paragraph({ pageBreakBefore: true, children: [new TextRun("")] }),
      h1("1. Introduction and Background"),
      body("Pathfinding and maze solving are foundational problems in computer science with real-world applications in robotics navigation, game AI, and network routing. This project implements an interactive maze generator and solver that compares three classical graph search algorithms: Breadth-First Search (BFS), Depth-First Search (DFS), and A* (A-star)."),
      sp(),
      body("The motivation behind this project is to make abstract algorithmic behaviour tangible and visual. Rather than simply stating that \u201CBFS guarantees the shortest path,\u201D a user can watch BFS and A* explore the same maze simultaneously and observe the difference in how they navigate \u2014 BFS expanding outward in uniform concentric rings, A* steering purposefully toward the goal. This visual contrast makes the theoretical differences immediately intuitive."),
      sp(),
      body("The maze is generated programmatically using a recursive backtracking algorithm, ensuring every maze produced is a perfect maze: fully connected, with exactly one path between any two cells. This controlled structure guarantees fair and reproducible comparisons between algorithms."),
      sp(),
      new Paragraph({
        alignment: AlignmentType.JUSTIFIED,
        spacing: { before: 60, after: 60 },
        children: [
          new TextRun({ text: "The interactive dashboard is deployed at: ", size: 20, font: "Arial", color: "222222" }),
          link("mazesolverprogrmaingproject.streamlit.app", "https://mazesolverprogrmaingproject.streamlit.app/"),
          new TextRun({ text: "   \u2022   Source code: ", size: 20, font: "Arial", color: "222222" }),
          link("github.com/SabaZara/maze-solver", "https://github.com/SabaZara/maze-solver"),
        ]
      }),

      // ── SECTION 2 ───────────────────────────────────────────────────────────
      sp(),
      h1("2. Approach and Methodology"),

      h2("2.1 Maze Representation"),
      body("The maze is stored as a binary NumPy array of shape (2\u00d7rows+1, 2\u00d7cols+1). In this encoding:"),
      bullet("0 = wall pixel (black); 1 = passage pixel (white)"),
      bullet("Each logical maze cell (r, c) maps to grid pixel (2r+1, 2c+1)"),
      bullet("The wall between adjacent cells sits at the pixel halfway between them"),
      body("This compact representation allows direct rendering via matplotlib\u2019s imshow without custom drawing logic. Checking whether two cells are connected is a single array index lookup."),

      sp(),
      h2("2.2 Maze Generation: Recursive Backtracking"),
      body("The generator uses iterative DFS with an explicit stack (avoiding Python\u2019s recursion limit on large mazes):"),
      numbered("Start at cell (0,0), mark visited, push onto stack"),
      numbered("While stack is non-empty: find all unvisited neighbours of the current cell"),
      numbered("If neighbours exist: pick one at random, carve the wall between them, push neighbour"),
      numbered("If no neighbours: pop (backtrack)"),
      body("This produces a spanning tree of the cell graph \u2014 a perfect maze with no loops and exactly one solution path between any two cells."),

      sp(),
      h2("2.3 Solving Algorithms"),
      body("All three solvers work on maze-cell coordinates and check connectivity via the binary grid. Each records animation \u201Cframes\u201D \u2014 snapshots of visited cells at regular intervals \u2014 for step-by-step playback."),
      bullet("BFS (Breadth-First Search): Uses a deque. Explores all cells at distance d before d+1. Guaranteed shortest path."),
      bullet("DFS (Depth-First Search): Uses a stack. Dives deep before backtracking. Finds a path quickly but without a shortest-path guarantee."),
      bullet("A* (A-star): Uses a min-heap ordered by f = g + h, where g is cost from start and h is Manhattan distance to goal. Finds the shortest path while typically visiting fewer cells than BFS."),

      sp(),
      h2("2.4 Imperfect Mazes: The Loop Factor"),
      body("A perfect maze has exactly one path between any two cells, so all three algorithms always find the same path length. To make algorithmic differences meaningful, the generator supports a loop_factor parameter (0.0 to 0.5). After the perfect maze is generated, a random fraction of remaining internal walls are removed, creating cycles and multiple alternative routes."),
      body("With loops present, BFS and A* always find the true shortest path, while DFS \u2014 which commits to a branch and cannot globally backtrack \u2014 often finds a longer winding route. This is the key experimental result of the project."),

      h2("2.5 Key Design Choices"),
      bullet("Frame snapshots are pre-computed before rendering, then replayed via st.empty() \u2014 each iteration replaces the previous figure in place for smooth animation without full page rerenders."),
      bullet("A configurable frame interval caps animation at ~200 frames regardless of maze size, keeping playback fluid on any device."),
      bullet("st.session_state persists the generated maze and solver results across Streamlit rerenders so controls remain interactive without re-solving."),
      bullet("The loop_factor slider in the sidebar lets users switch between perfect and imperfect mazes interactively, observing in real time how algorithm behaviour changes."),

      // ── SECTION 3 ───────────────────────────────────────────────────────────
      sp(),
      h1("3. Programming Tools and Methods"),

      h2("Python Standard Library"),
      bullet("collections.deque: O(1) enqueue/dequeue for BFS \u2014 critical for performance on large mazes"),
      bullet("heapq: Binary min-heap for A* priority queue; O(log n) push and pop"),

      h2("NumPy"),
      body("Binary grid storage with O(1) wall lookup via direct array indexing. The full RGB colour overlay for rendering is computed in a single vectorised pass over the grid array, avoiding Python loops over pixels."),

      h2("Matplotlib"),
      body("Renders each maze frame using imshow on an RGB NumPy array. Colour overlays are applied by direct pixel assignment: visited cells in blue, solution path in gold, start in green, end in red. plt.close(fig) is called immediately after each st.pyplot() call to prevent memory accumulation during long animations."),

      h2("Streamlit"),
      bullet("st.session_state \u2014 maze and solver results persistence across rerenders"),
      bullet("st.empty() \u2014 single placeholder slot for in-place figure replacement (animation)"),
      bullet("st.columns() \u2014 three-column side-by-side layout for simultaneous algorithm comparison"),
      bullet("st.tabs() \u2014 separates Visualisation and Statistics views"),
      bullet("st.slider(), st.radio(), st.button() \u2014 sidebar controls for maze size, speed, algorithm selection"),

      h2("pandas"),
      body("Builds the comparison DataFrame in the Statistics tab and computes five derived metrics: efficiency (%), search overhead, wasted exploration (cells), maze coverage (%), and solve time (ms)."),

      h2("Project Structure"),
      bullet("maze_generator.py \u2014 iterative DFS maze generation"),
      bullet("maze_solver.py \u2014 BFS, DFS, A* algorithms with frame recording"),
      bullet("maze_renderer.py \u2014 matplotlib RGB figure builder and colour overlays"),
      bullet("app.py \u2014 Streamlit UI, animation loop, statistics tab"),

      // ── SECTION 4 ───────────────────────────────────────────────────────────
      sp(),
      h1("4. Results"),

      h2("4.1 Correctness"),
      body("On all tested maze sizes (5\u00d75 to 40\u00d740), BFS and A* consistently returned the same path length, confirming both find the optimal (shortest) solution. On perfect mazes, DFS also finds the same length since only one path exists. On imperfect mazes (with loops), DFS path length diverges significantly \u2014 matching the expected theoretical behaviour."),

      sp(),
      h2("4.2 Perfect Maze Results \u2014 15\u00d715, Loop Factor = 0"),
      body("With loop factor 0, only one path exists. All algorithms find the same path length; differences are only in exploration efficiency:"),
      sp(),
      resultsTablePerfect,
      sp(),
      body("Metrics: Efficiency (%) = path length \u00f7 cells visited \u00d7 100 (higher = better). Overhead = cells visited \u00f7 path length (lower = better, 1.0 = perfect)."),
      sp(),
      ...img("screenshot_sidebyside.png", 480, 160, "Figure 1. Perfect maze (loop=0): all three algorithms find the same path (gold). Blue = explored cells."),
      sp(),
      body("Key observations:"),
      bullet("All three find path length 79 \u2014 on a perfect maze only one solution exists."),
      bullet("DFS achieved 95.2% efficiency \u2014 it happened to explore almost only cells on the final path."),
      bullet("A* visited fewer cells than BFS (95 vs 109) thanks to the Manhattan heuristic."),

      sp(),
      h2("4.3 Imperfect Maze Results \u2014 15\u00d715, Loop Factor = 0.3"),
      body("With loop factor 0.3, approximately 30% of remaining internal walls are removed after generation, creating loops and multiple alternative paths. Now the algorithms genuinely diverge:"),
      sp(),
      resultsTableImperfect,
      sp(),
      ...img("screenshot_imperfect_sidebyside.png", 480, 160, "Figure 2. Imperfect maze (loop=0.3): BFS and A* find the short optimal path (31 steps); DFS finds a longer winding route (51 steps)."),
      ...img("screenshot_perfect_vs_imperfect.png", 480, 175, "Figure 3. Perfect vs imperfect maze comparison. Path length (left) and cells visited (right). On the imperfect maze DFS path length is 65% longer than BFS/A*."),
      sp(),
      body("Key observations:"),
      bullet("BFS and A* both find the optimal path (31 steps) \u2014 confirmed correct on mazes with loops."),
      bullet("DFS finds a path 65% longer (51 steps) \u2014 it cannot backtrack to find shortcuts once it commits to a branch."),
      bullet("A* visits the fewest cells (167) despite finding the optimal path \u2014 the heuristic focuses exploration toward the goal."),
      bullet("BFS visits all 225 cells before finding the goal \u2014 it exhaustively explores all directions."),
      bullet("This result proves that BFS and A* are optimal algorithms; DFS is not, which is the core theoretical claim of the project."),

      sp(),
      h2("4.4 Visual Dashboard"),
      body("The live dashboard at mazesolverprogrmaingproject.streamlit.app provides:"),
      bullet("Loop Factor slider \u2014 switch between perfect and imperfect mazes to observe algorithm divergence in real time"),
      bullet("Side-by-side animated view: all three algorithms animate simultaneously, making path length differences immediately visible"),
      bullet("Individual animated view: step-by-step playback with configurable speed"),
      bullet("Statistics tab: five-metric comparison table with winner callouts and bar charts"),
      bullet("Adjustable maze size (5\u00d75 to 40\u00d740) via sidebar sliders"),

      // ── REFERENCES ──────────────────────────────────────────────────────────
      new Paragraph({ pageBreakBefore: true, children: [new TextRun("")] }),
      h1("References"),
      body("Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009). Introduction to Algorithms (3rd ed.). MIT Press."),
      sp(),
      body("Hart, P. E., Nilsson, N. J., & Raphael, B. (1968). A formal basis for the heuristic determination of minimum cost paths. IEEE Transactions on Systems Science and Cybernetics, 4(2), 100\u2013107."),
      sp(),
      new Paragraph({
        children: [
          new TextRun({ text: "Streamlit documentation. ", size: 20, font: "Arial" }),
          link("https://docs.streamlit.io", "https://docs.streamlit.io"),
        ]
      }),
      sp(),
      new Paragraph({
        children: [
          new TextRun({ text: "NumPy documentation. ", size: 20, font: "Arial" }),
          link("https://numpy.org/doc", "https://numpy.org/doc"),
        ]
      }),
      sp(),
      new Paragraph({
        children: [
          new TextRun({ text: "GitHub repository. ", size: 20, font: "Arial" }),
          link("https://github.com/SabaZara/maze-solver", "https://github.com/SabaZara/maze-solver"),
        ]
      }),
      sp(),
      new Paragraph({
        children: [
          new TextRun({ text: "Live application. ", size: 20, font: "Arial" }),
          link("https://mazesolverprogrmaingproject.streamlit.app/", "https://mazesolverprogrmaingproject.streamlit.app/"),
        ]
      }),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("/Users/sabazarandia/Desktop/progrmaingfinalproject/report.docx", buf);
  console.log("report.docx created successfully");
});
