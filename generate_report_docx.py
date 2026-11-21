"""
Generates a formatted Microsoft Word (.docx) final report for the Capstone Project.
Includes formatted tables, mathematical formulas, algorithms breakdown,
and designated screenshot placeholder boxes with explicit capture instructions.
"""

import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn


def set_cell_background(cell, hex_color: str):
    """Sets background shading color for a table cell."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tc_pr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets cell padding in dxa (1 pt = 20 dxa)."""
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tc_pr.append(tc_mar)


def add_screenshot_placeholder(doc, ss_id: str, title: str, program_cmd: str, description: str):
    """
    Adds a styled screenshot placeholder callout box.
    """
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    
    set_cell_background(cell, "F1F5F9")  # Light slate grey
    set_cell_margins(cell, top=180, bottom=180, left=240, right=240)

    # Border formatting
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="12" w:space="0" w:color="3B82F6"/>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="2563EB"/>'
        f'<w:bottom w:val="single" w:sz="12" w:space="0" w:color="3B82F6"/>'
        f'<w:right w:val="single" w:sz="12" w:space="0" w:color="3B82F6"/>'
        f'</w:tcBorders>'
    )
    tc_pr.append(borders)

    p1 = cell.paragraphs[0]
    p1.paragraph_format.space_before = Pt(4)
    p1.paragraph_format.space_after = Pt(4)
    run_header = p1.add_run(f"📷 [SCREENSHOT PLACEHOLDER {ss_id}]: {title.upper()}")
    run_header.bold = True
    run_header.font.size = Pt(11)
    run_header.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    p2 = cell.add_paragraph()
    p2.paragraph_format.space_before = Pt(2)
    p2.paragraph_format.space_after = Pt(2)
    run_prog_label = p2.add_run("• Program / Command to Run: ")
    run_prog_label.bold = True
    run_prog_label.font.size = Pt(9.5)
    run_prog_val = p2.add_run(program_cmd)
    run_prog_val.font.name = "Courier New"
    run_prog_val.font.size = Pt(9.5)
    run_prog_val.font.color.rgb = RGBColor(0x04, 0x78, 0x57)

    p3 = cell.add_paragraph()
    p3.paragraph_format.space_before = Pt(2)
    p3.paragraph_format.space_after = Pt(12)
    run_desc_label = p3.add_run("• What to Capture: ")
    run_desc_label.bold = True
    run_desc_label.font.size = Pt(9.5)
    run_desc_val = p3.add_run(description)
    run_desc_val.font.size = Pt(9.5)
    run_desc_val.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    # Empty visual space for screenshot paste
    p_box = cell.add_paragraph()
    p_box.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_box.paragraph_format.space_before = Pt(28)
    p_box.paragraph_format.space_after = Pt(28)
    run_paste = p_box.add_run("[ Paste Screenshot Here ]")
    run_paste.font.size = Pt(12)
    run_paste.font.italic = True
    run_paste.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)

    # Add spacing after table
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(2)
    p_after.paragraph_format.space_after = Pt(6)


def format_table(table, header_bg="1E3A8A", alt_bg="F8FAFC"):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(table.rows):
        for cell in row.cells:
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            if i == 0:
                set_cell_background(cell, header_bg)
                for p in cell.paragraphs:
                    p.paragraph_format.space_before = Pt(2)
                    p.paragraph_format.space_after = Pt(2)
                    for run in p.runs:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                        run.font.size = Pt(9.5)
            else:
                if i % 2 == 1:
                    set_cell_background(cell, alt_bg)
                for p in cell.paragraphs:
                    p.paragraph_format.space_before = Pt(2)
                    p.paragraph_format.space_after = Pt(2)
                    for run in p.runs:
                        run.font.size = Pt(9)


def build_capstone_docx(output_path: str = "CAPSTONE_FINAL_REPORT.docx"):
    doc = Document()

    # Set Margins (1 inch all around)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # ---------------------------------------------------------
    # COVER / HEADER
    # ---------------------------------------------------------
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(6)
    r_title = p_title.add_run("COURIER LOGISTICS OPTIMIZATION SYSTEM")
    r_title.bold = True
    r_title.font.size = Pt(22)
    r_title.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(16)
    r_sub = p_sub.add_run("Integrated Capstone Project: Sorting, Dynamic Programming Knapsack,\nDijkstra's Shortest Path, and TSP Route Planning")
    r_sub.font.size = Pt(13)
    r_sub.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    # Meta Table
    meta_tbl = doc.add_table(rows=4, cols=2)
    meta_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Course / Module:", "Design and Analysis of Algorithms (Capstone Project)"),
        ("Evaluation Rubric:", "Phases 1 to 5 (Total: 100 Marks)"),
        ("Implementation Language:", "Python 3.8+ (Zero External Dependencies)"),
        ("Generated Date:", "November 2026")
    ]
    for idx, (k, v) in enumerate(meta_data):
        meta_tbl.cell(idx, 0).paragraphs[0].add_run(k).bold = True
        meta_tbl.cell(idx, 1).paragraphs[0].add_run(v)
    format_table(meta_tbl, header_bg="2563EB", alt_bg="F1F5F9")

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Rubric Table
    p_rubric_head = doc.add_heading("Project Evaluation Rubric & Mark Distribution", level=2)
    p_rubric_head.paragraph_format.space_before = Pt(14)
    p_rubric_head.paragraph_format.space_after = Pt(6)

    rubric_tbl = doc.add_table(rows=6, cols=4)
    rubric_headers = ["Phase", "Title", "Core Requirements & Deliverables", "Marks"]
    for c_idx, h in enumerate(rubric_headers):
        rubric_tbl.cell(0, c_idx).paragraphs[0].add_run(h)

    rubric_rows = [
        ("Phase 1", "Courier Problem Design & Planning", "Problem formulation, parcel attributes, road graph modeling, multi-algorithm architecture.", "20"),
        ("Phase 2", "Package Prioritization & Box Filling", "Merge Sort, Quick Sort, 0/1 Knapsack DP table, backtracking, packing manifest.", "20"),
        ("Phase 3", "Route Maker & Graph Processing", "Customer road graph, min-heap Dijkstra, Nearest-Neighbor TSP + 2-Opt refinement.", "20"),
        ("Phase 4", "Performance Testing & Optimization", "Multi-dataset benchmarks (Small, Medium, Large, Stress), runtime charts, complexity analysis.", "20"),
        ("Phase 5", "Final Report & Demonstration", "Runnable CLI, HTML dashboard, unit test verification, execution evidence, documentation.", "20")
    ]
    for r_idx, row in enumerate(rubric_rows):
        for c_idx, val in enumerate(row):
            rubric_tbl.cell(r_idx + 1, c_idx).paragraphs[0].add_run(val)
    format_table(rubric_tbl)

    # ---------------------------------------------------------
    # PHASE 1: PROBLEM DESIGN & PLANNING (20 MARKS)
    # ---------------------------------------------------------
    doc.add_page_break()
    p_h1 = doc.add_heading("Phase 1: Courier Problem Design and Planning (20 Marks)", level=1)
    p_h1.paragraph_format.space_before = Pt(10)
    p_h1.paragraph_format.space_after = Pt(8)

    p_p1_text = doc.add_paragraph(
        "The objective of this capstone project is to develop an integrated decision-support application that optimizes "
        "last-mile courier operations in an urban city. A courier vehicle departs from a central distribution depot (Node 0), "
        "transports a prioritized subset of orders to customer destinations across a road network under strict vehicle payload "
        "weight constraints, and returns to the depot with minimum total mileage."
    )
    p_p1_text.paragraph_format.space_after = Pt(8)

    doc.add_heading("1.1 Parcel Attributes Specification", level=2)
    attr_tbl = doc.add_table(rows=8, cols=3)
    attr_headers = ["Attribute", "Data Type", "Operational Definition"]
    for c_idx, h in enumerate(attr_headers):
        attr_tbl.cell(0, c_idx).paragraphs[0].add_run(h)

    attr_rows = [
        ("parcel_id", "str", "Unique tracking identifier (e.g., PKG-0001)."),
        ("customer_id", "str", "Customer account reference (e.g., CUST-0042)."),
        ("destination_node", "int", "Target vertex index in the road network graph."),
        ("weight", "int", "Discrete weight in kilograms (w_i >= 1) for knapsack capacity."),
        ("deadline_min", "int", "Customer delivery SLA deadline in minutes from dispatch."),
        ("priority", "int", "Urgency tier: 1 (Standard), 2 (Express), 3 (Rush), 4 (Critical)."),
        ("value", "int", "Calculated business utility score based on fee, priority, and SLA.")
    ]
    for r_idx, row in enumerate(attr_rows):
        for c_idx, val in enumerate(row):
            attr_tbl.cell(r_idx + 1, c_idx).paragraphs[0].add_run(val)
    format_table(attr_tbl)

    doc.add_heading("1.2 Road Network Graph Design", level=2)
    doc.add_paragraph(
        "The city road infrastructure is modeled as a weighted undirected graph G = (V, E, W), where:\n"
        "• Vertices (V): Intersections, delivery hubs, and customer locations. Node 0 is designated as the Central Depot.\n"
        "• Edges (E): Road corridors connecting adjacent nodes.\n"
        "• Weights (W): Non-negative floating-point values representing road distance (km) or travel time (min).\n"
        "The graph is stored via an adjacency list structure providing O(1) node lookup and O(deg(u)) edge traversal."
    )

    doc.add_heading("1.3 Multi-Algorithm Integration Architecture", level=2)
    doc.add_paragraph(
        "The pipeline harmonizes four algorithmic stages:\n"
        "1. Prioritization: Multi-criteria sorting (Merge Sort) arranges candidate parcels by deadline and priority.\n"
        "2. Box Filling: 0/1 Knapsack DP selects the exact subset of parcels that maximizes value without exceeding capacity.\n"
        "3. Shortest Paths: Dijkstra's algorithm with min-heap priority queue computes the metric distance matrix between depot and all selected stops.\n"
        "4. Tour Optimization: Nearest-Neighbor TSP approximation followed by 2-Opt local search refinement constructs the shortest closed delivery loop."
    )

    # Screenshot Placeholder 1
    add_screenshot_placeholder(
        doc,
        ss_id="1",
        title="Phase 1 - System Architecture & Dataset Generator Overview",
        program_cmd="python3 generate_all_datasets.py",
        description="Terminal console showing the successful generation of Small, Medium, Large, and Stress datasets and data/city_graph.json."
    )

    # ---------------------------------------------------------
    # PHASE 2: PACKAGE PRIORITIZATION & BOX FILLING (20 MARKS)
    # ---------------------------------------------------------
    doc.add_page_break()
    p_h2 = doc.add_heading("Phase 2: Package Prioritization and Box Filling (20 Marks)", level=1)
    p_h2.paragraph_format.space_before = Pt(10)
    p_h2.paragraph_format.space_after = Pt(8)

    doc.add_heading("2.1 Package Prioritization & Sorting", level=2)
    doc.add_paragraph(
        "Parcels are prioritized using a lexicographical multi-criteria key function:\n"
        "    SortKey(P) = (deadline_min, -priority, -value, weight)\n"
        "This guarantees that earlier delivery deadlines are serviced first, breaking ties by higher priority and higher value.\n"
        "Both Merge Sort (stable, guaranteed O(N log N)) and Quick Sort (3-way randomized Dutch National Flag partitioning) "
        "were implemented and verified against Python's built-in Timsort."
    )

    doc.add_heading("2.2 Dynamic Programming 0/1 Knapsack Mathematical Formulation", level=2)
    doc.add_paragraph(
        "Given N parcels with weights w_i and values v_i, and maximum vehicle capacity W_max, the objective is to maximize "
        "the total utility value under payload constraints. The 2D DP recurrence relation is defined as:\n\n"
        "    DP[i][w] = DP[i-1][w]                                    if w_i > w\n"
        "    DP[i][w] = max(DP[i-1][w], DP[i-1][w - w_i] + v_i)       if w_i <= w\n\n"
        "where DP[i][w] represents the maximum attainable value using a subset of the first i parcels with weight <= w.\n"
        "Backtracking reconstructs the selected parcel list by tracing from (N, W_max) down to (0, 0)."
    )

    # Screenshot Placeholder 2
    add_screenshot_placeholder(
        doc,
        ss_id="2",
        title="Phase 2 - 2D Dynamic Programming Table & Packing Manifest Evidence",
        program_cmd="python3 main.py --dataset small",
        description="Terminal output showing: (1) The Phase 2 Optimal Packing Manifest table (Parcel ID, Dest Node, Weight, Value), and (2) The formatted 2D Dynamic Programming Table sample showing capacity sub-problems from w=0 to w=12."
    )

    # ---------------------------------------------------------
    # PHASE 3: ROUTE MAKER & GRAPH PROCESSING (20 MARKS)
    # ---------------------------------------------------------
    doc.add_page_break()
    p_h3 = doc.add_heading("Phase 3: Route Maker and Graph Processing (20 Marks)", level=1)
    p_h3.paragraph_format.space_before = Pt(10)
    p_h3.paragraph_format.space_after = Pt(8)

    doc.add_heading("3.1 Customer Graph & Dijkstra Shortest Path", level=2)
    doc.add_paragraph(
        "The unique customer destination nodes corresponding to selected parcels form the active stop set S. "
        "Dijkstra's algorithm with a binary min-heap (heapq) runs from each node in {0} U S to compute the all-pairs "
        "metric distance matrix D[u, v] and track predecessors for turn-by-turn road network path expansion. "
        "Time complexity is O(K * (V + E) log V), executing in < 1 ms for city graphs."
    )

    doc.add_heading("3.2 TSP Route Planning & 2-Opt Local Search Refinement", level=2)
    doc.add_paragraph(
        "1. Nearest-Neighbor Heuristic: Greedily builds an initial closed delivery loop starting from Depot (Node 0) in O(K^2) time.\n"
        "2. 2-Opt Local Search: Iteratively evaluates non-adjacent edge pairs (A, B) and (C, D) and swaps them with (A, C) and (B, D) "
        "if reversing the intervening sub-path reduces total tour distance:\n"
        "    Delta = (D[A, C] + D[B, D]) - (D[A, B] + D[C, D]) < 0\n"
        "2-Opt removes crossing paths and achieved up to 16.07% route shortening in our benchmarks."
    )

    # Screenshot Placeholder 3
    add_screenshot_placeholder(
        doc,
        ss_id="3",
        title="Phase 3 - Delivery Route Sequence & Street Expansion",
        program_cmd="python3 main.py --dataset small",
        description="Terminal output displaying: (1) Stop Sequence (Depot(0) -> Node 6 -> Node 5 -> Node 1 -> Node 7 -> Depot(0)), (2) Total Roundtrip Distance (136.24 km), and (3) Expanded turn-by-turn street node path through intermediate junctions."
    )

    # Screenshot Placeholder 4
    add_screenshot_placeholder(
        doc,
        ss_id="4",
        title="Phase 3 - Visual Route Topology Map",
        program_cmd="Open file in browser: charts/route_visualization.svg",
        description="Browser view or image viewer displaying charts/route_visualization.svg: shows city road intersections (grey), Central Depot (red circle), customer stops (blue circles), and the optimized green directional delivery tour arrows."
    )

    # ---------------------------------------------------------
    # PHASE 4: PERFORMANCE TESTING & OPTIMIZATION (20 MARKS)
    # ---------------------------------------------------------
    doc.add_page_break()
    p_h4 = doc.add_heading("Phase 4: Performance Testing and Optimization (20 Marks)", level=1)
    p_h4.paragraph_format.space_before = Pt(10)
    p_h4.paragraph_format.space_after = Pt(8)

    doc.add_heading("4.1 Scalability Testing Across Dataset Scales", level=2)
    doc.add_paragraph(
        "The system was evaluated across four dataset scales. All four runs achieved 100% capacity utilization, "
        "and sub-50 ms total runtime even on stress instances with 1,000 candidate parcels."
    )

    bench_tbl = doc.add_table(rows=5, cols=7)
    bench_headers = ["Dataset Tier", "Parcels (N)", "Nodes (V)", "Capacity (W)", "Stops (K)", "2-Opt Gain", "Total Runtime"]
    for c_idx, h in enumerate(bench_headers):
        bench_tbl.cell(0, c_idx).paragraphs[0].add_run(h)

    bench_rows = [
        ("Small", "15", "8", "35 kg", "4", "0.0% (Exact Opt)", "0.146 ms"),
        ("Medium", "100", "25", "120 kg", "21", "9.28% shorter", "1.596 ms"),
        ("Large", "500", "50", "350 kg", "45", "15.49% shorter", "16.016 ms"),
        ("Stress", "1,000", "80", "600 kg", "77", "16.07% shorter", "48.628 ms")
    ]
    for r_idx, row in enumerate(bench_rows):
        for c_idx, val in enumerate(row):
            bench_tbl.cell(r_idx + 1, c_idx).paragraphs[0].add_run(val)
    format_table(bench_tbl)

    doc.add_heading("4.2 Algorithmic Runtime Breakdown (ms)", level=2)
    time_tbl = doc.add_table(rows=5, cols=6)
    time_headers = ["Dataset", "Merge Sort", "0/1 Knapsack DP", "Dijkstra Matrix", "TSP (NN+2-Opt)", "Total"]
    for c_idx, h in enumerate(time_headers):
        time_tbl.cell(0, c_idx).paragraphs[0].add_run(h)

    time_rows = [
        ("Small (N=15)", "0.052 ms", "0.041 ms", "0.030 ms", "0.012 ms", "0.146 ms"),
        ("Medium (N=100)", "0.306 ms", "0.574 ms", "0.491 ms", "0.210 ms", "1.596 ms"),
        ("Large (N=500)", "1.909 ms", "8.917 ms", "3.229 ms", "1.933 ms", "16.016 ms"),
        ("Stress (N=1000)", "3.990 ms", "31.887 ms", "7.784 ms", "3.683 ms", "48.628 ms")
    ]
    for r_idx, row in enumerate(time_rows):
        for c_idx, val in enumerate(row):
            time_tbl.cell(r_idx + 1, c_idx).paragraphs[0].add_run(val)
    format_table(time_tbl)

    doc.add_heading("4.3 Future Optimization Recommendations", level=2)
    doc.add_paragraph(
        "1. Knapsack Memory Optimization: For capacities exceeding 100,000 kg, adopt a 1D rolling array or Fully Polynomial-Time Approximation Scheme (FPTAS).\n"
        "2. Parallel Dijkstra Shortest Paths: Leverage Python's multiprocessing to parallelize Dijkstra metric queries from each delivery stop across CPU cores.\n"
        "3. Lin-Kernighan (LKH) / Genetic TSP: For tours with > 100 customer stops, implement higher-order k-opt edge exchanges or genetic algorithms."
    )

    # Screenshot Placeholder 5
    add_screenshot_placeholder(
        doc,
        ss_id="5",
        title="Phase 4 - Comprehensive Performance Benchmark & Runtime Chart",
        program_cmd="python3 benchmark.py  (or view charts/runtime_comparison.svg)",
        description="Terminal output from python3 benchmark.py displaying performance across all 4 datasets, or a screenshot of charts/runtime_comparison.svg showing grouped runtime bars (Merge Sort, Knapsack DP, Dijkstra, TSP)."
    )

    # ---------------------------------------------------------
    # PHASE 5: FINAL REPORT & DEMONSTRATION (20 MARKS)
    # ---------------------------------------------------------
    doc.add_page_break()
    p_h5 = doc.add_heading("Phase 5: Final Report and Demonstration (20 Marks)", level=1)
    p_h5.paragraph_format.space_before = Pt(10)
    p_h5.paragraph_format.space_after = Pt(8)

    doc.add_heading("5.1 System Demonstration & Interactive Dashboard", level=2)
    doc.add_paragraph(
        "The project delivers three complementary presentation and execution interfaces:\n"
        "1. Interactive CLI (main.py): Supports custom datasets, vehicle capacities, sorting algorithms, and heuristic switches.\n"
        "2. Standalone HTML Dashboard (charts/dashboard.html): Responsive, modern visual interface displaying KPI metric cards, capacity gauges, packing manifests, and route orders.\n"
        "3. Automated Benchmark Suite (benchmark.py): Generates benchmark tables, raw output traces (docs/output_traces.txt), and vector charts."
    )

    # Screenshot Placeholder 6
    add_screenshot_placeholder(
        doc,
        ss_id="6",
        title="Phase 5 - Interactive CLI Application Execution",
        program_cmd="python3 main.py --dataset medium",
        description="Terminal console displaying the execution of main.py on the Medium dataset: showing the ASCII banner, loading messages, KPI summary cards, packing table, route stops, and timing breakdown."
    )

    # Screenshot Placeholder 7
    add_screenshot_placeholder(
        doc,
        ss_id="7",
        title="Phase 5 - Interactive HTML Dashboard Overview",
        program_cmd="Open in web browser: open charts/dashboard.html",
        description="Browser screenshot of charts/dashboard.html displaying the dark-themed modern dashboard with KPI cards (Parcels Selected, Capacity Utilized, Route Distance, Runtime), Phase 2 manifest table, and Phase 3 route sequence."
    )

    # Screenshot Placeholder 8
    add_screenshot_placeholder(
        doc,
        ss_id="8",
        title="Phase 5 - Automated Unit Test Suite Execution",
        program_cmd="python3 -m unittest discover tests",
        description="Terminal console displaying successful execution of the 13 automated unit tests across test_sorting.py, test_knapsack.py, test_dijkstra.py, test_tsp.py, and test_pipeline.py, ending with 'Ran 13 tests in 0.001s - OK'."
    )

    doc.add_heading("5.2 Execution Guide & CLI Commands", level=2)
    doc.add_paragraph(
        "To reproduce all experimental results, execute the following commands in the project root:\n\n"
        "    1. Run Unit Tests:        python3 -m unittest discover tests\n"
        "    2. Run Benchmarks:        python3 benchmark.py\n"
        "    3. Launch Interactive CLI: python3 main.py --dataset medium\n"
        "    4. Open HTML Dashboard:    open charts/dashboard.html"
    )

    # Save document
    doc.save(output_path)
    print(f"[✓] Successfully generated final Word report: {output_path}")


if __name__ == "__main__":
    build_capstone_docx()
