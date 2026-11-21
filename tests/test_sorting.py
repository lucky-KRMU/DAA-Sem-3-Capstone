"""Unit tests for sorting algorithms and prioritization logic."""

import unittest
from src.models import Parcel
from src.algorithms.sorting import merge_sort, quick_sort, sort_parcels, compare_sorting_algorithms


class TestSortingAlgorithms(unittest.TestCase):

    def setUp(self):
        self.parcels = [
            Parcel("P1", "C1", 2, weight=5, deadline_min=120, priority=1, value=50),
            Parcel("P2", "C2", 3, weight=3, deadline_min=60,  priority=3, value=120),
            Parcel("P3", "C3", 1, weight=8, deadline_min=60,  priority=2, value=80),
            Parcel("P4", "C4", 4, weight=2, deadline_min=180, priority=4, value=200),
            Parcel("P5", "C5", 2, weight=4, deadline_min=60,  priority=3, value=150)
        ]

    def test_merge_sort_numeric(self):
        nums = [9, 3, 7, 1, 5, 2, 8, 4, 6]
        sorted_nums = merge_sort(nums)
        self.assertEqual(sorted_nums, [1, 2, 3, 4, 5, 6, 7, 8, 9])

    def test_quick_sort_numeric(self):
        nums = [5, 2, 8, 2, 5, 1, 9, 3, 8]
        sorted_nums = quick_sort(nums)
        self.assertEqual(sorted_nums, [1, 2, 2, 3, 5, 5, 8, 8, 9])

    def test_deadline_priority_sorting(self):
        # Earliest deadline first; if equal, higher priority first
        sorted_p = sort_parcels(self.parcels, criterion="deadline_priority", algorithm="merge_sort")
        # 60m deadlines: P2 (prio 3, val 120), P5 (prio 3, val 150), P3 (prio 2, val 80)
        # P5 has higher value so comes before P2
        self.assertEqual(sorted_p[0].parcel_id, "P5")
        self.assertEqual(sorted_p[1].parcel_id, "P2")
        self.assertEqual(sorted_p[2].parcel_id, "P3")
        self.assertEqual(sorted_p[3].parcel_id, "P1")  # 120m
        self.assertEqual(sorted_p[4].parcel_id, "P4")  # 180m

    def test_sorting_algorithms_equivalence(self):
        comp = compare_sorting_algorithms(self.parcels, criterion="deadline_priority")
        self.assertTrue(comp["merge_sort"]["is_correct"])
        self.assertTrue(comp["quick_sort"]["is_correct"])


if __name__ == "__main__":
    unittest.main()
