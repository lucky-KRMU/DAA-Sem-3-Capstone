"""Unit tests for TSP approximation and 2-opt refinement."""

import unittest
from src.algorithms.tsp import solve_tsp_nearest_neighbor, two_opt_optimize, solve_tsp_brute_force, tour_length


class TestTSP(unittest.TestCase):

    def setUp(self):
        # Metric distance matrix for 4 nodes: 0, 1, 2, 3
        # In Euclidean line: 0 at 0, 1 at 2, 2 at 5, 3 at 9
        coords = {0: 0, 1: 2, 2: 5, 3: 9}
        self.dist_matrix = {}
        for u, xu in coords.items():
            for v, xv in coords.items():
                self.dist_matrix[(u, v)] = float(abs(xu - xv))

    def test_tsp_brute_force_matches_optimum(self):
        stops = [1, 2, 3]
        best_tour, best_dist = solve_tsp_brute_force(0, stops, self.dist_matrix)
        # Optimal tour from 0 visiting 1, 2, 3 and returning to 0:
        # Distance = 0 -> 1 -> 2 -> 3 -> 0 = 2 + 3 + 4 + 9 = 18.0
        self.assertEqual(best_dist, 18.0)
        self.assertEqual(best_tour[0], 0)
        self.assertEqual(best_tour[-1], 0)

    def test_2opt_improves_or_matches_nn(self):
        stops = [1, 2, 3]
        nn_tour, nn_dist = solve_tsp_nearest_neighbor(0, stops, self.dist_matrix)
        opt_tour, opt_dist, _ = two_opt_optimize(nn_tour, self.dist_matrix)
        self.assertLessEqual(opt_dist, nn_dist)


if __name__ == "__main__":
    unittest.main()
