# Phase 2: Package Prioritization and Box Filling

## 1. Package Prioritization & Sorting
Parcels must be prioritized to ensure that high-urgency and tight-deadline packages are addressed first.

### Multi-Criteria Prioritization Function:
The sorting key evaluates parcels according to:
1. **Deadline ($d_i$)**: Ascending order (earliest deadline first).
2. **Priority ($p_i$)**: Descending order (Critical > Rush > Express > Standard).
3. **Value ($v_i$)**: Descending order.
4. **Weight ($w_i$)**: Ascending order.

$$\text{Key}(P) = (d_i, -p_i, -v_i, w_i)$$

### Sorting Algorithm Benchmark:
Both custom Merge Sort and 3-way partitioned randomized Quick Sort were implemented and benchmarked against Python's built-in Timsort:
- **Merge Sort**: Stable divide-and-conquer, $O(N \log N)$ worst-case.
- **Quick Sort**: In-place divide-and-conquer with randomized pivot, average $O(N \log N)$, worst-case $O(N^2)$ mitigated via 3-way Dutch National Flag partitioning.

---

## 2. Dynamic Programming 0/1 Knapsack Box Filling
Given $N$ candidate parcels each with weight $w_i \in \mathbb{Z}^+$ and value $v_i \in \mathbb{Z}^+$, and a van capacity $W_{max}$, select a subset $S \subseteq \{1, \dots, N\}$ such that:
$$\max \sum_{i \in S} v_i \quad \text{subject to} \quad \sum_{i \in S} w_i \le W_{max}$$

### Recurrence Relation:
Let $DP[i][w]$ denote the maximum value achievable considering the first $i$ parcels with maximum weight capacity $w$:
$$DP[i][w] = \begin{cases} 
0 & \text{if } i = 0 \text{ or } w = 0 \\
DP[i-1][w] & \text{if } w_i > w \\
\max(DP[i-1][w], DP[i-1][w - w_i] + v_i) & \text{if } w_i \le w 
\end{cases}$$

### Backtracking Reconstruction:
After populating the $(N+1) \times (W+1)$ matrix, items are retrieved by starting from $(N, W_{max})$:
- If $DP[i][w] \ne DP[i-1][w]$, parcel $i$ is included in the optimal set, and $w \leftarrow w - w_i$.
- Otherwise, parcel $i$ was excluded.

### DP Table Evidence (Small Dataset, Capacity = 35 kg):
```
Item (wt,val)      | w=  0 | w=  1 | w=  2 | w=  3 | w=  4 | w=  5 | w=  6 | w=  7 | w=  8 | w=  9 | w= 10 | w= 11 | w= 12 | ...
-----------------------------------------------------------------------------------------------------------------------------
Base (0, 0)        |     0 |     0 |     0 |     0 |     0 |     0 |     0 |     0 |     0 |     0 |     0 |     0 |     0
PPKG-0013 (6kg, 15 |     0 |     0 |     0 |     0 |     0 |     0 |   159 |   159 |   159 |   159 |   159 |   159 |   159
PPKG-0009 (3kg, 15 |     0 |     0 |     0 |   153 |   153 |   153 |   159 |   159 |   159 |   312 |   312 |   312 |   312
PPKG-0010 (2kg, 13 |     0 |     0 |   134 |   153 |   153 |   287 |   287 |   287 |   293 |   312 |   312 |   446 |   446
PPKG-0004 (8kg, 79 |     0 |     0 |   134 |   153 |   153 |   287 |   287 |   287 |   293 |   312 |   312 |   446 |   446
PPKG-0002 (3kg, 89 |     0 |     0 |   134 |   153 |   153 |   287 |   287 |   287 |   376 |   376 |   376 |   446 |   446
...
```

### Result:
- Optimal parcels selected: 8
- Packed weight: 35 kg / 35 kg (**100.0% utilization**)
- Total value achieved: 762 (Theoretical fractional upper bound: 777.75)
