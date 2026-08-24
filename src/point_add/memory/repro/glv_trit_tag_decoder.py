#!/usr/bin/env python3
"""Exact GLV trit interpretation and low-degree tag decoder gates."""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
from collections import defaultdict
from typing import Any, Sequence

import affine_shell_transducer as shell
import coupled_transposed_seed as coupled
import curve_support_online_constant_seed as support


BASE_COMMIT = "cbf229dbd46a7c677fe2e28da882b4f8a02bac7f"
BASE_TREE = "eab2326ce33549eceeb5c10aa64eae33f148b0ac"
TEST_PRIMES = support.TEST_PRIMES
GLV_PRIMES = tuple(prime for prime in TEST_PRIMES if prime % 3 == 1)


def matrix_rank(rows: Sequence[Sequence[int]], modulus: int) -> int:
    matrix = [[value % modulus for value in row] for row in rows]
    rank = 0
    columns = len(matrix[0]) if matrix else 0
    for column in range(columns):
        pivot = next(
            (
                row
                for row in range(rank, len(matrix))
                if matrix[row][column] != 0
            ),
            None,
        )
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        inverse = pow(matrix[rank][column], -1, modulus)
        matrix[rank] = [value * inverse % modulus for value in matrix[rank]]
        for row in range(rank + 1, len(matrix)):
            if matrix[row][column] == 0:
                continue
            scale = matrix[row][column]
            matrix[row] = [
                (left - scale * right) % modulus
                for left, right in zip(matrix[row], matrix[rank])
            ]
        rank += 1
        if rank == len(matrix):
            break
    return rank


@functools.lru_cache(maxsize=None)
def _first_point_rows(modulus: int) -> tuple[dict[str, int], ...]:
    classical_x, classical_y = support.first_classical_point(modulus)
    rows = []
    for output_x, output_y in support.curve_points(modulus):
        multiplier = (classical_x - output_x) % modulus
        if multiplier == 0:
            continue
        product = (output_y + classical_y) % modulus
        value = product * pow(multiplier, -1, modulus) % modulus
        matrix = coupled.orientation_one_matrix(modulus, multiplier)
        r = matrix["r"] % modulus
        k = matrix["k"] % modulus
        rows.append(
            {
                "T": multiplier,
                "lambda": value,
                "z": product,
                "r": r,
                "k": k,
                "output_x": output_x,
                "output_y": output_y,
            }
        )
    return tuple(rows)


@functools.lru_cache(maxsize=None)
def linear_seed_affine_case_report(modulus: int) -> dict[str, Any]:
    features = []
    augmented = []
    for row in _first_point_rows(modulus):
        values = (
            -row["r"] * row["lambda"],
            row["k"] * row["lambda"],
            row["k"] * row["T"],
            row["k"],
            row["z"],
            1,
        )
        features.append(values)
        augmented.append((*values, row["T"]))
    feature_rank = matrix_rank(features, modulus)
    augmented_rank = matrix_rank(augmented, modulus)
    return {
        "modulus": modulus,
        "width": modulus.bit_length(),
        "support_states": len(features),
        "features": (
            "-r*lambda",
            "k*lambda",
            "k*T",
            "k",
            "z",
            "1",
        ),
        "feature_rank": feature_rank,
        "augmented_rank": augmented_rank,
        "relaxed_affine_decoder_exists": augmented_rank == feature_rank,
    }


@functools.lru_cache(maxsize=None)
def linear_fractional_case_report(modulus: int) -> dict[str, Any]:
    first = support.first_point_affine_decoder_report(modulus)
    selected = first["selected_seed"]
    rows = []
    outputs: set[tuple[int, int]] = set()
    for row in _first_point_rows(modulus):
        garbage = (
            -row["r"] * row["lambda"] + row["k"] * selected
        ) % modulus
        product = row["z"]
        multiplier = row["T"]
        outputs.add((garbage, product))
        rows.append(
            (
                garbage,
                product,
                1,
                -multiplier * garbage,
                -multiplier * product,
                -multiplier,
            )
        )
    rank = matrix_rank(rows, modulus)
    return {
        "modulus": modulus,
        "width": modulus.bit_length(),
        "support_states": len(rows),
        "selected_seed": selected,
        "selected_seed_signed": first["selected_seed_signed"],
        "injectivity_failures": len(rows) - len(outputs),
        "matrix_rank": rank,
        "nullity": 6 - rank,
        "linear_fractional_decoder_exists": rank < 6,
    }


def nontrivial_cube_root_of_unity(modulus: int) -> int:
    if modulus % 3 != 1:
        raise ValueError("a nontrivial field cube root requires p congruent to one mod 3")
    return next(
        value
        for value in range(2, modulus)
        if pow(value, 3, modulus) == 1
    )


@functools.lru_cache(maxsize=None)
def glv_orbit_case_report(modulus: int) -> dict[str, Any]:
    beta = nontrivial_cube_root_of_unity(modulus)
    y_fibers: dict[int, set[int]] = defaultdict(set)
    for x, y in support.curve_points(modulus):
        y_fibers[y].add(x)

    orbit_failures = 0
    transcript = hashlib.sha256()
    for y, roots in sorted(y_fibers.items()):
        root = min(roots)
        expected = (
            {0}
            if root == 0
            else {root, beta * root % modulus, beta * beta * root % modulus}
        )
        orbit_failures += roots != expected
        transcript.update(shell.canonical_json((y, sorted(roots))))

    classical_x, classical_y = support.first_classical_point(modulus)
    tagged_t_failures = 0
    tagged_curve_failures = 0
    tagged_z_fibers: dict[int, int] = defaultdict(int)
    for row in _first_point_rows(modulus):
        tagged_z_fibers[row["z"]] += 1
        tagged_t_failures += row["T"] != (classical_x - row["output_x"]) % modulus
        tagged_curve_failures += (
            row["output_y"] * row["output_y"]
            - row["output_x"] ** 3
            - 7
        ) % modulus != 0
        tagged_t_failures += row["z"] != (row["output_y"] + classical_y) % modulus

    return {
        "modulus": modulus,
        "width": modulus.bit_length(),
        "beta": beta,
        "beta_squared": beta * beta % modulus,
        "curve_points": len(support.curve_points(modulus)),
        "curve_y_fibers": len(y_fibers),
        "maximum_curve_y_fiber": max(len(values) for values in y_fibers.values()),
        "orbit_failures": orbit_failures,
        "tagged_states": len(_first_point_rows(modulus)),
        "maximum_tagged_z_fiber": max(tagged_z_fibers.values()),
        "tagged_t_failures": tagged_t_failures,
        "tagged_curve_failures": tagged_curve_failures,
        "orbit_sha256": transcript.hexdigest(),
    }


def run_gate() -> dict[str, Any]:
    linear_cases = [
        linear_seed_affine_case_report(prime) for prime in TEST_PRIMES
    ]
    rational_cases = [
        linear_fractional_case_report(prime) for prime in TEST_PRIMES
    ]
    glv_cases = [glv_orbit_case_report(prime) for prime in GLV_PRIMES]
    linear_closed = all(
        not case["relaxed_affine_decoder_exists"]
        and case["augmented_rank"] > case["feature_rank"]
        for case in linear_cases
    )
    rational_closed = all(
        not case["linear_fractional_decoder_exists"]
        and case["matrix_rank"] == 6
        and case["injectivity_failures"] == 0
        for case in rational_cases
    )
    glv_passed = all(
        case["orbit_failures"] == 0
        and case["tagged_t_failures"] == 0
        and case["tagged_curve_failures"] == 0
        for case in glv_cases
    )

    payload: dict[str, Any] = {
        "schema": "glv-trit-tag-decoder-v1",
        "scope": "LINEAR_SEEDS_AFFINE_POSTDECODERS_AND_SELECTED_CONSTANT_SEED_MOBIUS_POSTDECODERS",
        "base_commit": BASE_COMMIT,
        "base_tree": BASE_TREE,
        "linear_seed_cases": linear_cases,
        "linear_fractional_cases": rational_cases,
        "glv_orbit_cases": glv_cases,
        "linear_seed_verdict": (
            "HARD_NACK_LINEAR_SEED_AFFINE_POSTDECODER"
            if linear_closed
            else "HOLD_LINEAR_SEED_AFFINE_POSTDECODER"
        ),
        "linear_fractional_verdict": (
            "HARD_NACK_CONSTANT_SEED_LINEAR_FRACTIONAL_POSTDECODER"
            if rational_closed
            else "HOLD_CONSTANT_SEED_LINEAR_FRACTIONAL_POSTDECODER"
        ),
        "glv_identity_verdict": (
            "ADMIT_GLV_TRIT_INTERPRETATION_ONLY"
            if glv_passed
            else "HARD_NACK_GLV_TRIT_INTERPRETATION"
        ),
        "verdict": (
            "HARD_NACK_GLV_TRIT_LINEAR_TAG_DECODER"
            if linear_closed and rational_closed and glv_passed
            else "HOLD_GLV_TRIT_LINEAR_TAG_DECODER"
        ),
        "full_field_candidate": False,
        "next_grammar": "RATIONAL_EUCLID_TAG_ROOT_CARRIER",
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
