# Phase 4: Performance Testing and Optimization

## 1. Experimental Methodology
To evaluate system scalability, rigorous benchmarks were conducted across four dataset tiers:

| Dataset Tier | Candidate Parcels ($N$) | Road Graph Nodes ($V$) | Vehicle Capacity ($W$) | Unique Delivery Stops ($K$) |
| :--- | :--- | :--- | :--- | :--- |
| **Small** | 15 | 8 | 35 kg | 4 |
| **Medium** | 100 | 25 | 120 kg | 21 |
| **Large** | 500 | 50 | 350 kg | 45 |
| **Stress** | 1000 | 80 | 600 kg | 77 |

---

## 2. Empirical Runtime Results

| Dataset | Merge Sort (ms) | 0/1 Knapsack DP (ms) | Dijkstra Matrix (ms) | TSP (NN+2-Opt) (ms) | Total Pipeline (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Small** | 0.052 ms | 0.041 ms | 0.030 ms | 0.012 ms | **0.146 ms** |
| **Medium** | 0.306 ms | 0.574 ms | 0.491 ms | 0.210 ms | **1.596 ms** |
| **Large** | 1.909 ms | 8.917 ms | 3.229 ms | 1.933 ms | **16.016 ms** |
| **Stress** | 3.990 ms | 31.887 ms | 7.784 ms | 3.683 ms | **48.628 ms** |

---

## 3. Algorithmic Complexity Analysis

| Algorithm | Theoretical Time Complexity | Theoretical Space Complexity | Empirical Behavior Observed |
| :--- | :--- | :--- | :--- |
| **Merge Sort** | $O(N \log N)$ | $O(N)$ | Scales sub-linearly; under 4 ms for 1,000 items. |
| **0/1 Knapsack DP** | $O(N \cdot W)$ | $O(N \cdot W)$ | Dominates runtime as $N \times W$ scales from 525 to 600,000 operations (~31.8 ms). |
| **Dijkstra Matrix** | $O(K \cdot (V + E) \log V)$ | $O(V + E)$ | Fast execution via binary min-heap; 7.78 ms for 80 nodes across 77 sources. |
| **TSP (NN + 2-Opt)** | $O(K^2)$ + local search | $O(K)$ | Near instantaneous (< 4 ms for 77 stops) with up to 16.07% distance improvement. |

---

## 4. Bottleneck Identification & Optimization Strategies

### 1. Knapsack Memory & Time Optimization
- **Current Bottleneck**: The full 2D table uses $(N+1) \times (W+1)$ integers. At $N=1000, W=600$, this requires 601,000 cells.
- **Future Improvements**:
  - **1D Rolling Array**: If the full table is not needed for external inspection, space can be reduced to $O(W)$ using bitwise back-tracking sets.
  - **Branch-and-Bound / FPTAS**: For massive capacities ($W > 100,000$), a Fully Polynomial-Time Approximation Scheme (FPTAS) can guarantee a $(1 - \epsilon)$ approximation in $O(N^3 / \epsilon)$.

### 2. Road Network Routing Scaling
- **Current Bottleneck**: Computing all-pairs Dijkstra for $K$ stops requires $K$ separate Dijkstra passes.
- **Future Improvements**:
  - **Contraction Hierarchies (CH) or A* Search**: Pre-processing highway hierarchies allows point-to-point queries in sub-millisecond times for real continental road networks (millions of vertices).
  - **Parallel Dijkstra**: Because shortest-path queries from each unique delivery stop are independent, they can be trivially parallelized using multi-threading or multiprocessing across CPU cores.

### 3. TSP Metaheuristics
- **Lin-Kernighan Heuristic (LKH)**: For deliveries with hundreds of stops per trip, LKH or Genetic Algorithms with edge recombination can produce near-exact TSP solutions within 1-2% of the Held-Karp lower bound.
