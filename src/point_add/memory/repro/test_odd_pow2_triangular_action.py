#!/usr/bin/env python3
"""Tests for the odd power-of-two triangular unit action."""

from __future__ import annotations

import unittest

import odd_pow2_triangular_action as action


class OddPow2TriangularActionTests(unittest.TestCase):
    def test_exhaustive_small_widths_match_multiplication(self) -> None:
        for width in range(1, 10):
            report = action.exhaustive_width_report(width)
            self.assertEqual(report["forward_failures"], 0)
            self.assertEqual(report["inverse_failures"], 0)
            self.assertEqual(report["preserved_multiplier_failures"], 0)

    def test_even_multiplier_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            action.forward(2, 3, 4)

    def test_resource_formula_at_production_width(self) -> None:
        resource = action.resource_report(256)
        self.assertEqual(resource["and_toffolis"], 32_640)
        self.assertEqual(resource["adder_toffolis"], 32_385)
        self.assertEqual(resource["total_toffolis"], 65_025)
        self.assertEqual(resource["peak_qubits"], 1_022)
        self.assertTrue(resource["inside_component_budget"])

    def test_gate_admits_only_the_pow2_subprimitive(self) -> None:
        report = action.run_gate()
        self.assertEqual(report["verdict"], "ADMIT_ODD_POW2_TRIANGULAR_SUBPRIMITIVE")
        self.assertEqual(report["remaining_blocker"], "PSEUDO_MERSENNE_NONLOCAL_FOLD")
        self.assertFalse(report["full_field_candidate"])
        self.assertFalse(report["authority"]["provider"])
        self.assertFalse(report["authority"]["submission"])


if __name__ == "__main__":
    unittest.main()
