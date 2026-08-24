#!/usr/bin/env python3
"""Exact natural trace-tag search for curve-support root selection."""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
from collections import defaultdict
from typing import Any, Sequence

import affine_shell_transducer as shell
import curve_support_online_constant_seed as support
import online_transposed_unit_action as online
import quotient_euclid_unit_action as euclid
import rational_euclid_tag_root_carrier as rational


BASE_COMMIT = "cbf229dbd46a7c677fe2e28da882b4f8a02bac7f"
BASE_TREE = "eab2326ce33549eceeb5c10aa64eae33f148b0ac"
EXACT_BRANCH_PRIMES = (31, 61, 127, 1021, 4093)
AFFINE_PRIMES = (31, 61, 127, 251, 509, 1021, 4093)
SECP256K1_P = (1 << 256) - (1 << 32) - 977
SECP256K1_GX = int(
    "79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798",
    16,
)
PRODUCTION_SAMPLE_COUNT = 10_000
STATISTIC_NAMES = (
    "length",
    "sum",
    "alternating_sum",
    "first",
    "last",
    "penultimate",
    "quotient_popcount",
    "maximum",
    "weighted_sum",
    "quotient_xor",
    "r",
    "k",
)


@functools.lru_cache(maxsize=None)
def trace_statistics(modulus: int, multiplier: int) -> tuple[int, ...]:
    quotients = euclid.euclid_trace(modulus, multiplier)
    matrix = online.matrix_from_quotients(modulus, multiplier, quotients)
    if matrix["orientation"] != 1:
        alternate = quotients[:-1] + (quotients[-1] - 1, 1)
        matrix = online.matrix_from_quotients(modulus, multiplier, alternate)
    quotient_xor = 0
    for quotient in quotients:
        quotient_xor ^= quotient
    return (
        len(quotients),
        sum(quotients),
        sum(
            quotient if index % 2 == 0 else -quotient
            for index, quotient in enumerate(quotients)
        ),
        quotients[0],
        quotients[-1],
        quotients[-2] if len(quotients) > 1 else 0,
        sum(quotient.bit_count() for quotient in quotients),
        max(quotients),
        sum((index + 1) * quotient for index, quotient in enumerate(quotients)),
        quotient_xor,
        matrix["r"],
        matrix["k"],
    )


def tag_schemes(maximum_bits: int) -> tuple[tuple[int, tuple[Any, ...]], ...]:
    schemes: list[tuple[int, tuple[Any, ...]]] = []
    for name in STATISTIC_NAMES:
        for bits in range(1, maximum_bits + 1):
            schemes.append((bits, (name, bits)))
    for left_index, left_name in enumerate(STATISTIC_NAMES):
        for right_name in STATISTIC_NAMES[left_index + 1 :]:
            for total_bits in range(2, maximum_bits + 1):
                for left_bits in range(1, total_bits):
                    schemes.append(
                        (
                            total_bits,
                            (left_name, left_bits, right_name, total_bits - left_bits),
                        )
                    )
    schemes.sort(key=lambda item: (item[0], item[1]))
    return tuple(schemes)


def _tag(statistics: Sequence[int], scheme: Sequence[Any]) -> int | tuple[int, int]:
    left_name, left_bits = scheme[:2]
    left = statistics[STATISTIC_NAMES.index(left_name)] & ((1 << left_bits) - 1)
    if len(scheme) == 2:
        return left
    right_name, right_bits = scheme[2:]
    right = statistics[STATISTIC_NAMES.index(right_name)] & ((1 << right_bits) - 1)
    return left, right


def _branch_collisions(
    fibers: Sequence[Sequence[int]],
    statistics: dict[int, tuple[int, ...]],
    scheme: Sequence[Any],
    *,
    early_exit: bool = False,
) -> int:
    collisions = 0
    for fiber in fibers:
        tags = {_tag(statistics[multiplier], scheme) for multiplier in fiber}
        collisions += len(fiber) - len(tags)
        if early_exit and collisions:
            return collisions
    return collisions


@functools.lru_cache(maxsize=None)
def exact_branch_case_report(modulus: int) -> dict[str, Any]:
    if modulus not in EXACT_BRANCH_PRIMES:
        raise ValueError("modulus is not an exact GLV branch-test field")
    classical_point = support.first_classical_point(modulus)
    groups = support._support_groups(modulus, classical_point)
    fibers = tuple(
        tuple(multiplier for _base_g, _k, multiplier, _value in values)
        for values in groups.values()
        if len(values) > 1
    )
    statistics = {
        multiplier: trace_statistics(modulus, multiplier)
        for multiplier in range(1, modulus)
    }
    winner: tuple[Any, ...] | None = None
    minimum_bits: int | None = None
    for bits, scheme in tag_schemes(modulus.bit_length()):
        if _branch_collisions(fibers, statistics, scheme, early_exit=True) == 0:
            minimum_bits = bits
            winner = scheme
            break
    if winner is None or minimum_bits is None:
        raise AssertionError("full-width k must distinguish every multiplier")
    fiber_failures = sum(
        len(fiber) > 3 or len(fiber) != len(set(fiber)) for fiber in fibers
    )
    return {
        "modulus": modulus,
        "width": modulus.bit_length(),
        "classical_x": classical_point[0],
        "classical_y": classical_point[1],
        "multi_state_fibers": len(fibers),
        "curve_fiber_failures": fiber_failures,
        "minimum_tag_bits": minimum_bits,
        "winning_scheme": winner,
        "winning_collisions": _branch_collisions(fibers, statistics, winner),
    }


def _affine_consistent(
    modulus: int,
    rows: Sequence[tuple[int, int, int]],
    statistics: dict[int, tuple[int, ...]],
    scheme: Sequence[Any],
) -> bool:
    classes: dict[int | tuple[int, int], list[tuple[int, int, int]]] = defaultdict(list)
    for garbage, product, multiplier in rows:
        classes[_tag(statistics[multiplier], scheme)].append(
            (garbage, product, multiplier)
        )
    for values in classes.values():
        features = [(garbage, product, 1) for garbage, product, _ in values]
        augmented = [
            (garbage, product, 1, multiplier)
            for garbage, product, multiplier in values
        ]
        if rational.matrix_rank(features, modulus) != rational.matrix_rank(
            augmented,
            modulus,
        ):
            return False
    return True


@functools.lru_cache(maxsize=None)
def affine_decoder_case_report(modulus: int) -> dict[str, Any]:
    if modulus not in AFFINE_PRIMES:
        raise ValueError("modulus is not an exact affine trace-tag field")
    rows = rational.selected_seed_support(modulus)
    statistics = {
        multiplier: trace_statistics(modulus, multiplier)
        for multiplier in range(1, modulus)
    }
    winner: tuple[Any, ...] | None = None
    minimum_bits: int | None = None
    for bits, scheme in tag_schemes(modulus.bit_length()):
        if _affine_consistent(modulus, rows, statistics, scheme):
            minimum_bits = bits
            winner = scheme
            break
    if winner is None or minimum_bits is None:
        raise AssertionError("full-width k must yield singleton-T tag classes")
    return {
        "modulus": modulus,
        "width": modulus.bit_length(),
        "support_states": len(rows),
        "minimum_tag_bits": minimum_bits,
        "winning_scheme": winner,
        "full_word_tag_only": minimum_bits >= modulus.bit_length(),
        "k_is_modular_inverse": all(
            trace_statistics(modulus, multiplier)[STATISTIC_NAMES.index("k")]
            * multiplier
            % modulus
            == 1
            for multiplier in range(1, modulus)
        ),
    }


def _nontrivial_cube_root_of_unity(modulus: int) -> int:
    exponent = (modulus - 1) // 3
    for generator in range(2, 100):
        candidate = pow(generator, exponent, modulus)
        if candidate != 1:
            if pow(candidate, 3, modulus) != 1:
                raise AssertionError("candidate must be a cube root of unity")
            return candidate
    raise AssertionError("small generator search failed")


@functools.lru_cache(maxsize=None)
def _production_triples(
    sample_count: int,
) -> tuple[tuple[tuple[tuple[int, ...], ...], ...], int, str, int]:
    beta = _nontrivial_cube_root_of_unity(SECP256K1_P)
    triples: list[tuple[tuple[int, ...], ...]] = []
    sample_sha = hashlib.sha256()
    draw = 0
    while len(triples) < sample_count:
        output_x = int.from_bytes(
            hashlib.sha256(
                f"support-trace-root-selector:{draw}".encode("ascii")
            ).digest(),
            "big",
        ) % SECP256K1_P
        draw += 1
        if output_x == 0:
            continue
        right_side = (pow(output_x, 3, SECP256K1_P) + 7) % SECP256K1_P
        if pow(right_side, (SECP256K1_P - 1) // 2, SECP256K1_P) != 1:
            continue
        roots = (
            output_x,
            beta * output_x % SECP256K1_P,
            beta * beta * output_x % SECP256K1_P,
        )
        multipliers = tuple(
            (SECP256K1_GX - root) % SECP256K1_P for root in roots
        )
        if 0 in multipliers:
            continue
        triples.append(
            tuple(
                trace_statistics(SECP256K1_P, multiplier)
                for multiplier in multipliers
            )
        )
        sample_sha.update(output_x.to_bytes(32, "big"))
    return tuple(triples), draw, sample_sha.hexdigest(), beta


def _sample_collisions(
    triples: Sequence[Sequence[Sequence[int]]],
    scheme: Sequence[Any],
    *,
    early_exit: bool = False,
) -> int:
    collisions = 0
    for triple in triples:
        tags = {_tag(statistics, scheme) for statistics in triple}
        collisions += len(triple) - len(tags)
        if early_exit and collisions:
            return collisions
    return collisions


@functools.lru_cache(maxsize=None)
def production_sample_report(sample_count: int = PRODUCTION_SAMPLE_COUNT) -> dict[str, Any]:
    triples, draws, sample_sha, beta = _production_triples(sample_count)
    winner: tuple[Any, ...] | None = None
    minimum_bits: int | None = None
    for bits, scheme in tag_schemes(32):
        if _sample_collisions(triples, scheme, early_exit=True) == 0:
            minimum_bits = bits
            winner = scheme
            break
    if winner is None or minimum_bits is None:
        raise AssertionError("no natural tag found within the declared sample budget")

    curve = []
    if len(winner) == 4:
        left_name, _left_bits, right_name, _right_bits = winner
        for total_bits in range(2, minimum_bits + 1):
            candidates = []
            for left_bits in range(1, total_bits):
                scheme = (
                    left_name,
                    left_bits,
                    right_name,
                    total_bits - left_bits,
                )
                candidates.append((_sample_collisions(triples, scheme), scheme))
            collisions, scheme = min(candidates)
            curve.append(
                {
                    "total_bits": total_bits,
                    "allocation": (scheme[1], scheme[3]),
                    "collisions": collisions,
                }
            )

    return {
        "field": "secp256k1",
        "sample_method": "sha256('support-trace-root-selector:' || decimal_index)",
        "sample_count": sample_count,
        "draws": draws,
        "sample_sha256": sample_sha,
        "beta": beta,
        "classical_x": SECP256K1_GX,
        "minimum_tag_bits": minimum_bits,
        "winning_scheme": winner,
        "winning_collisions": _sample_collisions(triples, winner),
        "winning_collision_curve": curve,
        "exhaustive_production_certificate": False,
        "reversible_cost_known": False,
        "root_carrier_proved": False,
    }


def run_gate() -> dict[str, Any]:
    branch_cases = [
        exact_branch_case_report(prime) for prime in EXACT_BRANCH_PRIMES
    ]
    affine_cases = [affine_decoder_case_report(prime) for prime in AFFINE_PRIMES]
    production = production_sample_report()
    branch_budgets = [case["minimum_tag_bits"] for case in branch_cases]
    branch_budgets_grow = all(
        left <= right for left, right in zip(branch_budgets, branch_budgets[1:])
    ) and branch_budgets[-1] > branch_budgets[0]
    full_word_affine = all(
        case["full_word_tag_only"]
        and case["minimum_tag_bits"] == case["width"]
        and case["k_is_modular_inverse"]
        for case in affine_cases
    )
    sample_passed = (
        production["winning_collisions"] == 0
        and production["minimum_tag_bits"] > 2
        and not production["exhaustive_production_certificate"]
        and not production["root_carrier_proved"]
    )
    closed = branch_budgets_grow and full_word_affine and sample_passed

    payload: dict[str, Any] = {
        "schema": "support-trace-root-selector-v1",
        "scope": "NATURAL_LOW_BIT_TRACE_TAGS_AND_TAG_CONDITIONED_AFFINE_DECODERS_ONLY",
        "base_commit": BASE_COMMIT,
        "base_tree": BASE_TREE,
        "statistic_library": STATISTIC_NAMES,
        "exact_branch_cases": branch_cases,
        "affine_decoder_cases": affine_cases,
        "production_sample": production,
        "branch_identity_verdict": (
            "ADMIT_TRACE_BRANCH_TAG_SAMPLE_ONLY"
            if sample_passed
            else "HARD_NACK_TRACE_BRANCH_TAG_SAMPLE"
        ),
        "verdict": (
            "HARD_NACK_SUPPORT_TRACE_ROOT_SELECTOR_NATURAL_TAGS"
            if closed
            else "HOLD_SUPPORT_TRACE_ROOT_SELECTOR_NATURAL_TAGS"
        ),
        "arbitrary_factored_decoders_closed": False,
        "full_field_candidate": False,
        "next_grammar": "TRACE_CONDITIONED_COUPLED_SEED",
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
    parser.add_argument("--sample-count", type=int, default=PRODUCTION_SAMPLE_COUNT)
    args = parser.parse_args()
    report = run_gate() if args.sample_count == PRODUCTION_SAMPLE_COUNT else production_sample_report(args.sample_count)
    print(json.dumps(report, sort_keys=True, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
