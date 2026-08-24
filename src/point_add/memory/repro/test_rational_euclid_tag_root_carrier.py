#!/usr/bin/env python3
"""Tests for the rational Euclid-tag root-carrier gate."""

from __future__ import annotations

import unittest

import rational_euclid_tag_root_carrier as carrier


class RationalEuclidTagRootCarrierTests(unittest.TestCase):
    def test_polynomial_decoder_first_appears_at_interpolation_capacity(self) -> None:
        expected = {
            31: ((4, 15, 15, 16), (5, 21, 18, 18)),
            61: ((9, 55, 55, 56), (10, 66, 58, 58)),
            127: ((14, 120, 120, 121), (15, 136, 124, 124)),
            251: ((20, 231, 231, 232), (21, 253, 249, 249)),
            509: ((30, 496, 496, 497), (31, 528, 507, 507)),
        }
        for prime, pair in expected.items():
            report = carrier.polynomial_case_report(prime)
            rejected, admitted = report["last_rejected"], report["first_admitted"]
            self.assertEqual(
                (
                    rejected["degree"],
                    rejected["monomials"],
                    rejected["feature_rank"],
                    rejected["augmented_rank"],
                ),
                pair[0],
            )
            self.assertEqual(
                (
                    admitted["degree"],
                    admitted["monomials"],
                    admitted["feature_rank"],
                    admitted["augmented_rank"],
                ),
                pair[1],
            )
            self.assertEqual(report["first_capacity_degree"], admitted["degree"])
            self.assertTrue(report["interpolation_capacity_only"])

    def test_rational_nullspace_first_appears_at_dimensional_capacity(self) -> None:
        expected = {
            31: ((2, 6, 12, 12, 0), (3, 10, 20, 18, 2)),
            61: ((6, 28, 56, 56, 0), (7, 36, 72, 58, 14)),
            127: ((9, 55, 110, 110, 0), (10, 66, 132, 124, 8)),
            251: ((14, 120, 240, 240, 0), (15, 136, 272, 249, 23)),
            509: ((21, 253, 506, 506, 0), (22, 276, 552, 507, 45)),
        }
        for prime, pair in expected.items():
            report = carrier.rational_case_report(prime)
            rejected, possible = report["last_rejected"], report["first_possible"]
            self.assertEqual(
                (
                    rejected["degree"],
                    rejected["monomials"],
                    rejected["columns"],
                    rejected["rank"],
                    rejected["nullity"],
                ),
                pair[0],
            )
            self.assertEqual(
                (
                    possible["degree"],
                    possible["monomials"],
                    possible["columns"],
                    possible["rank"],
                    possible["nullity"],
                ),
                pair[1],
            )
            self.assertEqual(report["first_capacity_degree"], possible["degree"])
            self.assertTrue(report["dimensional_capacity_only"])
            self.assertFalse(report["denominator_certified_nonzero"])

    def test_gate_closes_total_degree_field_maps_only(self) -> None:
        report = carrier.run_gate()
        self.assertEqual(
            report["verdict"],
            "HARD_NACK_RATIONAL_EUCLID_TAG_ROOT_CARRIER_INTERPOLATION_ONLY",
        )
        self.assertEqual(report["next_grammar"], "BOOLEAN_EUCLID_TAG_ROOT_CARRIER")
        self.assertFalse(report["full_field_candidate"])
        self.assertTrue(all(not allowed for allowed in report["authority"].values()))


if __name__ == "__main__":
    unittest.main()
