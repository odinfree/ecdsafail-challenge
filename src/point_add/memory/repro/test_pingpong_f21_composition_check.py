#!/usr/bin/env python3

from __future__ import annotations

import copy
import pathlib
import sys
import unittest


HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from pingpong_f21_composition_check import (  # noqa: E402
    NO_BIT,
    check_evidence,
    map_transform_indices,
    parse_iterations,
    parse_scan,
    parse_transforms,
)


def scan_line(*, ops: int, executed_t: int, digest: str = "ab" * 32) -> str:
    return (
        "DIRTY_SCAN mirror_check -> FAITHFUL (qubits, bits and phase all agree)\n"
        "DIRTY_SCAN rounds=2 lanes=128 "
        f"ops={ops} executed_t={executed_t} average_t={executed_t / 128:.8f} "
        "classical=0 phase_shots=0 any_fault_shots=0 "
        "lambda_total_per_9024=0.00 phase_bad_rounds=0/2 "
        "ancilla_bad_rounds=0/2 dirty_free_events=0 (cap 0) "
        "attributable=false last_phase=0x0000000000000000 "
        f"outcome_digest={digest}\n"
    )


def candidate_log(*, condition: int = NO_BIT, fixpoint: bool = True) -> str:
    second = (
        "CONSTPROP iter=2 ccx_total=98 dropped=0 folded_cx=0 folded_x=0 "
        "inverse_pairs=0 aff_drop=0 aff_fold=0 "
        "(this-iter toffoli removed = 0)\n"
        if fixpoint
        else ""
    )
    return (
        "CONSTPROP_TRANSFORM label=constant index=10 "
        "decision=DropZeroCtrl { ctrl: QubitId(8) } kind=CCX "
        f"controls=(8, 9) target=10 condition={condition}\n"
        "CONSTPROP_TRANSFORM label=affine index=20 "
        "decision=FoldEqualCtrls { a: QubitId(11), b: QubitId(12), "
        "keep_ctrl: QubitId(11) } kind=CCX controls=(11, 12) "
        f"target=13 condition={condition}\n"
        "CONSTPROP iter=1 ccx_total=100 dropped=1 folded_cx=0 folded_x=0 "
        "inverse_pairs=0 aff_drop=0 aff_fold=1 "
        "(this-iter toffoli removed = 2)\n"
        + second
        + scan_line(ops=999, executed_t=1152)
    )


class PingpongF21CompositionCheckTest(unittest.TestCase):
    def setUp(self) -> None:
        self.baseline_fingerprint = {
            "emitted_ops": 1000,
            "qubits": 1265,
            "max_referenced_qubit_id": 1264,
            "compressed_ops_sha256": "1" * 64,
            "canonical_semantic_sha256": "2" * 64,
            "operation_kind_counts": [0] * 18,
        }
        self.candidate_fingerprint = {
            **self.baseline_fingerprint,
            "emitted_ops": 999,
            "compressed_ops_sha256": "3" * 64,
            "canonical_semantic_sha256": "4" * 64,
        }
        self.baseline_text = scan_line(ops=1000, executed_t=1408)
        self.candidate_text = candidate_log()

    def check(self) -> dict[str, object]:
        return check_evidence(
            self.baseline_fingerprint,
            self.candidate_fingerprint,
            parse_scan(self.baseline_text),
            parse_scan(self.candidate_text),
            parse_transforms(self.candidate_text),
            parse_iterations(self.candidate_text),
            expected_rounds=2,
        )

    def test_accepts_exact_q1265_full_state_composition(self) -> None:
        verdict = self.check()
        self.assertEqual("ADMIT_TO_HUMAN_REVIEW_F21", verdict["verdict"])
        self.assertEqual(2, verdict["executed_t_delta_per_lane"])
        self.assertEqual(2, verdict["transform_count"])
        self.assertEqual(11.0, verdict["baseline_average_t"])
        self.assertEqual(9.0, verdict["candidate_average_t"])
        self.assertEqual(11, verdict["baseline_rounded_t"])
        self.assertEqual(9, verdict["candidate_rounded_t"])
        self.assertEqual(13_915, verdict["baseline_evaluator_style_score"])
        self.assertEqual(11_385, verdict["candidate_evaluator_style_score"])

    def test_evaluator_metrics_round_half_up_from_exact_totals(self) -> None:
        self.baseline_text = scan_line(ops=1000, executed_t=1472)
        self.candidate_text = candidate_log().replace(
            scan_line(ops=999, executed_t=1152),
            scan_line(ops=999, executed_t=1216),
        )
        verdict = self.check()
        self.assertEqual(11.5, verdict["baseline_average_t"])
        self.assertEqual(9.5, verdict["candidate_average_t"])
        self.assertEqual(12, verdict["baseline_rounded_t"])
        self.assertEqual(10, verdict["candidate_rounded_t"])

    def test_rejects_unequal_full_state_digest(self) -> None:
        self.candidate_text = candidate_log().replace("ab" * 32, "cd" * 32)
        with self.assertRaisesRegex(ValueError, "outcome_digest"):
            self.check()

    def test_rejects_non_q1265_artifact(self) -> None:
        self.candidate_fingerprint = copy.deepcopy(self.candidate_fingerprint)
        self.candidate_fingerprint["qubits"] = 1266
        with self.assertRaisesRegex(ValueError, "Q1265"):
            self.check()

    def test_rejects_non_no_bit_transform(self) -> None:
        self.candidate_text = candidate_log(condition=7)
        with self.assertRaisesRegex(ValueError, "NO_BIT"):
            self.check()

    def test_rejects_missing_fixpoint(self) -> None:
        self.candidate_text = candidate_log(fixpoint=False)
        with self.assertRaisesRegex(ValueError, "fixpoint"):
            self.check()

    def test_rejects_inconsistent_t_accounting(self) -> None:
        self.baseline_text = scan_line(ops=1000, executed_t=1407)
        with self.assertRaisesRegex(ValueError, "integral per-lane"):
            self.check()

    def test_rejects_duplicate_dirty_scan_summary(self) -> None:
        with self.assertRaisesRegex(ValueError, "exactly one DIRTY_SCAN summary"):
            parse_scan(self.baseline_text + self.baseline_text)

    def test_maps_affine_indices_through_constant_deletions(self) -> None:
        transforms = [
            {"label": "constant", "index": 1, "decision": "DropZeroCtrl { x }"},
            {"label": "constant", "index": 4, "decision": "FoldCx { x }"},
            {"label": "affine", "index": 2, "decision": "FoldEqualCtrls { x }"},
        ]
        self.assertEqual([1, 4, 3], map_transform_indices(transforms))


if __name__ == "__main__":
    unittest.main()
