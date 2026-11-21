"""
Dynamic Programming 0/1 Knapsack algorithm for optimal courier box filling.
Maximizes total delivery priority/value subject to maximum van/box weight capacity.
"""

import time
from typing import List, Tuple, Dict, Any, Optional
from ..models import Parcel, PackingResult


def knapsack_01_dp_with_table(parcels: List[Parcel], capacity: int) -> PackingResult:
    """
    Standard 2D Dynamic Programming 0/1 Knapsack with explicit DP table construction
    and full backtracking for parcel selection.

    Time Complexity: O(N * W)
    Space Complexity: O(N * W)

    Table definition:
      dp[i][w] = maximum total parcel value attainable using a subset of the first i parcels
                 with an accumulated weight not exceeding w.
    """
    t0 = time.perf_counter()
    n = len(parcels)
    W = capacity

    # dp[i][w]: (n + 1) rows x (W + 1) columns
    dp = [[0] * (W + 1) for _ in range(n + 1)]

    # Fill DP Table
    for i in range(1, n + 1):
        p = parcels[i - 1]
        w_i = p.weight
        v_i = p.value
        for w in range(W + 1):
            if w_i <= w:
                # Decision: either exclude parcel i or include parcel i
                dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - w_i] + v_i)
            else:
                # Parcel i is too heavy for current sub-capacity w
                dp[i][w] = dp[i - 1][w]

    total_value = dp[n][W]

    # Backtracking to identify selected items
    selected_indices = []
    curr_w = W
    for i in range(n, 0, -1):
        if dp[i][curr_w] != dp[i - 1][curr_w]:
            # Parcel i - 1 was included in the optimal solution
            selected_indices.append(i - 1)
            curr_w -= parcels[i - 1].weight

    selected_indices.reverse()
    selected_set = set(selected_indices)

    selected_parcels = [parcels[i] for i in selected_indices]
    unselected_parcels = [parcels[i] for i in range(n) if i not in selected_set]
    total_weight = sum(p.weight for p in selected_parcels)

    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    return PackingResult(
        selected_parcels=selected_parcels,
        unselected_parcels=unselected_parcels,
        total_weight=total_weight,
        total_value=total_value,
        capacity=capacity,
        dp_table=dp,
        execution_time_ms=elapsed_ms
    )


def knapsack_01_dp(parcels: List[Parcel], capacity: int) -> PackingResult:
    """
    Wrapper for 0/1 Knapsack DP box filling.
    Uses 2D DP with table and backtracking.
    """
    return knapsack_01_dp_with_table(parcels, capacity)


def format_dp_table_sample(dp: List[List[int]], parcels: List[Parcel], max_cols: int = 15, max_rows: int = 12) -> str:
    """
    Formats the DP table into an ASCII representation for evidence / report demonstration.
    """
    if not dp or not dp[0]:
        return "Empty DP Table"

    num_rows = min(len(dp), max_rows + 1)
    num_cols = min(len(dp[0]), max_cols + 1)

    lines = []
    # Header
    col_headers = [f"w={w:>3}" for w in range(num_cols)]
    lines.append(f"{'Item (wt,val)':<18} | " + " | ".join(col_headers) + (" | ..." if len(dp[0]) > num_cols else ""))
    lines.append("-" * (21 + (num_cols * 8)))

    # Row 0: Base case
    row0_vals = [f"{dp[0][w]:>5}" for w in range(num_cols)]
    lines.append(f"{'Base (0, 0)':<18} | " + " | ".join(row0_vals))

    for i in range(1, num_rows):
        p = parcels[i - 1]
        label = f"P{p.parcel_id} ({p.weight}kg, {p.value}v)"[:18]
        row_vals = [f"{dp[i][w]:>5}" for w in range(num_cols)]
        lines.append(f"{label:<18} | " + " | ".join(row_vals))

    if len(dp) > num_rows:
        lines.append(f"... ({len(dp) - num_rows} more parcel rows truncated) ...")

    return "\n".join(lines)


def fractional_knapsack_greedy(parcels: List[Parcel], capacity: int) -> Tuple[float, List[Tuple[Parcel, float]]]:
    """
    Greedy Fractional Knapsack algorithm (Upper Bound reference).
    Sorts by value/weight ratio and greedily consumes capacity.
    """
    sorted_parcels = sorted(parcels, key=lambda p: p.value / max(1, p.weight), reverse=True)
    curr_weight = 0.0
    total_value = 0.0
    allocation = []

    for p in sorted_parcels:
        if curr_weight + p.weight <= capacity:
            allocation.append((p, 1.0))
            curr_weight += p.weight
            total_value += p.value
        else:
            remain = capacity - curr_weight
            if remain > 0:
                fraction = remain / p.weight
                allocation.append((p, fraction))
                total_value += p.value * fraction
                curr_weight = capacity
            break

    return total_value, allocation
