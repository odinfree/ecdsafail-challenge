#!/usr/bin/env python3
"""Exact curve-support gate for an online Euclid row with constant seed."""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
from collections import Counter, defaultdict
from itertools import combinations
from typing import Any

import affine_shell_transducer as shell
import coupled_transposed_seed as coupled


BASE_COMMIT = "cbf229dbd46a7c677fe2e28da882b4f8a02bac7f"
BASE_TREE = "eab2326ce33549eceeb5c10aa64eae33f148b0ac"
TEST_PRIMES = (31, 61, 127, 251, 509, 1021, 2039, 4093)
SECP256K1_P = (1 << 256) - (1 << 32) - 977
CURRENT_SQUARE_T = 54_876.89
REPLACEMENT_T_CEILING = 335_738.86


@functools.lru_cache(maxsize=None)
def curve_points(modulus: int) -> tuple[tuple[int, int], ...]:
    roots: dict[int, list[int]] = defaultdict(list)
    for value in range(modulus):
        roots[value * value % modulus].append(value)
    return tuple(
        (x, y)
        for x in range(modulus)
        for y in roots[(x * x * x + 7) % modulus]
    )


def first_classical_point(modulus: int) -> tuple[int, int]:
    return next((x, y) for x, y in curve_points(modulus) if y != 0)


@functools.lru_cache(maxsize=None)
def _cofactor_coefficients(modulus: int) -> tuple[tuple[int, int], ...]:
    rows = [(0, 0)]
    for multiplier in range(1, modulus):
        matrix = coupled.orientation_one_matrix(modulus, multiplier)
        rows.append((matrix["r"] % modulus, matrix["k"] % modulus))
    return tuple(rows)


def _signed_constant(value: int, modulus: int) -> int:
    return value if value <= modulus // 2 else value - modulus


def _constant_order(modulus: int):
    yield 0
    for magnitude in range(1, modulus):
        yield magnitude
        yield (-magnitude) % modulus


def _support_groups(
    modulus: int,
    classical_point: tuple[int, int],
) -> dict[int, list[tuple[int, int, int, int]]]:
    """Group `(g(0), k, T, lambda)` by the already-correct output `z`."""
    classical_x, classical_y = classical_point
    inverses = [0] + [pow(value, -1, modulus) for value in range(1, modulus)]
    coefficients = _cofactor_coefficients(modulus)
    groups: dict[int, list[tuple[int, int, int, int]]] = defaultdict(list)
    for output_x, output_y in curve_points(modulus):
        multiplier = (classical_x - output_x) % modulus
        if multiplier == 0:
            continue
        product = (output_y + classical_y) % modulus
        value = product * inverses[multiplier] % modulus
        r, k = coefficients[multiplier]
        groups[product].append((-r * value % modulus, k, multiplier, value))
    return groups


def _forbidden_constants(
    modulus: int,
    groups: dict[int, list[tuple[int, int, int, int]]],
) -> tuple[set[int], int]:
    forbidden: set[int] = set()
    unavoidable = 0
    for values in groups.values():
        for left, right in combinations(values, 2):
            left_g, left_k, _left_t, _left_lambda = left
            right_g, right_k, _right_t, _right_lambda = right
            denominator = (left_k - right_k) % modulus
            numerator = (right_g - left_g) % modulus
            if denominator == 0:
                unavoidable += numerator == 0
            else:
                forbidden.add(numerator * pow(denominator, -1, modulus) % modulus)
    return forbidden, unavoidable


def classical_point_seed_report(
    modulus: int,
    classical_point: tuple[int, int],
) -> dict[str, Any]:
    groups = _support_groups(modulus, classical_point)
    forbidden, unavoidable = _forbidden_constants(modulus, groups)
    selected = next(
        (constant for constant in _constant_order(modulus) if constant not in forbidden),
        None,
    )
    injectivity_failures = 0
    product_failures = 0
    maximum_z_fiber = 0
    if selected is not None:
        for product, values in groups.items():
            outputs = []
            maximum_z_fiber = max(maximum_z_fiber, len(values))
            for base_g, k, multiplier, value in values:
                outputs.append((base_g + k * selected) % modulus)
                second = (multiplier * value - modulus * selected) % modulus
                product_failures += second != product
            injectivity_failures += len(outputs) - len(set(outputs))

    support_states = sum(len(values) for values in groups.values())
    return {
        "classical_x": classical_point[0],
        "classical_y": classical_point[1],
        "support_states": support_states,
        "z_fibers": len(groups),
        "maximum_z_fiber": maximum_z_fiber,
        "forbidden_constants": len(forbidden),
        "unavoidable_collisions": unavoidable,
        "selected_seed": selected,
        "selected_seed_signed": (
            _signed_constant(selected, modulus) if selected is not None else None
        ),
        "injectivity_failures": injectivity_failures,
        "product_failures": product_failures,
    }


@functools.lru_cache(maxsize=None)
def all_classical_points_report(modulus: int) -> dict[str, Any]:
    reports = [
        classical_point_seed_report(modulus, point)
        for point in curve_points(modulus)
    ]
    seed_histogram = Counter(
        abs(report["selected_seed_signed"])
        for report in reports
        if report["selected_seed_signed"] is not None
    )
    transcript = hashlib.sha256()
    for report in reports:
        transcript.update(shell.canonical_json(report))
    return {
        "modulus": modulus,
        "width": modulus.bit_length(),
        "prime_mod_3": modulus % 3,
        "classical_points": len(reports),
        "support_states": sum(report["support_states"] for report in reports),
        "maximum_z_fiber": max(report["maximum_z_fiber"] for report in reports),
        "maximum_forbidden_constants": max(
            report["forbidden_constants"] for report in reports
        ),
        "unavoidable_collision_points": sum(
            report["unavoidable_collisions"] != 0 for report in reports
        ),
        "uncertified_points": sum(
            report["selected_seed"] is None for report in reports
        ),
        "zero_seed_points": sum(report["selected_seed"] == 0 for report in reports),
        "maximum_absolute_seed": max(seed_histogram, default=0),
        "absolute_seed_histogram": dict(sorted(seed_histogram.items())),
        "injectivity_failures": sum(
            report["injectivity_failures"] for report in reports
        ),
        "product_failures": sum(report["product_failures"] for report in reports),
        "transcript_sha256": transcript.hexdigest(),
    }


def _affine_solution(
    equations: list[tuple[int, int, int, int]],
    modulus: int,
) -> tuple[int, int, int] | None:
    matrix = [list(row) for row in equations]
    rank = 0
    pivots: list[int] = []
    for column in range(3):
        pivot = next(
            (
                row
                for row in range(rank, len(matrix))
                if matrix[row][column] % modulus
            ),
            None,
        )
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        inverse = pow(matrix[rank][column] % modulus, -1, modulus)
        matrix[rank] = [value * inverse % modulus for value in matrix[rank]]
        for row in range(len(matrix)):
            if row == rank or matrix[row][column] % modulus == 0:
                continue
            scale = matrix[row][column] % modulus
            matrix[row] = [
                (left - scale * right) % modulus
                for left, right in zip(matrix[row], matrix[rank])
            ]
        pivots.append(column)
        rank += 1

    if any(
        all(value % modulus == 0 for value in row[:3]) and row[3] % modulus
        for row in matrix
    ):
        return None
    solution = [0, 0, 0]
    for row, column in enumerate(pivots):
        solution[column] = matrix[row][3] % modulus
    if any(
        (a * solution[0] + b * solution[1] + c * solution[2] - target)
        % modulus
        for a, b, c, target in equations
    ):
        return None
    return tuple(solution)


@functools.lru_cache(maxsize=None)
def first_point_affine_decoder_report(modulus: int) -> dict[str, Any]:
    classical_point = first_classical_point(modulus)
    seed_report = classical_point_seed_report(modulus, classical_point)
    selected = seed_report["selected_seed"]
    if selected is None:
        raise AssertionError("first classical point must have a certified seed")
    groups = _support_groups(modulus, classical_point)
    equations = []
    outputs: set[tuple[int, int]] = set()
    product_failures = 0
    for product, values in groups.items():
        for base_g, k, multiplier, value in values:
            garbage = (base_g + k * selected) % modulus
            equations.append((garbage, product, 1, multiplier))
            outputs.add((garbage, product))
            product_failures += product != multiplier * value % modulus
    solution = _affine_solution(equations, modulus)
    return {
        "modulus": modulus,
        "width": modulus.bit_length(),
        "classical_x": classical_point[0],
        "classical_y": classical_point[1],
        "support_states": len(equations),
        "selected_seed": selected,
        "selected_seed_signed": _signed_constant(selected, modulus),
        "injectivity_failures": len(equations) - len(outputs),
        "product_failures": product_failures,
        "affine_decoder_exists": solution is not None,
        "affine_decoder": solution,
    }


def secp_cube_root_cost_report() -> dict[str, Any]:
    subgroup_order = (SECP256K1_P - 1) // 3
    exponent = (subgroup_order + 1) // 3
    if 3 * exponent % subgroup_order != 1:
        raise AssertionError("root exponent does not invert cubing on the image")
    squarings = exponent.bit_length() - 1
    square_only_t = squarings * CURRENT_SQUARE_T
    return {
        "prime": SECP256K1_P,
        "prime_mod_3": SECP256K1_P % 3,
        "prime_mod_9": SECP256K1_P % 9,
        "subgroup_order": subgroup_order,
        "subgroup_order_mod_3": subgroup_order % 3,
        "root_exponent": exponent,
        "root_exponent_bits": exponent.bit_length(),
        "root_exponent_popcount": exponent.bit_count(),
        "binary_squarings": squarings,
        "current_square_t": CURRENT_SQUARE_T,
        "square_only_t": square_only_t,
        "replacement_t_ceiling": REPLACEMENT_T_CEILING,
        "budget_multiple": square_only_t / REPLACEMENT_T_CEILING,
        "favorable_omissions": (
            "all non-square multiplies",
            "GLV branch extraction",
            "routing",
            "off-support extension",
            "cleanup",
        ),
        "verdict": "HARD_NACK_CURRENT_SQUARE_CUBIC_DECOMPRESS",
    }


def run_gate() -> dict[str, Any]:
    support_cases = [all_classical_points_report(prime) for prime in TEST_PRIMES]
    affine_cases = [
        first_point_affine_decoder_report(prime) for prime in TEST_PRIMES
    ]
    cube_root = secp_cube_root_cost_report()
    identity_passed = all(
        case["unavoidable_collision_points"] == 0
        and case["uncertified_points"] == 0
        and case["injectivity_failures"] == 0
        and case["product_failures"] == 0
        for case in support_cases
    )
    affine_closed = all(
        not case["affine_decoder_exists"]
        and case["injectivity_failures"] == 0
        and case["product_failures"] == 0
        for case in affine_cases
    )
    cube_root_closed = cube_root["square_only_t"] > REPLACEMENT_T_CEILING

    payload: dict[str, Any] = {
        "schema": "curve-support-online-constant-seed-v1",
        "scope": "REDUCED_WIDTH_CURVE_SUPPORT_AND_NATURAL_POSTDECODERS_ONLY",
        "base_commit": BASE_COMMIT,
        "base_tree": BASE_TREE,
        "support_cases": support_cases,
        "affine_decoder_cases": affine_cases,
        "secp_cube_root": cube_root,
        "identity_verdict": (
            "ADMIT_CURVE_SUPPORT_CONSTANT_SEED_INJECTIVITY_TOY_ONLY"
            if identity_passed
            else "HARD_NACK_CURVE_SUPPORT_CONSTANT_SEED_INJECTIVITY"
        ),
        "affine_decoder_verdict": (
            "HARD_NACK_AFFINE_CONSTANT_SEED_POSTDECODER"
            if affine_closed
            else "HOLD_AFFINE_CONSTANT_SEED_POSTDECODER"
        ),
        "cube_root_verdict": cube_root["verdict"],
        "verdict": (
            "HARD_NACK_CURVE_SUPPORT_CONSTANT_SEED_NATURAL_DECODERS"
            if identity_passed and affine_closed and cube_root_closed
            else "HOLD_CURVE_SUPPORT_CONSTANT_SEED_NATURAL_DECODERS"
        ),
        "production_seed_certificate": False,
        "off_support_extension": False,
        "full_field_candidate": False,
        "next_grammar": "GLV_TRIT_TAG_DECODER",
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
