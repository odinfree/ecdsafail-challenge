#!/usr/bin/env python3
"""Tests for the support-trace root-selector gate."""

from __future__ import annotations

import unittest

import support_trace_root_selector as selector


class SupportTraceRootSelectorTests(unittest.TestCase):
    def test_exact_branch_selector_budgets_grow(self) -> None:
        expected = {
            31: (3, ("alternating_sum", 3)),
            61: (3, ("maximum", 1, "weighted_sum", 2)),
            127: (4, ("alternating_sum", 3, "last", 1)),
            1021: (8, ("alternating_sum", 6, "last", 2)),
            4093: (10, ("alternating_sum", 3, "k", 7)),
        }
        for prime, (bits, scheme) in expected.items():
            report = selector.exact_branch_case_report(prime)
            self.assertEqual(report["minimum_tag_bits"], bits)
            self.assertEqual(tuple(report["winning_scheme"]), scheme)
            self.assertEqual(report["winning_collisions"], 0)
            self.assertEqual(report["curve_fiber_failures"], 0)

    def test_piecewise_affine_decoder_needs_a_full_word_tag(self) -> None:
        expected = {
            31: (5, ("alternating_sum", 3, "maximum", 2)),
            61: (6, ("k", 6)),
            127: (7, ("k", 7)),
            251: (8, ("k", 8)),
            509: (9, ("k", 9)),
            1021: (10, ("k", 10)),
            4093: (12, ("k", 12)),
        }
        for prime, (bits, scheme) in expected.items():
            report = selector.affine_decoder_case_report(prime)
            self.assertEqual(report["minimum_tag_bits"], bits)
            self.assertEqual(tuple(report["winning_scheme"]), scheme)
            self.assertEqual(bits, report["width"])
            self.assertTrue(report["full_word_tag_only"])

    def test_production_sample_branch_tag_is_not_a_certificate(self) -> None:
        report = selector.production_sample_report()
        self.assertEqual(report["sample_count"], 10_000)
        self.assertEqual(report["draws"], 20_143)
        self.assertEqual(
            report["sample_sha256"],
            "d80ea7aaa4ab582b497314c44fb2e948bbe191637fa9d442f83a0f8c7b71a570",
        )
        self.assertEqual(report["minimum_tag_bits"], 13)
        self.assertEqual(tuple(report["winning_scheme"]), ("sum", 7, "maximum", 6))
        self.assertEqual(report["winning_collisions"], 0)
        self.assertEqual(
            [row["collisions"] for row in report["winning_collision_curve"]],
            [6877, 3594, 1815, 881, 434, 203, 96, 45, 18, 9, 4, 0],
        )
        self.assertFalse(report["exhaustive_production_certificate"])

    def test_gate_admits_only_sample_label_and_closes_natural_decoder(self) -> None:
        report = selector.run_gate()
        self.assertEqual(
            report["branch_identity_verdict"],
            "ADMIT_TRACE_BRANCH_TAG_SAMPLE_ONLY",
        )
        self.assertEqual(
            report["verdict"],
            "HARD_NACK_SUPPORT_TRACE_ROOT_SELECTOR_NATURAL_TAGS",
        )
        self.assertEqual(report["next_grammar"], "TRACE_CONDITIONED_COUPLED_SEED")
        self.assertFalse(report["full_field_candidate"])
        self.assertTrue(all(not allowed for allowed in report["authority"].values()))


if __name__ == "__main__":
    unittest.main()
