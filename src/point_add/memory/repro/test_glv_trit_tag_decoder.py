#!/usr/bin/env python3
"""Tests for the GLV trit-tag decoder gates."""

from __future__ import annotations

import unittest

import glv_trit_tag_decoder as decoder


class GlvTritTagDecoderTests(unittest.TestCase):
    def test_relaxed_linear_seed_affine_decoder_system_is_inconsistent(self) -> None:
        for prime in decoder.TEST_PRIMES:
            report = decoder.linear_seed_affine_case_report(prime)
            self.assertEqual(report["feature_rank"], 5)
            self.assertEqual(report["augmented_rank"], 6)
            self.assertFalse(report["relaxed_affine_decoder_exists"])

    def test_selected_seed_has_no_linear_fractional_decoder(self) -> None:
        for prime in decoder.TEST_PRIMES:
            report = decoder.linear_fractional_case_report(prime)
            self.assertEqual(report["matrix_rank"], 6)
            self.assertEqual(report["nullity"], 0)
            self.assertFalse(report["linear_fractional_decoder_exists"])
            self.assertEqual(report["injectivity_failures"], 0)

    def test_glv_fibers_are_exact_three_root_orbits(self) -> None:
        for prime in (31, 61, 127, 1021, 4093):
            report = decoder.glv_orbit_case_report(prime)
            self.assertEqual(prime % 3, 1)
            self.assertNotEqual(report["beta"], 1)
            self.assertEqual(pow(report["beta"], 3, prime), 1)
            self.assertEqual(report["maximum_curve_y_fiber"], 3)
            self.assertEqual(report["orbit_failures"], 0)
            self.assertEqual(report["tagged_t_failures"], 0)

    def test_gate_closes_linear_tags_but_preserves_glv_interpretation(self) -> None:
        report = decoder.run_gate()
        self.assertEqual(
            report["linear_seed_verdict"],
            "HARD_NACK_LINEAR_SEED_AFFINE_POSTDECODER",
        )
        self.assertEqual(
            report["linear_fractional_verdict"],
            "HARD_NACK_CONSTANT_SEED_LINEAR_FRACTIONAL_POSTDECODER",
        )
        self.assertEqual(
            report["glv_identity_verdict"],
            "ADMIT_GLV_TRIT_INTERPRETATION_ONLY",
        )
        self.assertEqual(report["verdict"], "HARD_NACK_GLV_TRIT_LINEAR_TAG_DECODER")
        self.assertEqual(
            report["next_grammar"],
            "RATIONAL_EUCLID_TAG_ROOT_CARRIER",
        )
        self.assertFalse(report["full_field_candidate"])
        self.assertTrue(all(not allowed for allowed in report["authority"].values()))


if __name__ == "__main__":
    unittest.main()
