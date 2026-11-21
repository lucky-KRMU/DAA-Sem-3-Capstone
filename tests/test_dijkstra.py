"""Unit tests for Dijkstra's shortest path algorithm."""

import unittest
from src.models import RoadGraph
from src.algorithms.dijkstra import dijkstra, reconstruct_path, compute_all_pairs_metric


class TestDijkstra(unittest.TestCase):

    def setUp(self):
        # 4-node graph:
        # 0 --(2)--> 1 --(3)--> 3
        # 0 --(6)--> 2 --(1)--> 3
        # 1 --(1)--> 2
        self.graph = RoadGraph(4)
        for i in range(4):
            self.graph.add_node(i, f"Node {i}")
        self.graph.add_edge(0, 1, 2.0, bidirectional=True)
        self.graph.add_edge(1, 3, 3.0, bidirectional=True)
        self.graph.add_edge(0, 2, 6.0, bidirectional=True)
        self.graph.add_edge(2, 3, 1.0, bidirectional=True)
        self.graph.add_edge(1, 2, 1.0, bidirectional=True)

    def test_shortest_paths_from_source(self):
        dists, preds = dijkstra(self.graph, 0)
        # Distances from 0:
        # To 0: 0
        # To 1: 2
        # To 2: 0->1->2 = 2+1 = 3 (better than direct 6)
        # To 3: 0->1->2->3 = 2+1+1 = 4 (better than 0->1->3 = 5)
        self.assertEqual(dists[0], 0.0)
        self.assertEqual(dists[1], 2.0)
        self.assertEqual(dists[2], 3.0)
        self.assertEqual(dists[3], 4.0)

        path_to_3 = reconstruct_path(preds, target=3, source=0)
        self.assertEqual(path_to_3, [0, 1, 2, 3])

    def test_all_pairs_metric(self):
        dist_mat, path_mat, _ = compute_all_pairs_metric(self.graph, [0, 2, 3])
        self.assertEqual(dist_mat[(0, 3)], 4.0)
        self.assertEqual(dist_mat[(3, 0)], 4.0)
        self.assertEqual(dist_mat[(2, 3)], 1.0)


if __name__ == "__main__":
    unittest.main()
