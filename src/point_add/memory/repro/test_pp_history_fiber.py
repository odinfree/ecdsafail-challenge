from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPRO_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(REPRO_DIR))

from pp_history_fiber import (
    Config,
    bit1,
    enumerate_fibers,
    half_mod,
    local_predecessor_signs,
    render_receipt,
    run_case,
)


class ArithmeticTests(unittest.TestCase):
    def test_bit1_uses_fixed_width_twos_complement(self) -> None:
        self.assertEqual(bit1(-1, 5), 1)
        self.assertEqual(bit1(-3, 5), 0)

    def test_half_mod_is_inverse_of_doubling(self) -> None:
        for value in range(29):
            self.assertEqual((2 * half_mod(value, 29)) % 29, value)

    def test_each_walk_step_is_integral_and_odd(self) -> None:
        trace = run_case(Config(width=5, modulus=29, rounds=12), 7, 11)
        for state in trace.states:
            self.assertEqual(state.u & 1, 1)
            self.assertEqual(state.v & 1, 1)


class FiberTests(unittest.TestCase):
    def test_every_width5_history_round_trips(self) -> None:
        report = enumerate_fibers(Config(width=5, modulus=29, rounds=12))
        self.assertEqual(report.input_count, 29 * 28)
        self.assertEqual(report.rounds[-1].round_index, 12)
        self.assertTrue(report.round_trip_ok)
        self.assertTrue(report.walk_converged)

    def test_local_walk_endpoint_has_two_predecessor_signs(self) -> None:
        self.assertEqual(
            local_predecessor_signs(source=5, post_target=3, width=5),
            (0, 1),
        )


class CliTests(unittest.TestCase):
    def test_receipt_is_byte_deterministic(self) -> None:
        args = ["--width", "5", "--modulus", "29", "--rounds", "12"]
        self.assertEqual(render_receipt(args), render_receipt(args))

    def test_production_projection_uses_retained_word_not_ratio(self) -> None:
        args = ["--width", "5", "--modulus", "29", "--rounds", "12"]
        receipt = json.loads(render_receipt(args))
        self.assertEqual(receipt["projected_resident_history"], 256)
        self.assertIn(
            "retained 256-bit denominator",
            receipt["model_scope"]["projection_method"],
        )


if __name__ == "__main__":
    unittest.main()
