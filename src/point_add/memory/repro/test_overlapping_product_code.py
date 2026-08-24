#!/usr/bin/env python3
"""Tests for the overlapping controlled-constant product-code gate."""

from __future__ import annotations

import unittest

import overlapping_product_code as gate


class OverlappingProductCodeTests(unittest.TestCase):
    def test_toy_transform_and_inverse_are_exact(self) -> None:
        report = gate.toy_case_report(31)
        self.assertEqual(report["active_bits"], 3)
        self.assertEqual(report["coefficient_count"], 8)
        self.assertEqual(report["reconstruction_failures"], 0)
        self.assertTrue(report["all_transform_controls_passed"])

    def test_sparse_synthetic_control_recovers_declared_support(self) -> None:
        report = gate.sparse_control_report(31, 3)
        self.assertEqual(report["coefficient_failures"], 0)
        self.assertEqual(report["reconstruction_failures"], 0)
        self.assertEqual(report["recovered_nonidentity_masks"], report["declared_masks"])

    def test_production_subcube_is_fully_dense(self) -> None:
        report = gate.production_subcube_report()
        self.assertTrue(report["all_checks_passed"])
        self.assertEqual(report["active_bits"], 19)
        self.assertEqual(report["coefficient_count"], 1 << 19)
        self.assertEqual(report["nonempty_nonidentity_coefficients"], (1 << 19) - 1)
        self.assertEqual(report["reconstruction_failures"], 0)
        self.assertEqual(len(report["coefficient_sha256"]), 64)

    def test_gate_rejects_literal_overlapping_factor_grammar(self) -> None:
        report = gate.run_gate((31, 61, 127, 251))
        self.assertEqual(report["verdict"], "HARD_NACK_OVERLAPPING_PRODUCT_CODE")
        self.assertTrue(report["production_subcube_fully_dense"])
        self.assertTrue(report["all_controls_passed"])
        self.assertEqual(report["next_grammar"], "JOINT_ARITHMETIC_UNIT_ACTION")
        self.assertFalse(report["authority"]["provider"])
        self.assertFalse(report["authority"]["submission"])


if __name__ == "__main__":
    unittest.main()
