# Phase 1: Courier Problem Design and Planning

## 1. Executive Summary & Problem Formulation
The goal of this project is to develop an integrated logistics decision-support application that optimizes last-mile courier delivery operations. A courier vehicle departs from a central distribution hub (**Depot**), delivers a prioritized subset of orders to various customer locations across a city road network within strict vehicle weight capacities and delivery deadlines, and safely returns to the depot.

The system addresses two fundamental NP-hard optimization problems harmonized in a real-world pipeline:
1. **The 0/1 Knapsack Problem**: Maximizing delivery value/utility under vehicle weight constraints.
2. **The Traveling Salesperson Problem (TSP)** on a road network: Minimizing total transit distance/time while visiting all selected delivery destinations.

---

## 2. Parcel Attributes Specification
Every candidate parcel order in the system is defined by the following attributes:

| Attribute | Data Type | Description |
| :--- | :--- | :--- |
| `parcel_id` | `str` | Unique order identifier (e.g., `PKG-0001`). |
| `customer_id` | `str` | Customer account identifier (e.g., `CUST-0042`). |
| `destination_node` | `int` | Destination node ID in the road network graph. |
| `weight` | `int` | Discrete weight in kilograms ($w_i \ge 1$). |
| `deadline_min` | `int` | Customer delivery deadline in minutes from dispatch. |
| `priority` | `int` | Urgency tier: 1 (Standard), 2 (Express), 3 (Rush), 4 (Critical Medical). |
| `value` | `int` | Calculated business utility / service fee / SLA penalty score. |
| `description` | `str` | Package description or special handling notes. |

### Utility Value Calculation
The parcel utility value $v_i$ reflects operational revenue, urgency penalty mitigation, and customer priority:
$$v_i = \text{base\_value}(\text{tier}) + 2 \times \text{priority}_i \times \max\left(1, \left\lfloor \frac{400 - \text{deadline}_i}{20} \right\rfloor\right) + \epsilon$$

---

## 3. Road Network Graph Representation
The city road network is modeled as a weighted undirected graph $G = (V, E)$:
- **Vertices ($V$)**: Represent road intersections, hubs, and customer zones. Node `0` is designated as the Central Depot.
- **Edges ($E$)**: Represent road segments connecting intersections.
- **Weights ($W(u, v)$)**: Non-negative floating-point values representing road distance (in km) or travel time (in minutes).

The graph is implemented using an **adjacency list** `Dict[int, List[Tuple[int, float]]]` providing $O(1)$ vertex lookup and $O(\text{deg}(v))$ edge traversal efficiency.

---

## 4. Algorithmic Pipeline Architecture

```
[ All Candidate Parcels ]
           │
           ▼
┌──────────────────────────────────────────────┐
│  Phase 2: Parcel Prioritization & Sorting    │
│  - Multi-criteria Ranking (Deadline, Prio)   │
│  - Algorithms: Merge Sort, Quick Sort        │
└──────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────┐
│  Phase 2: Dynamic Programming 0/1 Knapsack   │
│  - Constraint: Vehicle Capacity W_max        │
│  - DP Table Construction & Backtracking      │
└──────────────────────────────────────────────┘
           │
           ▼
    [ Selected Parcels ] ──► Extract Unique Destination Nodes
                                   │
                                   ▼
┌──────────────────────────────────────────────┐
│  Phase 3: Road Graph & Dijkstra Shortest Path│
│  - Min-Heap Priority Queue                   │
│  - Metric All-Pairs Distance Matrix          │
└──────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────┐
│  Phase 3: TSP Route Planning & Optimization  │
│  - Nearest-Neighbor Initial Tour             │
│  - 2-Opt Local Search Refinement             │
│  - Full Turn-by-Turn Path Expansion          │
└──────────────────────────────────────────────┘
                                   │
                                   ▼
[ Final Optimized Delivery Tour & Execution Metrics ]
```

### Algorithm Suitability Rationale:
- **Sorting (Merge Sort)**: Guarantees $O(N \log N)$ worst-case time complexity and preserves stability, ensuring deterministic multi-criteria ranking.
- **0/1 Knapsack (Dynamic Programming)**: Guarantees an exact optimal packing solution in pseudo-polynomial time $O(N \cdot W)$, avoiding exponential $O(2^N)$ brute force.
- **Dijkstra's Algorithm**: Utilizes a binary min-heap to find shortest road network paths in $O((V + E) \log V)$ with guaranteed non-negative weight optimality.
- **Nearest-Neighbor + 2-Opt**: Computes a fast initial tour in $O(K^2)$ and removes sub-tour crossings via 2-Opt edge exchanges, achieving near-optimal delivery sequences without the factorial explosion of exact TSP ($O(K!)$).
