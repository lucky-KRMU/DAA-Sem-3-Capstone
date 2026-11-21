"""
Traveling Salesperson Problem (TSP) solvers for delivery route planning.
Implements Nearest-Neighbor approximation, 2-Opt local search refinement,
and an exact Brute Force solver for small benchmark instances.
"""

import itertools
import time
from typing import List, Dict, Tuple, Set, Any


def tour_length(tour: List[int], dist_matrix: Dict[Tuple[int, int], float]) -> float:
    """Calculates total closed-loop length of a tour."""
    total = 0.0
    for i in range(len(tour) - 1):
        u, v = tour[i], tour[i + 1]
        d = dist_matrix.get((u, v), float('inf'))
        total += d
    return total


def solve_tsp_nearest_neighbor(start_node: int, stops: List[int], dist_matrix: Dict[Tuple[int, int], float]) -> Tuple[List[int], float]:
    """
    Constructs a delivery tour using the Nearest-Neighbor greedy heuristic.
    Starts at start_node (Depot), visits every stop in stops exactly once,
    and returns to start_node.

    Time Complexity: O(K^2) where K = len(stops)
    """
    unvisited: Set[int] = set(stops)
    unvisited.discard(start_node)

    tour = [start_node]
    curr = start_node

    while unvisited:
        # Find nearest unvisited stop from curr
        nearest_node = None
        min_dist = float('inf')
        for candidate in sorted(unvisited):
            d = dist_matrix.get((curr, candidate), float('inf'))
            if d < min_dist:
                min_dist = d
                nearest_node = candidate

        if nearest_node is None:
            # Graph disconnected fallback
            nearest_node = next(iter(unvisited))

        tour.append(nearest_node)
        unvisited.remove(nearest_node)
        curr = nearest_node

    # Complete the closed loop back to depot
    tour.append(start_node)
    total_dist = tour_length(tour, dist_matrix)
    return tour, total_dist


def two_opt_optimize(tour: List[int], dist_matrix: Dict[Tuple[int, int], float], max_iterations: int = 500) -> Tuple[List[int], float, int]:
    """
    Improves a tour using 2-opt local search.
    Iteratively swaps pairs of edges if reversing the sub-segment reduces total distance.

    Returns:
      best_tour: refined tour sequence
      best_distance: refined total distance
      iterations: number of improvement iterations executed
    """
    best_tour = list(tour)
    best_dist = tour_length(best_tour, dist_matrix)
    improved = True
    iterations = 0

    n = len(best_tour)
    # tour has format: [depot, s1, s2, ..., sn-2, depot] (length n >= 3)
    while improved and iterations < max_iterations:
        improved = False
        iterations += 1

        for i in range(1, n - 2):
            for j in range(i + 1, n - 1):
                # We consider cutting edges (i-1, i) and (j, j+1)
                # and reconnecting as (i-1, j) and (i, j+1)
                node_a, node_b = best_tour[i - 1], best_tour[i]
                node_c, node_d = best_tour[j], best_tour[j + 1]

                current_edges_cost = (dist_matrix.get((node_a, node_b), float('inf')) +
                                      dist_matrix.get((node_c, node_d), float('inf')))
                new_edges_cost = (dist_matrix.get((node_a, node_c), float('inf')) +
                                  dist_matrix.get((node_b, node_d), float('inf')))

                if new_edges_cost < current_edges_cost - 1e-9:
                    # Reverse segment from i to j inclusive
                    best_tour[i:j + 1] = reversed(best_tour[i:j + 1])
                    best_dist = tour_length(best_tour, dist_matrix)
                    improved = True
                    break
            if improved:
                break

    return best_tour, best_dist, iterations


def solve_tsp_combined(start_node: int, stops: List[int], dist_matrix: Dict[Tuple[int, int], float]) -> Tuple[List[int], float, Dict[str, Any]]:
    """
    Solves TSP by first constructing an initial tour with Nearest-Neighbor
    and then refining it with 2-Opt local search.
    """
    t0 = time.perf_counter()
    unique_stops = [s for s in set(stops) if s != start_node]

    if not unique_stops:
        return [start_node, start_node], 0.0, {
            "initial_dist": 0.0,
            "final_dist": 0.0,
            "improvement_pct": 0.0,
            "two_opt_iterations": 0,
            "time_ms": 0.0
        }

    # Step 1: Nearest Neighbor
    nn_tour, nn_dist = solve_tsp_nearest_neighbor(start_node, unique_stops, dist_matrix)

    # Step 2: 2-Opt
    opt_tour, opt_dist, iters = two_opt_optimize(nn_tour, dist_matrix)

    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    improvement_pct = ((nn_dist - opt_dist) / nn_dist * 100.0) if nn_dist > 0 else 0.0

    stats = {
        "initial_dist": nn_dist,
        "final_dist": opt_dist,
        "improvement_pct": improvement_pct,
        "two_opt_iterations": iters,
        "time_ms": elapsed_ms,
        "nn_tour": nn_tour
    }

    return opt_tour, opt_dist, stats


def solve_tsp_brute_force(start_node: int, stops: List[int], dist_matrix: Dict[Tuple[int, int], float]) -> Tuple[List[int], float]:
    """
    Exact TSP solver using full permutation search.
    Guarantees the global optimal tour.
    Feasible only for small instances (K <= 9).
    """
    unique_stops = [s for s in set(stops) if s != start_node]
    if not unique_stops:
        return [start_node, start_node], 0.0

    best_tour = None
    best_dist = float('inf')

    for perm in itertools.permutations(unique_stops):
        candidate_tour = [start_node] + list(perm) + [start_node]
        d = tour_length(candidate_tour, dist_matrix)
        if d < best_dist:
            best_dist = d
            best_tour = candidate_tour

    return best_tour or [start_node, start_node], best_dist
