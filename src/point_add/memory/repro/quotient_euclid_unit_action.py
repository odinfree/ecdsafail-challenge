#!/usr/bin/env python3
"""Exact oracle and transcript census for a quotient-Euclid field unit action."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections.abc import Iterable, Sequence
from typing import Any

import affine_shell_transducer as shell


BASE_COMMIT = "cbf229dbd46a7c677fe2e28da882b4f8a02bac7f"
BASE_TREE = "eab2326ce33549eceeb5c10aa64eae33f148b0ac"
SECP256K1_P = (1 << 256) - (1 << 32) - 977
LIVE_BINARY_ROUNDS = 696
CENSUS_PRIMES = {
    5: 31,
    6: 61,
    7: 127,
    8: 251,
    9: 509,
    10: 1021,
    11: 2039,
    12: 4093,
    13: 8191,
    14: 16381,
}


def euclid_trace(modulus: int, denominator: int) -> tuple[int, ...]:
    """Return the canonical positive quotient trace for ``(modulus, denominator)``."""
    if modulus <= 1:
        raise ValueError("modulus must exceed one")
    if denominator <= 0 or denominator >= modulus:
        raise ValueError("denominator must lie in [1, modulus)")
    if math.gcd(modulus, denominator) != 1:
        raise ValueError("denominator must be a unit modulo modulus")

    left = modulus
    right = denominator
    quotients: list[int] = []
    while right:
        quotient, remainder = divmod(left, right)
        if quotient <= 0:
            raise AssertionError("canonical Euclid quotient must be positive")
        quotients.append(quotient)
        left, right = right, remainder
    if left != 1 or quotients[-1] < 2:
        raise AssertionError("unit trace must terminate at (1,0) with q_last >= 2")
    return tuple(quotients)


def reconstruct_inputs(quotients: Sequence[int]) -> tuple[int, int]:
    """Reconstruct the Euclid inputs from terminal state ``(1,0)``."""
    if not quotients or any(q <= 0 for q in quotients):
        raise ValueError("quotient trace must be nonempty and positive")
    left, right = 1, 0
    for quotient in reversed(quotients):
        left, right = quotient * left + right, left
    return left, right


def action_from_trace(
    modulus: int,
    value: int,
    quotients: Sequence[int],
) -> tuple[int, int]:
    """Apply the reversed quotient recurrence to ``(value, 0)`` modulo ``modulus``."""
    if value < 0 or value >= modulus:
        raise ValueError("value must be canonical modulo modulus")
    left, right = value, 0
    for quotient in reversed(quotients):
        left, right = (quotient * left + right) % modulus, left
    return left, right


def inverse_from_trace(
    modulus: int,
    left: int,
    right: int,
    quotients: Sequence[int],
) -> tuple[int, int]:
    """Invert ``action_from_trace`` on an arbitrary canonical register pair."""
    if not (0 <= left < modulus and 0 <= right < modulus):
        raise ValueError("registers must be canonical modulo modulus")
    for quotient in quotients:
        left, right = right, (left - quotient * right) % modulus
    return left, right


def forward_action(modulus: int, denominator: int, value: int) -> tuple[int, int]:
    return action_from_trace(modulus, value, euclid_trace(modulus, denominator))


def inverse_action(
    modulus: int,
    denominator: int,
    left: int,
    right: int,
) -> tuple[int, int]:
    return inverse_from_trace(
        modulus,
        left,
        right,
        euclid_trace(modulus, denominator),
    )


def gamma_encode(values: Iterable[int]) -> str:
    """Encode positive integers with the prefix-free Elias-gamma code."""
    pieces: list[str] = []
    count = 0
    for value in values:
        if value <= 0:
            raise ValueError("gamma values must be positive")
        binary = format(value, "b")
        pieces.append("0" * (len(binary) - 1) + binary)
        count += 1
    if count == 0:
        raise ValueError("gamma stream must be nonempty")
    return "".join(pieces)


def gamma_decode(bits: str) -> tuple[int, ...]:
    """Decode a complete Elias-gamma stream and reject any truncated suffix."""
    if not bits or any(bit not in "01" for bit in bits):
        raise ValueError("gamma stream must be a nonempty bit string")
    values: list[int] = []
    cursor = 0
    while cursor < len(bits):
        zero_count = 0
        while cursor < len(bits) and bits[cursor] == "0":
            zero_count += 1
            cursor += 1
        if cursor >= len(bits):
            raise ValueError("truncated gamma prefix")
        word_end = cursor + zero_count + 1
        if word_end > len(bits):
            raise ValueError("truncated gamma payload")
        values.append(int(bits[cursor:word_end], 2))
        cursor = word_end
    return tuple(values)


def trace_metrics(quotients: Sequence[int], width: int) -> dict[str, int]:
    payload_bits = sum(quotient.bit_length() for quotient in quotients)
    gamma_bits = sum(2 * quotient.bit_length() - 1 for quotient in quotients)
    shifted_add_terms = sum(quotient.bit_count() for quotient in quotients)
    return {
        "steps": len(quotients),
        "quotient_payload_bits": payload_bits,
        "gamma_bits": gamma_bits,
        "shifted_add_terms": shifted_add_terms,
        "shifted_add_word_area": shifted_add_terms * width,
        "max_quotient_bits": max(quotient.bit_length() for quotient in quotients),
    }


def exhaustive_action_report(modulus: int) -> dict[str, Any]:
    width = modulus.bit_length()
    forward_failures = 0
    inverse_failures = 0
    zero_companion_failures = 0
    checked_pairs = 0
    transcript = hashlib.sha256()
    byte_width = (width + 7) // 8

    for denominator in range(1, modulus):
        quotients = euclid_trace(modulus, denominator)
        for value in range(modulus):
            left, right = action_from_trace(modulus, value, quotients)
            recovered_left, recovered_right = inverse_from_trace(
                modulus,
                left,
                right,
                quotients,
            )
            forward_failures += right != denominator * value % modulus
            zero_companion_failures += left != 0
            inverse_failures += (recovered_left, recovered_right) != (value, 0)
            checked_pairs += 1
            for item in (denominator, value, left, right, recovered_left, recovered_right):
                transcript.update(item.to_bytes(byte_width, "big"))

    return {
        "modulus": modulus,
        "width": width,
        "checked_pairs": checked_pairs,
        "forward_failures": forward_failures,
        "inverse_failures": inverse_failures,
        "zero_companion_failures": zero_companion_failures,
        "transcript_sha256": transcript.hexdigest(),
    }


def _metric_summary(rows: Sequence[dict[str, int]], prefix: str = "") -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name in (
        "steps",
        "quotient_payload_bits",
        "gamma_bits",
        "shifted_add_terms",
        "shifted_add_word_area",
        "max_quotient_bits",
    ):
        values = sorted(row[name] for row in rows)
        if name == "max_quotient_bits":
            result[f"{prefix}min_trace_max_quotient_bits"] = values[0]
            result[f"{prefix}max_quotient_bits"] = values[-1]
            result[f"{prefix}p95_max_quotient_bits"] = values[
                (95 * len(values) - 1) // 100
            ]
            result[f"{prefix}mean_max_quotient_bits"] = round(
                sum(values) / len(values),
                6,
            )
        else:
            result[f"{prefix}min_{name}"] = values[0]
            result[f"{prefix}max_{name}"] = values[-1]
            result[f"{prefix}p95_{name}"] = values[(95 * len(values) - 1) // 100]
            result[f"{prefix}total_{name}"] = sum(values)
            result[f"{prefix}mean_{name}"] = round(sum(values) / len(values), 6)
    return result


def denominator_census(modulus: int) -> dict[str, Any]:
    width = modulus.bit_length()
    rows: list[dict[str, int]] = []
    reconstruction_failures = 0
    codec_failures = 0
    final_quotient_failures = 0
    for denominator in range(1, modulus):
        quotients = euclid_trace(modulus, denominator)
        reconstruction_failures += reconstruct_inputs(quotients) != (modulus, denominator)
        encoded = gamma_encode(quotients)
        codec_failures += gamma_decode(encoded) != quotients
        final_quotient_failures += quotients[-1] < 2
        rows.append(trace_metrics(quotients, width))

    return {
        "modulus": modulus,
        "width": width,
        "denominators": modulus - 1,
        "reconstruction_failures": reconstruction_failures,
        "codec_failures": codec_failures,
        "final_quotient_failures": final_quotient_failures,
        **_metric_summary(rows),
    }


def small_width_census() -> dict[int, dict[str, Any]]:
    return {
        width: denominator_census(modulus)
        for width, modulus in CENSUS_PRIMES.items()
    }


def _sample_denominator(index: int) -> int:
    digest = hashlib.sha256(
        f"quotient-euclid-secp256k1:{index}".encode("ascii")
    ).digest()
    return int.from_bytes(digest, "big") % (SECP256K1_P - 1) + 1


def production_sample_report(sample_count: int = 10_000) -> dict[str, Any]:
    if sample_count <= 0:
        raise ValueError("sample count must be positive")
    rows: list[dict[str, int]] = []
    reconstruction_failures = 0
    codec_failures = 0
    sample_sha = hashlib.sha256()
    for index in range(sample_count):
        denominator = _sample_denominator(index)
        quotients = euclid_trace(SECP256K1_P, denominator)
        reconstruction_failures += reconstruct_inputs(quotients) != (
            SECP256K1_P,
            denominator,
        )
        encoded = gamma_encode(quotients)
        codec_failures += gamma_decode(encoded) != quotients
        rows.append(trace_metrics(quotients, 256))
        sample_sha.update(denominator.to_bytes(32, "big"))
        sample_sha.update(len(encoded).to_bytes(2, "big"))

    return {
        "field": "secp256k1",
        "sample_method": "sha256('quotient-euclid-secp256k1:' || decimal_index)",
        "sample_count": sample_count,
        "sample_sha256": sample_sha.hexdigest(),
        "reconstruction_failures": reconstruction_failures,
        "codec_failures": codec_failures,
        **_metric_summary(rows),
    }


def run_gate() -> dict[str, Any]:
    exact_cases = [
        exhaustive_action_report(modulus)
        for modulus in (31, 61, 127, 251)
    ]
    census = small_width_census()
    production = production_sample_report()
    exact_passed = all(
        case["forward_failures"] == 0
        and case["inverse_failures"] == 0
        and case["zero_companion_failures"] == 0
        for case in exact_cases
    )
    transcript_passed = all(
        row["reconstruction_failures"] == 0
        and row["codec_failures"] == 0
        and row["final_quotient_failures"] == 0
        for row in census.values()
    ) and production["reconstruction_failures"] == 0 and production["codec_failures"] == 0
    observed_margin = (
        production["max_steps"] < LIVE_BINARY_ROUNDS
        and production["max_quotient_payload_bits"] < LIVE_BINARY_ROUNDS
        and production["max_gamma_bits"] < LIVE_BINARY_ROUNDS
    )
    admitted = exact_passed and transcript_passed and observed_margin

    payload: dict[str, Any] = {
        "schema": "quotient-euclid-unit-action-v1",
        "scope": "EXACT_RECURRENCE_AND_TRANSCRIPT_ECONOMICS_ONLY",
        "base_commit": BASE_COMMIT,
        "base_tree": BASE_TREE,
        "live_binary_rounds": LIVE_BINARY_ROUNDS,
        "exact_action_cases": exact_cases,
        "small_width_census": census,
        "production_sample": production,
        "exact_passed": exact_passed,
        "transcript_passed": transcript_passed,
        "observed_margin": observed_margin,
        "verdict": (
            "ADMIT_QUOTIENT_EUCLID_RECURRENCE_ONLY"
            if admitted
            else "HARD_NACK_QUOTIENT_EUCLID_RECURRENCE"
        ),
        "full_field_candidate": False,
        "remaining_blocker": "STATIC_REVERSIBLE_TRANSCRIPT_COMPILER",
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
