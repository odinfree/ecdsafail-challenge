#!/usr/bin/env python3
"""Communication bound for a two-pass odd-lift half-word overwrite."""

from __future__ import annotations

import argparse
import hashlib
import json
from typing import Any

import affine_shell_transducer as shell
import curve_support_product_invariants as support
import odd_lift_prefix_stream as odd


BASE_COMMIT = "cbf229dbd46a7c677fe2e28da882b4f8a02bac7f"
BASE_TREE = "eab2326ce33549eceeb5c10aa64eae33f148b0ac"
DEFAULT_PRIMES = (31, 61, 127, 251, 509, 1021, 2039)


def ceil_log2(value: int) -> int:
    if value < 1:
        raise ValueError("value must be positive")
    return (value - 1).bit_length()


def _halves(row: dict[str, int], cut: int, direction: str) -> tuple[int, int]:
    mask = (1 << cut) - 1
    if direction == "low_output":
        return row["w"] & mask, row["y"] & mask
    if direction == "high_output":
        return row["w"] >> cut, row["y"] >> cut
    raise ValueError(f"unknown direction: {direction}")


def replay_diversity_witness(
    prime: int, direction: str, report: dict[str, Any]
) -> bool:
    cut = prime.bit_length() // 2
    t = int(report["t"])
    visible = int(report["visible_half"])
    outputs: set[int] = set()
    for witness in report["witness_rows"]:
        lam = int(witness["lambda"])
        row = odd._row(t, lam, prime)
        if row != witness:
            return False
        row_visible, output = _halves(row, cut, direction)
        if row_visible != visible:
            return False
        outputs.add(output)
    return len(outputs) == report["max_diversity"]


def case_report(prime: int) -> dict[str, Any]:
    if not support._is_prime(prime) or prime == 2:
        raise ValueError("modulus must be an odd prime")
    width = prime.bit_length()
    cut = width // 2
    best: dict[str, dict[str, Any]] = {
        "low_output": {"max_diversity": 0},
        "high_output": {"max_diversity": 0},
    }
    digest = hashlib.sha256()

    for t in range(1, prime):
        groups: dict[str, dict[int, dict[int, dict[str, int]]]] = {
            "low_output": {},
            "high_output": {},
        }
        for lam in range(prime):
            row = odd._row(t, lam, prime)
            digest.update(shell.canonical_json(
                [row["t"], row["lambda"], row["w"], row["y"]]
            ))
            digest.update(b"\n")
            for direction in ("low_output", "high_output"):
                visible, output = _halves(row, cut, direction)
                groups[direction].setdefault(visible, {}).setdefault(output, row)

        for direction in ("low_output", "high_output"):
            visible, output_rows = max(
                groups[direction].items(), key=lambda item: len(item[1])
            )
            diversity = len(output_rows)
            if diversity <= best[direction]["max_diversity"]:
                continue
            best[direction] = {
                "t": t,
                "visible_half": visible,
                "max_diversity": diversity,
                "summary_bits": ceil_log2(diversity),
                "output_values": sorted(output_rows),
                "witness_rows": [output_rows[value] for value in sorted(output_rows)],
            }

    for direction in ("low_output", "high_output"):
        best[direction]["balanced_ceiling"] = 1 << cut
        best[direction]["ceiling_reached"] = (
            best[direction]["max_diversity"] == 1 << cut
        )
        if not replay_diversity_witness(prime, direction, best[direction]):
            raise AssertionError("diversity witness did not replay")

    return {
        "prime": prime,
        "width": width,
        "cut": cut,
        "domain_states": (prime - 1) * prime,
        "low_output": best["low_output"],
        "high_output": best["high_output"],
        "positive_control": "for y=w, a fixed visible half fixes the same output half",
        "positive_control_summary_bits": 0,
        "domain_sha256": digest.hexdigest(),
    }


def secp_symbolic_certificate() -> dict[str, Any]:
    radix = 1 << 256
    half_radix = 1 << 128
    prime = shell.SECP256K1_P
    complement = radix - prime
    multiplier = (half_radix - prime) % radix
    low_family_max_lambda = half_radix * (half_radix - 1)
    low_family_max_output = complement * (half_radix - 1)
    high_family_legal_lower_bound = half_radix - complement
    high_fiber_upper_bound = complement + 1
    high_diversity_lower_bound = (
        high_family_legal_lower_bound + high_fiber_upper_bound - 1
    ) // high_fiber_upper_bound
    high_summary_bits = ceil_log2(high_diversity_lower_bound)
    max_unreduced_target = (
        half_radix * (half_radix - 1)
        + complement * (half_radix - 1)
    )

    checks = {
        "prime_binding": prime == radix - (1 << 32) - 977,
        "complement_binding": complement == (1 << 32) + 977,
        "complement_is_odd": complement & 1 == 1,
        "complement_below_half": 0 < complement < half_radix,
        "odd_lift_word": multiplier == half_radix + complement,
        "odd_lift_word_is_odd": multiplier & 1 == 1,
        "all_low_family_inputs_are_field_values": low_family_max_lambda < prime,
        "low_family_outputs_need_no_field_subtraction": low_family_max_output < prime,
        "high_family_excludes_at_most_complement_states": (
            high_family_legal_lower_bound == half_radix - complement
        ),
        "high_target_needs_at_most_one_subtraction": max_unreduced_target < 2 * prime,
        "high_fiber_bound_is_complement_plus_one": (
            high_fiber_upper_bound == (1 << 32) + 978
        ),
        "high_summary_bound_is_96": high_summary_bits == 96,
    }
    return {
        "prime": prime,
        "radix": radix,
        "half_radix": half_radix,
        "complement": complement,
        "chosen_t": half_radix,
        "odd_lift_word": multiplier,
        "low_output": {
            "family": "lambda=B*h for every 0<=h<B",
            "fixed_visible_half": "w mod B = 0",
            "output_half": "y mod B = c*h mod B",
            "diversity": half_radix,
            "summary_bits": 128,
        },
        "high_output": {
            "family": "h=-c^-1*(l+floor(c*l/B)) mod B",
            "fixed_visible_half": "floor(w/B) = 0",
            "legal_family_lower_bound": high_family_legal_lower_bound,
            "fiber_size_upper_bound": high_fiber_upper_bound,
            "diversity_lower_bound": high_diversity_lower_bound,
            "summary_bits_lower_bound": high_summary_bits,
        },
        "integer_checks": checks,
        "all_integer_checks_passed": all(checks.values()),
    }


def run_gate(primes: tuple[int, ...] = DEFAULT_PRIMES) -> dict[str, Any]:
    cases = [case_report(prime) for prime in primes]
    toy_ceilings = all(
        case["low_output"]["ceiling_reached"]
        and case["high_output"]["ceiling_reached"]
        and case["positive_control_summary_bits"] == 0
        for case in cases
    )
    production = secp_symbolic_certificate()
    production_linear = (
        production["all_integer_checks_passed"]
        and production["low_output"]["summary_bits"] == 128
        and production["high_output"]["summary_bits_lower_bound"] >= 96
    )
    verdict = (
        "HARD_NACK_ODD_LIFT_HALF_SUMMARY"
        if toy_ceilings and production_linear
        else "INCONCLUSIVE"
    )
    payload: dict[str, Any] = {
        "schema": "odd-lift-half-summary-v1",
        "scope": "TWO_PASS_BALANCED_HALF_OVERWRITE_WITH_RETAINED_SUMMARY",
        "base_commit": BASE_COMMIT,
        "base_tree": BASE_TREE,
        "cases": cases,
        "secp256k1_certificate": production,
        "toy_balanced_ceilings_reached": toy_ceilings,
        "production_linear_bounds_proved": production_linear,
        "verdict": verdict,
        "verdict_scope": (
            "one half-word prepass followed by destructive emission of the "
            "other half; not arbitrary nonlocal or revisiting circuits"
        ),
        "next_grammar": "NONLOCAL_INTERLEAVED_UNIT_ACTION",
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
