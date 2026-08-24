#!/usr/bin/env python3
"""Exact gates for blockwise Euclid cross-determinant compaction."""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
from collections import defaultdict
from typing import Any

import affine_shell_transducer as shell
import quotient_euclid_unit_action as euclid


BASE_COMMIT = "cbf229dbd46a7c677fe2e28da882b4f8a02bac7f"
BASE_TREE = "eab2326ce33549eceeb5c10aa64eae33f148b0ac"
IDENTITY_PRIMES = (31, 61, 127, 251)
RANK_PRIMES = (31, 61, 127, 251, 509, 1021, 2039, 4093)
COMPONENT_Q_CAP = 1100
PRODUCTION_WIDTH = 256


def _bits(value: int) -> int:
    return value.bit_length()


def _matrix_multiply(
    left: tuple[tuple[int, int], tuple[int, int]],
    right: tuple[tuple[int, int], tuple[int, int]],
) -> tuple[tuple[int, int], tuple[int, int]]:
    return (
        (
            left[0][0] * right[0][0] + left[0][1] * right[1][0],
            left[0][0] * right[0][1] + left[0][1] * right[1][1],
        ),
        (
            left[1][0] * right[0][0] + left[1][1] * right[1][0],
            left[1][0] * right[0][1] + left[1][1] * right[1][1],
        ),
    )


def prefix_checkpoint(modulus: int, multiplier: int, cut_width: int) -> dict[str, Any]:
    """Return the canonical Euclid prefix ending inside ``cut_width`` bits."""
    if multiplier <= 0 or multiplier >= modulus:
        raise ValueError("multiplier must be nonzero and canonical modulo modulus")
    if cut_width < 1 or cut_width > modulus.bit_length():
        raise ValueError("cut width must lie in the field width")

    left, right = modulus, multiplier
    matrix = ((1, 0), (0, 1))
    quotients: list[int] = []
    while right and max(_bits(left), _bits(right)) > cut_width:
        quotient, remainder = divmod(left, right)
        matrix = _matrix_multiply(matrix, ((0, 1), (1, -quotient)))
        quotients.append(quotient)
        left, right = right, remainder

    return {
        "left": left,
        "right": right,
        "matrix": matrix,
        "quotients": tuple(quotients),
        "orientation": -1 if len(quotients) & 1 else 1,
    }


def transformed_seed_row(
    modulus: int,
    multiplier: int,
    value: int,
    cut_width: int,
) -> tuple[int, int]:
    """Transform the cheap seed row ``(lambda,T)`` by the same prefix."""
    if value < 0 or value >= modulus:
        raise ValueError("value must be canonical modulo modulus")
    checkpoint = prefix_checkpoint(modulus, multiplier, cut_width)
    (a, b), (c, d) = checkpoint["matrix"]
    return (
        (value * a + multiplier * c) % modulus,
        (value * b + multiplier * d) % modulus,
    )


def checkpoint_product(
    modulus: int,
    multiplier: int,
    value: int,
    cut_width: int,
) -> int:
    checkpoint = prefix_checkpoint(modulus, multiplier, cut_width)
    seed_left, seed_right = transformed_seed_row(
        modulus,
        multiplier,
        value,
        cut_width,
    )
    cross = (
        checkpoint["left"] * seed_right
        - checkpoint["right"] * seed_left
    ) % modulus
    return (-checkpoint["orientation"] * cross) % modulus


@functools.lru_cache(maxsize=None)
def identity_case_report(modulus: int) -> dict[str, Any]:
    width = modulus.bit_length()
    row_failures = 0
    determinant_failures = 0
    checked_states = 0
    transcript = hashlib.sha256()
    byte_width = (width + 7) // 8

    for cut_width in range(1, width + 1):
        for multiplier in range(1, modulus):
            checkpoint = prefix_checkpoint(modulus, multiplier, cut_width)
            (a, b), (c, d) = checkpoint["matrix"]
            row_failures += (
                modulus * a + multiplier * c,
                modulus * b + multiplier * d,
            ) != (checkpoint["left"], checkpoint["right"])
            row_failures += a * d - b * c != checkpoint["orientation"]
            for value in range(modulus):
                product = checkpoint_product(
                    modulus,
                    multiplier,
                    value,
                    cut_width,
                )
                determinant_failures += product != multiplier * value % modulus
                checked_states += 1
                for item in (cut_width, multiplier, value, product):
                    transcript.update(item.to_bytes(byte_width, "big"))

    return {
        "modulus": modulus,
        "width": width,
        "checked_states": checked_states,
        "row_failures": row_failures,
        "determinant_failures": determinant_failures,
        "transcript_sha256": transcript.hexdigest(),
    }


def _prefix_metric_states(multiplier: int) -> list[tuple[int, int, int, int]]:
    left, right = euclid.SECP256K1_P, multiplier
    raw_bits = 0
    gamma_bits = 0
    states = [(max(_bits(left), _bits(right)), _bits(left) + _bits(right), 0, 0)]
    while right:
        quotient, remainder = divmod(left, right)
        quotient_bits = quotient.bit_length()
        raw_bits += quotient_bits
        gamma_bits += 2 * quotient_bits - 1
        left, right = right, remainder
        states.append(
            (
                max(_bits(left), _bits(right)),
                _bits(left) + _bits(right),
                raw_bits,
                gamma_bits,
            )
        )
    return states


@functools.lru_cache(maxsize=1)
def production_prefix_floor_report(sample_count: int = 10_000) -> dict[str, Any]:
    if sample_count <= 0:
        raise ValueError("sample count must be positive")
    max_raw_q = [0] * (PRODUCTION_WIDTH + 1)
    max_gamma_q = [0] * (PRODUCTION_WIDTH + 1)
    raw_witness = [-1] * (PRODUCTION_WIDTH + 1)
    gamma_witness = [-1] * (PRODUCTION_WIDTH + 1)
    sample_hash = hashlib.sha256()

    for sample_index in range(sample_count):
        multiplier = euclid._sample_denominator(sample_index)
        states = _prefix_metric_states(multiplier)
        cursor = 0
        for cut_width in range(PRODUCTION_WIDTH, 0, -1):
            while cursor + 1 < len(states) and states[cursor][0] > cut_width:
                cursor += 1
            _, residual_bits, raw_bits, gamma_bits = states[cursor]
            raw_q = 3 * PRODUCTION_WIDTH + residual_bits + raw_bits
            gamma_q = 3 * PRODUCTION_WIDTH + residual_bits + gamma_bits
            if raw_q > max_raw_q[cut_width]:
                max_raw_q[cut_width] = raw_q
                raw_witness[cut_width] = sample_index
            if gamma_q > max_gamma_q[cut_width]:
                max_gamma_q[cut_width] = gamma_q
                gamma_witness[cut_width] = sample_index
        sample_hash.update(multiplier.to_bytes(32, "big"))

    material_cuts = range(1, PRODUCTION_WIDTH)
    minimum_raw = min(max_raw_q[cut_width] for cut_width in material_cuts)
    minimum_gamma = min(max_gamma_q[cut_width] for cut_width in material_cuts)
    raw_minimizers = tuple(
        cut_width
        for cut_width in material_cuts
        if max_raw_q[cut_width] == minimum_raw
    )
    gamma_minimizers = tuple(
        cut_width
        for cut_width in material_cuts
        if max_gamma_q[cut_width] == minimum_gamma
    )

    return {
        "field": "secp256k1",
        "sample_method": "sha256('quotient-euclid-secp256k1:' || decimal_index)",
        "sample_count": sample_count,
        "sample_sha256": sample_hash.hexdigest(),
        "cut_widths": PRODUCTION_WIDTH - 1,
        "floor_formula": "3n+bitlen(u)+bitlen(v)+prefix_payload_bits",
        "minimum_worst_raw_q": minimum_raw,
        "raw_minimizing_cut_widths": raw_minimizers,
        "raw_witness_sample_index": raw_witness[raw_minimizers[0]],
        "raw_excess_over_component_cap_q": minimum_raw - COMPONENT_Q_CAP,
        "minimum_worst_gamma_q": minimum_gamma,
        "gamma_minimizing_cut_widths": gamma_minimizers,
        "gamma_witness_sample_index": gamma_witness[gamma_minimizers[0]],
        "cut_32_worst_raw_q": max_raw_q[32],
        "cut_32_worst_gamma_q": max_gamma_q[32],
        "per_cut_worst_raw_q": tuple(max_raw_q[1:PRODUCTION_WIDTH]),
        "per_cut_worst_gamma_q": tuple(max_gamma_q[1:PRODUCTION_WIDTH]),
        "excluded_costs": (
            "quotient_boundaries",
            "parser",
            "quotient_arithmetic",
            "controls",
            "carries",
            "orientation",
            "determinant",
            "cleanup",
        ),
    }


def _checkpoint_state(
    modulus: int,
    multiplier: int,
    value: int,
    cut_width: int,
) -> tuple[int, int, int, int, int]:
    checkpoint = prefix_checkpoint(modulus, multiplier, cut_width)
    seed_left, seed_right = transformed_seed_row(
        modulus,
        multiplier,
        value,
        cut_width,
    )
    parity = int(checkpoint["orientation"] < 0)
    return (
        checkpoint["left"],
        checkpoint["right"],
        seed_left,
        seed_right,
        parity,
    )


@functools.lru_cache(maxsize=None)
def code_free_case_report(modulus: int) -> dict[str, Any]:
    width = modulus.bit_length()
    cases = []
    representative = None
    for cut_width in range(1, width + 1):
        counts: dict[tuple[int, int, int, int, int], int] = defaultdict(int)
        first_input: dict[tuple[int, int, int, int, int], tuple[int, int]] = {}
        witness = None
        for multiplier in range(1, modulus):
            for value in range(modulus):
                state = _checkpoint_state(modulus, multiplier, value, cut_width)
                if state in first_input and witness is None:
                    witness = {
                        "state": state,
                        "input_1": first_input[state],
                        "input_2": (multiplier, value),
                    }
                else:
                    first_input.setdefault(state, (multiplier, value))
                counts[state] += 1
        collisions = sum(count - 1 for count in counts.values())
        if collisions:
            representative = witness
        cases.append(
            {
                "cut_width": cut_width,
                "inputs": modulus * (modulus - 1),
                "distinct_states": len(counts),
                "collisions": collisions,
                "max_fiber_size": max(counts.values()),
                "representative_collision": witness,
            }
        )

    collision_free_shrinks = [
        width - case["cut_width"]
        for case in cases
        if case["collisions"] == 0
    ]
    return {
        "modulus": modulus,
        "width": width,
        "seed": "(lambda,T)",
        "cuts": cases,
        "deepest_collision_free_shrink_bits": max(collision_free_shrinks),
        "representative_collision": representative,
    }


def _residual_key(modulus: int, multiplier: int, cut_width: int) -> tuple[int, int, int]:
    checkpoint = prefix_checkpoint(modulus, multiplier, cut_width)
    return (
        checkpoint["left"],
        checkpoint["right"],
        int(checkpoint["orientation"] < 0),
    )


def _mobius_transform(truth_table: list[int], variables: int) -> list[int]:
    coefficients = truth_table.copy()
    for bit in range(variables):
        bit_mask = 1 << bit
        for index in range(len(coefficients)):
            if index & bit_mask:
                coefficients[index] ^= coefficients[index ^ bit_mask]
    return coefficients


@functools.lru_cache(maxsize=None)
def rank_decoder_anf_report(modulus: int) -> dict[str, Any]:
    width = modulus.bit_length()
    cut_width = width // 2
    fibers: dict[tuple[int, int, int], list[int]] = defaultdict(list)
    for multiplier in range(1, modulus):
        fibers[_residual_key(modulus, multiplier, cut_width)].append(multiplier)

    max_fiber_size = max(len(values) for values in fibers.values())
    rank_bits = (max_fiber_size - 1).bit_length()
    variables = 2 * cut_width + 1 + rank_bits
    table_size = 1 << variables
    output_mask = sum(1 << bit for bit in range(1, width, 2))
    truth_table = [0] * table_size
    decoder_states = 0
    transcript = hashlib.sha256()

    for (left, right, parity), multipliers in fibers.items():
        for rank, multiplier in enumerate(multipliers):
            index = (
                left
                | (right << cut_width)
                | (parity << (2 * cut_width))
                | (rank << (2 * cut_width + 1))
            )
            truth_table[index] = (multiplier & output_mask).bit_count() & 1
            decoder_states += 1
            transcript.update(index.to_bytes((variables + 7) // 8, "big"))
            transcript.update(multiplier.to_bytes((width + 7) // 8, "big"))

    coefficients = _mobius_transform(truth_table, variables)
    support = [index for index, coefficient in enumerate(coefficients) if coefficient]
    degree = max(index.bit_count() for index in support) if support else 0
    return {
        "modulus": modulus,
        "width": width,
        "cut_width": cut_width,
        "residual_keys": len(fibers),
        "decoder_states": decoder_states,
        "max_fiber_size": max_fiber_size,
        "rank_bits": rank_bits,
        "variables": variables,
        "output_mask": output_mask,
        "truth_table_size": table_size,
        "anf_degree": degree,
        "anf_density": len(support),
        "anf_density_fraction": len(support) / table_size,
        "decoder_support_sha256": transcript.hexdigest(),
    }


def run_gate() -> dict[str, Any]:
    identity_cases = [identity_case_report(modulus) for modulus in IDENTITY_PRIMES]
    prefix_floor = production_prefix_floor_report()
    code_free_cases = [code_free_case_report(modulus) for modulus in IDENTITY_PRIMES]
    rank_cases = [rank_decoder_anf_report(modulus) for modulus in RANK_PRIMES]

    identity_passed = all(
        case["row_failures"] == 0 and case["determinant_failures"] == 0
        for case in identity_cases
    )
    stored_prefix_closed = prefix_floor["minimum_worst_raw_q"] > COMPONENT_Q_CAP
    code_free_closed = all(
        case["deepest_collision_free_shrink_bits"] <= 1
        and case["cuts"][case["width"] - 3]["collisions"] > 0
        for case in code_free_cases
    )
    rank_decoder_closed = all(
        case["anf_degree"] >= case["variables"] - 1
        and case["anf_density"] > case["truth_table_size"] // 4
        for case in rank_cases
    )

    payload: dict[str, Any] = {
        "schema": "blockwise-residual-cofactor-compactor-v1",
        "scope": "PREFIX_DETERMINANT_AND_NATURAL_HISTORY_OR_RANK_CODECS_ONLY",
        "base_commit": BASE_COMMIT,
        "base_tree": BASE_TREE,
        "component_q_cap": COMPONENT_Q_CAP,
        "identity_cases": identity_cases,
        "production_prefix_floor": prefix_floor,
        "code_free_cases": code_free_cases,
        "rank_decoder_cases": rank_cases,
        "identity_verdict": (
            "ADMIT_PREFIX_CROSS_DETERMINANT_PRODUCT_IDENTITY_ONLY"
            if identity_passed
            else "HARD_NACK_PREFIX_CROSS_DETERMINANT_PRODUCT_IDENTITY"
        ),
        "stored_prefix_verdict": (
            "HARD_NACK_STORED_PREFIX_Q_FLOOR"
            if stored_prefix_closed
            else "HOLD_STORED_PREFIX_Q_FLOOR"
        ),
        "code_free_verdict": (
            "HARD_NACK_QUOTIENT_FREE_PREFIX_COLLISION"
            if code_free_closed
            else "HOLD_QUOTIENT_FREE_PREFIX_COLLISION"
        ),
        "rank_decoder_verdict": (
            "HARD_NACK_ZERO_EXTENDED_RESIDUAL_RANK_DECODER"
            if rank_decoder_closed
            else "HOLD_ZERO_EXTENDED_RESIDUAL_RANK_DECODER"
        ),
        "verdict": (
            "HARD_NACK_BLOCKWISE_RESIDUAL_COFACTOR_COMPACTOR_NATURAL_CODECS"
            if identity_passed
            and stored_prefix_closed
            and code_free_closed
            and rank_decoder_closed
            else "HOLD_BLOCKWISE_RESIDUAL_COFACTOR_COMPACTOR_NATURAL_CODECS"
        ),
        "universal_lower_bound": False,
        "full_field_candidate": False,
        "next_grammar": "CROSS_DETERMINANT_CONTINUANT_RANK_CODEC",
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
