#!/usr/bin/env python3
"""Exact Boolean support-degree and canonical-ANF Euclid-tag gates."""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
from itertools import combinations
from math import comb
from typing import Any

import affine_shell_transducer as shell
import rational_euclid_tag_root_carrier as rational


BASE_COMMIT = "cbf229dbd46a7c677fe2e28da882b4f8a02bac7f"
BASE_TREE = "eab2326ce33549eceeb5c10aa64eae33f148b0ac"
TEST_PRIMES = rational.TEST_PRIMES


def _insert_basis(basis: dict[int, int], value: int) -> bool:
    while value:
        pivot = value.bit_length() - 1
        if pivot in basis:
            value ^= basis[pivot]
        else:
            basis[pivot] = value
            return True
    return False


def _in_span(basis: dict[int, int], value: int) -> bool:
    while value:
        pivot = value.bit_length() - 1
        if pivot not in basis:
            return False
        value ^= basis[pivot]
    return True


def _monomial_column(inputs: tuple[int, ...], variable_subset: tuple[int, ...]) -> int:
    subset_mask = sum(1 << bit for bit in variable_subset)
    column = 0
    for row, input_word in enumerate(inputs):
        if input_word & subset_mask == subset_mask:
            column |= 1 << row
    return column


def _cumulative_monomials(variables: int, degree: int) -> int:
    return sum(comb(variables, term_degree) for term_degree in range(degree + 1))


@functools.lru_cache(maxsize=None)
def support_degree_case_report(modulus: int) -> dict[str, Any]:
    rows = rational.selected_seed_support(modulus)
    width = modulus.bit_length()
    variables = 2 * width
    inputs = tuple(garbage | (product << width) for garbage, product, _ in rows)
    targets = tuple(
        sum(
            1 << row
            for row, (_garbage, _product, multiplier) in enumerate(rows)
            if multiplier >> bit & 1
        )
        for bit in range(width)
    )

    capacity_degree = next(
        degree
        for degree in range(variables + 1)
        if _cumulative_monomials(variables, degree) >= len(rows)
    )
    basis: dict[int, int] = {}
    unresolved = set(range(width))
    bit_reports: list[dict[str, int] | None] = [None] * width
    previous_rank = 0
    previous_contains = [False] * width
    capacity_rank = 0

    for degree in range(variables + 1):
        for variable_subset in combinations(range(variables), degree):
            _insert_basis(basis, _monomial_column(inputs, variable_subset))
        feature_rank = len(basis)
        for bit in tuple(unresolved):
            if _in_span(basis, targets[bit]):
                bit_reports[bit] = {
                    "bit": bit,
                    "minimum_degree": degree,
                    "preceding_feature_rank": previous_rank,
                    "preceding_augmented_rank": (
                        previous_rank if previous_contains[bit] else previous_rank + 1
                    ),
                    "admitted_feature_rank": feature_rank,
                    "admitted_augmented_rank": feature_rank,
                }
                unresolved.remove(bit)
        if degree == capacity_degree:
            capacity_rank = feature_rank
        if not unresolved and degree >= capacity_degree:
            break
        previous_rank = feature_rank
        previous_contains = [_in_span(basis, target) for target in targets]

    if any(report is None for report in bit_reports):
        raise AssertionError("complete Boolean basis must contain every output bit")
    output_bits = [report for report in bit_reports if report is not None]
    transcript = hashlib.sha256(shell.canonical_json(rows)).hexdigest()
    return {
        "modulus": modulus,
        "width": width,
        "input_variables": variables,
        "support_states": len(rows),
        "support_sha256": transcript,
        "first_capacity_degree": capacity_degree,
        "capacity_monomials": _cumulative_monomials(variables, capacity_degree),
        "capacity_feature_rank": capacity_rank,
        "output_bits": output_bits,
        "interpolation_capacity_only": (
            capacity_rank == len(rows)
            and all(bit["minimum_degree"] == capacity_degree for bit in output_bits)
            and all(
                bit["preceding_augmented_rank"]
                == bit["preceding_feature_rank"] + 1
                for bit in output_bits
            )
        ),
    }


@functools.lru_cache(maxsize=None)
def zero_extension_case_report(modulus: int) -> dict[str, Any]:
    rows = rational.selected_seed_support(modulus)
    width = modulus.bit_length()
    variables = 2 * width
    table_size = 1 << variables
    coefficients = [0] * table_size
    for garbage, product, multiplier in rows:
        coefficients[garbage | (product << width)] = multiplier

    for bit in range(variables):
        step = 1 << bit
        for base in range(0, table_size, 2 * step):
            for index in range(base + step, base + 2 * step):
                coefficients[index] ^= coefficients[index - step]

    degrees = [0] * width
    counts = [0] * width
    for monomial, coefficient in enumerate(coefficients):
        if coefficient == 0:
            continue
        degree = monomial.bit_count()
        for bit in range(width):
            if coefficient >> bit & 1:
                counts[bit] += 1
                degrees[bit] = max(degrees[bit], degree)

    return {
        "modulus": modulus,
        "width": width,
        "maximum_input_degree": variables,
        "truth_table_rows": table_size,
        "anf_degrees": degrees,
        "minimum_degree": min(degrees),
        "maximum_degree": max(degrees),
        "coefficient_counts": counts,
        "coefficient_densities": [count / table_size for count in counts],
        "minimum_density": min(counts) / table_size,
        "maximum_density": max(counts) / table_size,
        "high_degree_dense": (
            min(degrees) >= variables - 2
            and min(counts) * 10 >= table_size
        ),
    }


def run_gate() -> dict[str, Any]:
    support_cases = [support_degree_case_report(prime) for prime in TEST_PRIMES]
    zero_cases = [zero_extension_case_report(prime) for prime in TEST_PRIMES]
    degree_one_absent = all(
        all(bit["minimum_degree"] > 1 for bit in case["output_bits"])
        for case in support_cases
    )
    capacity_only = all(case["interpolation_capacity_only"] for case in support_cases)
    degree_grows_beyond_two = (
        max(
            bit["minimum_degree"]
            for case in support_cases
            for bit in case["output_bits"]
        )
        > 2
    )
    zero_high_degree_dense = all(case["high_degree_dense"] for case in zero_cases)
    zero_degrees_grow = all(
        left["maximum_degree"] < right["maximum_degree"]
        for left, right in zip(zero_cases, zero_cases[1:])
    )
    closed = (
        degree_one_absent
        and capacity_only
        and degree_grows_beyond_two
        and zero_high_degree_dense
        and zero_degrees_grow
    )

    payload: dict[str, Any] = {
        "schema": "boolean-euclid-tag-root-carrier-v1",
        "scope": "SELECTED_CONSTANT_SEED_BOOLEAN_SUPPORT_DEGREE_AND_ZERO_EXTENSION_ANF_ONLY",
        "base_commit": BASE_COMMIT,
        "base_tree": BASE_TREE,
        "support_degree_cases": support_cases,
        "zero_extension_cases": zero_cases,
        "degree_one_family_absent": degree_one_absent,
        "arbitrary_factored_boolean_circuits_closed": False,
        "verdict": (
            "HARD_NACK_BOOLEAN_EUCLID_TAG_ROOT_CARRIER_NATURAL_ANF"
            if closed
            else "HOLD_BOOLEAN_EUCLID_TAG_ROOT_CARRIER"
        ),
        "full_field_candidate": False,
        "next_grammar": "SUPPORT_TRACE_ROOT_SELECTOR",
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
