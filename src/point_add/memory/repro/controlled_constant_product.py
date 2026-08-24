#!/usr/bin/env python3
"""Exact rectangle gate for controlled-constant product codes."""

from __future__ import annotations

import argparse
import hashlib
import json
from typing import Any

import affine_shell_transducer as shell
import curve_support_product_invariants as support


BASE_COMMIT = "cbf229dbd46a7c677fe2e28da882b4f8a02bac7f"
BASE_TREE = "eab2326ce33549eceeb5c10aa64eae33f148b0ac"
DEFAULT_PRIMES = (31, 61, 127, 251, 509, 1021, 2039)


def rectangle_witness(prime: int, i: int, j: int, k: int) -> dict[str, Any]:
    width = prime.bit_length()
    if len({i, j, k}) != 3 or min(i, j, k) < 0 or max(i, j, k) >= width:
        raise ValueError("i, j, and k must be distinct in-range bit positions")
    a = 1 << i
    b_delta = 1 << j
    context = 1 << k
    values = [context, context + a, context + b_delta, context + a + b_delta]
    if values[-1] >= prime:
        raise ValueError("rectangle is not contained in the nonzero field domain")
    residual = (values[0] * values[3] - values[1] * values[2]) % prime
    return {
        "bits": [i, j],
        "context_bit": k,
        "values": values,
        "residual": residual,
        "expected_residual": (-(a * b_delta)) % prime,
    }


def replay_rectangle_witness(prime: int, witness: dict[str, Any]) -> bool:
    i, j = map(int, witness["bits"])
    regenerated = rectangle_witness(prime, i, j, int(witness["context_bit"]))
    return regenerated == witness and regenerated["residual"] != 0


def _compressed_digit(value: int, mask: int, width: int) -> int:
    digit = 0
    out_bit = 0
    for bit in range(width):
        if (mask >> bit) & 1:
            digit |= ((value >> bit) & 1) << out_bit
            out_bit += 1
    return digit


def _synthetic_factor(value: int, left_mask: int, prime: int) -> int:
    width = prime.bit_length()
    full_mask = (1 << width) - 1
    right_mask = full_mask ^ left_mask
    left = _compressed_digit(value, left_mask, width)
    right = _compressed_digit(value, right_mask, width)
    return 5 * pow(2, left, prime) * pow(3, right, prime) % prime


def case_report(prime: int) -> dict[str, Any]:
    if not support._is_prime(prime) or prime <= 7:
        raise ValueError("modulus must be an odd prime greater than seven")
    width = prime.bit_length()
    full_mask = (1 << width) - 1
    partitions_tested = 0
    target_zero_residuals = 0
    synthetic_control_failures = 0
    samples: list[dict[str, Any]] = []
    digest = hashlib.sha256()

    # Quotient complementary bipartitions by requiring bit zero on the left.
    for left_mask in range(1, full_mask):
        if left_mask & 1 == 0:
            continue
        right_mask = full_mask ^ left_mask
        if right_mask == 0:
            continue
        i = next(bit for bit in range(width) if (left_mask >> bit) & 1)
        j = next(bit for bit in range(width) if (right_mask >> bit) & 1)
        k = next(bit for bit in range(width) if bit not in (i, j))
        witness = rectangle_witness(prime, i, j, k)
        target_zero_residuals += witness["residual"] == 0
        values = witness["values"]
        synthetic = [_synthetic_factor(value, left_mask, prime) for value in values]
        synthetic_residual = (
            synthetic[0] * synthetic[3] - synthetic[1] * synthetic[2]
        ) % prime
        synthetic_control_failures += synthetic_residual != 0
        digest.update(shell.canonical_json(
            [left_mask, right_mask, witness, synthetic_residual]
        ))
        digest.update(b"\n")
        if len(samples) < 4:
            samples.append(witness)
        partitions_tested += 1

    expected_partitions = (1 << (width - 1)) - 1
    return {
        "prime": prime,
        "width": width,
        "partitions_tested": partitions_tested,
        "expected_unordered_bipartitions": expected_partitions,
        "target_zero_residuals": target_zero_residuals,
        "synthetic_control_failures": synthetic_control_failures,
        "all_partitions_rejected": (
            partitions_tested == expected_partitions
            and target_zero_residuals == 0
            and synthetic_control_failures == 0
        ),
        "sample_witnesses": samples,
        "partition_sha256": digest.hexdigest(),
    }


def secp_symbolic_certificate() -> dict[str, Any]:
    prime = shell.SECP256K1_P
    width = 256
    bit_pairs = 0
    invalid_context_values = 0
    zero_residuals = 0
    formula_failures = 0
    digest = hashlib.sha256()
    samples: list[dict[str, Any]] = []
    for i in range(width):
        for j in range(i + 1, width):
            k = next(bit for bit in range(width) if bit not in (i, j))
            witness = rectangle_witness(prime, i, j, k)
            invalid_context_values += witness["values"][-1] >= prime
            zero_residuals += witness["residual"] == 0
            formula_failures += witness["residual"] != witness["expected_residual"]
            digest.update(shell.canonical_json(witness))
            digest.update(b"\n")
            if (i, j) in ((0, 1), (0, 255), (254, 255)):
                samples.append(witness)
            bit_pairs += 1

    checks = {
        "prime_above_largest_three_bit_context": prime > 7 * (1 << 253),
        "all_bit_pairs_checked": bit_pairs == width * (width - 1) // 2,
        "all_context_values_legal": invalid_context_values == 0,
        "all_rectangle_residuals_nonzero": zero_residuals == 0,
        "all_residual_formulas_exact": formula_failures == 0,
    }
    one_window_entries = prime - 1
    return {
        "prime": prime,
        "width": width,
        "bit_pairs_checked": bit_pairs,
        "invalid_context_values": invalid_context_values,
        "zero_residuals": zero_residuals,
        "formula_failures": formula_failures,
        "symbolic_residual": "-2^(i+j) mod p",
        "sample_witnesses": samples,
        "pair_sha256": digest.hexdigest(),
        "one_window_entries": one_window_entries,
        "one_window_entry_index_bits": one_window_entries.bit_length(),
        "one_window_is_exponential": one_window_entries.bit_length() == width,
        "checks": checks,
        "all_checks_passed": all(checks.values()),
    }


def run_gate(primes: tuple[int, ...] = DEFAULT_PRIMES) -> dict[str, Any]:
    cases = [case_report(prime) for prime in primes]
    all_toy = all(case["all_partitions_rejected"] for case in cases)
    production = secp_symbolic_certificate()
    production_interacts = production["all_checks_passed"]
    verdict = (
        "HARD_NACK_CONTROLLED_CONSTANT_PRODUCT_CODE"
        if all_toy and production_interacts and production["one_window_is_exponential"]
        else "INCONCLUSIVE"
    )
    payload: dict[str, Any] = {
        "schema": "controlled-constant-product-code-v1",
        "scope": "DISJOINT_WINDOW_CONTROLLED_CLASSICAL_UNIT_FACTORS",
        "base_commit": BASE_COMMIT,
        "base_tree": BASE_TREE,
        "cases": cases,
        "secp256k1_certificate": production,
        "all_toy_partitions_rejected": all_toy,
        "production_all_bit_pairs_interact": production_interacts,
        "verdict": verdict,
        "verdict_scope": (
            "products of independent disjoint-window classical multipliers; "
            "not overlapping or adaptive arithmetic factors"
        ),
        "next_grammar": "OVERLAPPING_NONLOCAL_UNIT_ACTION",
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
