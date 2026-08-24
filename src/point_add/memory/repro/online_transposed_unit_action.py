#!/usr/bin/env python3
"""Exact collision gate for an online transposed Euclid row action."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Sequence
from typing import Any

import affine_shell_transducer as shell
import quotient_euclid_unit_action as euclid


BASE_COMMIT = "cbf229dbd46a7c677fe2e28da882b4f8a02bac7f"
BASE_TREE = "eab2326ce33549eceeb5c10aa64eae33f148b0ac"
TEST_PRIMES = (31, 61, 127, 251)


def row_apply(quotients: Sequence[int], left: int, right: int) -> tuple[int, int]:
    """Right-multiply a row by E(q_0)...E(q_last)."""
    for quotient in quotients:
        left, right = right, left - quotient * right
    return left, right


def alternate_quotients(modulus: int, multiplier: int) -> tuple[int, ...]:
    canonical = euclid.euclid_trace(modulus, multiplier)
    if canonical[-1] < 2:
        raise AssertionError("canonical final quotient must be at least two")
    return canonical[:-1] + (canonical[-1] - 1, 1)


def matrix_from_quotients(
    modulus: int,
    multiplier: int,
    quotients: Sequence[int],
) -> dict[str, Any]:
    first_row = row_apply(quotients, 1, 0)
    second_row = row_apply(quotients, 0, 1)
    if first_row[1] == multiplier:
        sign = 1
    elif first_row[1] == -multiplier:
        sign = -1
    else:
        raise AssertionError("quotient product does not contain multiplier column")
    rows = (
        (sign * first_row[0], sign * first_row[1]),
        (sign * second_row[0], sign * second_row[1]),
    )
    r = -rows[0][0]
    k = rows[1][0]
    reduced_row = (
        modulus * rows[0][0] + multiplier * rows[1][0],
        modulus * rows[0][1] + multiplier * rows[1][1],
    )
    if reduced_row not in ((1, 0), (-1, 0)):
        raise AssertionError("normalized quotient row must terminate at signed one")
    return {
        "quotients": tuple(quotients),
        "sign": sign,
        "rows": rows,
        "r": r,
        "k": k,
        "reduced_row": reduced_row,
        "orientation": reduced_row[0],
    }


def normalized_matrix(modulus: int, multiplier: int) -> dict[str, Any]:
    return matrix_from_quotients(
        modulus,
        multiplier,
        euclid.euclid_trace(modulus, multiplier),
    )


def online_action(
    modulus: int,
    multiplier: int,
    value: int,
    seed: int = 0,
    *,
    alternate: bool = False,
) -> tuple[int, int]:
    if value < 0 or value >= modulus or seed < 0 or seed >= modulus:
        raise ValueError("value and seed must be canonical modulo modulus")
    quotients = (
        alternate_quotients(modulus, multiplier)
        if alternate
        else euclid.euclid_trace(modulus, multiplier)
    )
    matrix = matrix_from_quotients(modulus, multiplier, quotients)
    (a, b), (c, d) = matrix["rows"]
    return (a * value + c * seed) % modulus, (b * value + d * seed) % modulus


def direction_ratio(
    modulus: int,
    multiplier: int,
    *,
    alternate: bool = False,
) -> int:
    quotients = (
        alternate_quotients(modulus, multiplier)
        if alternate
        else euclid.euclid_trace(modulus, multiplier)
    )
    matrix = matrix_from_quotients(modulus, multiplier, quotients)
    direction_g = matrix["rows"][0][0] % modulus
    return direction_g * pow(multiplier, -1, modulus) % modulus


def first_nonparallel_pair(
    modulus: int,
    *,
    alternate: bool = False,
) -> tuple[int, int]:
    first = 1
    first_ratio = direction_ratio(modulus, first, alternate=alternate)
    for multiplier in range(2, modulus):
        if direction_ratio(modulus, multiplier, alternate=alternate) != first_ratio:
            return first, multiplier
    raise ValueError("all fixed-multiplier line directions are parallel")


def line_intersection(
    modulus: int,
    multiplier_1: int,
    seed_1: int,
    multiplier_2: int,
    seed_2: int,
    *,
    alternate: bool = False,
) -> dict[str, Any]:
    if multiplier_1 == multiplier_2:
        raise ValueError("multipliers must differ")
    matrices = []
    for multiplier in (multiplier_1, multiplier_2):
        quotients = (
            alternate_quotients(modulus, multiplier)
            if alternate
            else euclid.euclid_trace(modulus, multiplier)
        )
        matrices.append(matrix_from_quotients(modulus, multiplier, quotients))
    (a1, _), (c1_unit, _) = matrices[0]["rows"]
    (a2, _), (c2_unit, _) = matrices[1]["rows"]
    intercept_1 = c1_unit * seed_1 % modulus
    intercept_2 = c2_unit * seed_2 % modulus
    lambda_2_scale = multiplier_1 * pow(multiplier_2, -1, modulus) % modulus
    denominator = (a1 - a2 * lambda_2_scale) % modulus
    if denominator == 0:
        raise ValueError("lines are parallel")
    lambda_1 = (
        (intercept_2 - intercept_1) * pow(denominator, -1, modulus)
    ) % modulus
    lambda_2 = lambda_2_scale * lambda_1 % modulus
    output_1 = online_action(
        modulus,
        multiplier_1,
        lambda_1,
        seed_1 % modulus,
        alternate=alternate,
    )
    output_2 = online_action(
        modulus,
        multiplier_2,
        lambda_2,
        seed_2 % modulus,
        alternate=alternate,
    )
    if output_1 != output_2:
        raise AssertionError("nonparallel line intersection failed to replay")
    return {
        "input_1": (multiplier_1, lambda_1),
        "input_2": (multiplier_2, lambda_2),
        "seed_1": seed_1 % modulus,
        "seed_2": seed_2 % modulus,
        "output_1": output_1,
        "output_2": output_2,
    }


def _case_report(modulus: int, *, alternate: bool) -> dict[str, Any]:
    product_failures = 0
    matrix_failures = 0
    ratios: dict[int, list[int]] = {}
    transcript = hashlib.sha256()
    byte_width = (modulus.bit_length() + 7) // 8
    for multiplier in range(1, modulus):
        quotients = (
            alternate_quotients(modulus, multiplier)
            if alternate
            else euclid.euclid_trace(modulus, multiplier)
        )
        matrix = matrix_from_quotients(modulus, multiplier, quotients)
        matrix_failures += matrix["reduced_row"][1] != 0
        matrix_failures += abs(matrix["reduced_row"][0]) != 1
        matrix_failures += (
            matrix["k"] * multiplier - matrix["r"] * modulus
            != matrix["orientation"]
        )
        ratio = matrix["rows"][0][0] * pow(multiplier, -1, modulus) % modulus
        ratios.setdefault(ratio, []).append(multiplier)
        for value in range(modulus):
            garbage, product = online_action(
                modulus,
                multiplier,
                value,
                alternate=alternate,
            )
            product_failures += product != multiplier * value % modulus
            for item in (multiplier, value, garbage, product):
                transcript.update(item.to_bytes(byte_width, "big"))

    t1, t2 = first_nonparallel_pair(modulus, alternate=alternate)
    witnesses = []
    for seed_name, seed_function in (
        ("zero", lambda value: 0),
        ("one", lambda value: 1),
        ("identity", lambda value: value),
        ("square", lambda value: value * value % modulus),
    ):
        witness = line_intersection(
            modulus,
            t1,
            seed_function(t1),
            t2,
            seed_function(t2),
            alternate=alternate,
        )
        witness["seed_family"] = seed_name
        witnesses.append(witness)

    return {
        "modulus": modulus,
        "width": modulus.bit_length(),
        "expansion": "alternate_final_one" if alternate else "canonical",
        "multipliers": modulus - 1,
        "input_pairs": modulus * (modulus - 1),
        "matrix_failures": matrix_failures,
        "product_failures": product_failures,
        "distinct_direction_ratios": len(ratios),
        "largest_parallel_family": max(len(values) for values in ratios.values()),
        "first_nonparallel_pair": (t1, t2),
        "universal_collision_proved": len(ratios) > 1,
        "representative_intersections": witnesses,
        "transcript_sha256": transcript.hexdigest(),
    }


def case_report(modulus: int) -> dict[str, Any]:
    return _case_report(modulus, alternate=False)


def alternate_expansion_report(modulus: int) -> dict[str, Any]:
    return _case_report(modulus, alternate=True)


def run_gate() -> dict[str, Any]:
    canonical_cases = [case_report(modulus) for modulus in TEST_PRIMES]
    alternate_cases = [alternate_expansion_report(modulus) for modulus in TEST_PRIMES]
    exact_passed = all(
        case["matrix_failures"] == 0 and case["product_failures"] == 0
        for case in canonical_cases + alternate_cases
    )
    collision_proved = all(
        case["universal_collision_proved"]
        for case in canonical_cases + alternate_cases
    )
    payload: dict[str, Any] = {
        "schema": "online-transposed-unit-action-v1",
        "scope": "SEPARABLE_SECOND_SEED_H_OF_T",
        "base_commit": BASE_COMMIT,
        "base_tree": BASE_TREE,
        "canonical_cases": canonical_cases,
        "alternate_final_expansion_cases": alternate_cases,
        "exact_online_product_passed": exact_passed,
        "universal_line_collision_proved": collision_proved,
        "verdict": (
            "HARD_NACK_ONLINE_TRANSPOSED_SEPARABLE_SEED"
            if exact_passed and collision_proved
            else "HOLD_ONLINE_TRANSPOSED_SEPARABLE_SEED"
        ),
        "full_field_candidate": False,
        "next_grammar": "NONLINEAR_COUPLED_TRANSPOSED_ACTION",
        "authority": {
            "provider": False,
            "nonce_grind": False,
            "fleet": False,
            "queue": False,
            "push": False,
            "public_note": False,
            "promotion": False,
            "submission": False,
        },
    }
    payload["receipt_sha256"] = hashlib.sha256(shell.canonical_json(payload)).hexdigest()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run_gate(), sort_keys=True, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
