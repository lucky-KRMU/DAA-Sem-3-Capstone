"""
Dataset generator for Courier Delivery System.
Creates synthetic road networks and parcel pools across small, medium, and large scales.
Exports to JSON and CSV format.
"""

import json
import csv
import random
import math
from typing import Dict, List, Tuple, Any
from .models import Parcel, RoadGraph, DeliveryPoint


def generate_city_road_network(num_nodes: int = 15,
                               area_width: float = 50.0,
                               area_height: float = 50.0,
                               edge_connectivity: float = 0.25,
                               seed: int = 42) -> RoadGraph:
    """
    Generates a connected planar-like road graph with coordinates and edge weights (distances in km).
    Node 0 is designated as the Central Depot.
    """
    rng = random.Random(seed)
    graph = RoadGraph(num_nodes)

    # 1. Generate node coordinates
    # Depot at center
    graph.add_node(0, "Central Depot", area_width / 2.0, area_height / 2.0, is_depot=True)

    for i in range(1, num_nodes):
        x = round(rng.uniform(2.0, area_width - 2.0), 2)
        y = round(rng.uniform(2.0, area_height - 2.0), 2)
        name = f"Delivery Hub/Customer Zone {i}"
        graph.add_node(i, name, x, y, is_depot=False)

    # 2. Build Minimum Spanning Tree (MST) using Prim's algorithm to ensure connectivity
    in_tree = {0}
    nodes_left = set(range(1, num_nodes))

    while nodes_left:
        best_u, best_v = None, None
        min_dist = float('inf')
        for u in in_tree:
            p_u = graph.nodes[u]
            for v in nodes_left:
                p_v = graph.nodes[v]
                euc = math.hypot(p_u.x - p_v.x, p_u.y - p_v.y)
                if euc < min_dist:
                    min_dist = euc
                    best_u, best_v = u, v

        # Add edge with slight road circuitous factor (1.1x - 1.3x Euclidean distance)
        road_dist = round(min_dist * rng.uniform(1.05, 1.25), 2)
        graph.add_edge(best_u, best_v, road_dist, bidirectional=True)
        in_tree.add(best_v)
        nodes_left.remove(best_v)

    # 3. Add extra edges for network density based on proximity
    for u in range(num_nodes):
        for v in range(u + 1, num_nodes):
            # Check if edge already exists
            existing = any(nb == v for nb, _ in graph.get_neighbors(u))
            if not existing:
                p_u = graph.nodes[u]
                p_v = graph.nodes[v]
                dist = math.hypot(p_u.x - p_v.x, p_u.y - p_v.y)
                # If nodes are close and passes random threshold
                if dist < (area_width * 0.4) and rng.random() < edge_connectivity:
                    road_dist = round(dist * rng.uniform(1.05, 1.3), 2)
                    graph.add_edge(u, v, road_dist, bidirectional=True)

    return graph


def generate_parcels(num_parcels: int,
                     num_nodes: int,
                     seed: int = 101) -> List[Parcel]:
    """
    Generates synthetic parcel orders destined for customer nodes in the road graph.
    Parcels have realistic weights, deadlines, priority categories, and calculated values.
    """
    rng = random.Random(seed)
    parcels: List[Parcel] = []

    priority_tiers = [
        # (priority, weight_min, weight_max, deadline_min, deadline_max, base_val_multiplier)
        (1, 1, 10, 180, 360, 10),   # Standard / Low Priority
        (2, 2, 12, 120, 240, 25),   # Express / Medium Priority
        (3, 1, 8,   60, 150, 50),   # Rush / High Priority
        (4, 1, 5,   30, 90,  100)   # Critical Medical / Same-Hour Priority
    ]
    # Distribution: Low 40%, Medium 35%, High 20%, Critical 5%
    weights_distribution = [0.40, 0.35, 0.20, 0.05]

    for i in range(1, num_parcels + 1):
        tier_choice = rng.choices(priority_tiers, weights=weights_distribution)[0]
        prio, w_min, w_max, d_min, d_max, base_val = tier_choice

        # Destination node between 1 and num_nodes - 1 (Node 0 is Depot)
        dest_node = rng.randint(1, max(1, num_nodes - 1))
        weight = rng.randint(w_min, w_max)
        deadline = rng.randint(d_min, d_max)

        # Value formula combines urgency score, base service fee, and SLA risk compensation
        urgency_factor = max(1, int(400 - deadline) // 20)
        value = int(base_val + (urgency_factor * prio * 2) + rng.randint(5, 20))

        p_id = f"PKG-{i:04d}"
        c_id = f"CUST-{(dest_node * 10 + (i % 7)):04d}"
        desc = f"Tier-{prio} Delivery to Node {dest_node}"

        parcels.append(Parcel(
            parcel_id=p_id,
            customer_id=c_id,
            destination_node=dest_node,
            weight=weight,
            deadline_min=deadline,
            priority=prio,
            value=value,
            description=desc
        ))

    return parcels


def export_parcels_csv(parcels: List[Parcel], filepath: str):
    """Exports parcels to CSV."""
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["parcel_id", "customer_id", "destination_node", "weight_kg", "deadline_min", "priority", "value", "description"])
        for p in parcels:
            writer.writerow([p.parcel_id, p.customer_id, p.destination_node, p.weight, p.deadline_min, p.priority, p.value, p.description])


def export_dataset_json(parcels: List[Parcel], graph: RoadGraph, filepath: str, metadata: Dict[str, Any] = None):
    """Exports complete dataset (parcels + road graph) to JSON."""
    payload = {
        "metadata": metadata or {},
        "graph": graph.to_dict(),
        "parcels": [p.to_dict() for p in parcels]
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def load_dataset_json(filepath: str) -> Tuple[List[Parcel], RoadGraph, Dict[str, Any]]:
    """Loads dataset from JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    parcels = [Parcel.from_dict(p) for p in data.get("parcels", [])]
    graph = RoadGraph.from_dict(data.get("graph", {}))
    metadata = data.get("metadata", {})
    return parcels, graph, metadata
