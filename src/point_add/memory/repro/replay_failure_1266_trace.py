#!/usr/bin/env python3
"""Source-bound trace for the Q1266 replay failure exposed at trusted shot 231.

This records the Phase-1 diagnosis and the single authorized Phase-2/3
width-54 hypothesis test; it is not a production fix.  It reuses the literal
promoted walk/replay model in ``replay_window_census.py`` and stops at the
first arithmetic divergence from exact modular recurrence.

The trusted full-evaluator matrix in the JSON report is a record of local
``eval_circuit`` runs.  The arithmetic trace itself is recomputed on every
invocation from the captured candidate-XOF input point.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


PROMOTED_COMMIT = "67524171baaf568dc3dc606f38515745f70804ff"
PROMOTED_TREE = "8202910d176fa1f3332ff961e6f3f789ca6a7ac2"
PINGPONG_SHA256 = "b675ce80635d53ee6bd7e1ea4e872042c10581091993975b8c4a16b6fbe30981"

FAILING_SETTINGS = {
    "SUB4_PP_PEAK": 1266,
    "SUB4_PP_R1": 317,
    "SUB4_PP_R1_MUL": 318,
    "SUB4_PP_R2": 631,
}
BAKED_SETTINGS = {
    "SUB4_PP_PEAK": 1267,
    "SUB4_PP_R1": 335,
    "SUB4_PP_R1_MUL": 315,
    "SUB4_PP_R2": 645,
}

FAILING_OPS_SHA256 = "c1f7f1c6ded74f050ff201fdcff40d1d194b8e0f0a9ffb9665d65412443ec619"
BAKED_OPS_SHA256 = "87371140be9e81a7b4a79b87b92cd0a8b0f13362bee5ecb23229807a8af6d05e"
FOLD54_OPS_SHA256 = "da4b56ad5c2fca6df66d2dc3f8486c24ee5d4c86ef70d3853cf9b98eb603ff5f"

TARGET = (
    int("026e6b9fffecd1eb7cf3c5b5c791a2ffec463157631c0d576f1d85d2af232e08", 16),
    int("d66bd6036dc37c6df7475ccdb8e557cd7d91d62022f9d0f91dad5a6cb171add5", 16),
)
OFFSET = (
    int("78fc99157c51b479b618ac02e400df9b53ac4a6b31d88c7ecfc7f1ffb46802ff", 16),
    int("bc92be8c952f00b8aaa6fc2da230d7e79b01ee29149f5eae9cc4a71f1c77a2c7", 16),
)
EXPECTED = (
    int("add4f1e87335c3a0a6869d4aff9ccb3c88fb4ce6802cef54f567d798feda394e", 16),
    int("8fdf34c981c8d86d842b58754b8b7184bddecfa221bbc1e84b24acacc4a1aaf7", 16),
)
CANDIDATE_GOT = (
    int("add4f1e87335c3a0a6869d4aff9ccb3c88fb4ce6802cef54f567d798feda394e", 16),
    int("e415187149986142643589bf0680734f8232dacdcbd612d173e3da8f93e3fa80", 16),
)


def hx(value: int) -> str:
    return f"0x{value:064x}"


def load_model(path: Path) -> Any:
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("replay_window_census", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load model at {path}")
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    return model


def trace_divide(model: Any, denominator: int, numerator: int, tape: list[int]) -> dict[str, Any] | None:
    inverse_two = pow(2, -1, model.P)
    actual_x = ideal_x = 0
    actual_y = ideal_y = numerator
    for round_index, sign in enumerate(tape):
        actual_source, actual_target = (
            (actual_x, actual_y) if round_index % 2 == 0 else (actual_y, actual_x)
        )
        ideal_source, ideal_target = (
            (ideal_x, ideal_y) if round_index % 2 == 0 else (ideal_y, ideal_x)
        )
        expected = (
            ideal_target + (ideal_source if sign == 0 else -ideal_source)
        ) * inverse_two % model.P
        if round_index == 0:
            actual = model.mod_halve_actual(actual_target, 54)
        elif round_index == 1:
            actual = model.mod_halve_actual(
                model.seed_round_one_actual(actual_source, sign), 54
            )
        else:
            _, actual = model.divide_cell_actual(actual_source, actual_target, sign, 54)
        if (
            actual_source != ideal_source
            or actual_target != ideal_target
            or actual != expected
        ):
            return {
                "round": round_index,
                "sign": sign,
                "actual": hx(actual),
                "expected": hx(expected),
            }
        if round_index % 2 == 0:
            actual_y = actual
            ideal_y = expected
        else:
            actual_x = actual
            ideal_x = expected
    return None


def trace_multiply(
    model: Any,
    numerator: int,
    terminal_u: int,
    terminal_v: int,
    tape: list[int],
) -> dict[str, Any] | None:
    actual_x = ideal_x = (-numerator) % model.P if terminal_u < 0 else numerator
    actual_y = ideal_y = (-numerator) % model.P if terminal_v < 0 else numerator
    for round_index in reversed(range(len(tape))):
        tape_sign = tape[round_index]
        arg_sign = 1 - tape_sign
        actual_source, actual_target = (
            (actual_x, actual_y) if round_index % 2 == 0 else (actual_y, actual_x)
        )
        ideal_source, ideal_target = (
            (ideal_x, ideal_y) if round_index % 2 == 0 else (ideal_y, ideal_x)
        )
        expected = (
            2 * ideal_target
            + (ideal_source if arg_sign == 0 else -ideal_source)
        ) % model.P
        if round_index == 0:
            actual = model.mod_double_actual(actual_target, 53)
        elif round_index == 1:
            actual = model.seed_round_one_inverse_actual(
                model.mod_double_actual(actual_target, 53),
                actual_source,
                tape_sign,
            )
        else:
            _, actual = model.multiply_cell_actual(
                actual_source, actual_target, arg_sign, 53
            )
        if (
            actual_source != ideal_source
            or actual_target != ideal_target
            or actual != expected
        ):
            return {
                "round": round_index,
                "tape_sign": tape_sign,
                "arg_sign": arg_sign,
                "source": actual_source,
                "target": actual_target,
                "actual": actual,
                "expected": expected,
            }
        if round_index % 2 == 0:
            actual_y = actual
            ideal_y = expected
        else:
            actual_x = actual
            ideal_x = expected
    return None


def run_multiply_actual(
    model: Any,
    numerator: int,
    terminal_u: int,
    terminal_v: int,
    tape: list[int],
) -> tuple[int, int]:
    x = (-numerator) % model.P if terminal_u < 0 else numerator
    y = (-numerator) % model.P if terminal_v < 0 else numerator
    for round_index in reversed(range(len(tape))):
        tape_sign = tape[round_index]
        source, target = (x, y) if round_index % 2 == 0 else (y, x)
        if round_index == 0:
            updated = model.mod_double_actual(target, 53)
        elif round_index == 1:
            updated = model.seed_round_one_inverse_actual(
                model.mod_double_actual(target, 53), source, tape_sign
            )
        else:
            _, updated = model.multiply_cell_actual(
                source, target, 1 - tape_sign, 53
            )
        if round_index % 2 == 0:
            y = updated
        else:
            x = updated
    return x, y


def fold_boundary(model: Any, divergence: dict[str, Any]) -> dict[str, Any]:
    source = divergence["source"]
    target = divergence["target"]
    sign = divergence["arg_sign"]
    width = 53
    doubled_out = target >> 255
    shifted = (2 * target) & model.MASK256
    accumulator = shifted if sign == 0 else model.MASK256 ^ shifted
    total = accumulator + source
    summed = total & model.MASK256
    add_out = total >> 256
    routed = doubled_out & (sign ^ add_out)
    minus_f = routed & sign
    plus_two_f = routed ^ minus_f
    plus_f = add_out ^ doubled_out ^ minus_f
    correction_multiple = plus_f + 2 * plus_two_f - minus_f
    mask = (1 << width) - 1
    low_total = (summed & mask) + correction_multiple * model.F
    truncated = (summed & ~mask) | (low_total & mask)
    full = (summed + correction_multiple * model.F) & model.MASK256
    return {
        "fold_window": width,
        "doubled_out": doubled_out,
        "add_out": add_out,
        "routed": routed,
        "minus_f": minus_f,
        "plus_f": plus_f,
        "plus_2f": plus_two_f,
        "correction_multiple_f": correction_multiple,
        "summed_before_fold": hx(summed),
        "low_window_before": hex(summed & mask),
        "low_window_plus_correction": hex(low_total),
        "carry_out_of_bit_52": low_total >> width,
        "truncated_output": hx(truncated),
        "full_carry_output": hx(full),
        "dropped_delta": hex(full - truncated),
    }


def main() -> None:
    repo = Path(__file__).resolve().parents[4]
    model = load_model(Path(__file__).with_name("replay_window_census.py"))
    tree = model.git(repo, "rev-parse", f"{PROMOTED_COMMIT}^{{tree}}")
    if tree != PROMOTED_TREE:
        raise RuntimeError(f"promoted tree drift: {tree}")
    pingpong = model.promoted_text(repo, "src/point_add/pingpong_div.rs")
    source_hash = hashlib.sha256(pingpong.encode()).hexdigest()
    if source_hash != PINGPONG_SHA256:
        raise RuntimeError(f"pingpong source drift: {source_hash}")
    schedule = model.parse_array(pingpong, "WIDTH_SCHEDULE", 700)
    repairs = set(model.parse_array(pingpong, "WIDTH_REPAIR", 100))

    dx = (TARGET[0] - OFFSET[0]) % model.P
    dy = (TARGET[1] - OFFSET[1]) % model.P
    slope = dy * pow(dx, -1, model.P) % model.P
    result_x = (slope * slope - TARGET[0] - OFFSET[0]) % model.P
    result_y = (slope * (TARGET[0] - result_x) - TARGET[1]) % model.P
    if (result_x, result_y) != EXPECTED:
        raise AssertionError("captured input does not reproduce trusted expected point")
    multiply_denominator = (OFFSET[0] - result_x) % model.P

    divide_walk = model.walk_transcript(dx, 696, schedule, repairs, 54, 26)
    multiply_walk = model.walk_transcript(
        multiply_denominator, 694, schedule, repairs, 54, 26
    )
    if divide_walk is None or multiply_walk is None:
        raise AssertionError("captured shot failed a walk width/terminal gate")
    divide_terminal_u, divide_terminal_v, divide_tape = divide_walk
    multiply_terminal_u, multiply_terminal_v, multiply_tape = multiply_walk
    divide_divergence = trace_divide(model, dx, dy, divide_tape)
    multiply_divergence = trace_multiply(
        model,
        slope,
        multiply_terminal_u,
        multiply_terminal_v,
        multiply_tape,
    )
    if divide_divergence is not None:
        raise AssertionError(f"unexpected divide divergence: {divide_divergence}")
    if multiply_divergence is None:
        raise AssertionError("expected a multiply replay divergence")
    boundary = fold_boundary(model, multiply_divergence)

    if multiply_divergence["round"] != 508:
        raise AssertionError(f"first multiply divergence drift: {multiply_divergence}")
    if multiply_divergence["expected"] - multiply_divergence["actual"] != 1 << 53:
        raise AssertionError("first divergence is not the expected dropped bit-53 carry")
    if boundary["correction_multiple_f"] != 2 or boundary["carry_out_of_bit_52"] != 1:
        raise AssertionError(f"unexpected fold boundary: {boundary}")
    multiply_actual_x, multiply_actual_y = run_multiply_actual(
        model,
        slope,
        multiply_terminal_u,
        multiply_terminal_v,
        multiply_tape,
    )
    shell_output_y = (multiply_actual_y - OFFSET[1]) % model.P
    if shell_output_y != CANDIDATE_GOT[1]:
        raise AssertionError(
            f"literal replay output does not match trusted Y: {shell_output_y:#x}"
        )

    report = {
        "verdict": "HARD_NACK_MUL_FOLD54_REPAIR",
        "source": {
            "commit": PROMOTED_COMMIT,
            "tree": PROMOTED_TREE,
            "pingpong_sha256": source_hash,
        },
        "exact_reproducer": {
            "settings": FAILING_SETTINGS,
            "command": (
                "SUB4_PP_PEAK=1266 SUB4_PP_R1=317 SUB4_PP_R1_MUL=318 "
                "SUB4_PP_R2=631 ./target/release/build_circuit && "
                "./target/release/eval_circuit"
            ),
            "ops_sha256": FAILING_OPS_SHA256,
            "trusted_counts": {
                "shots": 9024,
                "classical_mismatches": 20,
                "phase_garbage_batches": 13,
                "ancilla_garbage_batches": 0,
                "first_classical_mismatch": 231,
            },
        },
        "baked_control": {
            "settings": BAKED_SETTINGS,
            "ops_sha256": BAKED_OPS_SHA256,
            "trusted_counts": {
                "shots": 9024,
                "classical_mismatches": 0,
                "phase_garbage_batches": 0,
                "ancilla_garbage_batches": 0,
            },
        },
        "fixed_xof_matrix_measured": {
            "candidate_stream_candidate_xof": [20, 13, 0],
            "baked_stream_baked_xof": [0, 0, 0],
            "baked_stream_candidate_xof": [20, 13, 0],
            "candidate_stream_baked_xof": [0, 1, 0],
            "tuple_order": [
                "classical_mismatches",
                "phase_garbage_batches",
                "ancilla_garbage_batches",
            ],
        },
        "fold54_hypothesis_test": {
            "only_changed_setting": "SUB4_PP_REPLAY_FOLD_WINDOW_MUL=54",
            "local_round_508_result": {
                "width_53_dropped_delta": "0x20000000000000",
                "width_54_matches_exact": True,
            },
            "candidate_ops_sha256": FOLD54_OPS_SHA256,
            "fixed_candidate_xof_red": {
                "qubits": 1266,
                "average_t": 911719.507,
                "classical_mismatches": 20,
                "phase_garbage_batches": 13,
                "ancilla_garbage_batches": 0,
                "first_classical_mismatch": 231,
            },
            "fixed_candidate_xof_green_attempt": {
                "qubits": 1266,
                "average_t": 912419.193,
                "rounded_t": 912419,
                "average_t_delta": 699.686,
                "emitted_ops": 12608848,
                "classical_mismatches": 16,
                "phase_garbage_batches": 7,
                "ancilla_garbage_batches": 0,
                "first_classical_mismatch": 724,
            },
            "gates": {
                "fixed_xof_correctness_green": False,
                "qubits_equal_1266": True,
                "rounded_t_at_most_912109": False,
                "natural_trusted_stream": "NOT_RUN_AFTER_FIXED_XOF_AND_ECONOMICS_FAILURE",
            },
            "disposition": (
                "HARD_NACK: the one-bit widening repairs the localized round-508 "
                "event but neither clears the frozen population nor fits the T budget"
            ),
        },
        "shot_231": {
            "target": [hx(TARGET[0]), hx(TARGET[1])],
            "offset": [hx(OFFSET[0]), hx(OFFSET[1])],
            "trusted_got": [hx(CANDIDATE_GOT[0]), hx(CANDIDATE_GOT[1])],
            "trusted_expected": [hx(EXPECTED[0]), hx(EXPECTED[1])],
            "divide_denominator": hx(dx),
            "divide_numerator": hx(dy),
            "slope": hx(slope),
            "multiply_denominator": hx(multiply_denominator),
        },
        "first_divergence": {
            "direction": "multiply",
            "cell": "signed_mod_double_add_pm_fused",
            "round": multiply_divergence["round"],
            "tape_sign": multiply_divergence["tape_sign"],
            "arg_sign": multiply_divergence["arg_sign"],
            "source": hx(multiply_divergence["source"]),
            "target": hx(multiply_divergence["target"]),
            "actual": hx(multiply_divergence["actual"]),
            "expected": hx(multiply_divergence["expected"]),
            "divide_replay_divergence": divide_divergence,
            "arithmetic_boundary": boundary,
            "propagation": {
                "multiply_actual_endpoint_x": hx(multiply_actual_x),
                "multiply_actual_endpoint_y": hx(multiply_actual_y),
                "coordinate_shell_output_y": hx(shell_output_y),
                "matches_trusted_shot_231_y": True,
            },
        },
        "classification": {
            "underlying_fault": "structural truncated multiply-fold carry loss",
            "candidate_vs_baked_gate_delta": (
                "Fiat-Shamir nonce/checkpoint exposure, not a new R1/R2 geometry value bug"
            ),
            "phase_note": (
                "candidate geometry adds one phase-garbage batch under the baked XOF; "
                "the candidate XOF gives 13 under either stream"
            ),
        },
        "model_boundary": (
            "literal promoted classical walk/replay arithmetic; measurement-conditioned "
            "phase is not simulated by this Python trace"
        ),
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
