#!/usr/bin/env python3
"""Tests for the quotient-Euclid static compiler budget gate."""

from __future__ import annotations

import unittest

import quotient_euclid_static_compiler as compiler


class QuotientEuclidStaticCompilerTests(unittest.TestCase):
    def test_current_sample_witnesses_both_direct_layouts_over_q_cap(self) -> None:
        report = compiler.layout_gate()
        self.assertEqual(report["scratch_cap"], 588)
        self.assertEqual(report["raw_layout"]["peak_qubits"], 1123)
        self.assertEqual(report["gamma_layout"]["peak_qubits"], 1316)
        self.assertFalse(report["raw_layout"]["fits_q"])
        self.assertFalse(report["gamma_layout"]["fits_q"])

    def test_historical_gate_ledger_is_conservative_and_over_budget(self) -> None:
        report = compiler.historical_cost_gate()
        self.assertGreater(report["optimistic_total_toffolis"], compiler.COMPONENT_T_CAP)
        self.assertGreater(report["gap_to_component_cap"], 400_000)
        self.assertFalse(report["fits_t"])

    def test_gate_nacks_only_the_static_transcript_compiler(self) -> None:
        report = compiler.run_gate()
        self.assertEqual(
            report["verdict"],
            "HARD_NACK_QUOTIENT_EUCLID_STATIC_TRANSCRIPT_COMPILER",
        )
        self.assertTrue(report["recurrence_remains_admitted"])
        self.assertEqual(report["next_grammar"], "ONLINE_TRANSPOSED_UNIT_ACTION")
        self.assertFalse(report["full_field_candidate"])
        self.assertFalse(report["authority"]["provider"])
        self.assertFalse(report["authority"]["push"])
        self.assertFalse(report["authority"]["submission"])


if __name__ == "__main__":
    unittest.main()
