"""
Interactive CLI for the Courier Logistics Optimization System.
Provides full user control over dataset selection, vehicle capacity, sorting heuristics,
and routing algorithms with visual terminal reporting.
"""

import argparse
import sys
import os
from typing import List, Dict, Any

from src.dataset_generator import load_dataset_json, generate_parcels, generate_city_road_network
from src.pipeline import CourierOptimizationPipeline
from src.algorithms.knapsack import format_dp_table_sample
from src.visualization import generate_html_dashboard, generate_route_map_svg, generate_runtime_chart_svg


def print_banner():
    banner = r"""
================================================================================
   🚚 COURIER LOGISTICS OPTIMIZER - INTEGRATED CAPSTONE APPLICATION
      [Sorting] + [0/1 Knapsack DP] + [Dijkstra] + [TSP Route Maker]
================================================================================
"""
    print(banner)


def display_results(result: Dict[str, Any], show_dp_sample: bool = True):
    summary = result["summary"]
    packing = result["packing_result"]
    route = result["route_result"]
    timings = result["runtime_breakdown"]

    print("\n" + "=" * 80)
    print("                      EXECUTION & OPTIMIZATION RESULTS")
    print("=" * 80)

    # 1. Summary Cards
    print("\n[+] HIGH-LEVEL PERFORMANCE SUMMARY:")
    print(f"  • Candidate Parcels in Pool:   {summary['total_parcels_pool']} parcels (Total Weight: {summary['total_weight_pool']} kg)")
    print(f"  • Selected Parcels Packed:     {summary['selected_parcels_count']} parcels")
    print(f"  • Van Capacity Limit:          {summary['vehicle_capacity']} kg")
    print(f"  • Packed Weight:               {summary['packed_weight']} kg ({summary['capacity_utilization_pct']}% capacity utilized)")
    print(f"  • Packed Utility Value:        {summary['packed_value']} pts (Fractional Upper Bound: {summary['fractional_upper_bound']})")
    print(f"  • Unique Customer Stops:       {summary['unique_customer_stops']} destinations")
    print(f"  • Optimized Route Distance:    {summary['total_route_distance_km']} km (2-Opt improvement: {summary['tsp_improvement_pct']}%)")
    print(f"  • End-to-End Runtime:          {timings['total_pipeline_ms']:.3f} ms")

    # 2. Phase 2: Packing Manifest Table
    print("\n[+] PHASE 2: OPTIMAL PACKING MANIFEST (0/1 KNAPSACK DP):")
    print("-" * 80)
    print(f"{'Parcel ID':<12} | {'Dest Node':<10} | {'Weight (kg)':<12} | {'Deadline':<10} | {'Priority':<10} | {'Value':<8}")
    print("-" * 80)
    for p in packing.selected_parcels[:15]:
        prio_str = {1: "Low (1)", 2: "Med (2)", 3: "High (3)", 4: "Crit (4)"}.get(p.priority, str(p.priority))
        print(f"{p.parcel_id:<12} | Node {p.destination_node:<5} | {p.weight:<12} | {p.deadline_min}m{'':<6} | {prio_str:<10} | {p.value:<8}")
    if len(packing.selected_parcels) > 15:
        print(f"... and {len(packing.selected_parcels) - 15} more parcels selected ...")
    print("-" * 80)

    # 3. DP Table Sample Evidence
    if show_dp_sample and packing.dp_table:
        print("\n[+] PHASE 2: EVIDENCE - 2D DYNAMIC PROGRAMMING TABLE (SUBSET):")
        dp_sample = format_dp_table_sample(packing.dp_table, result["sorted_parcels"], max_cols=10, max_rows=6)
        print(dp_sample)

    # 4. Phase 3: Route Sequence
    print("\n[+] PHASE 3: FINAL DELIVERY ROUTE SEQUENCE (TSP + DIJKSTRA):")
    stops_str = " ➔ ".join([f"Depot(0)" if s == 0 else f"Node {s}" for s in route.delivery_stops])
    print(f"  Stop Sequence: {stops_str}")
    print(f"  Total Roundtrip Distance: {route.total_distance:.2f} km")

    # Turn by turn street expansion
    if len(route.full_path) <= 30:
        full_road_str = " -> ".join([str(n) for n in route.full_path])
        print(f"  Expanded Street Node Path: {full_road_str}")
    else:
        print(f"  Expanded Street Node Path: {len(route.full_path)} total road intersections traversed.")

    # 5. Phase 4: Runtime Breakdown
    print("\n[+] PHASE 4: ALGORITHMIC RUNTIME BREAKDOWN:")
    print("-" * 80)
    print(f"  1. Sorting ({result['sorted_parcels'][0].parcel_id if result['sorted_parcels'] else 'N/A'}...): {timings['sorting_ms']:.4f} ms")
    print(f"  2. 0/1 Knapsack DP Optimization:               {timings['knapsack_dp_ms']:.4f} ms")
    print(f"  3. Dijkstra All-Pairs Shortest Path Matrix:    {timings['dijkstra_ms']:.4f} ms")
    print(f"  4. TSP Route Optimization (NN + 2-Opt):        {timings['tsp_ms']:.4f} ms")
    print(f"  -------------------------------------------------------------")
    print(f"  TOTAL PIPELINE EXECUTION TIME:                 {timings['total_pipeline_ms']:.4f} ms")
    print("=" * 80 + "\n")


def main():
    print_banner()

    parser = argparse.ArgumentParser(description="Integrated Courier Logistics Optimizer")
    parser.add_argument("--dataset", choices=["small", "medium", "large", "stress"], default="small",
                        help="Pre-configured dataset size to evaluate (default: small)")
    parser.add_argument("--custom-file", type=str, default=None,
                        help="Path to custom JSON dataset file")
    parser.add_argument("--capacity", type=int, default=None,
                        help="Van carrying capacity in kg (defaults to dataset recommendation)")
    parser.add_argument("--sort-criterion", choices=["deadline_priority", "priority_deadline", "value_density"],
                        default="deadline_priority", help="Sorting prioritization rule")
    parser.add_argument("--sort-algorithm", choices=["merge_sort", "quick_sort", "timsort"],
                        default="merge_sort", help="Sorting algorithm to employ")
    parser.add_argument("--no-2opt", action="store_true",
                        help="Disable 2-Opt local search refinement (Nearest-Neighbor only)")
    parser.add_argument("--export-html", type=str, default="charts/dashboard.html",
                        help="Path to export interactive HTML dashboard")

    args = parser.parse_args()

    # Determine dataset path and default capacity
    if args.custom_file:
        data_path = args.custom_file
        default_cap = 50
    else:
        dataset_map = {
            "small": ("data/small_dataset.json", 35),
            "medium": ("data/medium_dataset.json", 120),
            "large": ("data/large_dataset.json", 350),
            "stress": ("data/stress_dataset.json", 600)
        }
        data_path, default_cap = dataset_map[args.dataset]

    cap = args.capacity if args.capacity is not None else default_cap

    if not os.path.exists(data_path):
        print(f"Dataset {data_path} not found. Generating default datasets first...")
        from generate_all_datasets import main as gen_main
        gen_main()

    print(f"[*] Loading dataset from '{data_path}'...")
    parcels, graph, meta = load_dataset_json(data_path)
    print(f"[*] Loaded {len(parcels)} parcels across {graph.num_nodes} road graph nodes.")
    print(f"[*] Vehicle Capacity Limit: {cap} kg")
    print(f"[*] Sorting: Criterion='{args.sort_criterion}', Algorithm='{args.sort_algorithm}'")
    print(f"[*] Routing: Dijkstra + TSP ({'Nearest-Neighbor only' if args.no_2opt else 'Nearest-Neighbor + 2-Opt'})")

    pipeline = CourierOptimizationPipeline(graph, depot_node=0)
    result = pipeline.run(
        all_parcels=parcels,
        vehicle_capacity=cap,
        sort_criterion=args.sort_criterion,
        sort_algorithm=args.sort_algorithm,
        use_two_opt=(not args.no_2opt)
    )

    display_results(result, show_dp_sample=(args.dataset == "small"))

    if args.export_html:
        os.makedirs(os.path.dirname(args.export_html) or ".", exist_ok=True)
        generate_html_dashboard(result, args.export_html)
        print(f"[✓] Interactive HTML Dashboard exported to: {args.export_html}")


if __name__ == "__main__":
    main()
