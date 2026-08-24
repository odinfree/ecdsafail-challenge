#!/usr/bin/env python3
"""Exact gates for the two natural online-cofactor cleanup strategies."""

from __future__ import annotations

import argparse
import hashlib
import json
from typing import Any

import affine_shell_transducer as shell
import coupled_transposed_seed as seed


BASE_COMMIT = "cbf229dbd46a7c677fe2e28da882b4f8a02bac7f"
BASE_TREE = "eab2326ce33549eceeb5c10aa64eae33f148b0ac"
TEST_PRIMES = (31, 61, 127, 251)
COMPONENT_Q_CAP = 1100
PROTECTED_PEAK_Q = 1266


def output_frame_garbage(modulus: int, multiplier: int, product: int) -> int:
    """Recover r_T*lambda from the surviving frame (T, z=T*lambda)."""
    if multiplier <= 0 or multiplier >= modulus:
        raise ValueError("multiplier must be nonzero and canonical modulo modulus")
    if product < 0 or product >= modulus:
        raise ValueError("product must be canonical modulo modulus")
    matrix = seed.orientation_one_matrix(modulus, multiplier)
    value = product * pow(multiplier, -1, modulus) % modulus
    return matrix["r"] * value % modulus


def alternating_output_mask(width: int) -> int:
    """Select bits 1,3,5,... of the discarded field word."""
    if width < 1:
        raise ValueError("width must be positive")
    return sum(1 << bit for bit in range(1, width, 2))


def zero_extended_phase_bit(
    modulus: int,
    multiplier_bits: int,
    product_bits: int,
    output_mask: int,
) -> int:
    """Totalize illegal bit patterns to zero, then return selected parity."""
    if not 1 <= multiplier_bits < modulus or not 0 <= product_bits < modulus:
        return 0
    garbage = output_frame_garbage(modulus, multiplier_bits, product_bits)
    return (garbage & output_mask).bit_count() & 1


def _mobius_transform(truth_table: list[int], variable_count: int) -> list[int]:
    coefficients = truth_table.copy()
    for bit in range(variable_count):
        bit_mask = 1 << bit
        for index in range(len(coefficients)):
            if index & bit_mask:
                coefficients[index] ^= coefficients[index ^ bit_mask]
    return coefficients


def phase_anf_report(modulus: int) -> dict[str, Any]:
    """Measure one deterministic zero-extended phase coordinate exactly."""
    width = modulus.bit_length()
    variable_count = 2 * width
    table_size = 1 << variable_count
    word_mask = (1 << width) - 1
    output_mask = alternating_output_mask(width)
    truth_table = [0] * table_size
    transcript = hashlib.sha256()

    for index in range(table_size):
        multiplier = index & word_mask
        product = index >> width
        phase = zero_extended_phase_bit(
            modulus,
            multiplier,
            product,
            output_mask,
        )
        truth_table[index] = phase
        transcript.update(bytes((phase,)))

    coefficients = _mobius_transform(truth_table, variable_count)
    support = [index for index, coefficient in enumerate(coefficients) if coefficient]
    degree = max(index.bit_count() for index in support) if support else 0
    return {
        "modulus": modulus,
        "width": width,
        "variables": variable_count,
        "output_mask": output_mask,
        "legal_states": modulus * (modulus - 1),
        "truth_table_size": table_size,
        "anf_degree": degree,
        "anf_density": len(support),
        "anf_density_fraction": len(support) / table_size,
        "truth_table_sha256": transcript.hexdigest(),
    }


def dual_row_qubit_report(width: int) -> dict[str, Any]:
    """Return the field-word floor before any controls, carries, or cleanup."""
    if width < 1:
        raise ValueError("width must be positive")
    value_words = 2
    product_words = 2
    cancellation_words = 2
    total_words = value_words + product_words + cancellation_words
    field_word_floor = total_words * width
    return {
        "width": width,
        "value_words": value_words,
        "product_words": product_words,
        "cancellation_words": cancellation_words,
        "total_words": total_words,
        "field_word_floor_q": field_word_floor,
        "component_cap_q": COMPONENT_Q_CAP,
        "protected_peak_q": PROTECTED_PEAK_Q,
        "excess_over_component_cap_q": field_word_floor - COMPONENT_Q_CAP,
        "excess_over_protected_peak_q": field_word_floor - PROTECTED_PEAK_Q,
        "excluded_costs": (
            "quotient_extraction",
            "arithmetic_carries",
            "orientation",
            "zero_fiber_logic",
            "cleanup",
        ),
    }


def exact_garbage_failures(modulus: int) -> int:
    failures = 0
    for multiplier in range(1, modulus):
        matrix = seed.orientation_one_matrix(modulus, multiplier)
        for value in range(modulus):
            product = multiplier * value % modulus
            failures += (
                output_frame_garbage(modulus, multiplier, product)
                != matrix["r"] * value % modulus
            )
    return failures


def run_gate() -> dict[str, Any]:
    qubits = dual_row_qubit_report(256)
    phase_cases = []
    for modulus in TEST_PRIMES:
        report = phase_anf_report(modulus)
        report["garbage_relation_failures"] = exact_garbage_failures(modulus)
        phase_cases.append(report)

    dual_row_closed = (
        qubits["field_word_floor_q"] > qubits["component_cap_q"]
        and qubits["field_word_floor_q"] > qubits["protected_peak_q"]
    )
    measurement_closed = all(
        case["garbage_relation_failures"] == 0
        and case["anf_degree"] >= 2 * case["width"] - 3
        and case["anf_density"] > case["truth_table_size"] // 5
        for case in phase_cases
    )

    payload: dict[str, Any] = {
        "schema": "online-cofactor-product-recurrence-v1",
        "scope": "COHERENT_DUAL_ROW_AND_ZERO_EXTENDED_PHASE_COORDINATE_ONLY",
        "base_commit": BASE_COMMIT,
        "base_tree": BASE_TREE,
        "dual_row_qubits": qubits,
        "phase_cases": phase_cases,
        "coherent_dual_row_verdict": (
            "HARD_NACK_COHERENT_DUAL_ROW_Q_FLOOR"
            if dual_row_closed
            else "HOLD_COHERENT_DUAL_ROW_Q_FLOOR"
        ),
        "measurement_cleanup_verdict": (
            "HARD_NACK_ZERO_EXTENDED_COFACTOR_MBUC"
            if measurement_closed
            else "HOLD_ZERO_EXTENDED_COFACTOR_MBUC"
        ),
        "verdict": (
            "HARD_NACK_ONLINE_COFACTOR_NATURAL_CLEANUPS"
            if dual_row_closed and measurement_closed
            else "HOLD_ONLINE_COFACTOR_NATURAL_CLEANUPS"
        ),
        "universal_lower_bound": False,
        "full_field_candidate": False,
        "next_grammar": "BLOCKWISE_RESIDUAL_COFACTOR_COMPACTOR",
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
