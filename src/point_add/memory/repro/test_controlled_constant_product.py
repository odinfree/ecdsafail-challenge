#!/usr/bin/env python3
"""Tests for the controlled-constant product-code gate."""

from __future__ import annotations

import unittest

import controlled_constant_product as gate


class ControlledConstantProductTests(unittest.TestCase):
    def test_four_state_rectangle_has_exact_nonzero_residual(self) -> None:
        witness = gate.rectangle_witness(31, 0, 1, 2)
        self.assertEqual(witness["values"], [4, 5, 6, 7])
        self.assertEqual(witness["residual"], 29)
        self.assertEqual(witness["expected_residual"], 29)
        self.assertTrue(gate.replay_rectangle_witness(31, witness))

    def test_every_two_window_partition_is_rejected_with_clean_controls(self) -> None:
        report = gate.case_report(31)
        self.assertEqual(report["partitions_tested"], (1 << (5 - 1)) - 1)
        self.assertEqual(report["target_zero_residuals"], 0)
        self.assertEqual(report["synthetic_control_failures"], 0)
        self.assertTrue(report["all_partitions_rejected"])
        for witness in report["sample_witnesses"]:
            self.assertTrue(gate.replay_rectangle_witness(31, witness))

    def test_secp_symbolic_certificate_covers_every_bit_pair(self) -> None:
        report = gate.secp_symbolic_certificate()
        self.assertTrue(report["all_checks_passed"])
        self.assertEqual(report["bit_pairs_checked"], 256 * 255 // 2)
        self.assertEqual(report["invalid_context_values"], 0)
        self.assertEqual(report["zero_residuals"], 0)
        self.assertTrue(report["one_window_is_exponential"])

    def test_gate_rejects_independent_window_product_codes(self) -> None:
        report = gate.run_gate((31, 61, 127, 251))
        self.assertEqual(
            report["verdict"], "HARD_NACK_CONTROLLED_CONSTANT_PRODUCT_CODE"
        )
        self.assertTrue(report["all_toy_partitions_rejected"])
        self.assertTrue(report["production_all_bit_pairs_interact"])
        self.assertEqual(report["next_grammar"], "OVERLAPPING_NONLOCAL_UNIT_ACTION")
        self.assertFalse(report["authority"]["provider"])
        self.assertFalse(report["authority"]["submission"])


if __name__ == "__main__":
    unittest.main()
