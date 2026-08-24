from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPRO_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(REPRO_DIR))

from pp_odd_passenger import (
    DEFAULT_SOURCE,
    audit_source,
    prove_initial_state,
    prove_recurrence,
    recurrence_row,
    render_receipt,
)


class OddRecurrenceTests(unittest.TestCase):
    def test_complete_low_two_support_preserves_oddness(self) -> None:
        rows = prove_recurrence()
        self.assertEqual(len(rows), 4)
        self.assertEqual({row["numerator_mod4"] for row in rows}, {2})
        self.assertEqual({row["next_target_bit0"] for row in rows}, {1})

    def test_sign_rule_is_bit_one_xor(self) -> None:
        for source_bit1 in (0, 1):
            for target_bit1 in (0, 1):
                row = recurrence_row(source_bit1, target_bit1)
                self.assertEqual(row["sign"], source_bit1 ^ target_bit1)

    def test_even_denominator_lifts_to_an_odd_congruent_representative(self) -> None:
        row = prove_initial_state(29, 8)
        self.assertEqual(row["denominator_bit0"], 0)
        self.assertEqual(row["lifted_bit0"], 1)

    def test_odd_denominator_is_already_odd(self) -> None:
        row = prove_initial_state(29, 9)
        self.assertEqual(row["denominator_bit0"], 1)
        self.assertEqual(row["lifted_bit0"], 1)


class SourceAuditTests(unittest.TestCase):
    def test_frozen_source_has_four_replay_only_loan_intervals(self) -> None:
        report = audit_source(DEFAULT_SOURCE)
        self.assertEqual(report["loan_intervals"], 4)
        self.assertTrue(report["replay_only"])

    def test_receipt_is_byte_deterministic(self) -> None:
        first = render_receipt([])
        self.assertEqual(first, render_receipt([]))
        self.assertEqual(json.loads(first)["verdict"], "PASS")


if __name__ == "__main__":
    unittest.main()
