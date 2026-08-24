#!/usr/bin/env python3
"""Exact causal-overwrite gate for odd-lifted modular multiplication."""

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


def odd_lift(t: int, prime: int) -> tuple[int, int]:
    """Return the odd signed representative and its power-of-two word."""
    if not 0 < t < prime or prime % 2 == 0:
        raise ValueError("require an odd modulus and 0 < T < p")
    width = prime.bit_length()
    signed = t if t & 1 else t - prime
    return signed, signed % (1 << width)


def _row(t: int, lam: int, prime: int) -> dict[str, int]:
    width = prime.bit_length()
    radix = 1 << width
    signed, multiplier = odd_lift(t, prime)
    return {
        "t": t,
        "lambda": lam,
        "signed_lift": signed,
        "multiplier": multiplier,
        "w": multiplier * lam % radix,
        "y": t * lam % prime,
    }


def _key(direction: str, row: dict[str, int], bit: int) -> tuple[int, int]:
    if direction == "low_to_high":
        return (
            row["w"] & ((1 << (bit + 1)) - 1),
            row["y"] & ((1 << bit) - 1),
        )
    if direction == "high_to_low":
        return row["w"] >> bit, row["y"] >> (bit + 1)
    raise ValueError(f"unknown direction: {direction}")


def _public_row(row: dict[str, int]) -> dict[str, int]:
    return {name: row[name] for name in (
        "t", "lambda", "signed_lift", "multiplier", "w", "y"
    )}


def replay_collision(prime: int, direction: str, witness: dict[str, Any]) -> bool:
    """Recompute and verify one directional collision witness."""
    bit = int(witness["bit"])
    left_given = witness["left"]
    right_given = witness["right"]
    left = _row(int(left_given["t"]), int(left_given["lambda"]), prime)
    right = _row(int(right_given["t"]), int(right_given["lambda"]), prime)
    if _public_row(left) != left_given or _public_row(right) != right_given:
        return False
    if left["t"] != right["t"] or left["lambda"] == right["lambda"]:
        return False
    return (
        _key(direction, left, bit) == _key(direction, right, bit)
        and ((left["y"] >> bit) & 1) != ((right["y"] >> bit) & 1)
    )


def curve_support_report(prime: int) -> dict[str, Any]:
    """Report the same collision census on valid curve-supported rows."""
    _case, support_rows = support._support_rows(prime)
    width = prime.bit_length()
    seen: dict[str, dict[int, dict[tuple[int, int, int], dict[str, int]]]] = {
        direction: {bit: {} for bit in range(width)}
        for direction in ("low_to_high", "high_to_low")
    }
    witnesses: dict[str, dict[int, dict[str, Any]]] = {
        "low_to_high": {},
        "high_to_low": {},
    }
    zero_t_states = 0
    product_failures = 0
    digest = hashlib.sha256()
    for _x, _y, _d, t, lam, product in support_rows:
        digest.update(shell.canonical_json([t, lam, product]))
        digest.update(b"\n")
        if t == 0:
            zero_t_states += 1
            continue
        row = _row(t, lam, prime)
        product_failures += row["y"] != product
        for direction in ("low_to_high", "high_to_low"):
            for bit in range(width):
                if bit in witnesses[direction]:
                    continue
                causal_key = _key(direction, row, bit)
                key = (t, *causal_key)
                previous = seen[direction][bit].get(key)
                if previous is None:
                    seen[direction][bit][key] = row
                    continue
                if ((previous["y"] >> bit) & 1) == ((row["y"] >> bit) & 1):
                    continue
                witness = {
                    "bit": bit,
                    "causal_key": list(causal_key),
                    "left": _public_row(previous),
                    "right": _public_row(row),
                }
                if not replay_collision(prime, direction, witness):
                    raise AssertionError("curve-support collision did not replay")
                witnesses[direction][bit] = witness

    reports: dict[str, dict[str, Any]] = {}
    for direction in ("low_to_high", "high_to_low"):
        ordered = [witnesses[direction][bit] for bit in sorted(witnesses[direction])]
        reports[direction] = {
            "blocked_bits": sorted(witnesses[direction]),
            "blocked_bit_count": len(ordered),
            "witnesses": ordered,
            "diagnostic_only": True,
        }
    return {
        "support_states": len(support_rows),
        "nonzero_t_states": len(support_rows) - zero_t_states,
        "zero_t_states": zero_t_states,
        "product_failures": product_failures,
        "low_to_high": reports["low_to_high"],
        "high_to_low": reports["high_to_low"],
        "support_sha256": digest.hexdigest(),
    }


def case_report(prime: int) -> dict[str, Any]:
    """Enumerate one complete nonzero-field multiplier domain."""
    if not support._is_prime(prime) or prime == 2:
        raise ValueError("modulus must be an odd prime")
    width = prime.bit_length()
    radix = 1 << width
    pending = {
        "low_to_high": set(range(width)),
        "high_to_low": set(range(width)),
    }
    witnesses: dict[str, dict[int, dict[str, Any]]] = {
        "low_to_high": {},
        "high_to_low": {},
    }
    odd_lift_failures = 0
    power_two_bijection_failures = 0
    recovery_failures = 0
    target_failures = 0
    digest = hashlib.sha256()

    for t in range(1, prime):
        signed, multiplier = odd_lift(t, prime)
        odd_lift_failures += (multiplier & 1) != 1
        odd_lift_failures += signed % prime != t
        inverse = pow(multiplier, -1, radix)
        images = {multiplier * value % radix for value in range(radix)}
        power_two_bijection_failures += len(images) != radix

        seen: dict[str, dict[int, dict[tuple[int, int], dict[str, int]]]] = {
            direction: {bit: {} for bit in bits}
            for direction, bits in pending.items()
        }
        for lam in range(prime):
            row = _row(t, lam, prime)
            recovery_failures += inverse * row["w"] % radix != lam
            target_failures += (signed * lam - row["y"]) % prime != 0
            digest.update(shell.canonical_json(
                [t, lam, signed, multiplier, row["w"], row["y"]]
            ))
            digest.update(b"\n")

            for direction in ("low_to_high", "high_to_low"):
                for bit in tuple(pending[direction]):
                    key = _key(direction, row, bit)
                    previous = seen[direction][bit].get(key)
                    if previous is None:
                        seen[direction][bit][key] = row
                        continue
                    if ((previous["y"] >> bit) & 1) == ((row["y"] >> bit) & 1):
                        continue
                    witness = {
                        "bit": bit,
                        "causal_key": list(key),
                        "left": _public_row(previous),
                        "right": _public_row(row),
                    }
                    if not replay_collision(prime, direction, witness):
                        raise AssertionError("constructed collision did not replay")
                    witnesses[direction][bit] = witness
                    pending[direction].remove(bit)

    direction_reports: dict[str, dict[str, Any]] = {}
    for direction in ("low_to_high", "high_to_low"):
        ordered = [witnesses[direction][bit] for bit in sorted(witnesses[direction])]
        direction_reports[direction] = {
            "blocked_bits": sorted(witnesses[direction]),
            "blocked_bit_count": len(ordered),
            "unblocked_bits": sorted(pending[direction]),
            "witnesses": ordered,
            "direction_blocked": bool(ordered),
        }

    return {
        "prime": prime,
        "width": width,
        "radix": radix,
        "domain_states": (prime - 1) * prime,
        "odd_lift_failures": odd_lift_failures,
        "power_two_bijection_failures": power_two_bijection_failures,
        "recovery_failures": recovery_failures,
        "target_failures": target_failures,
        "positive_control": "unreduced target equals w",
        "positive_control_proof": (
            "for y=w, the requested output bit is present in w[0:k+1] "
            "and in w[k:n], respectively"
        ),
        "positive_control_failures": 0,
        "low_to_high": direction_reports["low_to_high"],
        "high_to_low": direction_reports["high_to_low"],
        "curve_support_diagnostic": curve_support_report(prime),
        "domain_sha256": digest.hexdigest(),
    }


def run_gate(primes: tuple[int, ...] = DEFAULT_PRIMES) -> dict[str, Any]:
    cases = [case_report(prime) for prime in primes]
    controls_passed = all(
        case["odd_lift_failures"] == 0
        and case["power_two_bijection_failures"] == 0
        and case["recovery_failures"] == 0
        and case["target_failures"] == 0
        and case["positive_control_failures"] == 0
        for case in cases
    )
    scaled = [case for case in cases if case["width"] >= 6]
    both_blocked = bool(scaled) and all(
        case["low_to_high"]["direction_blocked"]
        and case["high_to_low"]["direction_blocked"]
        for case in scaled
    )
    verdict = (
        "HARD_NACK_ODD_LIFT_PREFIX_STREAM"
        if controls_passed and both_blocked
        else "INCONCLUSIVE"
    )
    payload: dict[str, Any] = {
        "schema": "odd-lift-prefix-stream-v1",
        "scope": "ODD_LIFT_ONE_PASS_CAUSAL_CORRECTION",
        "base_commit": BASE_COMMIT,
        "base_tree": BASE_TREE,
        "cases": cases,
        "all_controls_passed": controls_passed,
        "both_directions_blocked_at_every_width_ge_6": both_blocked,
        "verdict": verdict,
        "verdict_scope": (
            "strict one-pass low-to-high or high-to-low correction after "
            "odd multiplication modulo 2^n; not arbitrary nonlocal circuits"
        ),
        "next_grammar": "NONLOCAL_DIRECT_UNIT_ACTION",
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
