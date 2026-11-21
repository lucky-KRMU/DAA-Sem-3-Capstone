"""Integration tests for end-to-end Courier Optimization Pipeline."""

import unittest
from src.dataset_generator import load_dataset_json
from src.pipeline import CourierOptimizationPipeline


class TestPipeline(unittest.TestCase):

    def setUp(self):
        self.parcels, self.graph, _ = load_dataset_json("data/small_dataset.json")
        self.pipeline = CourierOptimizationPipeline(self.graph, depot_node=0)

    def test_pipeline_execution(self):
        capacity = 35
        result = self.pipeline.run(
            all_parcels=self.parcels,
            vehicle_capacity=capacity,
            sort_criterion="deadline_priority",
            sort_algorithm="merge_sort",
            use_two_opt=True
        )

        summary = result["summary"]
        packing = result["packing_result"]
        route = result["route_result"]

        # 1. Van capacity must never be exceeded
        self.assertLessEqual(packing.total_weight, capacity)

        # 2. Total value must be > 0
        self.assertGreater(packing.total_value, 0)

        # 3. Route must start and end at Depot (node 0)
        self.assertEqual(route.delivery_stops[0], 0)
        self.assertEqual(route.delivery_stops[-1], 0)

        # 4. All selected parcels' destinations must be visited in the tour
        visited_nodes = set(route.delivery_stops)
        for p in packing.selected_parcels:
            self.assertIn(p.destination_node, visited_nodes)

        # 5. Route distance must be positive
        self.assertGreater(route.total_distance, 0.0)


if __name__ == "__main__":
    unittest.main()
