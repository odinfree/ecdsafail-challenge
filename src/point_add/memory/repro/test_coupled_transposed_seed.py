#!/usr/bin/env python3
"""Tests for the coupled online-transposition seed gate."""

from __future__ import annotations

import unittest

import coupled_transposed_seed as seed


class CoupledTransposedSeedTests(unittest.TestCase):
    def test_orientation_is_normalized_to_positive_one(self) -> None:
        for prime in (31, 61, 127, 251):
            for multiplier in range(1, prime):
                matrix = seed.orientation_one_matrix(prime, multiplier)
                self.assertEqual(matrix["orientation"], 1)
                self.assertEqual(matrix["reduced_row"], (1, 0))

    def test_alignment_coefficient_forces_any_common_direction(self) -> None:
        for prime in (31, 61, 127):
            for common_direction in (0, 1, prime // 2):
                for multiplier in range(1, prime):
                    matrix = seed.orientation_one_matrix(prime, multiplier)
                    coefficient = seed.aligned_seed_coefficient(
                        prime,
                        multiplier,
                        common_direction,
                    )
                    actual = (
                        -matrix["r"] + matrix["k"] * coefficient
                    ) % prime
                    self.assertEqual(actual, common_direction * multiplier % prime)

    def test_ideal_coupled_seed_yields_exact_in_place_product(self) -> None:
        for prime in (31, 61, 127, 251):
            report = seed.case_report(prime)
            self.assertEqual(report["ideal_output_failures"], 0)
            self.assertEqual(report["orientation_failures"], 0)

    def test_cofactor_seed_polynomial_has_full_field_degree(self) -> None:
        expected_terms = {31: 15, 61: 32, 127: 65, 251: 127}
        for prime, terms in expected_terms.items():
            report = seed.case_report(prime)
            self.assertEqual(report["cofactor_polynomial_degree"], prime - 1)
            self.assertEqual(report["cofactor_polynomial_nonzero_terms"], terms)
            self.assertEqual(
                report["best_nonzero_terms_after_c_times_t_squared"],
                terms - 1,
            )
            self.assertEqual(report["best_degree_after_c_times_t_squared"], prime - 1)

    def test_interpolant_replays_every_input(self) -> None:
        for prime in (31, 61, 127):
            report = seed.case_report(prime)
            coefficients = tuple(report["cofactor_polynomial_coefficients"])
            for multiplier in range(prime):
                self.assertEqual(
                    seed.evaluate_polynomial(coefficients, multiplier, prime),
                    seed.cofactor_seed_value(prime, multiplier),
                )

    def test_gate_admits_identity_but_closes_bounded_degree_generator(self) -> None:
        report = seed.run_gate()
        self.assertEqual(
            report["identity_verdict"],
            "ADMIT_IDEAL_COUPLED_SEED_IDENTITY_ONLY",
        )
        self.assertEqual(
            report["verdict"],
            "HARD_NACK_BOUNDED_DEGREE_COUPLED_SEED",
        )
        self.assertEqual(
            report["next_grammar"],
            "ONLINE_COFACTOR_PRODUCT_RECURRENCE",
        )
        self.assertFalse(report["full_field_candidate"])
        self.assertFalse(report["authority"]["provider"])
        self.assertFalse(report["authority"]["submission"])


if __name__ == "__main__":
    unittest.main()
