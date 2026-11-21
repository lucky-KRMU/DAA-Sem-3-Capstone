"""
Visualization module for Courier Delivery System.
Generates standalone SVG charts, route topology maps, HTML interactive dashboards,
and rich terminal ASCII visual reports without any external dependencies.
"""

import math
from typing import List, Dict, Any, Tuple
from .models import RoadGraph, Parcel, RouteResult, PackingResult


def generate_runtime_chart_svg(benchmark_data: List[Dict[str, Any]], output_path: str):
    """
    Generates a multi-series SVG grouped bar chart comparing algorithm runtimes across dataset scales.
    benchmark_data contains dicts with keys: 'name', 'sorting_ms', 'knapsack_dp_ms', 'dijkstra_ms', 'tsp_ms'
    """
    width = 800
    height = 500
    margin_left = 80
    margin_right = 40
    margin_top = 70
    margin_bottom = 80

    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom

    categories = [d["name"] for d in benchmark_data]
    series_keys = [
        ("sorting_ms", "Merge Sort", "#3b82f6"),
        ("knapsack_dp_ms", "0/1 Knapsack DP", "#10b981"),
        ("dijkstra_ms", "Dijkstra SP Matrix", "#f59e0b"),
        ("tsp_ms", "TSP (NN + 2-Opt)", "#8b5cf6")
    ]

    # Find max value for y-axis
    max_val = 0.01
    for d in benchmark_data:
        for key, _, _ in series_keys:
            max_val = max(max_val, d.get(key, 0.0))

    # Round up max_val to nice ceiling
    y_max = math.ceil(max_val * 1.25 * 10) / 10.0
    if y_max <= 0:
        y_max = 1.0

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%" style="background:#ffffff; font-family:system-ui, -apple-system, sans-serif;">',
        f'<rect width="{width}" height="{height}" fill="#f8fafc" rx="8"/>',
        f'<text x="{width/2}" y="35" text-anchor="middle" font-size="20" font-weight="bold" fill="#0f172a">Algorithmic Runtime Performance Comparison</text>',
        f'<text x="{width/2}" y="55" text-anchor="middle" font-size="12" fill="#64748b">Measured runtime in milliseconds (ms) across dataset scales</text>'
    ]

    # Gridlines and Y-axis labels
    y_ticks = 5
    for i in range(y_ticks + 1):
        y_val = (y_max / y_ticks) * i
        y_pos = margin_top + plot_h - (i / y_ticks) * plot_h
        svg_lines.append(f'<line x1="{margin_left}" y1="{y_pos}" x2="{margin_left + plot_w}" y2="{y_pos}" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="3,3"/>')
        svg_lines.append(f'<text x="{margin_left - 10}" y="{y_pos + 4}" text-anchor="end" font-size="11" fill="#64748b">{y_val:.2f} ms</text>')

    # Grouped bars
    num_groups = len(benchmark_data)
    group_width = plot_w / max(1, num_groups)
    bar_width = (group_width * 0.7) / len(series_keys)

    for g_idx, data_point in enumerate(benchmark_data):
        g_x_start = margin_left + g_idx * group_width + (group_width * 0.15)
        # X-axis category label
        center_x = g_x_start + (len(series_keys) * bar_width) / 2
        svg_lines.append(f'<text x="{center_x}" y="{margin_top + plot_h + 25}" text-anchor="middle" font-size="13" font-weight="600" fill="#1e293b">{data_point["name"]}</text>')
        svg_lines.append(f'<text x="{center_x}" y="{margin_top + plot_h + 42}" text-anchor="middle" font-size="10" fill="#64748b">(N={data_point.get("num_parcels", "-")})</text>')

        for s_idx, (s_key, s_label, s_color) in enumerate(series_keys):
            val = data_point.get(s_key, 0.0)
            bar_h = (val / y_max) * plot_h
            bar_x = g_x_start + s_idx * bar_width
            bar_y = margin_top + plot_h - bar_h

            svg_lines.append(f'<rect x="{bar_x:.1f}" y="{bar_y:.1f}" width="{bar_width*0.85:.1f}" height="{max(1.0, bar_h):.1f}" fill="{s_color}" rx="3">')
            svg_lines.append(f'<title>{s_label} ({data_point["name"]}): {val:.3f} ms</title>')
            svg_lines.append('</rect>')

            # Value label on top of bar if bar_h is large enough
            if bar_h > 15:
                svg_lines.append(f'<text x="{bar_x + (bar_width*0.85)/2:.1f}" y="{bar_y - 4:.1f}" text-anchor="middle" font-size="9" font-weight="bold" fill="#334155">{val:.2f}</text>')

    # Axes lines
    svg_lines.append(f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_h}" stroke="#94a3b8" stroke-width="2"/>')
    svg_lines.append(f'<line x1="{margin_left}" y1="{margin_top + plot_h}" x2="{margin_left + plot_w}" y2="{margin_top + plot_h}" stroke="#94a3b8" stroke-width="2"/>')

    # Legend
    legend_x = margin_left + 20
    legend_y = height - 20
    for s_idx, (_, s_label, s_color) in enumerate(series_keys):
        lx = legend_x + s_idx * 170
        svg_lines.append(f'<rect x="{lx}" y="{legend_y - 10}" width="14" height="14" fill="{s_color}" rx="3"/>')
        svg_lines.append(f'<text x="{lx + 20}" y="{legend_y + 2}" font-size="11" fill="#334155">{s_label}</text>')

    svg_lines.append('</svg>')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_lines))


def generate_route_map_svg(graph: RoadGraph, route_stops: List[int], output_path: str):
    """
    Renders an SVG map of the road network graph with the computed delivery tour highlighted.
    """
    width = 800
    height = 600
    margin = 60

    # Find bounding box of coordinates
    xs = [node.x for node in graph.nodes.values()] or [0, 50]
    ys = [node.y for node in graph.nodes.values()] or [0, 50]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max(1.0, max_x - min_x)
    span_y = max(1.0, max_y - min_y)

    def to_svg(x: float, y: float) -> Tuple[float, float]:
        sx = margin + ((x - min_x) / span_x) * (width - 2 * margin)
        sy = height - (margin + ((y - min_y) / span_y) * (height - 2 * margin))
        return sx, sy

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%" style="background:#ffffff; font-family:system-ui, sans-serif;">',
        f'<rect width="{width}" height="{height}" fill="#0f172a" rx="10"/>',
        f'<text x="{width/2}" y="35" text-anchor="middle" font-size="20" font-weight="bold" fill="#f8fafc">Optimized Courier Delivery Route Map</text>',
        f'<text x="{width/2}" y="55" text-anchor="middle" font-size="12" fill="#94a3b8">Depot -> Delivery Stops -> Depot (TSP Closed Loop)</text>',
        '<defs>',
        '<marker id="arrow" viewBox="0 0 10 10" refX="22" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="#10b981"/>',
        '</marker>',
        '</defs>'
    ]

    # 1. Draw all underlying road segments
    seen_edges = set()
    for u in graph.adj:
        for v, w in graph.adj[u]:
            edge_id = tuple(sorted((u, v)))
            if edge_id not in seen_edges:
                seen_edges.add(edge_id)
                n1, n2 = graph.nodes[u], graph.nodes[v]
                x1, y1 = to_svg(n1.x, n1.y)
                x2, y2 = to_svg(n2.x, n2.y)
                svg.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#334155" stroke-width="2" stroke-opacity="0.7"/>')
                # Optional distance label midpoint
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                svg.append(f'<text x="{mid_x:.1f}" y="{mid_y:.1f}" font-size="8" fill="#64748b" text-anchor="middle">{w}km</text>')

    # 2. Draw TSP route segments with directional green lines
    for i in range(len(route_stops) - 1):
        u, v = route_stops[i], route_stops[i + 1]
        n1, n2 = graph.nodes[u], graph.nodes[v]
        x1, y1 = to_svg(n1.x, n1.y)
        x2, y2 = to_svg(n2.x, n2.y)
        svg.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#10b981" stroke-width="4.5" marker-end="url(#arrow)" stroke-linecap="round"/>')

    # 3. Draw Nodes
    route_stop_order = {}
    for idx, stop in enumerate(route_stops[:-1]):
        route_stop_order[stop] = idx

    for node_id, node in graph.nodes.items():
        sx, sy = to_svg(node.x, node.y)
        if node.is_depot:
            # Central Depot node
            svg.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="14" fill="#ef4444" stroke="#ffffff" stroke-width="3"/>')
            svg.append(f'<text x="{sx:.1f}" y="{sy+4:.1f}" font-size="10" font-weight="bold" fill="#ffffff" text-anchor="middle">DEPOT</text>')
            svg.append(f'<text x="{sx:.1f}" y="{sy+26:.1f}" font-size="11" font-weight="bold" fill="#fca5a5" text-anchor="middle">Start/End (0)</text>')
        elif node_id in route_stop_order:
            # Active delivery stop
            stop_seq = route_stop_order[node_id]
            svg.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="12" fill="#3b82f6" stroke="#ffffff" stroke-width="2.5"/>')
            svg.append(f'<text x="{sx:.1f}" y="{sy+4:.1f}" font-size="10" font-weight="bold" fill="#ffffff" text-anchor="middle">#{stop_seq}</text>')
            svg.append(f'<text x="{sx:.1f}" y="{sy-16:.1f}" font-size="10" fill="#93c5fd" text-anchor="middle">Node {node_id}</text>')
        else:
            # Inactive road junction
            svg.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="6" fill="#475569" stroke="#1e293b" stroke-width="1.5"/>')
            svg.append(f'<text x="{sx:.1f}" y="{sy-9:.1f}" font-size="8" fill="#64748b" text-anchor="middle">{node_id}</text>')

    # Map Legend
    svg.append(f'<rect x="30" y="{height-50}" width="400" height="35" fill="#1e293b" rx="6"/>')
    svg.append(f'<circle cx="50" cy="{height-32}" r="8" fill="#ef4444"/>')
    svg.append(f'<text x="65" y="{height-28}" font-size="11" fill="#f8fafc">Depot</text>')
    svg.append(f'<circle cx="120" cy="{height-32}" r="8" fill="#3b82f6"/>')
    svg.append(f'<text x="135" y="{height-28}" font-size="11" fill="#f8fafc">Customer Stop</text>')
    svg.append(f'<line x1="240" y1="{height-32}" x2="275" y2="{height-32}" stroke="#10b981" stroke-width="3"/>')
    svg.append(f'<text x="285" y="{height-28}" font-size="11" fill="#f8fafc">Delivery Route</text>')

    svg.append('</svg>')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))


def generate_html_dashboard(pipeline_result: Dict[str, Any], output_path: str):
    """
    Builds a standalone responsive HTML dashboard report with modern CSS styling,
    KPI cards, delivery manifest, DP table visualization, and route breakdown.
    """
    summary = pipeline_result["summary"]
    runtime = pipeline_result["runtime_breakdown"]
    packing: PackingResult = pipeline_result["packing_result"]
    route: RouteResult = pipeline_result["route_result"]
    sorting = pipeline_result["sorting_benchmark"]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Courier Logistics Optimization Dashboard</title>
  <style>
    :root {{
      --primary: #2563eb;
      --success: #10b981;
      --warning: #f59e0b;
      --danger: #ef4444;
      --bg: #0f172a;
      --card-bg: #1e293b;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --border: #334155;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: var(--bg);
      color: var(--text-main);
      margin: 0;
      padding: 24px;
    }}
    .container {{
      max-width: 1200px;
      margin: 0 auto;
    }}
    header {{
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--border);
    }}
    h1 {{ margin: 0 0 8px 0; font-size: 28px; color: #60a5fa; }}
    p.subtitle {{ margin: 0; color: var(--text-muted); font-size: 14px; }}
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}
    .kpi-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
    }}
    .kpi-title {{ font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); }}
    .kpi-value {{ font-size: 26px; font-weight: bold; margin: 8px 0; color: #38bdf8; }}
    .kpi-sub {{ font-size: 11px; color: var(--text-muted); }}
    .section-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 24px;
    }}
    h2 {{ font-size: 18px; margin-top: 0; margin-bottom: 16px; color: #93c5fd; border-bottom: 1px solid var(--border); padding-bottom: 8px; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    th, td {{
      padding: 10px 12px;
      text-align: left;
      border-bottom: 1px solid var(--border);
    }}
    th {{ background: #0f172a; color: var(--text-muted); font-weight: 600; }}
    tr:hover {{ background: #334155; }}
    .badge {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 600;
    }}
    .badge-p1 {{ background: #334155; color: #94a3b8; }}
    .badge-p2 {{ background: #1e3a8a; color: #60a5fa; }}
    .badge-p3 {{ background: #78350f; color: #f59e0b; }}
    .badge-p4 {{ background: #7f1d1d; color: #f87171; }}
    .route-step {{
      display: inline-block;
      background: #1e3a8a;
      color: #93c5fd;
      padding: 4px 10px;
      border-radius: 16px;
      margin: 4px;
      font-size: 12px;
      font-weight: 600;
    }}
    .route-arrow {{ color: var(--success); font-weight: bold; margin: 0 4px; }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>🚚 Integrated Courier Logistics Optimization Engine</h1>
      <p class="subtitle">Capstone Project: Sorting + 0/1 Knapsack DP + Dijkstra Shortest Path + TSP Route Maker</p>
    </header>

    <!-- KPI Metric Cards -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-title">Parcels Selected / Total</div>
        <div class="kpi-value">{summary['selected_parcels_count']} / {summary['total_parcels_pool']}</div>
        <div class="kpi-sub">Value: {summary['packed_value']} (out of {summary['total_value_pool']})</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Vehicle Capacity Utilized</div>
        <div class="kpi-value">{summary['capacity_utilization_pct']}%</div>
        <div class="kpi-sub">{summary['packed_weight']} kg of {summary['vehicle_capacity']} kg limit</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Optimal Route Length</div>
        <div class="kpi-value">{summary['total_route_distance_km']} km</div>
        <div class="kpi-sub">{summary['unique_customer_stops']} delivery stops + return to depot</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Total Optimization Runtime</div>
        <div class="kpi-value">{runtime['total_pipeline_ms']:.2f} ms</div>
        <div class="kpi-sub">Sort: {runtime['sorting_ms']:.2f}ms | DP: {runtime['knapsack_dp_ms']:.2f}ms | Dijkstra: {runtime['dijkstra_ms']:.2f}ms</div>
      </div>
    </div>

    <!-- Phase 2: Packing Manifest -->
    <div class="section-card">
      <h2>📦 Phase 2: Optimal Box Filling Manifest (0/1 Knapsack DP)</h2>
      <p style="color:var(--text-muted); font-size:13px; margin-bottom:12px;">
        Selected <strong>{len(packing.selected_parcels)}</strong> parcels maximizing utility value ({packing.total_value} pts) within {summary['vehicle_capacity']} kg capacity.
      </p>
      <table>
        <thead>
          <tr>
            <th>Parcel ID</th>
            <th>Customer</th>
            <th>Dest Node</th>
            <th>Weight (kg)</th>
            <th>Deadline</th>
            <th>Priority</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
"""
    for p in packing.selected_parcels:
        badge_cls = f"badge-p{p.priority}"
        prio_label = {1: "Low", 2: "Medium", 3: "High", 4: "Critical"}.get(p.priority, "Standard")
        html += f"""          <tr>
            <td><strong>{p.parcel_id}</strong></td>
            <td>{p.customer_id}</td>
            <td>Node {p.destination_node}</td>
            <td>{p.weight} kg</td>
            <td>{p.deadline_min} mins</td>
            <td><span class="badge {badge_cls}">{prio_label}</span></td>
            <td><strong>{p.value}</strong></td>
          </tr>
"""
    html += f"""        </tbody>
      </table>
    </div>

    <!-- Phase 3: Route Plan -->
    <div class="section-card">
      <h2>🗺️ Phase 3: Final Delivery Route Sequence (TSP + Dijkstra)</h2>
      <p style="color:var(--text-muted); font-size:13px; margin-bottom:12px;">
        Tour Path: {' <span class="route-arrow">➔</span> '.join([f'<span class="route-step">{"Depot (0)" if s == 0 else f"Node {s}"}</span>' for s in route.delivery_stops])}
      </p>
      <p style="color:var(--text-muted); font-size:13px;">
        Total Travel Distance: <strong>{route.total_distance:.2f} km</strong> | 2-Opt Refinement Improvement: <strong>{summary['tsp_improvement_pct']}%</strong>
      </p>
    </div>

    <!-- Phase 4: Runtime Performance Breakdown -->
    <div class="section-card">
      <h2>⚡ Phase 4: Algorithmic Runtime Performance Breakdown</h2>
      <table>
        <thead>
          <tr>
            <th>Phase / Algorithm</th>
            <th>Complexity</th>
            <th>Measured Runtime</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>1. Sorting (Merge Sort)</td>
            <td>O(N log N)</td>
            <td>{runtime['sorting_ms']:.4f} ms</td>
            <td><span class="badge" style="background:#065f46; color:#34d399;">Optimal</span></td>
          </tr>
          <tr>
            <td>2. Box Filling (0/1 Knapsack DP)</td>
            <td>O(N &times; W)</td>
            <td>{runtime['knapsack_dp_ms']:.4f} ms</td>
            <td><span class="badge" style="background:#065f46; color:#34d399;">Optimal</span></td>
          </tr>
          <tr>
            <td>3. Shortest Paths (Dijkstra)</td>
            <td>O(K &times; (V + E) log V)</td>
            <td>{runtime['dijkstra_ms']:.4f} ms</td>
            <td><span class="badge" style="background:#065f46; color:#34d399;">Optimal</span></td>
          </tr>
          <tr>
            <td>4. Route Optimization (TSP NN + 2-Opt)</td>
            <td>O(K<sup>2</sup>)</td>
            <td>{runtime['tsp_ms']:.4f} ms</td>
            <td><span class="badge" style="background:#065f46; color:#34d399;">Optimal</span></td>
          </tr>
          <tr style="font-weight:bold; background:#1e293b;">
            <td>Total End-to-End Pipeline</td>
            <td>-</td>
            <td>{runtime['total_pipeline_ms']:.4f} ms</td>
            <td><span class="badge" style="background:#1e3a8a; color:#60a5fa;">Complete</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
