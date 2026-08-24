#!/usr/bin/env python3
"""Tests for the exact quotient-Euclid field unit action."""

from __future__ import annotations

import unittest

import quotient_euclid_unit_action as action


class QuotientEuclidUnitActionTests(unittest.TestCase):
    def test_canonical_traces_reconstruct_every_small_denominator(self) -> None:
        for prime in (31, 61, 127, 251):
            for denominator in range(1, prime):
                trace = action.euclid_trace(prime, denominator)
                self.assertGreaterEqual(trace[-1], 2)
                self.assertEqual(
                    action.reconstruct_inputs(trace),
                    (prime, denominator),
                )

    def test_gamma_codec_round_trips_every_trace_through_width_14(self) -> None:
        for prime in action.CENSUS_PRIMES.values():
            for denominator in range(1, prime):
                trace = action.euclid_trace(prime, denominator)
                encoded = action.gamma_encode(trace)
                self.assertEqual(action.gamma_decode(encoded), trace)

    def test_exact_action_and_inverse_exhaust_small_fields(self) -> None:
        for prime in (31, 61, 127, 251):
            report = action.exhaustive_action_report(prime)
            self.assertEqual(report["forward_failures"], 0)
            self.assertEqual(report["inverse_failures"], 0)
            self.assertEqual(report["zero_companion_failures"], 0)

    def test_complete_small_census_stays_inside_observed_envelopes(self) -> None:
        report = action.small_width_census()
        self.assertEqual(tuple(report), tuple(range(5, 15)))
        for width, row in report.items():
            self.assertLess(row["max_quotient_payload_bits"], 2 * width)
            self.assertLess(row["max_gamma_bits"], 3 * width)
            self.assertLess(row["max_steps"], width + 3)

    def test_production_sample_has_large_transcript_margin(self) -> None:
        report = action.production_sample_report(10_000)
        self.assertEqual(report["sample_count"], 10_000)
        self.assertLess(report["max_steps"], action.LIVE_BINARY_ROUNDS)
        self.assertLess(report["max_quotient_payload_bits"], action.LIVE_BINARY_ROUNDS)
        self.assertLess(report["max_gamma_bits"], action.LIVE_BINARY_ROUNDS)
        self.assertGreater(report["max_quotient_bits"], 8)

    def test_gate_admits_only_the_recurrence(self) -> None:
        report = action.run_gate()
        self.assertEqual(
            report["verdict"],
            "ADMIT_QUOTIENT_EUCLID_RECURRENCE_ONLY",
        )
        self.assertEqual(
            report["remaining_blocker"],
            "STATIC_REVERSIBLE_TRANSCRIPT_COMPILER",
        )
        self.assertFalse(report["full_field_candidate"])
        self.assertFalse(report["authority"]["provider"])
        self.assertFalse(report["authority"]["push"])
        self.assertFalse(report["authority"]["submission"])

    def test_invalid_inputs_and_malformed_gamma_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            action.euclid_trace(31, 0)
        with self.assertRaises(ValueError):
            action.euclid_trace(31, 31)
        with self.assertRaises(ValueError):
            action.euclid_trace(21, 7)
        with self.assertRaises(ValueError):
            action.gamma_encode((0,))
        with self.assertRaises(ValueError):
            action.gamma_decode("0")
        with self.assertRaises(ValueError):
            action.gamma_decode("101")


if __name__ == "__main__":
    unittest.main()
