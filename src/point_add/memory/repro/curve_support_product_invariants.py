#!/usr/bin/env python3
"""Exact affine-invariant census for the curve-supported shell product."""

from __future__ import annotations

import argparse
import hashlib
import json

import affine_shell_transducer as shell


BASE_COMMIT = "cbf229dbd46a7c677fe2e28da882b4f8a02bac7f"
BASE_TREE = "eab2326ce33549eceeb5c10aa64eae33f148b0ac"
DEFAULT_PRIMES = (31, 61, 127, 251, 509, 1021, 2039, 4093, 8191, 16381)


def _is_prime(value: int) -> bool:
    if value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    factor = 3
    while factor * factor <= value:
        if value % factor == 0:
            return False
        factor += 2
    return True


def affine_solution(features: tuple[int, ...], target: int) -> int | None:
    """Return one GF(2) feature mask for ``target``, or ``None``.

    Each integer is a bit-vector over the complete enumerated support.  The
    returned mask selects feature columns whose XOR is the target vector.
    """
    basis: dict[int, tuple[int, int]] = {}
    for index, feature in enumerate(features):
        vector = feature
        combination = 1 << index
        while vector:
            pivot = vector.bit_length() - 1
            row = basis.get(pivot)
            if row is None:
                basis[pivot] = (vector, combination)
                break
            vector ^= row[0]
            combination ^= row[1]

    vector = target
    combination = 0
    while vector:
        pivot = vector.bit_length() - 1
        row = basis.get(pivot)
        if row is None:
            return None
        vector ^= row[0]
        combination ^= row[1]
    return combination


def _support_rows(
    prime: int,
) -> tuple[shell.FieldCase, list[tuple[int, int, int, int, int, int]]]:
    case = shell.first_curve_point(prime)
    rows: list[tuple[int, int, int, int, int, int]] = []
    roots: dict[int, list[int]] = {}
    for y in range(prime):
        roots.setdefault(y * y % prime, []).append(y)
    for x in range(prime):
        if x == case.a:
            continue
        for y in roots.get((x**3 + 7) % prime, ()):
            d = (x - case.a) % prime
            lam = ((y - case.b) * shell.inv(d, prime)) % prime
            t = (d + 3 * case.a - lam * lam) % prime
            product = t * lam % prime
            rows.append((x, y, d, t, lam, product))
    return case, rows


def _bit_vectors(values: list[int], width: int) -> tuple[int, ...]:
    vectors = [0] * width
    for row_index, value in enumerate(values):
        for bit in range(width):
            vectors[bit] |= ((value >> bit) & 1) << row_index
    return tuple(vectors)


def _feature_names(width: int) -> tuple[str, ...]:
    return ("1",) + tuple(f"t{bit}" for bit in range(width)) + tuple(
        f"l{bit}" for bit in range(width)
    )


def _selected_names(mask: int, names: tuple[str, ...]) -> list[str]:
    return [name for index, name in enumerate(names) if (mask >> index) & 1]


def _separable_quadratic_features(
    t_vectors: tuple[int, ...],
    lambda_vectors: tuple[int, ...],
    support_states: int,
) -> tuple[tuple[int, ...], tuple[str, ...]]:
    """Return affine plus within-register degree-two features.

    Mixed ``T_i AND lambda_j`` terms are deliberately excluded: they are the
    targets whose elimination this grammar is meant to test.
    """
    features = [(1 << support_states) - 1, *t_vectors, *lambda_vectors]
    names = [
        "1",
        *(f"t{bit}" for bit in range(len(t_vectors))),
        *(f"l{bit}" for bit in range(len(lambda_vectors))),
    ]
    for prefix, vectors in (("t", t_vectors), ("l", lambda_vectors)):
        for left in range(len(vectors)):
            for right in range(left + 1, len(vectors)):
                features.append(vectors[left] & vectors[right])
                names.append(f"{prefix}{left}&{prefix}{right}")
    return tuple(features), tuple(names)


def case_report(prime: int) -> dict[str, object]:
    if not _is_prime(prime):
        raise ValueError("modulus must be prime")
    case, rows = _support_rows(prime)
    width = prime.bit_length()
    t_values = [row[3] for row in rows]
    lambda_values = [row[4] for row in rows]
    product_values = [row[5] for row in rows]
    t_vectors = _bit_vectors(t_values, width)
    lambda_vectors = _bit_vectors(lambda_values, width)
    product_vectors = _bit_vectors(product_values, width)
    constant = (1 << len(rows)) - 1
    features = (constant,) + t_vectors + lambda_vectors
    names = _feature_names(width)

    positive_controls_ok = all(
        affine_solution(features, feature) is not None for feature in features
    )
    if t_vectors and lambda_vectors:
        positive_controls_ok &= (
            affine_solution(features, t_vectors[0] ^ lambda_vectors[0]) is not None
        )

    full_constant = 0b1111
    full_x = 0b1100
    full_y = 0b1010
    full_support_and_rejected = (
        affine_solution((full_constant, full_x, full_y), full_x & full_y) is None
    )

    affine_partial_products: list[dict[str, object]] = []
    for t_bit, t_vector in enumerate(t_vectors):
        for lambda_bit, lambda_vector in enumerate(lambda_vectors):
            solution = affine_solution(features, t_vector & lambda_vector)
            if solution is not None:
                affine_partial_products.append(
                    {
                        "t_bit": t_bit,
                        "lambda_bit": lambda_bit,
                        "expression": _selected_names(solution, names),
                    }
                )

    affine_output_bits: list[dict[str, object]] = []
    for bit, vector in enumerate(product_vectors):
        solution = affine_solution(features, vector)
        if solution is not None:
            affine_output_bits.append(
                {"bit": bit, "expression": _selected_names(solution, names)}
            )

    identity_failures = sum(
        (d * t - (2 * case.b * lam - 3 * case.a * case.a)) % prime != 0
        for _x, _y, d, t, lam, _product in rows
    )
    return {
        "prime": prime,
        "width": width,
        "a": case.a,
        "b": case.b,
        "support_states": len(rows),
        "feature_count": len(features),
        "identity_failures": identity_failures,
        "positive_controls_ok": bool(positive_controls_ok),
        "full_support_and_rejected": full_support_and_rejected,
        "affine_partial_product_count": len(affine_partial_products),
        "affine_partial_products": affine_partial_products,
        "affine_output_bit_count": len(affine_output_bits),
        "affine_output_bits": affine_output_bits,
        "support_sha256": hashlib.sha256(shell.canonical_json(rows)).hexdigest(),
    }


def separable_quadratic_case_report(prime: int) -> dict[str, object]:
    """Test mixed product terms against separable degree-two features."""
    if not _is_prime(prime):
        raise ValueError("modulus must be prime")
    case, rows = _support_rows(prime)
    width = prime.bit_length()
    t_vectors = _bit_vectors([row[3] for row in rows], width)
    lambda_vectors = _bit_vectors([row[4] for row in rows], width)
    product_vectors = _bit_vectors([row[5] for row in rows], width)
    features, names = _separable_quadratic_features(
        t_vectors, lambda_vectors, len(rows)
    )

    positive_controls_ok = all(
        affine_solution(features, feature) is not None for feature in features
    )
    if width >= 2:
        synthetic = (t_vectors[0] & t_vectors[1]) ^ (
            lambda_vectors[0] & lambda_vectors[1]
        )
        positive_controls_ok &= affine_solution(features, synthetic) is not None

    full_constant = 0b11111111
    full_x = 0b11110000
    full_y = 0b11001100
    full_z = 0b10101010
    full_degree_two = (
        full_constant,
        full_x,
        full_y,
        full_z,
        full_x & full_y,
        full_x & full_z,
        full_y & full_z,
    )
    full_support_degree_three_rejected = (
        affine_solution(full_degree_two, full_x & full_y & full_z) is None
    )

    separable_mixed_partial_products: list[dict[str, object]] = []
    for t_bit, t_vector in enumerate(t_vectors):
        for lambda_bit, lambda_vector in enumerate(lambda_vectors):
            solution = affine_solution(features, t_vector & lambda_vector)
            if solution is not None:
                separable_mixed_partial_products.append(
                    {
                        "t_bit": t_bit,
                        "lambda_bit": lambda_bit,
                        "expression": _selected_names(solution, names),
                    }
                )

    separable_output_bits: list[dict[str, object]] = []
    for bit, vector in enumerate(product_vectors):
        solution = affine_solution(features, vector)
        if solution is not None:
            separable_output_bits.append(
                {"bit": bit, "expression": _selected_names(solution, names)}
            )

    identity_failures = sum(
        (d * t - (2 * case.b * lam - 3 * case.a * case.a)) % prime != 0
        for _x, _y, d, t, lam, _product in rows
    )
    return {
        "prime": prime,
        "width": width,
        "a": case.a,
        "b": case.b,
        "support_states": len(rows),
        "feature_count": len(features),
        "mixed_partial_products_tested": width * width,
        "modular_output_bits_tested": width,
        "identity_failures": identity_failures,
        "positive_controls_ok": bool(positive_controls_ok),
        "full_support_degree_three_rejected": full_support_degree_three_rejected,
        "separable_mixed_partial_product_count": len(
            separable_mixed_partial_products
        ),
        "separable_mixed_partial_products": separable_mixed_partial_products,
        "separable_output_bit_count": len(separable_output_bits),
        "separable_output_bits": separable_output_bits,
        "support_sha256": hashlib.sha256(shell.canonical_json(rows)).hexdigest(),
    }


def _persistent_pairs(cases: list[dict[str, object]], from_msb: bool) -> list[list[int]]:
    if len(cases) < 3:
        return []
    sets: list[set[tuple[int, int]]] = []
    for case in cases[-3:]:
        width = int(case["width"])
        pairs: set[tuple[int, int]] = set()
        for row in case["affine_partial_products"]:
            t_bit = int(row["t_bit"])
            lambda_bit = int(row["lambda_bit"])
            if from_msb:
                t_bit = width - 1 - t_bit
                lambda_bit = width - 1 - lambda_bit
            pairs.add((t_bit, lambda_bit))
        sets.append(pairs)
    return [list(pair) for pair in sorted(set.intersection(*sets))]


def _persistent_separable_pairs(
    cases: list[dict[str, object]], from_msb: bool
) -> list[list[int]]:
    if len(cases) < 3:
        return []
    sets: list[set[tuple[int, int]]] = []
    for case in cases[-3:]:
        width = int(case["width"])
        pairs: set[tuple[int, int]] = set()
        for row in case["separable_mixed_partial_products"]:
            t_bit = int(row["t_bit"])
            lambda_bit = int(row["lambda_bit"])
            if from_msb:
                t_bit = width - 1 - t_bit
                lambda_bit = width - 1 - lambda_bit
            pairs.add((t_bit, lambda_bit))
        sets.append(pairs)
    return [list(pair) for pair in sorted(set.intersection(*sets))]


def run_census(primes: tuple[int, ...]) -> dict[str, object]:
    cases = [case_report(prime) for prime in primes]
    persistent_lsb = _persistent_pairs(cases, from_msb=False)
    persistent_msb = _persistent_pairs(cases, from_msb=True)
    last_width = int(cases[-1]["width"])
    material_family = max(len(persistent_lsb), len(persistent_msb)) >= last_width
    payload: dict[str, object] = {
        "schema": "curve-support-product-invariants-v1",
        "scope": "AFFINE_CURVE_PRODUCT_SUPPORT",
        "base_commit": BASE_COMMIT,
        "base_tree": BASE_TREE,
        "cases": cases,
        "persistent_lsb_pairs_last_three_widths": persistent_lsb,
        "persistent_msb_pairs_last_three_widths": persistent_msb,
        "material_family": material_family,
        "admission_rule": "at least n persistent normalized partial-product relations across the largest three adjacent widths",
        "verdict": (
            "ADMIT_AFFINE_SUPPORT_FAMILY"
            if material_family
            else "HARD_NACK_AFFINE_CURVE_PRODUCT_SUPPORT"
        ),
        "verdict_scope": "affine simplification of T_i AND lambda_j and output bits on exact curve support",
        "next_grammar": "NONLINEAR_SUPPORT_COMPACTOR",
        "authority": {
            "provider": False,
            "nonce_grind": False,
            "push": False,
            "submission": False,
        },
    }
    payload["receipt_sha256"] = hashlib.sha256(shell.canonical_json(payload)).hexdigest()
    return payload


def run_separable_quadratic_census(primes: tuple[int, ...]) -> dict[str, object]:
    cases = [separable_quadratic_case_report(prime) for prime in primes]
    persistent_lsb = _persistent_separable_pairs(cases, from_msb=False)
    persistent_msb = _persistent_separable_pairs(cases, from_msb=True)
    last_width = int(cases[-1]["width"])
    material_family = max(len(persistent_lsb), len(persistent_msb)) >= last_width
    payload: dict[str, object] = {
        "schema": "separable-quadratic-curve-support-v1",
        "scope": "SEPARABLE_QUADRATIC_CURVE_SUPPORT",
        "grammar": "AFFINE_PLUS_INTRA_REGISTER_QUADRATICS",
        "base_commit": BASE_COMMIT,
        "base_tree": BASE_TREE,
        "cases": cases,
        "persistent_lsb_pairs_last_three_widths": persistent_lsb,
        "persistent_msb_pairs_last_three_widths": persistent_msb,
        "material_family": material_family,
        "admission_rule": "at least n persistent normalized mixed-product relations across the largest three adjacent widths",
        "verdict": (
            "ADMIT_SEPARABLE_QUADRATIC_SUPPORT_FAMILY"
            if material_family
            else "HARD_NACK_SEPARABLE_QUADRATIC_SUPPORT"
        ),
        "verdict_scope": "degree-two expressions using affine and within-register quadratic features only",
        "next_grammar": "CUBIC_OR_RATIONAL_SUPPORT_COMPACTOR",
        "authority": {
            "provider": False,
            "nonce_grind": False,
            "push": False,
            "submission": False,
        },
    }
    payload["receipt_sha256"] = hashlib.sha256(shell.canonical_json(payload)).hexdigest()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prime", type=int, action="append")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    report = run_census(tuple(args.prime or DEFAULT_PRIMES))
    print(json.dumps(report, sort_keys=True, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
