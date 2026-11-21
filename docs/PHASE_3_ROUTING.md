# Phase 3: Route Maker and Graph Processing

## 1. Customer Graph & Dijkstra Shortest Path
Once the optimal set of parcels is chosen by the 0/1 Knapsack engine, their destination nodes form the customer delivery stop set $\{s_1, s_2, \dots, s_k\}$. Together with the Central Depot (Node 0), this constitutes the active routing node set $S = \{0\} \cup \{s_1, \dots, s_k\}$.

### Dijkstra's Algorithm Implementation:
- **Data Structure**: Binary Min-Heap (`heapq`).
- **Complexity**: $O((V + E) \log V)$ per source node.
- **Predecessor Tracking**: For every node $v$, `predecessors[v]` stores the parent node along the shortest path, enabling full path reconstruction:
  $$\text{Path}(u, v) = [u, \dots, \text{pred}[\text{pred}[v]], \text{pred}[v], v]$$

### All-Pairs Metric Distance Matrix:
To support TSP tour solving, Dijkstra is executed from each unique stop $u \in S$. This builds a complete metric distance matrix $D[u, v]$ representing the true shortest road distance between any two stops.

---

## 2. TSP Delivery Route Construction & Optimization
Solving the overall delivery route requires finding a closed tour starting at Depot (0), visiting each delivery location $s_i \in S$, and returning to Depot (0), minimizing total distance:
$$\min \sum_{i=0}^{k} D[\pi(i), \pi(i+1)], \quad \text{where } \pi(0) = \pi(k+1) = 0$$

### Step 1: Nearest-Neighbor Approximation
Starting at Node 0, the courier greedily moves to the nearest unvisited customer stop:
$$v_{next} = \arg\min_{u \in \text{Unvisited}} D[v_{curr}, u]$$
- **Time Complexity**: $O(K^2)$, where $K = |S|$.

### Step 2: 2-Opt Local Search Heuristic
The Nearest-Neighbor tour often contains suboptimal crossing edges. The 2-Opt heuristic evaluates all pairs of non-adjacent edges $(A, B)$ and $(C, D)$ and tests whether replacing them with $(A, C)$ and $(B, D)$ reduces tour length:
$$\Delta = (D[A, C] + D[B, D]) - (D[A, B] + D[C, D])$$
If $\Delta < 0$, the sub-tour between $B$ and $C$ is reversed. This process repeats until no further 2-edge improvements can be found (local minimum).

### Benchmark Comparison (Small Dataset Instance):
| Method | Tour Sequence | Total Distance | Optimality Ratio |
| :--- | :--- | :--- | :--- |
| **Brute Force (Exact)** | `[0, 1, 5, 7, 6, 0]` | **136.24 km** | **1.000x (Optimal)** |
| **Nearest-Neighbor** | `[0, 6, 5, 1, 7, 0]` | 136.24 km | 1.000x |
| **2-Opt Refined** | `[0, 6, 5, 1, 7, 0]` | **136.24 km** | **1.000x** |

On larger instances, 2-Opt delivers substantial improvements over pure Nearest-Neighbor:
- **Medium (22 stops)**: 9.28% distance reduction.
- **Large (46 stops)**: 15.49% distance reduction.
- **Stress (78 stops)**: 16.07% distance reduction.

### Turn-by-Turn Road Expansion:
Every segment $(u, v)$ in the TSP tour is expanded using the pre-computed Dijkstra path, ensuring the driver receives street-by-street navigation directions through intermediate intersections.
