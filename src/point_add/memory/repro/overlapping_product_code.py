#!/usr/bin/env python3
"""Exact multiplicative Mobius census for overlapping product codes."""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
from typing import Any

import affine_shell_transducer as shell
import curve_support_product_invariants as support


BASE_COMMIT = "cbf229dbd46a7c677fe2e28da882b4f8a02bac7f"
BASE_TREE = "eab2326ce33549eceeb5c10aa64eae33f148b0ac"
DEFAULT_PRIMES = (31, 61, 127, 251, 509, 1021, 2039)


def batch_invert(values: list[int], prime: int) -> list[int]:
    """Invert a nonzero list with one field inversion."""
    prefix = [1]
    accumulator = 1
    for value in values:
        if value % prime == 0:
            raise ValueError("multiplicative transform contains zero")
        accumulator = accumulator * value % prime
        prefix.append(accumulator)
    inverse = pow(accumulator, -1, prime)
    result = [0] * len(values)
    for index in range(len(values) - 1, -1, -1):
        result[index] = inverse * prefix[index] % prime
        inverse = inverse * values[index] % prime
    return result


def mobius_transform(values: list[int], prime: int) -> list[int]:
    size = len(values)
    if size == 0 or size & (size - 1):
        raise ValueError("table length must be a nonzero power of two")
    result = [value % prime for value in values]
    bits = (size - 1).bit_length()
    for bit in range(bits):
        step = 1 << bit
        high_indices: list[int] = []
        denominators: list[int] = []
        for start in range(0, size, step << 1):
            for offset in range(step):
                low = start + offset
                high = low + step
                high_indices.append(high)
                denominators.append(result[low])
        inverses = batch_invert(denominators, prime)
        for high, inverse in zip(high_indices, inverses):
            result[high] = result[high] * inverse % prime
    return result


def zeta_transform(coefficients: list[int], prime: int) -> list[int]:
    size = len(coefficients)
    if size == 0 or size & (size - 1):
        raise ValueError("table length must be a nonzero power of two")
    result = [value % prime for value in coefficients]
    bits = (size - 1).bit_length()
    for bit in range(bits):
        step = 1 << bit
        for start in range(0, size, step << 1):
            for offset in range(step):
                low = start + offset
                high = low + step
                result[high] = result[high] * result[low] % prime
    return result


def _digest(values: list[int], width_bytes: int) -> str:
    digest = hashlib.sha256()
    for value in values:
        digest.update(value.to_bytes(width_bytes, "big"))
    return digest.hexdigest()


def toy_case_report(prime: int) -> dict[str, Any]:
    if not support._is_prime(prime) or prime <= 7:
        raise ValueError("modulus must be an odd prime greater than seven")
    width = prime.bit_length()
    active_bits = width - 2
    context = 1 << (width - 1)
    values = [context + mask for mask in range(1 << active_bits)]
    if values[-1] >= prime:
        raise ValueError("toy subcube must lie below the modulus")
    coefficients = mobius_transform(values, prime)
    reconstructed = zeta_transform(coefficients, prime)
    failures = sum(left != right for left, right in zip(values, reconstructed))
    width_bytes = (width + 7) // 8
    return {
        "prime": prime,
        "width": width,
        "active_bits": active_bits,
        "context": context,
        "coefficient_count": len(coefficients),
        "nonidentity_coefficients": sum(value != 1 for value in coefficients),
        "reconstruction_failures": failures,
        "value_sha256": _digest(values, width_bytes),
        "coefficient_sha256": _digest(coefficients, width_bytes),
        "all_transform_controls_passed": failures == 0,
    }


def sparse_control_report(prime: int, active_bits: int) -> dict[str, Any]:
    size = 1 << active_bits
    declared = sorted({0, 1, 3, 1 << (active_bits - 1), size - 1})
    constants = (7, 2, 3, 5, 11)
    coefficients = [1] * size
    for mask, constant in zip(declared, constants):
        coefficients[mask] = constant % prime
    values = zeta_transform(coefficients, prime)
    recovered = mobius_transform(values, prime)
    recovered_masks = [mask for mask, value in enumerate(recovered) if value != 1]
    return {
        "prime": prime,
        "active_bits": active_bits,
        "declared_masks": declared,
        "recovered_nonidentity_masks": recovered_masks,
        "coefficient_failures": sum(
            left != right for left, right in zip(coefficients, recovered)
        ),
        "reconstruction_failures": sum(
            left != right
            for left, right in zip(values, zeta_transform(recovered, prime))
        ),
    }


@functools.lru_cache(maxsize=1)
def production_subcube_report() -> dict[str, Any]:
    prime = shell.SECP256K1_P
    active_bits = 19
    size = 1 << active_bits
    context = 1 << 255
    values = [context + mask for mask in range(size)]
    coefficients = mobius_transform(values, prime)
    reconstructed = zeta_transform(coefficients, prime)
    reconstruction_failures = sum(
        left != right for left, right in zip(values, reconstructed)
    )
    nonempty_nonidentity = sum(value != 1 for value in coefficients[1:])
    samples = {
        str(mask): hex(coefficients[mask])
        for mask in (0, 1, 2, 3, 255, 65535, 1 << 18, size - 1)
    }
    checks = {
        "all_values_nonzero": values[0] > 0,
        "all_values_below_prime": values[-1] < prime,
        "coefficient_count_exact": len(coefficients) == size,
        "every_nonempty_coefficient_nonidentity": (
            nonempty_nonidentity == size - 1
        ),
        "exact_inverse_zeta_reconstruction": reconstruction_failures == 0,
    }
    return {
        "prime": prime,
        "context": context,
        "active_bits": active_bits,
        "value_count": size,
        "coefficient_count": len(coefficients),
        "nonempty_nonidentity_coefficients": nonempty_nonidentity,
        "identity_nonempty_coefficients": (size - 1) - nonempty_nonidentity,
        "reconstruction_failures": reconstruction_failures,
        "value_sha256": _digest(values, 32),
        "coefficient_sha256": _digest(coefficients, 32),
        "sample_coefficients": samples,
        "checks": checks,
        "all_checks_passed": all(checks.values()),
    }


def run_gate(primes: tuple[int, ...] = DEFAULT_PRIMES) -> dict[str, Any]:
    cases = [toy_case_report(prime) for prime in primes]
    sparse_controls = [
        sparse_control_report(prime, min(5, prime.bit_length() - 2))
        for prime in primes
    ]
    all_controls = all(case["all_transform_controls_passed"] for case in cases) and all(
        row["coefficient_failures"] == 0 and row["reconstruction_failures"] == 0
        for row in sparse_controls
    )
    production = production_subcube_report()
    fully_dense = (
        production["all_checks_passed"]
        and production["nonempty_nonidentity_coefficients"] == (1 << 19) - 1
    )
    verdict = (
        "HARD_NACK_OVERLAPPING_PRODUCT_CODE"
        if all_controls and fully_dense
        else "INCONCLUSIVE"
    )
    payload: dict[str, Any] = {
        "schema": "overlapping-product-code-v1",
        "scope": "LITERAL_MULTIPLICATIVE_BOOLEAN_MOBIUS_FACTOR_SCHEDULE",
        "base_commit": BASE_COMMIT,
        "base_tree": BASE_TREE,
        "cases": cases,
        "sparse_controls": sparse_controls,
        "production_subcube": production,
        "all_controls_passed": all_controls,
        "production_subcube_fully_dense": fully_dense,
        "verdict": verdict,
        "verdict_scope": (
            "literal factor-by-factor conjunction-controlled constant units; "
            "not joint arithmetic synthesis"
        ),
        "next_grammar": "JOINT_ARITHMETIC_UNIT_ACTION",
        "authority": {
            "provider": False,
            "nonce_grind": False,
            "fleet": False,
            "queue": False,
            "push": False,
            "public_note": False,
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
    report = run_gate(tuple(args.prime or DEFAULT_PRIMES))
    print(json.dumps(report, sort_keys=True, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
