"""
Data models for the Courier Delivery System.
Defines Parcel, Customer, DeliveryPoint, RoadGraph, and DeliveryPlan.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
import json


@dataclass
class Parcel:
    """Represents an individual parcel to be delivered."""
    parcel_id: str
    customer_id: str
    destination_node: int
    weight: int              # Weight in kg (must be positive integer for discrete 0/1 knapsack)
    deadline_min: int        # Delivery deadline in minutes from dispatch
    priority: int            # 1: Low, 2: Medium, 3: High, 4: Critical
    value: int               # Delivery value / utility score derived from priority and SLA
    description: str = ""

    def __repr__(self) -> str:
        return (f"Parcel({self.parcel_id}, dest={self.destination_node}, "
                f"wt={self.weight}kg, dline={self.deadline_min}m, "
                f"prio={self.priority}, val={self.value})")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "parcel_id": self.parcel_id,
            "customer_id": self.customer_id,
            "destination_node": self.destination_node,
            "weight": self.weight,
            "deadline_min": self.deadline_min,
            "priority": self.priority,
            "value": self.value,
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Parcel":
        return cls(
            parcel_id=data["parcel_id"],
            customer_id=data["customer_id"],
            destination_node=data["destination_node"],
            weight=int(data["weight"]),
            deadline_min=int(data["deadline_min"]),
            priority=int(data["priority"]),
            value=int(data["value"]),
            description=data.get("description", "")
        )


@dataclass
class DeliveryPoint:
    """Represents a node/location in the delivery network."""
    node_id: int
    name: str
    x: float = 0.0          # Coordinate for 2D visualization
    y: float = 0.0
    is_depot: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "is_depot": self.is_depot
        }


class RoadGraph:
    """
    Weighted road network graph represented via adjacency lists.
    Nodes represent intersections or delivery locations (node 0 is default Depot).
    Edges represent road segments with distance/travel time weights.
    """
    def __init__(self, num_nodes: int = 0):
        self.num_nodes: int = num_nodes
        self.nodes: Dict[int, DeliveryPoint] = {}
        self.adj: Dict[int, List[Tuple[int, float]]] = {}
        for i in range(num_nodes):
            self.adj[i] = []

    def add_node(self, node_id: int, name: str, x: float = 0.0, y: float = 0.0, is_depot: bool = False):
        self.nodes[node_id] = DeliveryPoint(node_id, name, x, y, is_depot)
        if node_id not in self.adj:
            self.adj[node_id] = []
        if node_id >= self.num_nodes:
            self.num_nodes = max(self.num_nodes, node_id + 1)

    def add_edge(self, u: int, v: int, weight: float, bidirectional: bool = True):
        """Add an edge between u and v with non-negative weight."""
        if u not in self.adj:
            self.adj[u] = []
        if v not in self.adj:
            self.adj[v] = []
        self.adj[u].append((v, weight))
        if bidirectional:
            self.adj[v].append((u, weight))

    def get_neighbors(self, u: int) -> List[Tuple[int, float]]:
        return self.adj.get(u, [])

    def to_dict(self) -> Dict[str, Any]:
        edges = []
        seen = set()
        for u in self.adj:
            for v, w in self.adj[u]:
                edge_id = tuple(sorted((u, v)))
                if edge_id not in seen:
                    seen.add(edge_id)
                    edges.append({"u": u, "v": v, "weight": w})
        return {
            "num_nodes": self.num_nodes,
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": edges
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RoadGraph":
        g = cls(data.get("num_nodes", 0))
        for n_data in data.get("nodes", []):
            g.add_node(
                node_id=n_data["node_id"],
                name=n_data["name"],
                x=n_data.get("x", 0.0),
                y=n_data.get("y", 0.0),
                is_depot=n_data.get("is_depot", False)
            )
        for e in data.get("edges", []):
            g.add_edge(e["u"], e["v"], float(e["weight"]), bidirectional=True)
        return g


@dataclass
class PackingResult:
    """Result of Phase 2 Knapsack Box Filling."""
    selected_parcels: List[Parcel]
    unselected_parcels: List[Parcel]
    total_weight: int
    total_value: int
    capacity: int
    dp_table: Optional[List[List[int]]] = None
    execution_time_ms: float = 0.0


@dataclass
class RouteResult:
    """Result of Phase 3 Route Maker and Graph Processing."""
    depot_node: int
    delivery_stops: List[int]             # Stops sequence: [0, s1, s2, ..., 0]
    full_path: List[int]                  # Expanded street-by-street node sequence
    total_distance: float
    segment_distances: List[float]
    parcels_delivered_at_stop: Dict[int, List[Parcel]]
    execution_time_dijkstra_ms: float = 0.0
    execution_time_tsp_ms: float = 0.0
