#!/usr/bin/env python3
"""Tests for the curve-supported online constant-seed gate."""

from __future__ import annotations

import unittest

import curve_support_online_constant_seed as seed


class CurveSupportOnlineConstantSeedTests(unittest.TestCase):
    def test_every_classical_point_has_an_exact_toy_seed_certificate(self) -> None:
        expected = {
            31: (20, 360, 1),
            61: (60, 3480, 5),
            127: (126, 15624, 7),
            251: (251, 62500, 0),
            509: (509, 258064, 0),
            1021: (1035, 1069158, 8),
            2039: (2039, 4153444, 0),
            4093: (4170, 17380560, 10),
        }
        for prime, values in expected.items():
            report = seed.all_classical_points_report(prime)
            self.assertEqual(
                (
                    report["classical_points"],
                    report["support_states"],
                    report["maximum_absolute_seed"],
                ),
                values,
            )
            self.assertEqual(report["unavoidable_collision_points"], 0)
            self.assertEqual(report["injectivity_failures"], 0)
            self.assertEqual(report["product_failures"], 0)
            self.assertEqual(report["uncertified_points"], 0)

    def test_cube_permutation_fields_need_no_tag_seed(self) -> None:
        for prime in (251, 509, 2039):
            report = seed.all_classical_points_report(prime)
            self.assertEqual(prime % 3, 2)
            self.assertEqual(report["maximum_forbidden_constants"], 0)
            self.assertEqual(report["zero_seed_points"], report["classical_points"])

    def test_first_point_has_no_global_affine_postdecoder(self) -> None:
        selected = {31: 0, 61: 5, 127: 1, 251: 0, 509: 0, 1021: -2, 2039: 0, 4093: 1}
        for prime, constant in selected.items():
            report = seed.first_point_affine_decoder_report(prime)
            self.assertEqual(report["selected_seed_signed"], constant)
            self.assertFalse(report["affine_decoder_exists"])
            self.assertEqual(report["product_failures"], 0)
            self.assertEqual(report["injectivity_failures"], 0)

    def test_literal_secp_cube_root_is_over_budget_before_multiplies(self) -> None:
        report = seed.secp_cube_root_cost_report()
        self.assertEqual(report["prime_mod_9"], 7)
        self.assertEqual(report["subgroup_order_mod_3"], 2)
        self.assertEqual(report["root_exponent_bits"], 253)
        self.assertEqual(report["root_exponent_popcount"], 127)
        self.assertEqual(report["binary_squarings"], 252)
        self.assertAlmostEqual(report["square_only_t"], 13828976.28, places=2)
        self.assertGreater(report["budget_multiple"], 41)
        self.assertEqual(
            report["verdict"],
            "HARD_NACK_CURRENT_SQUARE_CUBIC_DECOMPRESS",
        )

    def test_gate_admits_injectivity_but_closes_natural_decoders(self) -> None:
        report = seed.run_gate()
        self.assertEqual(
            report["identity_verdict"],
            "ADMIT_CURVE_SUPPORT_CONSTANT_SEED_INJECTIVITY_TOY_ONLY",
        )
        self.assertEqual(
            report["affine_decoder_verdict"],
            "HARD_NACK_AFFINE_CONSTANT_SEED_POSTDECODER",
        )
        self.assertEqual(
            report["cube_root_verdict"],
            "HARD_NACK_CURRENT_SQUARE_CUBIC_DECOMPRESS",
        )
        self.assertEqual(
            report["verdict"],
            "HARD_NACK_CURVE_SUPPORT_CONSTANT_SEED_NATURAL_DECODERS",
        )
        self.assertEqual(report["next_grammar"], "GLV_TRIT_TAG_DECODER")
        self.assertFalse(report["full_field_candidate"])
        self.assertTrue(all(not allowed for allowed in report["authority"].values()))


if __name__ == "__main__":
    unittest.main()
