#!/usr/bin/env python3
"""Exact oracle and resource ledger for odd multiplication modulo 2^n."""

from __future__ import annotations

import argparse
import hashlib
import json
from typing import Any

import affine_shell_transducer as shell


BASE_COMMIT = "cbf229dbd46a7c677fe2e28da882b4f8a02bac7f"
BASE_TREE = "eab2326ce33549eceeb5c10aa64eae33f148b0ac"
COMPONENT_Q_BUDGET = 1_100
COMPONENT_T_BUDGET = 335_738.86


def _validate(multiplier: int, value: int, width: int) -> int:
    if width < 1:
        raise ValueError("width must be positive")
    modulus = 1 << width
    if multiplier < 0 or multiplier >= modulus:
        raise ValueError("multiplier does not fit width")
    if value < 0 or value >= modulus:
        raise ValueError("value does not fit width")
    if multiplier & 1 == 0:
        raise ValueError("multiplier must be odd")
    return modulus


def forward(multiplier: int, value: int, width: int) -> tuple[int, int]:
    """Apply the descending triangular recurrence exactly."""
    modulus = _validate(multiplier, value, width)
    result = value
    for index in range(width - 2, -1, -1):
        suffix_width = width - index - 1
        suffix_mask = (1 << suffix_width) - 1
        control = (result >> index) & 1
        suffix = result >> (index + 1)
        gated_addend = control * ((multiplier >> 1) & suffix_mask)
        suffix = (suffix + gated_addend) & suffix_mask
        result = (result & ((1 << (index + 1)) - 1)) | (suffix << (index + 1))
    return multiplier, result % modulus


def inverse(multiplier: int, value: int, width: int) -> tuple[int, int]:
    """Reverse the triangular recurrence in ascending control order."""
    modulus = _validate(multiplier, value, width)
    result = value
    for index in range(0, width - 1):
        suffix_width = width - index - 1
        suffix_mask = (1 << suffix_width) - 1
        control = (result >> index) & 1
        suffix = result >> (index + 1)
        gated_subtrahend = control * ((multiplier >> 1) & suffix_mask)
        suffix = (suffix - gated_subtrahend) & suffix_mask
        result = (result & ((1 << (index + 1)) - 1)) | (suffix << (index + 1))
    return multiplier, result % modulus


def exhaustive_width_report(width: int) -> dict[str, Any]:
    modulus = 1 << width
    forward_failures = 0
    inverse_failures = 0
    preserved_multiplier_failures = 0
    transcript = hashlib.sha256()
    byte_width = (width + 7) // 8
    for multiplier in range(1, modulus, 2):
        inverse_multiplier = pow(multiplier, -1, modulus)
        for value in range(modulus):
            kept, product = forward(multiplier, value, width)
            expected = multiplier * value % modulus
            forward_failures += product != expected
            preserved_multiplier_failures += kept != multiplier
            kept_inverse, recovered = inverse(multiplier, product, width)
            inverse_failures += recovered != value
            preserved_multiplier_failures += kept_inverse != multiplier
            transcript.update(multiplier.to_bytes(byte_width, "big"))
            transcript.update(value.to_bytes(byte_width, "big"))
            transcript.update(product.to_bytes(byte_width, "big"))
            transcript.update(recovered.to_bytes(byte_width, "big"))
            # Independent algebraic inverse control.
            inverse_failures += recovered != product * inverse_multiplier % modulus
    return {
        "width": width,
        "odd_multipliers": modulus // 2,
        "input_pairs": modulus * modulus // 2,
        "forward_failures": forward_failures,
        "inverse_failures": inverse_failures,
        "preserved_multiplier_failures": preserved_multiplier_failures,
        "transcript_sha256": transcript.hexdigest(),
    }


def resource_report(width: int) -> dict[str, Any]:
    if width < 1:
        raise ValueError("width must be positive")
    and_toffolis = width * (width - 1) // 2
    adder_toffolis = (width - 1) * (width - 2) // 2
    total_toffolis = (width - 1) ** 2
    peak_qubits = width * 2 if width == 1 else 4 * width - 2
    return {
        "width": width,
        "and_toffolis": and_toffolis,
        "adder_toffolis": adder_toffolis,
        "total_toffolis": total_toffolis,
        "peak_qubits": peak_qubits,
        "component_q_budget": COMPONENT_Q_BUDGET,
        "component_t_budget": COMPONENT_T_BUDGET,
        "inside_component_budget": (
            peak_qubits <= COMPONENT_Q_BUDGET
            and total_toffolis <= COMPONENT_T_BUDGET
        ),
    }


def run_gate() -> dict[str, Any]:
    cases = [exhaustive_width_report(width) for width in range(1, 10)]
    exhaustive_passed = all(
        case["forward_failures"] == 0
        and case["inverse_failures"] == 0
        and case["preserved_multiplier_failures"] == 0
        for case in cases
    )
    resource = resource_report(256)
    admitted = exhaustive_passed and resource["inside_component_budget"]
    payload: dict[str, Any] = {
        "schema": "odd-pow2-triangular-action-v1",
        "scope": "ODD_QUANTUM_MULTIPLIER_ACTION_MODULO_2_POW_N",
        "base_commit": BASE_COMMIT,
        "base_tree": BASE_TREE,
        "cases": cases,
        "exhaustive_passed": exhaustive_passed,
        "resource_256": resource,
        "resource_formula": {
            "and_toffolis": "n(n-1)/2",
            "adder_toffolis": "(n-1)(n-2)/2",
            "total_toffolis": "(n-1)^2",
            "peak_qubits_n_ge_2": "4n-2",
        },
        "verdict": (
            "ADMIT_ODD_POW2_TRIANGULAR_SUBPRIMITIVE"
            if admitted
            else "HARD_NACK_ODD_POW2_TRIANGULAR_ACTION"
        ),
        "full_field_candidate": False,
        "remaining_blocker": "PSEUDO_MERSENNE_NONLOCAL_FOLD",
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
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run_gate(), sort_keys=True, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
