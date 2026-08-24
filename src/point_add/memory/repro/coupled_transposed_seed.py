#!/usr/bin/env python3
"""Exact ideal identity and bounded-degree gate for a coupled Euclid seed."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Sequence
from typing import Any

import affine_shell_transducer as shell
import online_transposed_unit_action as online


BASE_COMMIT = "cbf229dbd46a7c677fe2e28da882b4f8a02bac7f"
BASE_TREE = "eab2326ce33549eceeb5c10aa64eae33f148b0ac"
TEST_PRIMES = (31, 61, 127, 251)


def orientation_one_matrix(modulus: int, multiplier: int) -> dict[str, Any]:
    matrix = online.normalized_matrix(modulus, multiplier)
    if matrix["orientation"] == 1:
        return matrix
    alternate = online.matrix_from_quotients(
        modulus,
        multiplier,
        online.alternate_quotients(modulus, multiplier),
    )
    if alternate["orientation"] != 1:
        raise AssertionError("alternate final-one expansion must flip orientation")
    return alternate


def cofactor_seed_value(modulus: int, multiplier: int) -> int:
    """Return ``T*r_T`` modulo p, totalized to zero at T=0."""
    if multiplier == 0:
        return 0
    if multiplier < 0 or multiplier >= modulus:
        raise ValueError("multiplier must be canonical modulo modulus")
    matrix = orientation_one_matrix(modulus, multiplier)
    return multiplier * matrix["r"] % modulus


def aligned_seed_coefficient(
    modulus: int,
    multiplier: int,
    common_direction: int,
) -> int:
    """The unique coefficient rotating the fixed-T line to a common slope."""
    if common_direction < 0 or common_direction >= modulus:
        raise ValueError("common direction must be canonical modulo modulus")
    return (
        cofactor_seed_value(modulus, multiplier)
        + common_direction * multiplier * multiplier
    ) % modulus


def ideal_action(modulus: int, multiplier: int, value: int) -> tuple[int, int]:
    """Apply the oracle-supplied coupled seed with common direction zero."""
    if value < 0 or value >= modulus:
        raise ValueError("value must be canonical modulo modulus")
    matrix = orientation_one_matrix(modulus, multiplier)
    coupled = cofactor_seed_value(modulus, multiplier) * value
    intercept_seed = multiplier * multiplier
    second_seed = (coupled + intercept_seed) % modulus
    (a, b), (c, d) = matrix["rows"]
    return (
        (a * value + c * second_seed) % modulus,
        (b * value + d * second_seed) % modulus,
    )


def interpolate_full_field(values: Sequence[int], modulus: int) -> tuple[int, ...]:
    """Interpolate values at nodes 0..p-1 into the unique degree-<p polynomial."""
    if len(values) != modulus:
        raise ValueError("one value is required for every field element")
    divided = [value % modulus for value in values]
    for order in range(1, modulus):
        inverse_denominator = pow(order, -1, modulus)
        for index in range(modulus - 1, order - 1, -1):
            divided[index] = (
                (divided[index] - divided[index - 1]) * inverse_denominator
            ) % modulus

    coefficients = [0] * modulus
    basis = [1]
    for order in range(modulus):
        for index, coefficient in enumerate(basis):
            coefficients[index] = (
                coefficients[index] + divided[order] * coefficient
            ) % modulus
        if order + 1 == modulus:
            continue
        next_basis = [0] * (len(basis) + 1)
        for index, coefficient in enumerate(basis):
            next_basis[index] = (
                next_basis[index] - order * coefficient
            ) % modulus
            next_basis[index + 1] = (
                next_basis[index + 1] + coefficient
            ) % modulus
        basis = next_basis
    return tuple(coefficients)


def evaluate_polynomial(
    coefficients: Sequence[int],
    value: int,
    modulus: int,
) -> int:
    result = 0
    for coefficient in reversed(coefficients):
        result = (result * value + coefficient) % modulus
    return result


def case_report(modulus: int) -> dict[str, Any]:
    orientation_failures = 0
    ideal_output_failures = 0
    transcript = hashlib.sha256()
    byte_width = (modulus.bit_length() + 7) // 8
    seed_values = [0]

    for multiplier in range(1, modulus):
        matrix = orientation_one_matrix(modulus, multiplier)
        orientation_failures += matrix["orientation"] != 1
        orientation_failures += matrix["reduced_row"] != (1, 0)
        orientation_failures += (
            matrix["k"] * multiplier - matrix["r"] * modulus != 1
        )
        seed_values.append(multiplier * matrix["r"] % modulus)
        for value in range(modulus):
            kept, product = ideal_action(modulus, multiplier, value)
            ideal_output_failures += (kept, product) != (
                multiplier,
                multiplier * value % modulus,
            )
            for item in (multiplier, value, kept, product):
                transcript.update(item.to_bytes(byte_width, "big"))

    coefficients = interpolate_full_field(seed_values, modulus)
    interpolation_failures = sum(
        evaluate_polynomial(coefficients, value, modulus) != seed_values[value]
        for value in range(modulus)
    )
    degree = max(
        index for index, coefficient in enumerate(coefficients) if coefficient != 0
    )
    nonzero_terms = sum(coefficient != 0 for coefficient in coefficients)
    quadratic_nonzero = coefficients[2] != 0
    best_terms = nonzero_terms - int(quadratic_nonzero)
    best_degree = degree if degree > 2 else 2

    return {
        "modulus": modulus,
        "width": modulus.bit_length(),
        "input_pairs": modulus * (modulus - 1),
        "orientation_failures": orientation_failures,
        "ideal_output_failures": ideal_output_failures,
        "interpolation_failures": interpolation_failures,
        "cofactor_polynomial_degree": degree,
        "cofactor_polynomial_nonzero_terms": nonzero_terms,
        "cofactor_polynomial_coefficients": coefficients,
        "quadratic_coefficient_nonzero": quadratic_nonzero,
        "best_degree_after_c_times_t_squared": best_degree,
        "best_nonzero_terms_after_c_times_t_squared": best_terms,
        "transcript_sha256": transcript.hexdigest(),
    }


def run_gate() -> dict[str, Any]:
    cases = [case_report(modulus) for modulus in TEST_PRIMES]
    identity_passed = all(
        case["orientation_failures"] == 0
        and case["ideal_output_failures"] == 0
        and case["interpolation_failures"] == 0
        for case in cases
    )
    full_degree = all(
        case["cofactor_polynomial_degree"] == case["modulus"] - 1
        and case["best_degree_after_c_times_t_squared"] == case["modulus"] - 1
        for case in cases
    )
    payload: dict[str, Any] = {
        "schema": "coupled-transposed-seed-v1",
        "scope": "IDEAL_IDENTITY_AND_BOUNDED_DEGREE_FIELD_POLYNOMIAL_GENERATOR",
        "base_commit": BASE_COMMIT,
        "base_tree": BASE_TREE,
        "cases": cases,
        "identity_verdict": (
            "ADMIT_IDEAL_COUPLED_SEED_IDENTITY_ONLY"
            if identity_passed
            else "HARD_NACK_IDEAL_COUPLED_SEED_IDENTITY"
        ),
        "verdict": (
            "HARD_NACK_BOUNDED_DEGREE_COUPLED_SEED"
            if identity_passed and full_degree
            else "HOLD_BOUNDED_DEGREE_COUPLED_SEED"
        ),
        "full_field_candidate": False,
        "remaining_blocker": "CIRCULAR_T_TIMES_R_TIMES_LAMBDA_SEED_PRODUCT",
        "next_grammar": "ONLINE_COFACTOR_PRODUCT_RECURRENCE",
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
