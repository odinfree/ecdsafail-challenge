#!/usr/bin/env python3
"""Exact interpolation gate for rational Euclid-tag root carriers."""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
from typing import Any, Sequence

import affine_shell_transducer as shell
import curve_support_online_constant_seed as support


BASE_COMMIT = "cbf229dbd46a7c677fe2e28da882b4f8a02bac7f"
BASE_TREE = "eab2326ce33549eceeb5c10aa64eae33f148b0ac"
TEST_PRIMES = (31, 61, 127, 251, 509)


def monomial_exponents(degree: int) -> tuple[tuple[int, int], ...]:
    return tuple(
        (g_power, z_power)
        for g_power in range(degree + 1)
        for z_power in range(degree + 1 - g_power)
    )


def matrix_rank(rows: Sequence[Sequence[int]], modulus: int) -> int:
    """Return exact rank over the prime field, eliminating below pivots only."""
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
        pivot_row = matrix[rank]
        inverse = pow(pivot_row[column], -1, modulus)
        pivot_row[column:] = [
            value * inverse % modulus for value in pivot_row[column:]
        ]
        for row in range(rank + 1, len(matrix)):
            target = matrix[row]
            scale = target[column]
            if scale == 0:
                continue
            target[column:] = [
                (left - scale * right) % modulus
                for left, right in zip(target[column:], pivot_row[column:])
            ]
        rank += 1
        if rank == len(matrix):
            break
    return rank


@functools.lru_cache(maxsize=None)
def selected_seed_support(modulus: int) -> tuple[tuple[int, int, int], ...]:
    """Return exact `(g,z,T)` rows for the first point's selected seed."""
    classical_point = support.first_classical_point(modulus)
    seed_report = support.classical_point_seed_report(modulus, classical_point)
    selected = seed_report["selected_seed"]
    if selected is None:
        raise AssertionError("first classical point must have a certified seed")
    rows = []
    for product, values in support._support_groups(modulus, classical_point).items():
        for base_g, k, multiplier, _value in values:
            rows.append(((base_g + k * selected) % modulus, product, multiplier))
    if len(rows) != len({(garbage, product) for garbage, product, _ in rows}):
        raise AssertionError("selected seed must be injective on exact support")
    return tuple(rows)


def _monomial_values(
    garbage: int,
    product: int,
    degree: int,
    modulus: int,
) -> tuple[int, ...]:
    garbage_powers = [1]
    product_powers = [1]
    for _ in range(degree):
        garbage_powers.append(garbage_powers[-1] * garbage % modulus)
        product_powers.append(product_powers[-1] * product % modulus)
    return tuple(
        garbage_powers[g_power] * product_powers[z_power] % modulus
        for g_power, z_power in monomial_exponents(degree)
    )


@functools.lru_cache(maxsize=None)
def _monomial_rows(
    modulus: int,
    degree: int,
) -> tuple[tuple[tuple[int, ...], int], ...]:
    return tuple(
        (_monomial_values(garbage, product, degree, modulus), multiplier)
        for garbage, product, multiplier in selected_seed_support(modulus)
    )


def _polynomial_degree_report(modulus: int, degree: int) -> dict[str, int | bool]:
    rows = _monomial_rows(modulus, degree)
    features = [values for values, _target in rows]
    augmented = [(*values, target) for values, target in rows]
    feature_rank = matrix_rank(features, modulus)
    augmented_rank = matrix_rank(augmented, modulus)
    return {
        "degree": degree,
        "monomials": len(monomial_exponents(degree)),
        "feature_rank": feature_rank,
        "augmented_rank": augmented_rank,
        "decoder_exists": feature_rank == augmented_rank,
    }


def _first_capacity_degree(support_states: int, multiplier: int = 1) -> int:
    degree = 0
    while multiplier * len(monomial_exponents(degree)) < support_states:
        degree += 1
    return degree


@functools.lru_cache(maxsize=None)
def polynomial_case_report(modulus: int) -> dict[str, Any]:
    support_states = len(selected_seed_support(modulus))
    admitted_degree = _first_capacity_degree(support_states)
    rejected = _polynomial_degree_report(modulus, admitted_degree - 1)
    admitted = _polynomial_degree_report(modulus, admitted_degree)
    return {
        "modulus": modulus,
        "width": modulus.bit_length(),
        "support_states": support_states,
        "first_capacity_degree": admitted_degree,
        "last_rejected": rejected,
        "first_admitted": admitted,
        "interpolation_capacity_only": (
            not rejected["decoder_exists"]
            and admitted["decoder_exists"]
            and admitted["monomials"] >= support_states
        ),
    }


def _rational_degree_report(modulus: int, degree: int) -> dict[str, int | bool]:
    source = _monomial_rows(modulus, degree)
    rows = [
        (*values, *((-target * value) % modulus for value in values))
        for values, target in source
    ]
    columns = 2 * len(monomial_exponents(degree))
    rank = matrix_rank(rows, modulus)
    return {
        "degree": degree,
        "monomials": columns // 2,
        "columns": columns,
        "rank": rank,
        "nullity": columns - rank,
        "relation_possible": rank < columns,
    }


@functools.lru_cache(maxsize=None)
def rational_case_report(modulus: int) -> dict[str, Any]:
    support_states = len(selected_seed_support(modulus))
    possible_degree = _first_capacity_degree(support_states + 1, multiplier=2)
    rejected = _rational_degree_report(modulus, possible_degree - 1)
    possible = _rational_degree_report(modulus, possible_degree)
    return {
        "modulus": modulus,
        "width": modulus.bit_length(),
        "support_states": support_states,
        "first_capacity_degree": possible_degree,
        "last_rejected": rejected,
        "first_possible": possible,
        "dimensional_capacity_only": (
            not rejected["relation_possible"]
            and possible["relation_possible"]
            and possible["columns"] > support_states
        ),
        "denominator_certified_nonzero": False,
    }


def run_gate() -> dict[str, Any]:
    polynomial_cases = [polynomial_case_report(prime) for prime in TEST_PRIMES]
    rational_cases = [rational_case_report(prime) for prime in TEST_PRIMES]
    polynomial_closed = all(
        case["interpolation_capacity_only"] for case in polynomial_cases
    )
    rational_closed = all(
        case["dimensional_capacity_only"]
        and not case["denominator_certified_nonzero"]
        for case in rational_cases
    )
    degrees_grow = all(
        left["first_admitted"]["degree"] < right["first_admitted"]["degree"]
        for left, right in zip(polynomial_cases, polynomial_cases[1:])
    ) and all(
        left["first_possible"]["degree"] < right["first_possible"]["degree"]
        for left, right in zip(rational_cases, rational_cases[1:])
    )

    payload: dict[str, Any] = {
        "schema": "rational-euclid-tag-root-carrier-v1",
        "scope": "SELECTED_CONSTANT_SEED_TOTAL_DEGREE_BIVARIATE_FIELD_MAPS_ONLY",
        "base_commit": BASE_COMMIT,
        "base_tree": BASE_TREE,
        "polynomial_cases": polynomial_cases,
        "rational_cases": rational_cases,
        "degrees_grow_with_width": degrees_grow,
        "rational_nullity_is_decoder_certificate": False,
        "verdict": (
            "HARD_NACK_RATIONAL_EUCLID_TAG_ROOT_CARRIER_INTERPOLATION_ONLY"
            if polynomial_closed and rational_closed and degrees_grow
            else "HOLD_RATIONAL_EUCLID_TAG_ROOT_CARRIER"
        ),
        "full_field_candidate": False,
        "next_grammar": "BOOLEAN_EUCLID_TAG_ROOT_CARRIER",
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
