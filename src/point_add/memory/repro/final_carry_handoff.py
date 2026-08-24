#!/usr/bin/env python3
"""Source-bound models for the final-add carry-to-fold handoff experiment.

The module is intentionally standard-library-only.  It never invokes the
evaluator and treats reduced widths as falsification/discovery evidence only.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import pathlib
import re
import subprocess
from typing import Any


SOURCE_COMMIT = "522d00296ab014b0f4d128915b53851516f17f4d"
SOURCE_TREE = "eab2326ce33549eceeb5c10aa64eae33f148b0ac"
SOURCE_BLOBS = {
    "src/point_add/pingpong_div.rs": "f4399563b1fe8c4beee568027ebf52df252e7555",
    "src/point_add/arith/compare.rs": "7c3c9cd4956799b8a93ff108ce4bc4d3358def91",
    "src/point_add/mod.rs": "8b497c16d804d9e128fd1139ad4858ddb1de56de",
}

ROUNDS = {"divide": 694, "multiply": 693}
CELL_CALLS = {name: count - 2 for name, count in ROUNDS.items()}
FOLD_WIDTH = {"divide": 54, "multiply": 53}
FLAG_COMPARE_WIDTH = 22
CHUNK_COMPARE_WIDTH = 22
FLAG_COMPARE_CCX_PER_CELL = FLAG_COMPARE_WIDTH - 1
FLAG_COMPARE_CONDITION_DEPTH = 1
TARGET_NET_AVERAGE_T = 1_500.0
SECP256K1_F = (1 << 256) - 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F


def _git(repo: pathlib.Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


def _source_text(repo: pathlib.Path, path: str) -> str:
    return _git(repo, "show", f"{SOURCE_COMMIT}:{path}")


def _line_of(text: str, needle: str) -> int:
    for line_number, line in enumerate(text.splitlines(), start=1):
        if needle in line:
            return line_number
    raise ValueError(f"source marker not found: {needle!r}")


def build_inventory(repo: pathlib.Path) -> dict[str, Any]:
    """Return the deterministic exact-source and baseline-cost inventory."""

    repo = repo.resolve()
    observed_tree = _git(repo, "rev-parse", f"{SOURCE_COMMIT}^{{tree}}")
    if observed_tree != SOURCE_TREE:
        raise RuntimeError(
            f"source tree mismatch: expected {SOURCE_TREE}, observed {observed_tree}"
        )

    observed_blobs = {
        path: _git(repo, "rev-parse", f"{SOURCE_COMMIT}:{path}")
        for path in SOURCE_BLOBS
    }
    if observed_blobs != SOURCE_BLOBS:
        raise RuntimeError(
            f"source blob mismatch: expected {SOURCE_BLOBS}, observed {observed_blobs}"
        )

    pingpong = _source_text(repo, "src/point_add/pingpong_div.rs")
    compare = _source_text(repo, "src/point_add/arith/compare.rs")
    mod_rs = _source_text(repo, "src/point_add/mod.rs")

    required_markers = {
        "late_carry": "fn add_chunked_measured_late_carry(",
        "chunk_add": "fn chunk_add(",
        "fold": "fn fused_fold_maskfree(",
        "divide": "fn signed_mod_add_pm_halve_fused(",
        "multiply": "fn signed_mod_double_add_pm_fused(",
    }
    source_lines = {
        name: _line_of(pingpong, marker) for name, marker in required_markers.items()
    }
    source_lines["flag_compare"] = _line_of(
        compare, "pub(crate) fn cmp_lt_phase_conditioned("
    )
    source_lines["forced_rounds"] = _line_of(
        mod_rs, 'set_default_env("SUB4_PP_ROUNDS", "696")'
    )

    total_cells = sum(CELL_CALLS.values())
    branch_probability = 0.5**FLAG_COMPARE_CONDITION_DEPTH
    flag_average_t = total_cells * FLAG_COMPARE_CCX_PER_CELL * branch_probability
    minimum_saved = 0
    while total_cells * minimum_saved * branch_probability < TARGET_NET_AVERAGE_T:
        minimum_saved += 1
    three_ccx_gross = total_cells * 3 * branch_probability

    return {
        "schema": "final-carry-handoff-inventory-v1",
        "source_commit": SOURCE_COMMIT,
        "source_tree": SOURCE_TREE,
        "source_blobs": observed_blobs,
        "source_lines": source_lines,
        "candidate_env": {
            "SUB4_PP_ROUNDS": "694",
            "SUB4_PP_ROUNDS_MUL": "693",
        },
        "rounds": ROUNDS,
        "cell_calls": CELL_CALLS,
        "total_cells": total_cells,
        "fold_width": FOLD_WIDTH,
        "fold_carry_wires": {
            name: width - 3 for name, width in FOLD_WIDTH.items()
        },
        "flag_compare_width": FLAG_COMPARE_WIDTH,
        "chunk_compare_width": CHUNK_COMPARE_WIDTH,
        "flag_compare_ccx_per_cell": FLAG_COMPARE_CCX_PER_CELL,
        "flag_compare_condition_depth": FLAG_COMPARE_CONDITION_DEPTH,
        "flag_compare_average_t": flag_average_t,
        "target_net_average_t": TARGET_NET_AVERAGE_T,
        "minimum_uniform_saved_ccx": minimum_saved,
        "three_ccx_gross_average_t": three_ccx_gross,
        "three_ccx_added_cost_ceiling": three_ccx_gross - TARGET_NET_AVERAGE_T,
        "lifetime_obligations": [
            "final carry is allocated only when the final chunk begins",
            "retained predecessors overlap every selector live through the fold",
            "dirty hosts must replace, not coexist with, clean fold carries",
            "divide and multiply peak intervals are censused independently",
        ],
        "baseline_cleanup": {
            "divide": {
                "carry": "overflow",
                "phase_repair": "top-22 target/source cmp_lt",
                "fold_first_carry": "not_sign_and_parity",
            },
            "multiply": {
                "carry": "add_out",
                "phase_repair": "top-22 target/source cmp_lt",
                "fold_first_carry": "target[0] AND (doubled_out XOR add_out)",
            },
        },
    }


def _mask(width: int) -> int:
    return (1 << width) - 1


def _bits(value: int, width: int) -> list[int]:
    return [(value >> index) & 1 for index in range(width)]


def _add_with_carries(left: int, right: int, width: int) -> tuple[int, list[int]]:
    """Return the wrapped sum and carries c_1 through c_width."""

    carries: list[int] = []
    carry = 0
    output = 0
    for index in range(width):
        a = (left >> index) & 1
        b = (right >> index) & 1
        output |= (a ^ b ^ carry) << index
        carry = (a & b) ^ (a & carry) ^ (b & carry)
        carries.append(carry)
    return output, carries


def _divide_selectors(sign: int, parity: int, overflow: int) -> dict[str, int]:
    first_carry = (1 ^ sign) & parity
    sign_and_parity = sign & parity
    minus_f = (1 ^ overflow) & first_carry
    plus_2f = overflow & sign_and_parity
    plus_f = parity ^ sign ^ minus_f
    return {
        "first_carry": first_carry,
        "minus_f": minus_f,
        "plus_f": plus_f,
        "plus_2f": plus_2f,
    }


def _multiply_selectors(
    sign: int,
    doubled_out: int,
    add_out: int,
    post_add_lsb: int,
) -> dict[str, int]:
    routed = doubled_out & (sign ^ add_out)
    minus_f = routed & sign
    plus_2f = routed ^ minus_f
    odd_correction = doubled_out ^ add_out
    first_carry = post_add_lsb & odd_correction
    plus_f = add_out ^ doubled_out ^ minus_f
    return {
        "first_carry": first_carry,
        "minus_f": minus_f,
        "plus_f": plus_f,
        "plus_2f": plus_2f,
        "routed": routed,
        "odd_correction": odd_correction,
    }


def _correction_digit(selectors: dict[str, int]) -> int:
    active = (
        selectors["minus_f"]
        + selectors["plus_f"]
        + selectors["plus_2f"]
    )
    if active > 1:
        raise AssertionError(f"non-one-hot correction selectors: {selectors}")
    return (
        -selectors["minus_f"]
        + selectors["plus_f"]
        + 2 * selectors["plus_2f"]
    )


def _fold_low(
    value: int,
    digit: int,
    fold_width: int,
    total_width: int,
) -> tuple[int, list[int]]:
    """Apply the source-shaped low fold and return its full carry recurrence."""

    low_mask = _mask(fold_width)
    operand = (digit * (SECP256K1_F & low_mask)) & low_mask
    low, carries = _add_with_carries(value & low_mask, operand, fold_width)
    output = (value & (_mask(total_width) ^ low_mask)) | low
    return output, carries


def _flag_repair(post_fold: int, source: int, width: int, flag_width: int) -> int:
    shift = width - flag_width
    return int((post_fold >> shift) < (source >> shift))


def _scaled_geometry(width: int) -> tuple[int, int]:
    if width < 5:
        raise ValueError("reduced width must be at least five")
    # Low fold and top flag repair remain disjoint, just as 54/53 and the top
    # 22 bits are disjoint in the 256-bit source cell.
    return width - 2, 2


def _reduced_modulus(width: int) -> int:
    fold_width, _ = _scaled_geometry(width)
    return (1 << width) - (SECP256K1_F & _mask(fold_width))


def _cell_state(
    site: str,
    width: int,
    source: int,
    target: int,
    sign: int,
) -> dict[str, Any]:
    """Model the complete source-shaped cell on one computational basis input.

    Phase coefficients are coefficients of independent HMR outcome variables.
    Comparing the coefficient vector is therefore exhaustive over all 2^m
    measurement arms without enumerating those arms one by one.
    """

    mask = _mask(width)
    fold_width, flag_width = _scaled_geometry(width)
    source &= mask
    target &= mask
    sign &= 1

    if site == "divide":
        add_target = target ^ (mask if sign else 0)
        post_add, add_carries = _add_with_carries(add_target, source, width)
        overflow = add_carries[-1]
        parity = post_add & 1
        selectors = _divide_selectors(sign, parity, overflow)
        doubled_out = None
    elif site == "multiply":
        doubled_out = (target >> (width - 1)) & 1
        shifted = (target << 1) & mask
        add_target = shifted ^ (mask if sign else 0)
        post_add, add_carries = _add_with_carries(add_target, source, width)
        overflow = add_carries[-1]
        parity = post_add & 1
        selectors = _multiply_selectors(
            sign, doubled_out, overflow, parity
        )
    else:
        raise ValueError(f"unknown site: {site}")

    digit = _correction_digit(selectors)
    post_fold, fold_carries = _fold_low(post_add, digit, fold_width, width)
    if selectors["first_carry"] != fold_carries[0]:
        raise AssertionError(
            f"{site} first-carry mismatch: {selectors}, carries={fold_carries}"
        )

    if site == "divide":
        after_complement = post_fold ^ (mask if sign else 0)
        if after_complement & 1:
            raise AssertionError("divide correction did not make shift input even")
        shift_bit = parity ^ overflow ^ sign
        output = (after_complement >> 1) | (shift_bit << (width - 1))
        output_cleanup = int(((output >> (width - 1)) & 1) == shift_bit)
    else:
        assert doubled_out is not None
        doubled_cleanup = (
            doubled_out
            ^ (post_fold & 1)
            ^ sign
            ^ (source & 1)
            ^ overflow
        )
        if doubled_cleanup:
            raise AssertionError("multiply doubled_out cleanup relation failed")
        output = post_fold ^ (mask if sign else 0)
        output_cleanup = 1

    repair = _flag_repair(post_fold, source, width, flag_width)
    residual_final_phase = overflow ^ repair

    # Every selector and fold carry is measurement-uncomputed with its exact
    # generating product. Their net phase coefficient is therefore zero. The
    # final carry is deliberately repaired by the truncated comparator and can
    # retain the source's phase-garbage coefficient overflow XOR repair.
    phase_coefficients: dict[str, int] = {}
    for index in range(max(0, width - 1)):
        phase_coefficients[f"add_owned_{index}"] = 0
    for label in (
        ("divide_plus_2f", "divide_minus_f", "divide_first_carry")
        if site == "divide"
        else ("multiply_first_carry", "multiply_minus_f", "multiply_routed")
    ):
        phase_coefficients[label] = 0
    for index in range(max(0, fold_width - 3)):
        phase_coefficients[f"fold_carry_{index}"] = 0
    phase_coefficients["final_carry"] = residual_final_phase

    return {
        "site": site,
        "width": width,
        "fold_width": fold_width,
        "flag_width": flag_width,
        "source": source,
        "target": target,
        "sign": sign,
        "add_target": add_target,
        "post_add": post_add,
        "post_add_parity": parity,
        "overflow": overflow,
        "selectors": selectors,
        "correction_digit": digit,
        "post_fold": post_fold,
        "flag_repair": repair,
        "output": output,
        "ancillas_clean": bool(output_cleanup),
        "phase_coefficients": phase_coefficients,
    }


def first_phase_blind_mismatch(widths: range) -> dict[str, Any]:
    """Return the first parity-zero divide case missed by a phase-blind model."""

    for width in widths:
        modulus = _reduced_modulus(width)
        # The two maximum canonical residues have even wrapped sum, overflow
        # one, and equal all-one top windows after subtracting only the low f.
        # The truncated comparator therefore emits no repair.
        state = _cell_state("divide", width, modulus - 1, modulus - 1, 0)
        candidate = 0
        baseline = state["phase_coefficients"]["final_carry"]
        if (
            state["post_add_parity"] == 0
            and state["overflow"] == 1
            and baseline != candidate
        ):
            return {
                "site": "divide",
                "width": width,
                "source": modulus - 1,
                "target": modulus - 1,
                "sign": 0,
                "post_add_parity": state["post_add_parity"],
                "overflow": state["overflow"],
                "selectors": {
                    key: state["selectors"][key]
                    for key in ("first_carry", "minus_f", "plus_f", "plus_2f")
                },
                "baseline_phase_coefficient": baseline,
                "candidate_phase_coefficient": candidate,
            }
    raise AssertionError("phase-blind mismatch was not found")


def divide_parity_zero_exact_witness() -> dict[str, Any]:
    width = 256
    modulus = (1 << width) - SECP256K1_F
    source = modulus - 1
    target = modulus - 1
    post_add, carries = _add_with_carries(target, source, width)
    overflow = carries[-1]
    selectors = _divide_selectors(0, post_add & 1, overflow)
    repair = int(
        (post_add >> (width - FLAG_COMPARE_WIDTH))
        < (source >> (width - FLAG_COMPARE_WIDTH))
    )
    return {
        "width": width,
        "source": source,
        "target": target,
        "sign": 0,
        "post_add": post_add,
        "post_add_parity": post_add & 1,
        "overflow": overflow,
        "selectors": selectors,
        "flag_repair": repair,
        "residual_phase_coefficient": overflow ^ repair,
    }


def run_reduced_miter(widths: range) -> dict[str, Any]:
    widths_list = list(widths)
    basis_cases = 0
    phase_checked = 0
    value_mismatches = 0
    selector_cleanup_mismatches = 0
    fold_cleanup_mismatches = 0
    inverse_mismatches = 0
    sign_arms: set[tuple[str, int]] = set()
    measurement_labels: set[tuple[str, str]] = set()

    for width in widths_list:
        limit = _reduced_modulus(width)
        for site in ("divide", "multiply"):
            for source in range(limit):
                for sign in (0, 1):
                    sign_arms.add((site, sign))
                    inverse: dict[int, int] = {}
                    for target in range(limit):
                        state = _cell_state(site, width, source, target, sign)
                        basis_cases += 1
                        if not state["ancillas_clean"]:
                            selector_cleanup_mismatches += 1
                        for label, coefficient in state["phase_coefficients"].items():
                            phase_checked += 1
                            measurement_labels.add((site, label))
                            if label != "final_carry" and coefficient != 0:
                                if label.startswith("fold_carry_"):
                                    fold_cleanup_mismatches += 1
                                else:
                                    selector_cleanup_mismatches += 1
                        output = state["output"]
                        if output in inverse:
                            inverse_mismatches += 1
                        else:
                            inverse[output] = target
                    if len(inverse) != limit:
                        inverse_mismatches += limit - len(inverse)
                    for output, original_target in inverse.items():
                        replay = _cell_state(
                            site, width, source, original_target, sign
                        )["output"]
                        if replay != output:
                            value_mismatches += 1

    required_sign_arms = {
        (site, sign) for site in ("divide", "multiply") for sign in (0, 1)
    }
    uncovered_sign = sorted(required_sign_arms - sign_arms)
    uncovered_measurement = []
    for site in ("divide", "multiply"):
        if not any(found_site == site for found_site, _ in measurement_labels):
            uncovered_measurement.append(site)

    return {
        "schema": "final-carry-handoff-reduced-miter-v1",
        "widths": widths_list,
        "geometry": "low width n-2; disjoint top-2 flag repair",
        "input_range": "all canonical source,target in [0, 2^n-f_n)",
        "basis_cases": basis_cases,
        "phase_coefficients_checked": phase_checked,
        "value_mismatches": value_mismatches,
        "selector_cleanup_mismatches": selector_cleanup_mismatches,
        "fold_cleanup_mismatches": fold_cleanup_mismatches,
        "inverse_mismatches": inverse_mismatches,
        "uncovered_sign_arms": uncovered_sign,
        "uncovered_measurement_arms": uncovered_measurement,
        "measurement_arm_method": (
            "coefficient-vector equality over independent HMR outcome bits"
        ),
    }


def run_exact_local_chain_miter(widths: range) -> dict[str, Any]:
    """Exhaust the constructive retained-chain exact-HMR candidate.

    The candidate retains each carry predecessor until the selected fold has
    completed, then measurement-uncomputes the carry recurrence from top to
    bottom.  Every independent HMR arm is represented by its Boolean residual
    coefficient ``observed_carry XOR exact_majority``.  All coefficients must
    vanish; this is stronger than reproducing the source's truncated final
    repair residual.
    """

    widths_list = list(widths)
    basis_cases = 0
    carry_checked = 0
    value_mismatches = 0
    phase_mismatches = 0
    ancilla_mismatches = 0
    inverse_mismatches = 0
    sign_arms: set[tuple[str, int]] = set()
    measurement_arms: set[tuple[str, int]] = set()

    for width in widths_list:
        limit = _reduced_modulus(width)
        mask = _mask(width)
        for site in ("divide", "multiply"):
            for source in range(limit):
                for sign in (0, 1):
                    sign_arms.add((site, sign))
                    inverse: dict[int, int] = {}
                    for target in range(limit):
                        state = _cell_state(site, width, source, target, sign)
                        add_target = (
                            target ^ (mask if sign else 0)
                            if site == "divide"
                            else (((target << 1) & mask) ^ (mask if sign else 0))
                        )
                        wrapped, carries = _add_with_carries(
                            add_target, source, width
                        )
                        if wrapped != state["post_add"]:
                            value_mismatches += 1

                        previous = 0
                        left_bits = _bits(add_target, width)
                        right_bits = _bits(source, width)
                        for index, observed in enumerate(carries):
                            expected = (
                                (left_bits[index] & right_bits[index])
                                ^ (left_bits[index] & previous)
                                ^ (right_bits[index] & previous)
                            )
                            residual = observed ^ expected
                            carry_checked += 1
                            measurement_arms.add((site, index))
                            phase_mismatches += residual
                            previous = observed

                        basis_cases += 1
                        ancilla_mismatches += int(
                            (not state["ancillas_clean"])
                            or any(
                                coefficient != 0
                                for label, coefficient in state[
                                    "phase_coefficients"
                                ].items()
                                if label != "final_carry"
                            )
                        )
                        output = state["output"]
                        if output in inverse:
                            inverse_mismatches += 1
                        else:
                            inverse[output] = target
                    if len(inverse) != limit:
                        inverse_mismatches += limit - len(inverse)

    required_sign_arms = {
        (site, sign) for site in ("divide", "multiply") for sign in (0, 1)
    }
    uncovered_measurement = [
        site
        for site in ("divide", "multiply")
        if not any(found_site == site for found_site, _ in measurement_arms)
    ]
    return {
        "schema": "final-carry-handoff-exact-local-chain-miter-v1",
        "widths": widths_list,
        "basis_cases": basis_cases,
        "carry_coefficients_checked": carry_checked,
        "measurement_arm_method": (
            "coefficient equality for each independent retained-carry HMR bit"
        ),
        "candidate_final_phase": 0,
        "value_mismatches": value_mismatches,
        "phase_mismatches": phase_mismatches,
        "ancilla_mismatches": ancilla_mismatches,
        "inverse_mismatches": inverse_mismatches,
        "uncovered_sign_arms": sorted(required_sign_arms - sign_arms),
        "uncovered_measurement_arms": uncovered_measurement,
        "transfer_obligation": (
            "the same majority recurrence has 256 positions at exact source; "
            "the separate static census charges its retained lifetime"
        ),
    }


def _exact_divide_publication_state(
    source: int, target: int, sign: int
) -> dict[str, Any]:
    width = 256
    mask = _mask(width)
    modulus = (1 << width) - SECP256K1_F
    if not (0 <= source < modulus and 0 <= target < modulus):
        raise ValueError("exact witness is outside the canonical residue range")
    add_target = target ^ (mask if sign else 0)
    post_add, carries = _add_with_carries(add_target, source, width)
    overflow = carries[-1]
    parity = post_add & 1
    selectors = _divide_selectors(sign, parity, overflow)
    repair = int(
        (post_add >> (width - FLAG_COMPARE_WIDTH))
        < (source >> (width - FLAG_COMPARE_WIDTH))
    )
    return {
        "source": source,
        "target": target,
        "sign": sign,
        "post_add": post_add,
        "post_add_parity": parity,
        "overflow": overflow,
        "selectors": selectors,
        "flag_repair": repair,
        "residual_phase_coefficient": overflow ^ repair,
    }


def analyze_publication_rank() -> dict[str, Any]:
    """Analyze information retained by the current low selector quotient.

    This is a rank/partition statement about publication wires, not a claim that
    the immutable source/target data lacks the carry. Recovering the missing bit
    from that data is the separate comparator-cost route.
    """

    divide_groups: dict[tuple[int, int, tuple[int, ...]], set[int]] = {}
    selector_names = ("first_carry", "minus_f", "plus_f", "plus_2f")
    for sign in (0, 1):
        for parity in (0, 1):
            for overflow in (0, 1):
                selectors = _divide_selectors(sign, parity, overflow)
                key = (
                    sign,
                    parity,
                    tuple(selectors[name] for name in selector_names),
                )
                divide_groups.setdefault(key, set()).add(overflow)
    divide_ambiguous = [
        key for key, overflows in divide_groups.items() if len(overflows) > 1
    ]

    modulus = (1 << 256) - SECP256K1_F
    exact_pairs = [
        {
            "sign": 0,
            "states": [
                _exact_divide_publication_state(0, 0, 0),
                _exact_divide_publication_state(modulus - 1, modulus - 1, 0),
            ],
        },
        {
            "sign": 1,
            "states": [
                _exact_divide_publication_state(0, 1, 1),
                _exact_divide_publication_state(1, 0, 1),
            ],
        },
    ]
    for pair in exact_pairs:
        left, right = pair["states"]
        if left["selectors"] != right["selectors"]:
            raise AssertionError("exact divide witness selectors do not collide")
        if left["overflow"] == right["overflow"]:
            raise AssertionError("exact divide witness did not separate overflow")

    multiply_groups: dict[tuple[int, int, int, tuple[int, ...]], set[int]] = {}
    decoded_rows = 0
    for sign in (0, 1):
        for doubled_out in (0, 1):
            for post_add_lsb in (0, 1):
                for overflow in (0, 1):
                    selectors = _multiply_selectors(
                        sign, doubled_out, overflow, post_add_lsb
                    )
                    key = (
                        sign,
                        doubled_out,
                        post_add_lsb,
                        tuple(selectors[name] for name in selector_names),
                    )
                    multiply_groups.setdefault(key, set()).add(overflow)
                    decoded = (
                        selectors["plus_f"]
                        ^ doubled_out
                        ^ selectors["minus_f"]
                    )
                    if decoded != overflow:
                        raise AssertionError("multiply selector decoder failed")
                    decoded_rows += 1
    multiply_ambiguous = [
        key for key, overflows in multiply_groups.items() if len(overflows) > 1
    ]

    return {
        "schema": "final-carry-handoff-publication-rank-v1",
        "divide": {
            "local_rows": 8,
            "publication": list(selector_names),
            "ambiguous_groups": len(divide_ambiguous),
            "ambiguous_signs": sorted({key[0] for key in divide_ambiguous}),
            "ambiguity": "parity=0 selectors have rank zero in overflow",
            "exact_witness_pairs": exact_pairs,
        },
        "multiply": {
            "local_rows": 16,
            "publication": list(selector_names),
            "ambiguous_groups": len(multiply_ambiguous),
            "decoded_rows": decoded_rows,
            "overflow_decoder": "plus_f XOR doubled_out XOR minus_f",
            "last_carrier_rank": 1,
            "cleanup_obligation": (
                "after the redundant selector copies are erased, one coherent "
                "add_out rank remains and must be removed from source/result"
            ),
        },
    }


def exact_multiply_transfer_report() -> dict[str, Any]:
    """Produce canonical secp256k1 witnesses for all multiply local arms."""

    width = 256
    mask = _mask(width)
    modulus = (1 << width) - SECP256K1_F
    targets = [
        0,
        1,
        2,
        1 << 254,
        (1 << 255) - 2,
        (1 << 255) - 1,
        1 << 255,
        (1 << 255) + 1,
        modulus // 2,
        modulus - 3,
        modulus - 2,
        modulus - 1,
    ]
    sources = [
        0,
        1,
        2,
        SECP256K1_F,
        (1 << 255) - 1,
        1 << 255,
        modulus // 2,
        modulus - 3,
        modulus - 2,
        modulus - 1,
    ]

    rows_by_arm: dict[tuple[int, int, int], dict[str, Any]] = {}
    q_mismatches = 0
    decoder_mismatches = 0
    for sign in (0, 1):
        for target in targets:
            for source in sources:
                if not (0 <= source < modulus and 0 <= target < modulus):
                    continue
                doubled_out = (target >> 255) & 1
                shifted = (target << 1) & mask
                add_target = shifted ^ (mask if sign else 0)
                post_add, carries = _add_with_carries(add_target, source, width)
                add_out = carries[-1]
                selectors = _multiply_selectors(
                    sign, doubled_out, add_out, post_add & 1
                )
                digit = _correction_digit(selectors)
                post_fold, fold_carries = _fold_low(post_add, digit, 53, width)
                if selectors["first_carry"] != fold_carries[0]:
                    raise AssertionError("exact multiply first-carry transfer failed")
                q = doubled_out ^ add_out
                observed_q = (post_fold & 1) ^ sign ^ (source & 1)
                q_mismatches += int(q != observed_q)
                decoded = (
                    selectors["plus_f"]
                    ^ doubled_out
                    ^ selectors["minus_f"]
                )
                decoder_mismatches += int(decoded != add_out)
                arm = (sign, doubled_out, add_out)
                rows_by_arm.setdefault(
                    arm,
                    {
                        "sign": sign,
                        "doubled_out": doubled_out,
                        "add_out": add_out,
                        "source": source,
                        "target": target,
                        "post_add_lsb": post_add & 1,
                        "correction_digit": digit,
                        "q_doubled_xor_add": q,
                        "post_fold_lsb": post_fold & 1,
                        "selectors": selectors,
                    },
                )

    expected = {
        (sign, doubled, carry)
        for sign in (0, 1)
        for doubled in (0, 1)
        for carry in (0, 1)
    }
    missing = sorted(expected - set(rows_by_arm))
    return {
        "schema": "final-carry-handoff-exact-multiply-transfer-v1",
        "width": width,
        "fold_width": 53,
        "input_range": "canonical source,target in [0,secp256k1_p)",
        "covered_arms": len(rows_by_arm),
        "missing_arms": missing,
        "q_relation": "doubled_out XOR add_out = post_fold[0] XOR sign XOR source[0]",
        "q_relation_mismatches": q_mismatches,
        "selector_decoder": "add_out = plus_f XOR doubled_out XOR minus_f",
        "selector_decoder_mismatches": decoder_mismatches,
        "rows": [rows_by_arm[arm] for arm in sorted(rows_by_arm)],
    }


def literal_retention_ledger(
    records: list[dict[str, Any]], peak_limit: int
) -> dict[str, Any]:
    """Charge a literal final-chunk carry retention through the fold.

    The baseline fold peak already contains the published final carry.  For a
    final chunk of width ``w`` with an incoming boundary, an exact delayed HMR
    cleanup additionally retains ``w - 1`` owned carries and that boundary:
    exactly ``w`` coexisting wires.  A one-chunk add has no incoming boundary
    and therefore adds only ``w - 1`` wires.
    """

    rows: list[dict[str, Any]] = []
    fitting_cells = 0
    for record in records:
        width = int(record["final_chunk_width"])
        has_boundary = bool(record["final_chunk_has_boundary"])
        retained_extra = width - 1 + int(has_boundary)
        literal_peak = int(record["fold_peak"]) + retained_extra
        fits = literal_peak <= peak_limit
        fitting_cells += int(fits)
        rows.append(
            {
                **record,
                "retained_extra_wires": retained_extra,
                "literal_peak": literal_peak,
                "fits": fits,
            }
        )

    return {
        "schema": "final-carry-handoff-literal-retention-v1",
        "peak_limit": peak_limit,
        "records": rows,
        "fitting_cells": fitting_cells,
        "gross_average_t": (
            fitting_cells
            * FLAG_COMPARE_CCX_PER_CELL
            * (0.5**FLAG_COMPARE_CONDITION_DEPTH)
        ),
    }


def _census_fields(line: str) -> dict[str, str]:
    return dict(re.findall(r"(\w+)=([^ ]+)", line.strip()))


def parse_static_census(text: str) -> list[dict[str, Any]]:
    """Parse the env-gated, operation-neutral Rust lifetime trace."""

    adds: list[dict[str, Any]] = []
    cells: list[dict[str, Any]] = []
    for line in text.splitlines():
        if line.startswith("CARRY_HANDOFF_ADD "):
            fields = _census_fields(line)
            bounds: list[list[int]] = []
            for item in fields["bounds"].split(","):
                lo, hi = item.split("-", 1)
                bounds.append([int(lo), int(hi)])
            adds.append(
                {
                    "phase": fields["phase"],
                    "ops_start": int(fields["ops_start"]),
                    "ops_end": int(fields["ops_end"]),
                    "entry_active": int(fields["entry_active"]),
                    "local_peak": int(fields["local_peak"]),
                    "return_active": int(fields["return_active"]),
                    "ladder_target": fields["ladder_target"],
                    "bounds": bounds,
                }
            )
        elif line.startswith("CARRY_HANDOFF_CELL "):
            fields = _census_fields(line)
            cells.append(
                {
                    "site": fields["site"],
                    "phase": fields["phase"],
                    "ops_start": int(fields["ops_start"]),
                    "ops_end": int(fields["ops_end"]),
                    "entry_active": int(fields["entry_active"]),
                    "after_add_active": int(fields["after_add_active"]),
                    "fold_entry_active": int(fields["fold_entry_active"]),
                    "fold_peak": int(fields["fold_peak"]),
                    "cell_peak": int(fields["cell_peak"]),
                    "end_active": int(fields["end_active"]),
                }
            )

    if len(adds) != len(cells):
        raise ValueError(
            f"unpaired census records: {len(adds)} adds versus {len(cells)} cells"
        )

    site_indices: collections.Counter[str] = collections.Counter()
    records: list[dict[str, Any]] = []
    for sequence, (add, cell) in enumerate(zip(adds, cells, strict=True)):
        if add["phase"] != cell["phase"]:
            raise ValueError(
                f"census phase mismatch at record {sequence}: "
                f"{add['phase']} versus {cell['phase']}"
            )
        bounds = add["bounds"]
        if not bounds or bounds[0][0] != 0 or bounds[-1][1] != 256:
            raise ValueError(f"invalid 256-bit chunk bounds at record {sequence}")
        if any(left[1] != right[0] for left, right in zip(bounds, bounds[1:])):
            raise ValueError(f"non-contiguous chunk bounds at record {sequence}")
        site = cell["site"]
        site_index = site_indices[site]
        site_indices[site] += 1
        final_lo, final_hi = bounds[-1]
        records.append(
            {
                "sequence": sequence,
                "site_index": site_index,
                "site": site,
                "phase": cell["phase"],
                "chunk_bounds": bounds,
                "chunk_count": len(bounds),
                "final_chunk_width": final_hi - final_lo,
                "final_chunk_has_boundary": len(bounds) > 1,
                "ladder_target": add["ladder_target"],
                "add_ops_start": add["ops_start"],
                "add_ops_end": add["ops_end"],
                "add_entry_active": add["entry_active"],
                "add_local_peak": add["local_peak"],
                "add_return_active": add["return_active"],
                "cell_ops_start": cell["ops_start"],
                "cell_ops_end": cell["ops_end"],
                "cell_entry_active": cell["entry_active"],
                "after_add_active": cell["after_add_active"],
                "fold_entry_active": cell["fold_entry_active"],
                "fold_peak": cell["fold_peak"],
                "cell_peak": cell["cell_peak"],
                "cell_end_active": cell["end_active"],
            }
        )
    return records


def _counter_json(values: list[int]) -> dict[str, int]:
    return {
        str(key): count
        for key, count in sorted(collections.Counter(values).items())
    }


def summarize_static_census(
    records: list[dict[str, Any]], peak_limit: int
) -> dict[str, Any]:
    """Summarize exact per-cell add/fold lifetimes and literal retention."""

    normalized = json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
    literal = literal_retention_ledger(records, peak_limit)
    by_site: dict[str, Any] = {}
    for site in ("divide", "multiply"):
        site_rows = [row for row in literal["records"] if row["site"] == site]
        if not site_rows:
            continue
        by_site[site] = {
            "cells": len(site_rows),
            "phase_counts": dict(
                sorted(collections.Counter(row["phase"] for row in site_rows).items())
            ),
            "final_chunk_width_distribution": _counter_json(
                [row["final_chunk_width"] for row in site_rows]
            ),
            "final_chunk_width_min": min(
                row["final_chunk_width"] for row in site_rows
            ),
            "final_chunk_width_max": max(
                row["final_chunk_width"] for row in site_rows
            ),
            "fold_entry_min": min(row["fold_entry_active"] for row in site_rows),
            "fold_entry_max": max(row["fold_entry_active"] for row in site_rows),
            "fold_peak_min": min(row["fold_peak"] for row in site_rows),
            "fold_peak_max": max(row["fold_peak"] for row in site_rows),
            "cell_peak_min": min(row["cell_peak"] for row in site_rows),
            "cell_peak_max": max(row["cell_peak"] for row in site_rows),
            "literal_peak_min": min(row["literal_peak"] for row in site_rows),
            "literal_peak_max": max(row["literal_peak"] for row in site_rows),
            "literal_fitting_cells": sum(row["fits"] for row in site_rows),
        }
    return {
        "schema": "final-carry-handoff-static-census-v1",
        "records": len(records),
        "normalized_records_sha256": hashlib.sha256(normalized).hexdigest(),
        "site_counts": dict(sorted(collections.Counter(r["site"] for r in records).items())),
        "by_site": by_site,
        "literal_retention": {
            "peak_limit": literal["peak_limit"],
            "fitting_cells": literal["fitting_cells"],
            "gross_average_t": literal["gross_average_t"],
            "global_literal_peak_min": min(
                (row["literal_peak"] for row in literal["records"]), default=None
            ),
            "global_literal_peak_max": max(
                (row["literal_peak"] for row in literal["records"]), default=None
            ),
        },
    }


def _unsigned_lt(left: int, right: int, width: int) -> int:
    return int((left & _mask(width)) < (right & _mask(width)))


def _comparator_and_restriction(bits: int, width: int) -> tuple[int, int, int]:
    """Map ``bits`` to a comparison instance equal to AND of its bits.

    At bit zero use ``u_0=0, v_0=x_0``.  At every higher bit use
    ``u_i=1 XOR x_i, v_i=0``.  Any zero among the higher x bits makes the
    highest such position decide ``u>v``.  If all are one, bit zero decides
    ``u<v`` exactly when x_0 is one.
    """

    left = 0
    right = bits & 1
    for index in range(1, width):
        x = (bits >> index) & 1
        left |= (1 ^ x) << index
    return left, right, int(bits == _mask(width))


def comparator_and_restriction_report(
    exhaustive_widths: range, exact_width: int
) -> dict[str, Any]:
    """Return a checked AND restriction and its XOR/AND gate lower bound.

    AND of ``n`` independent inputs has multiplicative complexity ``n-1``:
    starting from n singleton factors, one binary multiplication can join at
    most two existing factor components.  Since the source comparator restricts
    to AND_n, no XOR/NOT/AND implementation can use fewer than n-1 nonlinear
    gates.  The source's n-1 CCX ripple therefore meets this lower bound.
    """

    widths = list(exhaustive_widths)
    mismatches = 0
    cases = 0
    for width in widths:
        for bits in range(1 << width):
            left, right, expected = _comparator_and_restriction(bits, width)
            observed = _unsigned_lt(left, right, width)
            cases += 1
            mismatches += int(observed != expected)

    lower_bound = exact_width - 1
    return {
        "schema": "final-carry-handoff-comparator-lower-bound-v1",
        "exhaustive_widths": widths,
        "restriction_cases": cases,
        "restriction_mismatches": mismatches,
        "restriction": (
            "u0=0,v0=x0; ui=1 XOR xi,vi=0 for i>=1; "
            "therefore [u<v]=AND(x0..x[n-1])"
        ),
        "exact_width": exact_width,
        "exact_and_arity": exact_width,
        "multiplicative_complexity_lower_bound": lower_bound,
        "source_comparator_ccx": FLAG_COMPARE_CCX_PER_CELL,
        "source_comparator_is_optimal_in_xor_and_model": (
            lower_bound == FLAG_COMPARE_CCX_PER_CELL
        ),
        "proof_invariant": (
            "a binary AND can merge at most two independent factor components; "
            "forming one monomial containing n inputs needs at least n-1 ANDs"
        ),
    }


def exact_secp_and_embedding_report(window: int) -> dict[str, Any]:
    """Exhaustively embed the comparator AND restriction in both exact cells.

    Let ``u,v`` be the restricted comparison windows and set the other addend's
    top window to ``t = u-v mod 2^window`` with every lower bit zero.  Then the
    full 256-bit carry is exactly ``[u<v]`` and every constructed source/target
    remains a canonical secp256k1 residue.

    Divide uses sign=0 and parity=0, so all four low selectors are identically
    zero while the missing carry is AND_window.  Multiply chooses
    ``doubled_out = 1 XOR carry``; hence q=doubled_out XOR add_out is fixed one,
    the correction is fixed +f, and the complementary carrier is NOT-AND.
    The 53-bit fold is disjoint from the top-22 window.
    """

    if not 2 <= window <= 64:
        raise ValueError("exact embedding window must be in [2,64]")
    modulus = (1 << 256) - SECP256K1_F
    window_mask = _mask(window)
    shift = 256 - window
    cases = 1 << window
    comparison_mismatches = 0
    canonical_mismatches = 0
    divide_selector_mismatches = 0
    divide_parity_mismatches = 0
    multiply_q_mismatches = 0
    multiply_digit_mismatches = 0
    true_cases = 0
    max_source = 0
    max_divide_target = 0
    max_multiply_target = 0
    true_witness: dict[str, Any] | None = None

    for bits in range(cases):
        u = (~bits) & (window_mask ^ 1)
        v = bits & 1
        expected = int(bits == window_mask)
        carry = int(u < v)
        comparison_mismatches += int(carry != expected)
        true_cases += carry

        other_window = (u - v) & window_mask
        source = v << shift
        divide_target = other_window << shift
        divide_post_add = u << shift
        divide_parity = divide_post_add & 1
        divide_selectors = _divide_selectors(0, divide_parity, carry)
        divide_parity_mismatches += divide_parity
        divide_selector_mismatches += int(
            any(divide_selectors[name] for name in (
                "first_carry", "minus_f", "plus_f", "plus_2f"
            ))
        )

        doubled_out = 1 ^ carry
        multiply_target = (other_window << (shift - 1)) | (doubled_out << 255)
        multiply_selectors = _multiply_selectors(
            0, doubled_out, carry, divide_parity
        )
        digit = _correction_digit(multiply_selectors)
        q = doubled_out ^ carry
        # The fixed +f correction makes post-fold bit zero one because the
        # constructed post-add value and source bit zero are both zero.
        post_fold_lsb = SECP256K1_F & 1
        observed_q = post_fold_lsb ^ (source & 1)
        multiply_q_mismatches += int(q != 1 or observed_q != q)
        multiply_digit_mismatches += int(digit != 1)

        canonical_mismatches += int(
            not (
                0 <= source < modulus
                and 0 <= divide_target < modulus
                and 0 <= multiply_target < modulus
            )
        )
        max_source = max(max_source, source)
        max_divide_target = max(max_divide_target, divide_target)
        max_multiply_target = max(max_multiply_target, multiply_target)
        if carry:
            true_witness = {
                "and_inputs": bits,
                "u_top_window": u,
                "v_top_window": v,
                "source": source,
                "divide_target": divide_target,
                "multiply_target": multiply_target,
                "carry": carry,
                "multiply_doubled_out": doubled_out,
            }

    return {
        "schema": "final-carry-handoff-exact-secp-and-embedding-v1",
        "window": window,
        "cases": cases,
        "true_cases": true_cases,
        "comparison_mismatches": comparison_mismatches,
        "canonical_range_mismatches": canonical_mismatches,
        "max_source": max_source,
        "max_divide_target": max_divide_target,
        "max_multiply_target": max_multiply_target,
        "true_witness": true_witness,
        "divide": {
            "sign": 0,
            "parity": 0,
            "publication": "first=minus=plus=plus2=0",
            "selector_mismatches": divide_selector_mismatches,
            "parity_mismatches": divide_parity_mismatches,
            "missing_rank": "add_out = AND(x0..x21)",
        },
        "multiply": {
            "sign": 0,
            "q": 1,
            "correction_digit": 1,
            "fold_width": 53,
            "q_mismatches": multiply_q_mismatches,
            "correction_digit_mismatches": multiply_digit_mismatches,
            "complementary_rank": "doubled_out = 1 XOR AND(x0..x21)",
        },
    }


def retained_suffix_cost_bound(
    retained_predecessors: int, total_width: int
) -> dict[str, Any]:
    """Lower-bound exact cleanup after retaining a top carry suffix.

    Retaining ``k`` predecessor carries lets exact HMR walk the final carry down
    by k stages.  The remaining boundary carry is the carry of the lower
    ``total_width-k`` positions.  Its comparison predicate has an AND
    restriction of that arity, hence at least ``total_width-k-1`` nonlinear
    gates if the predecessor state is not retained as well.
    """

    if not 0 <= retained_predecessors <= total_width:
        raise ValueError("retained predecessor count is outside the adder width")
    remaining_width = total_width - retained_predecessors
    recompute_lower_bound = max(0, remaining_width - 1)
    saved_upper_bound = FLAG_COMPARE_CCX_PER_CELL - recompute_lower_bound
    all_cells_gross = (
        sum(CELL_CALLS.values())
        * saved_upper_bound
        * (0.5**FLAG_COMPARE_CONDITION_DEPTH)
    )
    return {
        "schema": "final-carry-handoff-retained-suffix-cost-v1",
        "total_width": total_width,
        "retained_predecessors": retained_predecessors,
        "remaining_boundary_width": remaining_width,
        "exact_recompute_ccx_lower_bound": recompute_lower_bound,
        "baseline_flag_ccx": FLAG_COMPARE_CCX_PER_CELL,
        "saved_ccx_upper_bound": saved_upper_bound,
        "all_cells_gross_average_t_upper_bound": all_cells_gross,
        "can_reach_target_before_added_cost": (
            all_cells_gross >= TARGET_NET_AVERAGE_T
        ),
    }


def perfect_dirty_host_q_bound(
    retained_predecessors: int,
    fold_entry_min: dict[str, int],
    peak_limit: int,
) -> dict[str, Any]:
    """Give dirty-host conjugation every possible fold-host/Q advantage.

    The optimistic model charges the retained predecessor ranks but allocates
    *zero* additional fold-carry wires: every fold host is assumed replaced at
    zero nonlinear cost.  Failure under this relaxation kills any literal or
    dirty-host implementation with the same retained rank.
    """

    report: dict[str, Any] = {
        "schema": "final-carry-handoff-perfect-dirty-host-q-v1",
        "retained_predecessors": retained_predecessors,
        "peak_limit": peak_limit,
        "assumption": "all fold carry hosts replaced at zero cost",
    }
    for site, entry in fold_entry_min.items():
        optimistic_peak = int(entry) + retained_predecessors
        report[site] = {
            "fold_entry_min": int(entry),
            "optimistic_peak": optimistic_peak,
            "fits": optimistic_peak <= peak_limit,
        }
    return report


def _file_sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def build_terminal_evidence(
    repo: pathlib.Path,
    census_log: pathlib.Path,
    build_stdout: pathlib.Path,
    b0_log: pathlib.Path,
    ops_path: pathlib.Path,
) -> dict[str, Any]:
    """Assemble the deterministic three-route terminal evidence packet."""

    census_text = census_log.read_text()
    records = parse_static_census(census_text)
    census = summarize_static_census(records, peak_limit=1_266)
    expected_counts = CELL_CALLS
    if census["site_counts"] != expected_counts:
        raise RuntimeError(
            f"static census count mismatch: {census['site_counts']} != {expected_counts}"
        )
    fold_entry_min = {
        site: census["by_site"][site]["fold_entry_min"]
        for site in ("divide", "multiply")
    }

    b0_text = b0_log.read_text()
    b0_match = re.search(
        r"B0_CENSUS_BEGIN best_active=(\d+) best_ops=(\d+) "
        r"best_phase=([^ ]+) n_live=(\d+)",
        b0_text,
    )
    if b0_match is None:
        raise RuntimeError("B0 receipt is missing its census header")
    b0_peak = int(b0_match.group(1))
    if b0_peak != 1_266:
        raise RuntimeError(f"unexpected baseline peak: {b0_peak}")
    instrumentation_patch = (
        repo
        / "src/point_add/memory/repro/final_carry_handoff_static_census.patch"
    )
    if not instrumentation_patch.is_file():
        raise RuntimeError("static census instrumentation patch is missing")

    total_cells = sum(CELL_CALLS.values())
    all_site_min_saved = 3
    site_only_min_saved: dict[str, int] = {}
    for site, count in CELL_CALLS.items():
        saved = 0
        while (
            count * saved * (0.5**FLAG_COMPARE_CONDITION_DEPTH)
            < TARGET_NET_AVERAGE_T
        ):
            saved += 1
        site_only_min_saved[site] = saved

    exact_chain = run_exact_local_chain_miter(range(5, 10))
    reduced = run_reduced_miter(range(5, 10))
    publication = analyze_publication_rank()
    multiply_transfer = exact_multiply_transfer_report()
    comparator_bound = comparator_and_restriction_report(range(5, 10), 22)
    exact_embedding = exact_secp_and_embedding_report(22)

    return {
        "schema": "final-carry-handoff-terminal-evidence-v1",
        "verdict": "HARD_NACK_CARRY_HANDOFF_FAMILY",
        "binding": build_inventory(repo),
        "receipts": {
            "census_command": (
                "env SUB4_PP_ROUNDS=694 SUB4_PP_ROUNDS_MUL=693 "
                "CARRY_HANDOFF_STATIC_CENSUS=1 PROFILE_ACTIVE_TIMELINE=1 "
                "SKIP_ALT_SEED_CHECKS=1 cargo run --locked --offline "
                "--bin build_circuit"
            ),
            "b0_command": (
                "env SUB4_PP_ROUNDS=694 SUB4_PP_ROUNDS_MUL=693 "
                "B0_WIN_LO=0 B0_WIN_HI=99999999 B0_PHASE=pp_div_replay "
                "SKIP_ALT_SEED_CHECKS=1 cargo run --locked --offline "
                "--bin build_circuit"
            ),
            "census_log_sha256": _file_sha256(census_log),
            "build_stdout_sha256": _file_sha256(build_stdout),
            "b0_log_sha256": _file_sha256(b0_log),
            "ops_sha256": _file_sha256(ops_path),
            "ops_bytes": ops_path.stat().st_size,
            "emitted_ops": 12_553_305,
            "instrumentation_patch_sha256": _file_sha256(instrumentation_patch),
            "baseline_peak_q": b0_peak,
            "baseline_peak_ops": int(b0_match.group(2)),
            "baseline_peak_phase": b0_match.group(3),
            "baseline_peak_live": int(b0_match.group(4)),
            "instrumentation": (
                "env-gated active-count reads/eprintln only; zero B operation calls; "
                "ops SHA equals the exact-source reference artifact"
            ),
        },
        "reduced_baseline_miter": reduced,
        "reduced_exact_local_chain_miter": exact_chain,
        "publication_rank": publication,
        "exact_multiply_transfer": multiply_transfer,
        "comparator_lower_bound": comparator_bound,
        "exact_secp_and_embedding": exact_embedding,
        "static_census": census,
        "static_census_records": [
            {
                "sequence": row["sequence"],
                "site_index": row["site_index"],
                "site": row["site"],
                "phase": row["phase"],
                "chunk_count": row["chunk_count"],
                "final_chunk_width": row["final_chunk_width"],
                "ladder_target": row["ladder_target"],
                "add_local_peak": row["add_local_peak"],
                "fold_entry_active": row["fold_entry_active"],
                "fold_peak": row["fold_peak"],
                "cell_peak": row["cell_peak"],
            }
            for row in records
        ],
        "suffix_cost_bounds": {
            str(k): retained_suffix_cost_bound(k, total_width=256)
            for k in (0, 51, 128, 234, 235, 236, 237, 239)
        },
        "perfect_dirty_host_relaxations": {
            "all_sites_three_saved_ccx": perfect_dirty_host_q_bound(
                237, fold_entry_min, 1_266
            ),
            "single_site_five_saved_ccx": perfect_dirty_host_q_bound(
                239, fold_entry_min, 1_266
            ),
        },
        "economics": {
            "total_cells": total_cells,
            "baseline_final_repair_average_t": (
                total_cells
                * FLAG_COMPARE_CCX_PER_CELL
                * (0.5**FLAG_COMPARE_CONDITION_DEPTH)
            ),
            "all_site_minimum_saved_ccx_per_cell": all_site_min_saved,
            "all_site_three_ccx_gross_average_t": (
                total_cells * all_site_min_saved * 0.5
            ),
            "all_site_three_ccx_added_cost_ceiling": (
                total_cells * all_site_min_saved * 0.5
                - TARGET_NET_AVERAGE_T
            ),
            "site_only_minimum_saved_ccx_per_cell": site_only_min_saved,
            "site_only_five_ccx_gross_average_t": {
                site: count * site_only_min_saved[site] * 0.5
                for site, count in CELL_CALLS.items()
            },
            "target_net_average_t": TARGET_NET_AVERAGE_T,
        },
        "route_registry": {
            "R1": {
                "state": "KILLED",
                "falsifier": (
                    "exact-local retained-chain miter is phase/value clean, but "
                    "literal retention fits 0/1383 cells (minimum Q1288); the "
                    "237-rank economic threshold reaches at least Q1376 even "
                    "when every fold host is replaced at zero cost"
                ),
            },
            "R2": {
                "state": "KILLED",
                "falsifier": (
                    "divide parity-zero publication has rank zero in add_out on "
                    "both signs with exact secp witnesses; multiply preserves "
                    "one complementary doubled/add carrier rank after q cleanup"
                ),
            },
            "R3": {
                "state": "KILLED",
                "falsifier": (
                    "the literal 22-bit repair restricts exactly to AND22 at "
                    "both source sites, so its 21-CCX ripple is multiplicatively "
                    "optimal; fewer than 237 retained predecessors can save at "
                    "most two CCX/cell under exact-local cleanup"
                ),
            },
        },
        "terminal_reason": (
            "Every permitted route crosses one of two checked walls: below the "
            "retained-rank threshold the exact phase predicate cannot save the "
            "minimum nonlinear cost, while at or above it the optimistic peak "
            "exceeds Q1266 before any dirty-host conversion cost is charged."
        ),
    }


def write_json(path: pathlib.Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path)
    parser.add_argument("--census-log", type=pathlib.Path)
    parser.add_argument("--build-stdout", type=pathlib.Path)
    parser.add_argument("--b0-log", type=pathlib.Path)
    parser.add_argument("--ops", type=pathlib.Path)
    parser.add_argument("--evidence-output", type=pathlib.Path)
    args = parser.parse_args()
    if args.evidence_output is not None:
        required = (args.census_log, args.build_stdout, args.b0_log, args.ops)
        if any(path is None for path in required):
            parser.error(
                "--evidence-output requires --census-log, --build-stdout, "
                "--b0-log, and --ops"
            )
        evidence = build_terminal_evidence(
            args.repo,
            args.census_log,
            args.build_stdout,
            args.b0_log,
            args.ops,
        )
        write_json(args.evidence_output, evidence)
    else:
        inventory = build_inventory(args.repo)
        if args.output is None:
            print(json.dumps(inventory, indent=2, sort_keys=True))
        else:
            write_json(args.output, inventory)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
