"""Unit tests for Dynamic Programming 0/1 Knapsack."""

import unittest
from src.models import Parcel
from src.algorithms.knapsack import knapsack_01_dp, knapsack_01_dp_with_table, fractional_knapsack_greedy


class TestKnapsackAlgorithms(unittest.TestCase):

    def setUp(self):
        # Classic knapsack instance
        # Items: (wt=2, val=3), (wt=3, val=4), (wt=4, val=5), (wt=5, val=6)
        # Capacity = 5 -> Best: item 1 (wt 2, val 3) + item 2 (wt 3, val 4) = wt 5, val 7
        self.parcels = [
            Parcel("P1", "C1", 1, weight=2, deadline_min=60, priority=1, value=3),
            Parcel("P2", "C2", 2, weight=3, deadline_min=60, priority=2, value=4),
            Parcel("P3", "C3", 3, weight=4, deadline_min=60, priority=3, value=5),
            Parcel("P4", "C4", 4, weight=5, deadline_min=60, priority=4, value=6),
        ]

    def test_optimal_solution(self):
        result = knapsack_01_dp(self.parcels, capacity=5)
        self.assertEqual(result.total_value, 7)
        self.assertEqual(result.total_weight, 5)
        selected_ids = {p.parcel_id for p in result.selected_parcels}
        self.assertEqual(selected_ids, {"P1", "P2"})

    def test_zero_capacity(self):
        result = knapsack_01_dp(self.parcels, capacity=0)
        self.assertEqual(result.total_value, 0)
        self.assertEqual(result.total_weight, 0)
        self.assertEqual(len(result.selected_parcels), 0)

    def test_infinite_capacity(self):
        # All items fit
        result = knapsack_01_dp(self.parcels, capacity=50)
        self.assertEqual(result.total_value, 18)
        self.assertEqual(result.total_weight, 14)
        self.assertEqual(len(result.selected_parcels), 4)

    def test_fractional_upper_bound(self):
        frac_val, _ = fractional_knapsack_greedy(self.parcels, capacity=5)
        dp_result = knapsack_01_dp(self.parcels, capacity=5)
        # Fractional value must always be >= discrete 0/1 knapsack value
        self.assertGreaterEqual(frac_val, dp_result.total_value)


if __name__ == "__main__":
    unittest.main()
