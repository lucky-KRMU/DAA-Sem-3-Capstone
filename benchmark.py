"""
Performance Benchmarking and Chart Generation Suite.
Evaluates algorithmic runtime across all datasets (Small, Medium, Large, Stress).
Generates SVG charts, HTML interactive dashboard, and output traces for the final report.
"""

import os
import sys
import time
from typing import List, Dict, Any

from src.dataset_generator import load_dataset_json
from src.pipeline import CourierOptimizationPipeline
from src.algorithms.sorting import compare_sorting_algorithms
from src.algorithms.tsp import solve_tsp_brute_force, solve_tsp_nearest_neighbor, two_opt_optimize
from src.algorithms.knapsack import format_dp_table_sample, fractional_knapsack_greedy
from src.visualization import (
    generate_runtime_chart_svg,
    generate_route_map_svg,
    generate_html_dashboard
)


def run_comprehensive_benchmarks() -> tuple[List[Dict[str, Any]], Dict[str, Any], str]:
    os.makedirs("charts", exist_ok=True)
    os.makedirs("docs", exist_ok=True)

    datasets = [
        ("Small", "data/small_dataset.json", 35),
        ("Medium", "data/medium_dataset.json", 120),
        ("Large", "data/large_dataset.json", 350),
        ("Stress", "data/stress_dataset.json", 600)
    ]

    benchmark_summary: List[Dict[str, Any]] = []
    trace_lines: List[str] = []

    trace_lines.append("=" * 80)
    trace_lines.append("   COURIER LOGISTICS OPTIMIZATION SYSTEM - COMPREHENSIVE EXECUTION TRACE")
    trace_lines.append("   Evaluation & Benchmarking across 5 Project Phases")
    trace_lines.append("=" * 80)
    trace_lines.append("")

    primary_pipeline_result = None

    for name, path, cap in datasets:
        trace_lines.append("-" * 80)
        trace_lines.append(f"BENCHMARK RUN: {name.upper()} DATASET ({path})")
        trace_lines.append("-" * 80)

        parcels, graph, meta = load_dataset_json(path)
        trace_lines.append(f"Loaded {len(parcels)} parcels, road network with {graph.num_nodes} nodes.")
        trace_lines.append(f"Vehicle Capacity Limit: {cap} kg")
        trace_lines.append("")

        pipeline = CourierOptimizationPipeline(graph, depot_node=0)
        result = pipeline.run(
            all_parcels=parcels,
            vehicle_capacity=cap,
            sort_criterion="deadline_priority",
            sort_algorithm="merge_sort",
            use_two_opt=True
        )

        if name == "Small":
            primary_pipeline_result = result
            # Generate DP table sample evidence for small dataset
            packing = result["packing_result"]
            dp_sample = format_dp_table_sample(packing.dp_table, result["sorted_parcels"], max_cols=12, max_rows=10)
            trace_lines.append("--- PHASE 2: DYNAMIC PROGRAMMING KNAPSACK TABLE EVIDENCE (SAMPLE) ---")
            trace_lines.append(dp_sample)
            trace_lines.append("")

            # Exact TSP Brute Force Comparison
            dest_nodes = [p.destination_node for p in packing.selected_parcels]
            unique_stops = sorted(list(set(dest_nodes)))
            trace_lines.append("--- PHASE 3: TSP EXACT VS APPROXIMATION BENCHMARK ---")
            all_stops = [0] + unique_stops
            from src.algorithms.dijkstra import compute_all_pairs_metric
            d_mat, _, _ = compute_all_pairs_metric(graph, all_stops)
            
            t0 = time.perf_counter()
            nn_tour, nn_dist = solve_tsp_nearest_neighbor(0, unique_stops, d_mat)
            nn_time = (time.perf_counter() - t0) * 1000.0

            t0 = time.perf_counter()
            opt_tour, opt_dist, iters = two_opt_optimize(nn_tour, d_mat)
            opt_time = (time.perf_counter() - t0) * 1000.0

            if len(unique_stops) <= 9:
                t0 = time.perf_counter()
                exact_tour, exact_dist = solve_tsp_brute_force(0, unique_stops, d_mat)
                exact_time = (time.perf_counter() - t0) * 1000.0
                ratio_nn = (nn_dist / exact_dist) if exact_dist > 0 else 1.0
                ratio_2opt = (opt_dist / exact_dist) if exact_dist > 0 else 1.0
                trace_lines.append(f"Exact Brute Force TSP Tour: {exact_tour} | Distance: {exact_dist:.2f} km | Runtime: {exact_time:.3f} ms")
                trace_lines.append(f"Nearest-Neighbor Tour:    {nn_tour} | Distance: {nn_dist:.2f} km (Ratio: {ratio_nn:.3f}x) | Runtime: {nn_time:.3f} ms")
                trace_lines.append(f"2-Opt Refined Tour:        {opt_tour} | Distance: {opt_dist:.2f} km (Ratio: {ratio_2opt:.3f}x) | Runtime: {opt_time:.3f} ms")
            trace_lines.append("")

        # Record timings
        timings = result["runtime_breakdown"]
        summary = result["summary"]
        benchmark_summary.append({
            "name": name,
            "num_parcels": len(parcels),
            "num_nodes": graph.num_nodes,
            "capacity": cap,
            "sorting_ms": round(timings["sorting_ms"], 4),
            "knapsack_dp_ms": round(timings["knapsack_dp_ms"], 4),
            "dijkstra_ms": round(timings["dijkstra_ms"], 4),
            "tsp_ms": round(timings["tsp_ms"], 4),
            "total_ms": round(timings["total_pipeline_ms"], 4),
            "packed_items": summary["selected_parcels_count"],
            "packed_weight": summary["packed_weight"],
            "packed_value": summary["packed_value"],
            "route_dist_km": summary["total_route_distance_km"],
            "stops": summary["unique_customer_stops"]
        })

        trace_lines.append("SUMMARY RESULTS:")
        trace_lines.append(f"  * Parcels Selected: {summary['selected_parcels_count']} / {summary['total_parcels_pool']}")
        trace_lines.append(f"  * Weight Packed: {summary['packed_weight']} / {summary['vehicle_capacity']} kg ({summary['capacity_utilization_pct']}%)")
        trace_lines.append(f"  * Total Value: {summary['packed_value']} (Greedy Fractional Upper Bound: {summary['fractional_upper_bound']})")
        trace_lines.append(f"  * Route Sequence: {' -> '.join(map(str, summary['route_tour_sequence']))}")
        trace_lines.append(f"  * Route Length: {summary['total_route_distance_km']} km (2-Opt improvement: {summary['tsp_improvement_pct']}%)")
        trace_lines.append(f"  * Runtimes: Sort={timings['sorting_ms']:.3f}ms | Knapsack={timings['knapsack_dp_ms']:.3f}ms | Dijkstra={timings['dijkstra_ms']:.3f}ms | TSP={timings['tsp_ms']:.3f}ms | Total={timings['total_pipeline_ms']:.3f}ms")
        trace_lines.append("")

    # Generate comparative charts
    generate_runtime_chart_svg(benchmark_summary, "charts/runtime_comparison.svg")

    if primary_pipeline_result:
        # Load small dataset graph for route map
        _, small_graph, _ = load_dataset_json("data/small_dataset.json")
        generate_route_map_svg(small_graph, primary_pipeline_result["route_result"].delivery_stops, "charts/route_visualization.svg")
        # Generate HTML dashboard
        generate_html_dashboard(primary_pipeline_result, "charts/dashboard.html")

    # Generate Sorting Specific Chart
    # Compare Merge vs Quick vs Timsort on 1000 items
    stress_parcels, _, _ = load_dataset_json("data/stress_dataset.json")
    sort_comp = compare_sorting_algorithms(stress_parcels)
    trace_lines.append("-" * 80)
    trace_lines.append("PHASE 2: DETAILED SORTING ALGORITHM BENCHMARK (N=1000 PARCELS)")
    trace_lines.append("-" * 80)
    for alg, data in sort_comp.items():
        trace_lines.append(f"  * {alg:<12}: Runtime = {data['time_ms']:.4f} ms | Correctness Verified = {data['is_correct']}")
    trace_lines.append("")

    trace_str = "\n".join(trace_lines)
    with open("docs/output_traces.txt", "w", encoding="utf-8") as f:
        f.write(trace_str)

    print(trace_str)
    return benchmark_summary, primary_pipeline_result, trace_str


if __name__ == "__main__":
    run_comprehensive_benchmarks()
