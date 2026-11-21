"""
Integrated Courier Logistics Optimization Pipeline.
Orchestrates:
  Phase 2: Parcel Prioritization (Sorting) & Box Filling (0/1 Knapsack DP)
  Phase 3: Route Maker & Graph Processing (Dijkstra + Nearest-Neighbor TSP + 2-Opt)
  Phase 4: Runtime profiling and end-to-end execution metrics
"""

import time
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict

from .models import Parcel, RoadGraph, PackingResult, RouteResult
from .algorithms.sorting import sort_parcels, compare_sorting_algorithms
from .algorithms.knapsack import knapsack_01_dp_with_table, fractional_knapsack_greedy
from .algorithms.dijkstra import compute_all_pairs_metric
from .algorithms.tsp import solve_tsp_combined, solve_tsp_nearest_neighbor, solve_tsp_brute_force


class CourierOptimizationPipeline:
    """
    End-to-End Delivery Trip Optimizer.
    Combines Sorting, Dynamic Programming Knapsack, Dijkstra Shortest Paths, and TSP.
    """

    def __init__(self, graph: RoadGraph, depot_node: int = 0):
        self.graph = graph
        self.depot_node = depot_node

    def run(self,
            all_parcels: List[Parcel],
            vehicle_capacity: int,
            sort_criterion: str = "deadline_priority",
            sort_algorithm: str = "merge_sort",
            use_two_opt: bool = True) -> Dict[str, Any]:
        """
        Executes the full logistics optimization workflow.

        Returns a dictionary containing:
          - 'sorted_parcels': parcels ordered by priority
          - 'sorting_benchmark': comparison of sorting algorithms
          - 'packing_result': PackingResult (selected parcels, weights, values, DP table)
          - 'route_result': RouteResult (stops, expanded path, distances)
          - 'runtime_breakdown': execution times for each pipeline stage
          - 'summary': high-level business and operational metrics
        """
        pipeline_start = time.perf_counter()
        timings = {}

        # -------------------------------------------------------------
        # Phase 2: Parcel Prioritization & Sorting
        # -------------------------------------------------------------
        t0 = time.perf_counter()
        sorting_comparison = compare_sorting_algorithms(all_parcels, criterion=sort_criterion)
        sorted_parcels = sort_parcels(all_parcels, criterion=sort_criterion, algorithm=sort_algorithm)
        timings["sorting_ms"] = (time.perf_counter() - t0) * 1000.0

        # -------------------------------------------------------------
        # Phase 2: Dynamic Programming 0/1 Knapsack Box Filling
        # -------------------------------------------------------------
        t0 = time.perf_counter()
        packing_result = knapsack_01_dp_with_table(sorted_parcels, capacity=vehicle_capacity)
        # Also compute fractional knapsack upper bound for comparison
        frac_bound, _ = fractional_knapsack_greedy(sorted_parcels, capacity=vehicle_capacity)
        timings["knapsack_dp_ms"] = (time.perf_counter() - t0) * 1000.0

        # Group selected parcels by destination node
        parcels_by_dest = defaultdict(list)
        for p in packing_result.selected_parcels:
            parcels_by_dest[p.destination_node].append(p)

        delivery_destinations = sorted(list(parcels_by_dest.keys()))

        # -------------------------------------------------------------
        # Phase 3: Route Maker & Graph Processing (Dijkstra)
        # -------------------------------------------------------------
        t0 = time.perf_counter()
        all_stops = [self.depot_node] + delivery_destinations
        dist_matrix, path_matrix, dijkstra_ms = compute_all_pairs_metric(self.graph, all_stops)
        timings["dijkstra_ms"] = dijkstra_ms

        # -------------------------------------------------------------
        # Phase 3: TSP Tour Construction & Optimization
        # -------------------------------------------------------------
        t0 = time.perf_counter()
        if use_two_opt:
            tsp_tour, tour_dist, tsp_stats = solve_tsp_combined(self.depot_node, delivery_destinations, dist_matrix)
        else:
            tsp_tour, tour_dist = solve_tsp_nearest_neighbor(self.depot_node, delivery_destinations, dist_matrix)
            tsp_stats = {
                "initial_dist": tour_dist,
                "final_dist": tour_dist,
                "improvement_pct": 0.0,
                "two_opt_iterations": 0,
                "time_ms": (time.perf_counter() - t0) * 1000.0
            }
        timings["tsp_ms"] = (time.perf_counter() - t0) * 1000.0

        # Expand metric TSP tour into detailed turn-by-turn road network path
        full_expanded_path: List[int] = []
        segment_distances: List[float] = []

        for i in range(len(tsp_tour) - 1):
            u, v = tsp_tour[i], tsp_tour[i + 1]
            seg_dist = dist_matrix.get((u, v), 0.0)
            segment_distances.append(seg_dist)
            road_seg = path_matrix.get((u, v), [u, v])
            if i == 0:
                full_expanded_path.extend(road_seg)
            else:
                full_expanded_path.extend(road_seg[1:])  # Avoid duplicate junction nodes

        route_result = RouteResult(
            depot_node=self.depot_node,
            delivery_stops=tsp_tour,
            full_path=full_expanded_path,
            total_distance=tour_dist,
            segment_distances=segment_distances,
            parcels_delivered_at_stop=dict(parcels_by_dest),
            execution_time_dijkstra_ms=timings["dijkstra_ms"],
            execution_time_tsp_ms=timings["tsp_ms"]
        )

        timings["total_pipeline_ms"] = (time.perf_counter() - pipeline_start) * 1000.0

        # Summary statistics
        total_value_pool = sum(p.value for p in all_parcels)
        total_weight_pool = sum(p.weight for p in all_parcels)
        val_ratio = (packing_result.total_value / total_value_pool * 100.0) if total_value_pool > 0 else 0.0
        cap_utilization = (packing_result.total_weight / vehicle_capacity * 100.0) if vehicle_capacity > 0 else 0.0

        summary = {
            "total_parcels_pool": len(all_parcels),
            "total_weight_pool": total_weight_pool,
            "total_value_pool": total_value_pool,
            "selected_parcels_count": len(packing_result.selected_parcels),
            "unselected_parcels_count": len(packing_result.unselected_parcels),
            "packed_weight": packing_result.total_weight,
            "vehicle_capacity": vehicle_capacity,
            "capacity_utilization_pct": round(cap_utilization, 2),
            "packed_value": packing_result.total_value,
            "fractional_upper_bound": round(frac_bound, 2),
            "value_retention_pct": round(val_ratio, 2),
            "unique_customer_stops": len(delivery_destinations),
            "total_route_distance_km": round(tour_dist, 2),
            "route_tour_sequence": tsp_tour,
            "tsp_improvement_pct": round(tsp_stats.get("improvement_pct", 0.0), 2)
        }

        return {
            "sorted_parcels": sorted_parcels,
            "sorting_benchmark": sorting_comparison,
            "packing_result": packing_result,
            "route_result": route_result,
            "tsp_stats": tsp_stats,
            "runtime_breakdown": timings,
            "summary": summary
        }
