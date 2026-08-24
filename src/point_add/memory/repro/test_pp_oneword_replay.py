from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPRO_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(REPRO_DIR))

from pp_oneword_replay import (
    reachable_replay_report,
    render_receipt,
    two_round_local_coordinate_exists,
)


class LocalClosureTests(unittest.TestCase):
    def test_no_nontrivial_two_round_coordinate(self) -> None:
        for modulus in (29, 61, 127):
            self.assertFalse(two_round_local_coordinate_exists(modulus))


class ReachableClassTests(unittest.TestCase):
    def test_terminal_classes_saturate_nonzero_field(self) -> None:
        for width, modulus, rounds in ((5, 29, 12), (6, 61, 17), (7, 127, 20)):
            report = reachable_replay_report(width, modulus, rounds)
            self.assertEqual(report.terminal_pair_classes, modulus - 1)
            self.assertEqual(report.minimum_terminal_code_bits, width)
            self.assertTrue(report.terminal_inverse_ok)

    def test_receipt_is_byte_deterministic(self) -> None:
        self.assertEqual(render_receipt(), render_receipt())
        receipt = json.loads(render_receipt())
        self.assertEqual(receipt["verdict"], "HARD_NACK")


if __name__ == "__main__":
    unittest.main()
