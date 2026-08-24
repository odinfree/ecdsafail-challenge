#!/usr/bin/env python3
"""Tests for the natural online-cofactor cleanup gates."""

from __future__ import annotations

import unittest

import online_cofactor_product_recurrence as cleanup


class OnlineCofactorProductRecurrenceTests(unittest.TestCase):
    def test_output_frame_garbage_matches_discarded_cofactor_word(self) -> None:
        for prime in (31, 61, 127, 251):
            for multiplier in range(1, prime):
                matrix = cleanup.seed.orientation_one_matrix(prime, multiplier)
                for value in range(prime):
                    product = multiplier * value % prime
                    self.assertEqual(
                        cleanup.output_frame_garbage(prime, multiplier, product),
                        matrix["r"] * value % prime,
                    )

    def test_zero_extended_alternating_phase_has_measured_dense_anf(self) -> None:
        expected = {
            31: (5, 10, 7, 254, 1024),
            61: (6, 42, 11, 1896, 4096),
            127: (7, 42, 14, 7394, 16384),
            251: (8, 170, 15, 31966, 65536),
        }
        for prime, values in expected.items():
            report = cleanup.phase_anf_report(prime)
            self.assertEqual(
                (
                    report["width"],
                    report["output_mask"],
                    report["anf_degree"],
                    report["anf_density"],
                    report["truth_table_size"],
                ),
                values,
            )
            self.assertGreaterEqual(report["anf_degree"], 2 * report["width"] - 3)
            self.assertGreater(report["anf_density"], report["truth_table_size"] // 5)

    def test_coherent_dual_row_exceeds_both_qubit_caps_before_controls(self) -> None:
        report = cleanup.dual_row_qubit_report(256)
        self.assertEqual(report["value_words"], 2)
        self.assertEqual(report["product_words"], 2)
        self.assertEqual(report["cancellation_words"], 2)
        self.assertEqual(report["total_words"], 6)
        self.assertEqual(report["field_word_floor_q"], 1536)
        self.assertEqual(report["excess_over_component_cap_q"], 436)
        self.assertEqual(report["excess_over_protected_peak_q"], 270)

    def test_gate_closes_only_the_two_natural_cleanup_grammars(self) -> None:
        report = cleanup.run_gate()
        self.assertEqual(
            report["coherent_dual_row_verdict"],
            "HARD_NACK_COHERENT_DUAL_ROW_Q_FLOOR",
        )
        self.assertEqual(
            report["measurement_cleanup_verdict"],
            "HARD_NACK_ZERO_EXTENDED_COFACTOR_MBUC",
        )
        self.assertEqual(
            report["verdict"],
            "HARD_NACK_ONLINE_COFACTOR_NATURAL_CLEANUPS",
        )
        self.assertEqual(
            report["next_grammar"],
            "BLOCKWISE_RESIDUAL_COFACTOR_COMPACTOR",
        )
        self.assertFalse(report["universal_lower_bound"])
        self.assertFalse(report["full_field_candidate"])
        self.assertTrue(all(not allowed for allowed in report["authority"].values()))


if __name__ == "__main__":
    unittest.main()
