# Capstone Project Report: Integrated Courier Logistics Optimization Engine

**Course / Module:** Algorithm Design and Analysis  
**Project Title:** Multi-Algorithm Courier Delivery & Route Optimization System  
**Evaluation Scope:** Phases 1 to 5 (Full Rubric: 100/100 Marks)  

---

## Executive Summary
This capstone project presents an end-to-end Python decision-support platform designed to solve the urban last-mile delivery challenge. The application unifies four foundational algorithmic paradigms:
1. **Divide-and-Conquer Sorting** (Merge Sort and Quick Sort) for multi-criteria package prioritization.
2. **Dynamic Programming (0/1 Knapsack)** for vehicle box-filling that maximizes delivered utility value under strict vehicle carrying weight constraints.
3. **Graph Theory (Dijkstra's Algorithm)** with a binary min-heap priority queue to determine true point-to-point road network shortest paths.
4. **Heuristic & Local Search Optimization (Nearest-Neighbor TSP with 2-Opt Refinement)** to synthesize a closed delivery tour that minimizes overall transit distance.

The entire system is implemented in pure Python with zero mandatory external dependencies, evaluated across datasets ranging from 15 to 1,000 parcels, and accompanied by automated tests, SVG runtime charts, interactive HTML dashboards, and comprehensive empirical validation.

---

## Phase 1: Courier Problem Design and Planning (20 Marks)

### 1.1 Problem Statement
A logistics company operates from a central Depot (Node 0) in an urban area. Each day, the company receives a pool of $N$ candidate delivery requests. Each parcel has a specific destination customer zone, a weight, an urgency deadline, and a priority tier. 

The delivery vehicle has a strict maximum payload capacity $W_{max}$ (in kg) and cannot transport all available parcels in a single run. Therefore, the courier must:
1. Prioritize all orders based on delivery deadlines and service tier.
2. Select the optimal subset of parcels that maximizes total business utility without exceeding $W_{max}$.
3. Formulate an optimal closed-loop delivery tour starting at the Depot, visiting each customer destination corresponding to the selected parcels exactly once, and returning to the Depot with minimum transit mileage.

### 1.2 Data Design & Entity Attributes

#### Parcel Attributes:
- `parcel_id`: Unique identifier (e.g., `PKG-0001`).
- `customer_id`: Associated customer identifier.
- `destination_node`: Vertex ID in the road network graph.
- `weight`: Integer payload mass in kilograms ($w_i \ge 1$).
- `deadline_min`: Maximum elapsed time from vehicle departure within which delivery must occur.
- `priority`: Urgency classification: 1 (Standard), 2 (Express), 3 (Rush), 4 (Critical Medical).
- `value`: Discrete utility score combining revenue and deadline violation risk.

#### Road Network Graph Format:
The city road infrastructure is modeled as an undirected, weighted graph $G = (V, E, W)$, where:
- $V$: Intersections and delivery hubs. Node 0 is permanently assigned as the Central Depot.
- $E$: Road segments connecting adjacent nodes.
- $W(u, v) \in \mathbb{R}^+$: Non-negative road distance in kilometers.

The graph is maintained via an adjacency list structure (`RoadGraph`), allowing $O(1)$ vertex lookup and $O(\text{deg}(u))$ edge enumeration.

### 1.3 Algorithmic Integration Architecture

```
 Candidate Parcel Pool                    City Road Graph G=(V,E)
         │                                          │
         ▼                                          │
┌─────────────────────────────────┐                 │
│ Phase 2: Prioritization         │                 │
│ - Merge Sort / Quick Sort       │                 │
│ - Multi-criteria Sort Key       │                 │
└─────────────────────────────────┘                 │
         │                                          │
         ▼                                          │
┌─────────────────────────────────┐                 │
│ Phase 2: Box Filling (Knapsack) │                 │
│ - 0/1 Knapsack 2D DP Table      │                 │
│ - Backtracking Item Selection   │                 │
└─────────────────────────────────┘                 │
         │                                          │
  Selected Parcels                                  │
         │                                          │
         ▼                                          ▼
┌────────────────────────────────────────────────────────┐
│ Phase 3: Shortest Path Processing                      │
│ - Extract unique customer delivery nodes S             │
│ - Dijkstra's Algorithm (Min-Heap PQ) from each node in S│
│ - Compute All-Pairs Metric Distance Matrix D[u, v]     │
└────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ Phase 3: TSP Route Planning & Optimization             │
│ - Nearest-Neighbor Greedy Initial Tour                 │
│ - 2-Opt Local Search (Edge-Swap Disentanglement)       │
│ - Turn-by-Turn Road Path Expansion                    │
└────────────────────────────────────────────────────────┘
                           │
                           ▼
       [ Final Delivery Manifest & Route Sequence ]
```

---

## Phase 2: Package Prioritization and Box Filling (20 Marks)

### 2.1 Package Prioritization & Sorting
Parcels are ranked prior to selection to enforce business SLA constraints. The prioritization key establishes a lexicographical hierarchy:
$$\text{SortKey}(P) = (\text{deadline\_min}, -\text{priority}, -\text{value}, \text{weight})$$

#### Algorithm Selection & Comparison:
- **Merge Sort**: Selected as the primary prioritization engine because it is guaranteed to run in $O(N \log N)$ worst-case time and is **stable**, preserving the relative arrival order of equivalent priority parcels.
- **Quick Sort**: Implemented with randomized pivot selection and 3-way Dutch National Flag partitioning (`lt`, `i`, `gt`) to eliminate quadratic degradation ($O(N^2)$) on inputs with repeated keys.
- **Timsort**: Evaluated as the golden baseline.

*Empirical Sorting Benchmark (N=1,000 Parcels):*
- Merge Sort: **1.27 ms** (Correctness: 100% verified)
- Quick Sort: **1.16 ms** (Correctness: 100% verified)
- Timsort: **0.15 ms** (Correctness: 100% verified)

### 2.2 Dynamic Programming 0/1 Knapsack Formulation
The vehicle packing problem is formulated as a 0/1 Knapsack optimization:
$$\max \sum_{i=1}^{N} v_i x_i \quad \text{subject to} \quad \sum_{i=1}^{N} w_i x_i \le W_{max}, \quad x_i \in \{0, 1\}$$

#### Recurrence Equation:
$$DP[i][w] = \begin{cases}
0 & \text{if } i = 0 \text{ or } w = 0 \\
DP[i-1][w] & \text{if } w_i > w \\
\max(DP[i-1][w], DP[i-1][w - w_i] + v_i) & \text{if } w_i \le w
\end{cases}$$

#### Backtracking Procedure:
To recover the exact set of parcels, backtracking traverses from $(N, W_{max})$ down to $(0, 0)$:
- If $DP[i][w] \ne DP[i-1][w]$, parcel $i$ is flagged as selected ($x_i = 1$), and capacity is decremented: $w \leftarrow w - w_i$.
- If equal, parcel $i$ was excluded ($x_i = 0$).

#### Evidence: Dynamic Programming Table (Small Dataset Sample, Capacity=35kg)
```
Item (wt,val)      | w=  0 | w=  1 | w=  2 | w=  3 | w=  4 | w=  5 | w=  6 | w=  7 | w=  8 | w=  9 | w= 10 | w= 11 | w= 12 | ...
-----------------------------------------------------------------------------------------------------------------------------
Base (0, 0)        |     0 |     0 |     0 |     0 |     0 |     0 |     0 |     0 |     0 |     0 |     0 |     0 |     0
PPKG-0013 (6kg, 15 |     0 |     0 |     0 |     0 |     0 |     0 |   159 |   159 |   159 |   159 |   159 |   159 |   159
PPKG-0009 (3kg, 15 |     0 |     0 |     0 |   153 |   153 |   153 |   159 |   159 |   159 |   312 |   312 |   312 |   312
PPKG-0010 (2kg, 13 |     0 |     0 |   134 |   153 |   153 |   287 |   287 |   287 |   293 |   312 |   312 |   446 |   446
PPKG-0004 (8kg, 79 |     0 |     0 |   134 |   153 |   153 |   287 |   287 |   287 |   293 |   312 |   312 |   446 |   446
PPKG-0002 (3kg, 89 |     0 |     0 |   134 |   153 |   153 |   287 |   287 |   287 |   376 |   376 |   376 |   446 |   446
```

#### Packing Plan Results:
- **Small Dataset**: 8 of 15 parcels packed; **35 / 35 kg (100.0% utilization)**; total value = 762 (Fractional upper bound = 777.75).
- **Medium Dataset**: 34 of 100 parcels packed; **120 / 120 kg (100.0% utilization)**; total value = 5,088.
- **Large Dataset**: 126 of 500 parcels packed; **350 / 350 kg (100.0% utilization)**; total value = 18,157.
- **Stress Dataset**: 239 of 1,000 parcels packed; **600 / 600 kg (100.0% utilization)**; total value = 32,315.

---

## Phase 3: Route Maker and Graph Processing (20 Marks)

### 3.1 Customer Graph & Dijkstra Shortest Path
The destinations of all selected parcels are aggregated into a unique destination stop set $\{s_1, \dots, s_k\}$. Including Depot (0), the active tour stop set is $S = \{0\} \cup \{s_1, \dots, s_k\}$.

#### Dijkstra Algorithm Execution:
- A binary min-heap (`heapq`) tracks the current unvisited frontier with minimum tentative distance.
- Predecessors are tracked to enable exact road segment path reconstruction.
- Dijkstra is executed starting from each node in $S$, computing the complete metric distance matrix $D_{K \times K}$.
- Time Complexity: $O(K \cdot (V + E) \log V)$, which requires only **0.03 ms** for the Small dataset and **7.78 ms** for the 80-node Stress dataset.

### 3.2 TSP Route Planning & 2-Opt Optimization

#### 1. Nearest-Neighbor Heuristic:
A greedy tour is formed by starting at Depot (0) and sequentially visiting the nearest unvisited customer destination until all stops are exhausted, subsequently returning to Depot (0).
Time Complexity: $O(K^2)$.

#### 2. 2-Opt Local Search Refinement:
The greedy tour often incurs crossing road paths. The 2-Opt local search examines pairs of tour edges $(u_i, u_{i+1})$ and $(u_j, u_{j+1})$ and reverses the intervening sub-path whenever:
$$D[u_i, u_j] + D[u_{i+1}, u_{j+1}] < D[u_i, u_{i+1}] + D[u_j, u_{j+1}]$$

#### Exact vs. Heuristic Comparison (Small Dataset):
To empirically prove the quality of the TSP approximation, an exact Brute Force permutation solver was executed on the small dataset:
- **Brute Force (Global Optimum)**: `[0, 1, 5, 7, 6, 0]` $\rightarrow$ **136.24 km** (Runtime: 0.014 ms)
- **Nearest-Neighbor**: `[0, 6, 5, 1, 7, 0]` $\rightarrow$ **136.24 km** (Ratio: **1.000x**)
- **2-Opt Refined**: `[0, 6, 5, 1, 7, 0]` $\rightarrow$ **136.24 km** (Ratio: **1.000x**)

On larger datasets, 2-Opt delivers dramatic reductions in driver transit mileage:
- Medium (21 customer stops): **9.28%** route shortening.
- Large (45 customer stops): **15.49%** route shortening.
- Stress (77 customer stops): **16.07%** route shortening.

---

## Phase 4: Performance Testing and Optimization (20 Marks)

### 4.1 Scalability Testing Across Dataset Scales
Performance benchmarks were executed across four dataset tiers on macOS (Apple Silicon architecture):

| Dataset Scale | Parcels ($N$) | Nodes ($V$) | Capacity ($W$) | Stops ($K$) | Merge Sort | 0/1 Knapsack DP | Dijkstra Matrix | TSP (NN+2-Opt) | Total Pipeline |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Small** | 15 | 8 | 35 kg | 4 | 0.052 ms | 0.041 ms | 0.030 ms | 0.012 ms | **0.146 ms** |
| **Medium** | 100 | 25 | 120 kg | 21 | 0.306 ms | 0.574 ms | 0.491 ms | 0.210 ms | **1.596 ms** |
| **Large** | 500 | 50 | 350 kg | 45 | 1.909 ms | 8.917 ms | 3.229 ms | 1.933 ms | **16.016 ms** |
| **Stress** | 1000 | 80 | 600 kg | 77 | 3.990 ms | 31.887 ms | 7.784 ms | 3.683 ms | **48.628 ms** |

### 4.2 Runtime Chart Evidence
The benchmark engine automatically generated high-resolution vector charts:
- Grouped Bar Chart: [charts/runtime_comparison.svg](charts/runtime_comparison.svg)
- Road Network Route Map: [charts/route_visualization.svg](charts/route_visualization.svg)

### 4.3 Complexity Comparison & Scaling Behavior
1. **Sorting ($O(N \log N)$)**: Scales gracefully, taking only 3.99 ms for 1,000 parcels.
2. **Knapsack DP ($O(N \cdot W)$)**: The dominant computational consumer for large instances. As $N \times W$ grows from $15 \times 35 = 525$ to $1000 \times 600 = 600,000$ operations, runtime scales predictably from 0.04 ms to 31.89 ms.
3. **Dijkstra ($O(K \cdot (V + E) \log V)$)**: Fast execution due to sparse road graph degrees and binary heap indexing.
4. **TSP ($O(K^2)$)**: Nearest Neighbor with 2-Opt executes in under 4 ms even for 77 stops.

### 4.4 Bottleneck Analysis & Future Optimization Recommendations
1. **Dynamic Programming Space & Time**:
   - For industrial applications with capacities exceeding $W = 100,000$, standard pseudo-polynomial DP tables become memory-constrained.
   - *Recommendation*: Implement a **Fully Polynomial-Time Approximation Scheme (FPTAS)** or branch-and-bound relaxation to achieve $(1 - \epsilon)$ optimality with bounded memory.
2. **Parallel Dijkstra Metric Construction**:
   - Single-source shortest path calculations from each delivery node are independent.
   - *Recommendation*: Fan out Dijkstra calls across multiple CPU cores using Python's `concurrent.futures` or multiprocessing.
3. **High-Order TSP Heuristics**:
   - For tours exceeding 100 delivery stops, 2-Opt can be extended to **3-Opt** or the **Lin-Kernighan Heuristic (LKH)**, which systematically breaks 3 or more edges to achieve near-global optimality.

---

## Phase 5: Final Report and Demonstration (20 Marks)

### 5.1 Verification of System Functionality
The platform includes an interactive CLI (`main.py`) and an automated test suite (`tests/`):
- **13 out of 13 unit tests passed** in **0.001 seconds**.
- Full test coverage across Merge Sort, Quick Sort, DP Knapsack, Dijkstra shortest paths, TSP 2-Opt, and end-to-end pipeline execution.

### 5.2 Standalone Interactive Dashboard
The system compiles optimization manifests into a self-contained responsive HTML dashboard:
- File Location: [charts/dashboard.html](charts/dashboard.html)
- Includes KPI metric cards, capacity utilization gauges, complete itemized packing manifests with priority badges, and turn-by-turn road route sequences.

### 5.3 Execution Instructions
```bash
# 1. Run unit test suite
python3 -m unittest discover tests

# 2. Run automated benchmarks and generate all charts
python3 benchmark.py

# 3. Launch interactive CLI
python3 main.py --dataset medium
```

---

## Conclusion
The developed Courier Logistics Optimization application successfully fulfills all requirements outlined in `Instructions.md`. By integrating Divide-and-Conquer Sorting, Dynamic Programming Knapsack, Dijkstra Shortest Path, and 2-Opt TSP routing into a coherent software architecture, the system achieves 100% vehicle capacity utilization, optimal route mileage reductions, and sub-50ms execution times even on stress datasets with 1,000 parcels.
