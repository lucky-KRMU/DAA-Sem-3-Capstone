"""
Dijkstra's shortest path algorithm with min-heap priority queue.
Computes point-to-point shortest road paths and constructs all-pairs distance matrices for delivery stops.
"""

import heapq
import time
from typing import Dict, List, Tuple, Optional, Set
from ..models import RoadGraph


def dijkstra(graph: RoadGraph, source: int) -> Tuple[Dict[int, float], Dict[int, Optional[int]]]:
    """
    Computes single-source shortest paths from source to all reachable nodes in graph.
    Uses binary min-heap (via heapq) with O((V + E) log V) complexity.

    Returns:
      distances: mapping from node_id -> minimum distance from source
      predecessors: mapping from node_id -> previous node on shortest path
    """
    distances: Dict[int, float] = {}
    predecessors: Dict[int, Optional[int]] = {}

    for node in graph.nodes:
        distances[node] = float('inf')
        predecessors[node] = None

    distances[source] = 0.0

    # Min-heap storing tuples of (current_dist, node_id)
    pq: List[Tuple[float, int]] = [(0.0, source)]
    visited: Set[int] = set()

    while pq:
        d, u = heapq.heappop(pq)

        if u in visited:
            continue
        visited.add(u)

        if d > distances[u]:
            continue

        for v, weight in graph.get_neighbors(u):
            new_dist = distances[u] + weight
            if new_dist < distances.get(v, float('inf')):
                distances[v] = new_dist
                predecessors[v] = u
                heapq.heappush(pq, (new_dist, v))

    return distances, predecessors


def reconstruct_path(predecessors: Dict[int, Optional[int]], target: int, source: int) -> List[int]:
    """
    Reconstructs the full sequence of graph nodes from source to target.
    """
    if target == source:
        return [source]
    if predecessors.get(target) is None:
        return []

    path = []
    curr: Optional[int] = target
    while curr is not None:
        path.append(curr)
        if curr == source:
            break
        curr = predecessors.get(curr)

    if path[-1] != source:
        return []  # Target was not reachable from source

    path.reverse()
    return path


def compute_all_pairs_metric(graph: RoadGraph, nodes_subset: List[int]) -> Tuple[Dict[Tuple[int, int], float], Dict[Tuple[int, int], List[int]], float]:
    """
    Computes all-pairs shortest paths and distances between all nodes in nodes_subset.
    Runs Dijkstra from each unique node in nodes_subset.

    Returns:
      dist_matrix: (u, v) -> shortest distance
      path_matrix: (u, v) -> full road path list [u, ..., v]
      elapsed_ms: execution time in milliseconds
    """
    t0 = time.perf_counter()
    unique_nodes = sorted(list(set(nodes_subset)))
    dist_matrix: Dict[Tuple[int, int], float] = {}
    path_matrix: Dict[Tuple[int, int], List[int]] = {}

    for u in unique_nodes:
        dists, preds = dijkstra(graph, u)
        for v in unique_nodes:
            if u == v:
                dist_matrix[(u, v)] = 0.0
                path_matrix[(u, v)] = [u]
            else:
                dist_matrix[(u, v)] = dists.get(v, float('inf'))
                path_matrix[(u, v)] = reconstruct_path(preds, v, u)

    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    return dist_matrix, path_matrix, elapsed_ms
