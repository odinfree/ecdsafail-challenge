#!/usr/bin/env python3
"""Tests for the exact odd-lift prefix-stream gate."""

from __future__ import annotations

import unittest

import odd_lift_prefix_stream as gate


class OddLiftPrefixStreamTests(unittest.TestCase):
    def test_signed_lift_is_odd_and_field_equivalent(self) -> None:
        prime = 31
        radix = 1 << prime.bit_length()
        for t in range(1, prime):
            signed, word = gate.odd_lift(t, prime)
            self.assertEqual(signed % prime, t)
            self.assertEqual(word, signed % radix)
            self.assertEqual(word & 1, 1)

    def test_power_of_two_multiply_recovers_every_input(self) -> None:
        prime = 31
        width = prime.bit_length()
        radix = 1 << width
        for t in range(1, prime):
            _signed, multiplier = gate.odd_lift(t, prime)
            inverse = pow(multiplier, -1, radix)
            images = set()
            for value in range(radix):
                image = multiplier * value % radix
                images.add(image)
                self.assertEqual(inverse * image % radix, value)
            self.assertEqual(len(images), radix)

    def test_exact_case_has_replayable_directional_collisions(self) -> None:
        report = gate.case_report(31)
        self.assertEqual(report["domain_states"], 30 * 31)
        self.assertEqual(report["odd_lift_failures"], 0)
        self.assertEqual(report["recovery_failures"], 0)
        self.assertEqual(report["target_failures"], 0)
        self.assertEqual(report["positive_control_failures"], 0)
        for direction in ("low_to_high", "high_to_low"):
            direction_report = report[direction]
            self.assertGreater(direction_report["blocked_bit_count"], 0)
            for witness in direction_report["witnesses"]:
                self.assertTrue(gate.replay_collision(31, direction, witness))

    def test_multiscale_gate_rejects_both_one_pass_directions(self) -> None:
        report = gate.run_gate((31, 61, 127, 251))
        self.assertEqual(report["verdict"], "HARD_NACK_ODD_LIFT_PREFIX_STREAM")
        self.assertTrue(report["all_controls_passed"])
        self.assertTrue(report["both_directions_blocked_at_every_width_ge_6"])
        self.assertEqual(report["next_grammar"], "NONLOCAL_DIRECT_UNIT_ACTION")
        self.assertFalse(report["authority"]["provider"])
        self.assertFalse(report["authority"]["submission"])

    def test_curve_support_is_reported_as_a_separate_diagnostic(self) -> None:
        report = gate.curve_support_report(31)
        self.assertGreater(report["support_states"], 0)
        self.assertEqual(
            report["support_states"],
            report["nonzero_t_states"] + report["zero_t_states"],
        )
        self.assertEqual(report["product_failures"], 0)
        for direction in ("low_to_high", "high_to_low"):
            for witness in report[direction]["witnesses"]:
                self.assertTrue(gate.replay_collision(31, direction, witness))


if __name__ == "__main__":
    unittest.main()
