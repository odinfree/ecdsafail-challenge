from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPRO_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(REPRO_DIR))

from pp_reachable_carry import (
    Config,
    analyze_config,
    carry_ladder,
    enumerate_observations,
    find_affine_solution,
    find_sparse_affine,
    render_receipt,
)


class CarryArithmeticTests(unittest.TestCase):
    def test_carry_ladder_matches_wrapped_addition(self) -> None:
        width = 8
        mask = (1 << width) - 1
        for source in (-29, -7, 1, 13, 29):
            for target in (-27, -1, 3, 19, 27):
                for sign in (0, 1):
                    trace = carry_ladder(source, target, sign, width)
                    signed_addend = -source if sign else source
                    self.assertEqual(trace.output, (target + signed_addend) & mask)

    def test_full_and_support_is_not_affine(self) -> None:
        rows = [
            ({"one": 1, "a": a, "b": b}, a & b)
            for a in (0, 1)
            for b in (0, 1)
        ]
        self.assertIsNone(find_sparse_affine(rows, max_terms=3))
        self.assertIsNone(find_affine_solution(rows))

    def test_xor_support_has_sparse_affine_expression(self) -> None:
        rows = [
            ({"one": 1, "a": a, "b": b}, a ^ b)
            for a in (0, 1)
            for b in (0, 1)
        ]
        self.assertEqual(find_sparse_affine(rows, max_terms=3), ("a", "b"))
        self.assertEqual(find_affine_solution(rows), ("a", "b"))


class ReachabilityTests(unittest.TestCase):
    def test_known_low_two_identities_hold_exhaustively(self) -> None:
        observations = enumerate_observations(Config(bits=5, modulus=29, rounds=15))
        self.assertGreater(len(observations), 0)
        for observation in observations:
            self.assertEqual(observation.carries[1], 1 ^ observation.sign)
            self.assertEqual(
                observation.carries[2],
                (observation.source >> 1) & 1,
            )

    def test_terminal_filter_is_explicit(self) -> None:
        observations = enumerate_observations(Config(bits=5, modulus=29, rounds=30))
        self.assertTrue(any(observation.terminal for observation in observations))
        self.assertTrue(any(not observation.terminal for observation in observations))

    def test_report_preserves_positive_controls(self) -> None:
        report = analyze_config(Config(bits=5, modulus=29, rounds=15))
        self.assertTrue(report.known_c1_holds)
        self.assertTrue(report.known_c2_holds)
        self.assertEqual(report.register_width, 8)
        self.assertEqual(report.denominator_count, 28)


class CliTests(unittest.TestCase):
    def test_receipt_is_byte_deterministic(self) -> None:
        args = ["--spec", "5:29:15"]
        self.assertEqual(render_receipt(args), render_receipt(args))
        receipt = json.loads(render_receipt(args))
        self.assertEqual(receipt["source_binding"]["commit"], "67524171baaf568dc3dc606f38515745f70804ff")
        self.assertEqual(receipt["width_reports"][0]["register_width"], 8)


if __name__ == "__main__":
    unittest.main()
