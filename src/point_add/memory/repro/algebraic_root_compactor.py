#!/usr/bin/env python3
"""Exact algebraic-root obligation and addition-chain cost gate."""

from __future__ import annotations

import argparse
import hashlib
import json

import affine_shell_transducer as shell
import curve_support_product_invariants as support


BASE_COMMIT = "cbf229dbd46a7c677fe2e28da882b4f8a02bac7f"
BASE_TREE = "eab2326ce33549eceeb5c10aa64eae33f148b0ac"
CURRENT_SQUARE_T = 54_876.89
REPLACEMENT_T_CEILING = 335_738.86


def case_report(prime: int) -> dict[str, object]:
    if prime in (2, 3, 7) or not support._is_prime(prime):
        raise ValueError("modulus must be a prime outside characteristics 2, 3, and 7")
    case, rows = support._support_rows(prime)
    root_identity_failures = 0
    output_equality_failures = 0
    inverse_slope_failures = 0
    fibers: dict[int, set[int]] = {}

    for _x, _y, _d, t, lam, product in rows:
        x_out = (case.a - t) % prime
        y_out = (product - case.b) % prime
        root_identity_failures += (
            y_out * y_out - (x_out**3 + 7)
        ) % prime != 0
        output_equality_failures += shell.transducer(case, t, lam) != (
            x_out,
            y_out,
        )
        if t:
            recovered = ((y_out + case.b) * shell.inv(t, prime)) % prime
            inverse_slope_failures += recovered != lam
        fibers.setdefault(t, set()).add(y_out)

    paired_root_sign_failures = 0
    for roots in fibers.values():
        if len(roots) > 2:
            paired_root_sign_failures += 1
        elif len(roots) == 2:
            left, right = sorted(roots)
            paired_root_sign_failures += (left + right) % prime != 0

    derivative_common_roots = 0
    for t in range(prime):
        radicand = ((case.a - t) ** 3 + 7) % prime
        derivative = (-3 * (case.a - t) ** 2) % prime
        derivative_common_roots += radicand == 0 and derivative == 0

    return {
        "prime": prime,
        "width": prime.bit_length(),
        "a": case.a,
        "b": case.b,
        "support_states": len(rows),
        "distinct_T": len(fibers),
        "maximum_root_fiber_size": max(map(len, fibers.values()), default=0),
        "root_identity": "(T*lambda-b)^2 = (a-T)^3 + 7",
        "root_identity_failures": root_identity_failures,
        "output_equality_failures": output_equality_failures,
        "inverse_slope_failures": inverse_slope_failures,
        "paired_root_sign_failures": paired_root_sign_failures,
        "derivative_common_roots": derivative_common_roots,
        "cubic_squarefree": derivative_common_roots == 0,
        "support_sha256": hashlib.sha256(shell.canonical_json(rows)).hexdigest(),
    }


def secp_addition_chain_report() -> dict[str, object]:
    prime = shell.SECP256K1_P
    exponent = (prime + 1) // 4
    lower_bound = exponent.bit_length() - 1
    relaxed_t = lower_bound * CURRENT_SQUARE_T
    return {
        "prime_mod_4": prime % 4,
        "root_method": "z^((p+1)/4) on quadratic residues",
        "root_exponent_hex": hex(exponent),
        "root_exponent_bit_length": exponent.bit_length(),
        "addition_chain_multiplication_lower_bound": lower_bound,
        "lower_bound_reason": "one multiplication can at most double the largest available exponent",
        "pricing_relaxation": "price every field multiplication as the current square and omit all other work",
        "current_square_t": CURRENT_SQUARE_T,
        "relaxed_square_only_t": relaxed_t,
        "replacement_t_ceiling": REPLACEMENT_T_CEILING,
        "budget_multiple": relaxed_t / REPLACEMENT_T_CEILING,
        "verdict": "HARD_NACK_ADDITION_CHAIN_DECOMPRESS",
    }


def run_gate(primes: tuple[int, ...]) -> dict[str, object]:
    cases = [case_report(prime) for prime in primes]
    squarefree = all(row["cubic_squarefree"] for row in cases)
    payload: dict[str, object] = {
        "schema": "algebraic-root-compactor-v1",
        "scope": "ALGEBRAIC_ROOT_CURVE_COMPACTOR",
        "base_commit": BASE_COMMIT,
        "base_tree": BASE_TREE,
        "cases": cases,
        "compactor_equivalence": {
            "forward": "Y=T*lambda-b",
            "root": "Y^2=(a-T)^3+7",
            "inverse_nonzero_T": "lambda=(Y+b)/T",
            "branch_bits": 1,
        },
        "rational_decoder": {
            "radicand_degree": 3,
            "radicand_squarefree": squarefree,
            "obstruction": "an odd-degree squarefree polynomial is not a square in the rational function field",
            "verdict": (
                "HARD_NACK_RATIONAL_ROOT_COMPACTOR"
                if squarefree
                else "INCONCLUSIVE"
            ),
        },
        "addition_chain": secp_addition_chain_report(),
        "verdict": "HARD_NACK_ALGEBRAIC_ROOT_COMPACTOR",
        "verdict_scope": "rational one-word decoder and ordinary monomial addition-chain point decompression",
        "next_grammar": "DIRECT_UNIT_ACTION",
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
    report = run_gate(tuple(args.prime or (31, 127, 251)))
    print(json.dumps(report, sort_keys=True, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
