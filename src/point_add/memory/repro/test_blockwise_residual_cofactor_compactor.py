#!/usr/bin/env python3
"""Tests for the blockwise residual cofactor-compactor gates."""

from __future__ import annotations

import unittest

import blockwise_residual_cofactor_compactor as compactor


class BlockwiseResidualCofactorCompactorTests(unittest.TestCase):
    def test_cross_determinant_is_the_product_at_every_residual_cut(self) -> None:
        for prime in (31, 61, 127, 251):
            report = compactor.identity_case_report(prime)
            self.assertEqual(report["checked_states"], prime * (prime - 1) * prime.bit_length())
            self.assertEqual(report["row_failures"], 0)
            self.assertEqual(report["determinant_failures"], 0)

    def test_free_parser_raw_prefix_still_misses_component_cap(self) -> None:
        report = compactor.production_prefix_floor_report()
        self.assertEqual(report["sample_count"], 10_000)
        self.assertEqual(report["cut_widths"], 255)
        self.assertEqual(report["minimum_worst_raw_q"], 1124)
        self.assertEqual(report["raw_minimizing_cut_widths"], (1, 2, 4, 5))
        self.assertEqual(report["raw_witness_sample_index"], 1973)
        self.assertEqual(report["raw_excess_over_component_cap_q"], 24)
        self.assertEqual(report["minimum_worst_gamma_q"], 1282)
        self.assertEqual(report["gamma_minimizing_cut_widths"], (255,))
        self.assertEqual(report["cut_32_worst_raw_q"], 1142)

    def test_code_free_prefix_collides_below_one_step_cut(self) -> None:
        expected_collisions = {
            31: (118, 22, 6, 0, 0),
            61: (538, 52, 24, 6, 0, 0),
            127: (3148, 748, 216, 32, 6, 0, 0),
            251: (14248, 4742, 964, 116, 34, 6, 0, 0),
        }
        for prime, expected in expected_collisions.items():
            report = compactor.code_free_case_report(prime)
            actual = tuple(case["collisions"] for case in report["cuts"])
            self.assertEqual(actual, expected)
            self.assertEqual(report["deepest_collision_free_shrink_bits"], 1)
            self.assertIsNotNone(report["representative_collision"])

    def test_minimum_fiber_rank_decoder_is_high_degree_and_dense(self) -> None:
        expected = {
            31: (2, 7, 3, 8, 7, 80, 256),
            61: (3, 7, 3, 10, 9, 384, 1024),
            127: (3, 15, 4, 11, 11, 672, 2048),
            251: (4, 15, 4, 13, 12, 2892, 8192),
            509: (4, 31, 5, 14, 14, 6104, 16384),
            1021: (5, 31, 5, 16, 15, 23496, 65536),
            2039: (5, 63, 6, 17, 16, 48392, 131072),
            4093: (6, 63, 6, 19, 19, 193812, 524288),
        }
        for prime, values in expected.items():
            report = compactor.rank_decoder_anf_report(prime)
            self.assertEqual(
                (
                    report["cut_width"],
                    report["max_fiber_size"],
                    report["rank_bits"],
                    report["variables"],
                    report["anf_degree"],
                    report["anf_density"],
                    report["truth_table_size"],
                ),
                values,
            )
            self.assertGreaterEqual(report["anf_degree"], report["variables"] - 1)
            self.assertGreater(report["anf_density"], report["truth_table_size"] // 4)

    def test_gate_admits_identity_and_closes_only_natural_codecs(self) -> None:
        report = compactor.run_gate()
        self.assertEqual(
            report["identity_verdict"],
            "ADMIT_PREFIX_CROSS_DETERMINANT_PRODUCT_IDENTITY_ONLY",
        )
        self.assertEqual(
            report["stored_prefix_verdict"],
            "HARD_NACK_STORED_PREFIX_Q_FLOOR",
        )
        self.assertEqual(
            report["code_free_verdict"],
            "HARD_NACK_QUOTIENT_FREE_PREFIX_COLLISION",
        )
        self.assertEqual(
            report["rank_decoder_verdict"],
            "HARD_NACK_ZERO_EXTENDED_RESIDUAL_RANK_DECODER",
        )
        self.assertEqual(
            report["verdict"],
            "HARD_NACK_BLOCKWISE_RESIDUAL_COFACTOR_COMPACTOR_NATURAL_CODECS",
        )
        self.assertFalse(report["universal_lower_bound"])
        self.assertFalse(report["full_field_candidate"])
        self.assertTrue(all(not allowed for allowed in report["authority"].values()))


if __name__ == "__main__":
    unittest.main()
