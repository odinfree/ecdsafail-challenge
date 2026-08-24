#!/usr/bin/env python3
"""Tests for the Boolean Euclid-tag root-carrier gate."""

from __future__ import annotations

import unittest

import boolean_euclid_tag_root_carrier as carrier


class BooleanEuclidTagRootCarrierTests(unittest.TestCase):
    def test_support_minimum_degree_hits_interpolation_capacity(self) -> None:
        expected = {
            31: (18, 2, 56, 9, 10),
            61: (58, 2, 79, 13, 14),
            127: (124, 3, 470, 106, 107),
            251: (249, 3, 697, 137, 138),
            509: (507, 3, 988, 172, 173),
        }
        for prime, values in expected.items():
            support, degree, monomials, previous_rank, previous_augmented = values
            report = carrier.support_degree_case_report(prime)
            self.assertEqual(report["support_states"], support)
            self.assertEqual(report["first_capacity_degree"], degree)
            self.assertEqual(report["capacity_monomials"], monomials)
            self.assertEqual(report["capacity_feature_rank"], support)
            self.assertEqual(
                {bit["minimum_degree"] for bit in report["output_bits"]},
                {degree},
            )
            self.assertEqual(
                {bit["preceding_feature_rank"] for bit in report["output_bits"]},
                {previous_rank},
            )
            self.assertEqual(
                {bit["preceding_augmented_rank"] for bit in report["output_bits"]},
                {previous_augmented},
            )
            self.assertTrue(report["interpolation_capacity_only"])

    def test_canonical_zero_extension_is_high_degree_and_dense(self) -> None:
        expected = {
            31: ([9, 9, 9, 9, 9], [144, 166, 140, 110, 146]),
            61: ([11, 11, 11, 11, 11, 11], [1904, 1758, 1236, 1242, 1854, 1734]),
            127: ([13, 13, 13, 13, 13, 13, 13], [4756, 4112, 4734, 4516, 4578, 5148, 5116]),
            251: ([15, 15, 15, 16, 16, 15, 16, 15], [19104, 21192, 19684, 19512, 21416, 20360, 20878, 21022]),
            509: ([18, 17, 17, 17, 17, 18, 18, 18, 17], [66002, 70928, 64964, 69468, 69246, 64660, 64260, 67950, 62348]),
        }
        for prime, (degrees, counts) in expected.items():
            report = carrier.zero_extension_case_report(prime)
            self.assertEqual(report["anf_degrees"], degrees)
            self.assertEqual(report["coefficient_counts"], counts)
            self.assertEqual(report["maximum_degree"], max(degrees))
            self.assertEqual(report["maximum_input_degree"], 2 * prime.bit_length())

    def test_gate_closes_only_natural_anf_decoder(self) -> None:
        report = carrier.run_gate()
        self.assertEqual(
            report["verdict"],
            "HARD_NACK_BOOLEAN_EUCLID_TAG_ROOT_CARRIER_NATURAL_ANF",
        )
        self.assertEqual(report["next_grammar"], "SUPPORT_TRACE_ROOT_SELECTOR")
        self.assertFalse(report["arbitrary_factored_boolean_circuits_closed"])
        self.assertFalse(report["full_field_candidate"])
        self.assertTrue(all(not allowed for allowed in report["authority"].values()))


if __name__ == "__main__":
    unittest.main()
