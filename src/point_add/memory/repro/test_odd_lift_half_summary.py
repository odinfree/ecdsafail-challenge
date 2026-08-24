#!/usr/bin/env python3
"""Tests for the exact odd-lift half-word summary gate."""

from __future__ import annotations

import unittest

import odd_lift_half_summary as gate


class OddLiftHalfSummaryTests(unittest.TestCase):
    def test_balanced_toy_census_reaches_both_diversity_ceilings(self) -> None:
        for prime in (31, 61, 127, 251):
            report = gate.case_report(prime)
            self.assertEqual(report["low_output"]["max_diversity"], 1 << report["cut"])
            self.assertEqual(report["high_output"]["max_diversity"], 1 << report["cut"])
            self.assertEqual(report["low_output"]["summary_bits"], report["cut"])
            self.assertEqual(report["high_output"]["summary_bits"], report["cut"])
            self.assertEqual(report["positive_control_summary_bits"], 0)
            for direction in ("low_output", "high_output"):
                self.assertTrue(gate.replay_diversity_witness(prime, direction, report[direction]))

    def test_secp_symbolic_certificate_is_exact_and_linear(self) -> None:
        report = gate.secp_symbolic_certificate()
        self.assertTrue(report["all_integer_checks_passed"])
        self.assertEqual(report["low_output"]["diversity"], 1 << 128)
        self.assertEqual(report["low_output"]["summary_bits"], 128)
        self.assertEqual(report["high_output"]["summary_bits_lower_bound"], 96)
        self.assertEqual(report["high_output"]["fiber_size_upper_bound"], (1 << 32) + 978)
        self.assertGreater(report["high_output"]["legal_family_lower_bound"], 1 << 127)

    def test_multiscale_gate_rejects_sublinear_half_summary(self) -> None:
        report = gate.run_gate((31, 61, 127, 251))
        self.assertEqual(report["verdict"], "HARD_NACK_ODD_LIFT_HALF_SUMMARY")
        self.assertTrue(report["toy_balanced_ceilings_reached"])
        self.assertTrue(report["production_linear_bounds_proved"])
        self.assertEqual(report["next_grammar"], "NONLOCAL_INTERLEAVED_UNIT_ACTION")
        self.assertFalse(report["authority"]["provider"])
        self.assertFalse(report["authority"]["submission"])


if __name__ == "__main__":
    unittest.main()
