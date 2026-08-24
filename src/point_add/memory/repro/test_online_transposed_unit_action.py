#!/usr/bin/env python3
"""Tests for the online transposed quotient-action collision gate."""

from __future__ import annotations

import unittest

import online_transposed_unit_action as action


class OnlineTransposedUnitActionTests(unittest.TestCase):
    def test_normalized_matrices_have_exact_bezout_shape(self) -> None:
        for prime in (31, 61, 127, 251):
            for multiplier in range(1, prime):
                matrix = action.normalized_matrix(prime, multiplier)
                self.assertEqual(matrix["reduced_row"], (1, 0))
                self.assertEqual(
                    matrix["k"] * multiplier - matrix["r"] * prime,
                    1,
                )
                self.assertEqual(
                    matrix["rows"],
                    ((-matrix["r"], multiplier), (matrix["k"], -prime)),
                )

    def test_online_row_yields_exact_product_for_every_small_pair(self) -> None:
        for prime in (31, 61, 127, 251):
            report = action.case_report(prime)
            self.assertEqual(report["product_failures"], 0)
            self.assertEqual(report["matrix_failures"], 0)

    def test_separable_seed_lines_have_multiple_directions(self) -> None:
        for prime in (31, 61, 127, 251):
            report = action.case_report(prime)
            self.assertGreater(report["distinct_direction_ratios"], 1)
            self.assertTrue(report["universal_collision_proved"])

    def test_intersection_witness_works_for_arbitrary_seed_values(self) -> None:
        prime = 251
        t1, t2 = action.first_nonparallel_pair(prime)
        for h1, h2 in ((0, 0), (1, 1), (t1, t2), (t1 * t1, t2 * t2)):
            witness = action.line_intersection(prime, t1, h1, t2, h2)
            self.assertNotEqual(witness["input_1"], witness["input_2"])
            self.assertEqual(witness["output_1"], witness["output_2"])

    def test_alternate_final_expansion_does_not_remove_obstruction(self) -> None:
        for prime in (31, 61, 127, 251):
            report = action.alternate_expansion_report(prime)
            self.assertEqual(report["product_failures"], 0)
            self.assertGreater(report["distinct_direction_ratios"], 1)

    def test_gate_closes_only_the_separable_seed_grammar(self) -> None:
        report = action.run_gate()
        self.assertEqual(
            report["verdict"],
            "HARD_NACK_ONLINE_TRANSPOSED_SEPARABLE_SEED",
        )
        self.assertEqual(
            report["next_grammar"],
            "NONLINEAR_COUPLED_TRANSPOSED_ACTION",
        )
        self.assertFalse(report["full_field_candidate"])
        self.assertFalse(report["authority"]["provider"])
        self.assertFalse(report["authority"]["push"])
        self.assertFalse(report["authority"]["submission"])


if __name__ == "__main__":
    unittest.main()
