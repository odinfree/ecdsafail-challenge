#!/usr/bin/env python3
"""Analyze the frozen X010 numerator-residual characterization log."""

from __future__ import annotations

import collections
import hashlib
import itertools
import json
import math
import pathlib
import sys
from typing import Callable, Iterable


P = (1 << 256) - (1 << 32) - 977
INV2 = (P + 1) // 2
EXPECTED_ROWS = 4096
EXPECTED_BATCHES = 64
EXPECTED_RECORDS_SHA256 = "7ce27cc97c07d8303c5c0f1f5b86c91c26377a0349225a85425b67a3b62b90b9"
ROW_PREFIX = "TEDDY_NUMERATOR_RESIDUAL_CHARACTERIZE_ROW "
BATCH_PREFIX = "TEDDY_NUMERATOR_RESIDUAL_CHARACTERIZE_BATCH "
PASS_PREFIX = "TEDDY_NUMERATOR_RESIDUAL_CHARACTERIZE PASS "

HEX_FIELDS = (
    "d",
    "input_c",
    "input_n",
    "c1",
    "n1",
    "c2_candidate",
    "n2_candidate",
    "c2_raw",
    "n2_raw",
    "c3_raw",
    "n3_raw",
    "delta_field",
    "delta_wrap",
)
INT_FIELDS = ("denominator_index", "seed_index", "sign1", "sign2")


def fail(message: str) -> None:
    raise SystemExit(f"analyze-teddy-numerator-residual: {message}")


def parse_fields(line: str, prefix: str) -> dict[str, str]:
    if not line.startswith(prefix):
        fail(f"line does not start with {prefix!r}")
    fields: dict[str, str] = {}
    for token in line[len(prefix) :].split():
        if "=" not in token:
            fail(f"malformed token {token!r}")
        key, value = token.split("=", 1)
        if key in fields:
            fail(f"duplicate field {key!r}")
        fields[key] = value
    return fields


def parse_rows(lines: Iterable[str]) -> list[dict[str, int | str]]:
    rows: list[dict[str, int | str]] = []
    for line in lines:
        if not line.startswith(ROW_PREFIX):
            continue
        raw = parse_fields(line, ROW_PREFIX)
        row: dict[str, int | str] = dict(raw)
        for field in HEX_FIELDS:
            if len(raw[field]) != 64:
                fail(f"{field} is not a 64-digit word")
            row[field] = int(raw[field], 16)
        for field in INT_FIELDS:
            row[field] = int(raw[field])
        rows.append(row)
    return rows


def hex256(value: int) -> str:
    return f"{value:064x}"


def table_sha256(counter: collections.Counter[int]) -> str:
    blob = "".join(
        f"{hex256(value)}\t{count}\n" for value, count in sorted(counter.items())
    ).encode("ascii")
    return hashlib.sha256(blob).hexdigest()


def residual_stats(values: list[int]) -> dict[str, object]:
    counter = collections.Counter(values)
    support = 0
    varying = 0
    first = values[0]
    for value in values:
        support |= value
        varying |= value ^ first
    entropy = -sum(
        (count / len(values)) * math.log2(count / len(values))
        for count in counter.values()
    )
    multiplicity_histogram = collections.Counter(counter.values())
    return {
        "distinct": len(counter),
        "zero_rows": counter[0],
        "entropy_bits": round(entropy, 12),
        "information_lower_bound_bits": (len(counter) - 1).bit_length(),
        "support_mask": hex256(support),
        "varying_mask": hex256(varying),
        "highest_active_bit": support.bit_length() - 1,
        "highest_varying_bit": varying.bit_length() - 1,
        "naive_fixed_width_bits": max(value.bit_length() for value in values),
        "multiplicity_histogram": {
            str(count): distinct_values
            for count, distinct_values in sorted(multiplicity_histogram.items())
        },
        "multiplicity_table_sha256": table_sha256(counter),
    }


Key = tuple[str, ...]


def fiber_stats(
    rows: list[dict[str, int | str]], key: Key
) -> dict[str, int]:
    fibers: dict[tuple[object, ...], list[tuple[int, int]]] = collections.defaultdict(list)
    for row in rows:
        signature = tuple(row[field] for field in key)
        fibers[signature].append((int(row["delta_field"]), int(row["delta_wrap"])))
    residual_counts = [len(set(values)) for values in fibers.values()]
    fiber_sizes = [len(values) for values in fibers.values()]
    return {
        "unique_keys": len(fibers),
        "largest_fiber": max(fiber_sizes),
        "conflicting_fibers": sum(count > 1 for count in residual_counts),
        "max_residual_pairs_per_fiber": max(residual_counts),
    }


def affine_consistency(
    rows: list[dict[str, int | str]], fields: Key
) -> dict[str, int | bool]:
    """Check whether one affine GF(2) map can produce the 256-bit residual."""

    basis: dict[int, tuple[int, int]] = {}
    for row_index, row in enumerate(rows):
        vector = 1
        offset = 1
        for field in fields:
            value = int(row[field])
            width = 1 if field in ("sign1", "sign2") else 256
            vector |= value << offset
            offset += width
        output = int(row["delta_field"])
        while vector:
            pivot = vector.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = (vector, output)
                break
            basis_vector, basis_output = basis[pivot]
            vector ^= basis_vector
            output ^= basis_output
        if vector == 0 and output != 0:
            return {
                "compatible": False,
                "rank": len(basis),
                "first_inconsistent_row": row_index,
            }
    return {
        "compatible": True,
        "rank": len(basis),
        "first_inconsistent_row": -1,
    }


def signed_half_xor_difference(row: dict[str, int | str]) -> int:
    if int(row["sign1"]) == 0:
        return 0
    direction = 1 if int(row["sign2"]) == 0 else -1
    c1 = int(row["c1"])
    normalized = c1 ^ P
    return (direction * (c1 - normalized) * INV2) % P


def group_rows(
    rows: list[dict[str, int | str]], predicate: Callable[[dict[str, int | str]], bool]
) -> list[dict[str, int | str]]:
    return [row for row in rows if predicate(row)]


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: analyze_teddy_numerator_residual.py STAGE_A_LOG")
    path = pathlib.Path(sys.argv[1])
    blob = path.read_bytes()
    digest = hashlib.sha256(blob).hexdigest()
    text = blob.decode("ascii")
    lines = text.splitlines()
    record_lines = [
        line
        for line in lines
        if line.startswith("TEDDY_NUMERATOR_RESIDUAL_CHARACTERIZE_")
        or line.startswith(PASS_PREFIX)
    ]
    records_blob = ("\n".join(record_lines) + "\n").encode("ascii")
    records_digest = hashlib.sha256(records_blob).hexdigest()
    if records_digest != EXPECTED_RECORDS_SHA256:
        fail(
            f"normalized record SHA-256 {records_digest} "
            f"!= frozen {EXPECTED_RECORDS_SHA256}"
        )
    rows = parse_rows(lines)
    if len(rows) != EXPECTED_ROWS:
        fail(f"row count {len(rows)} != {EXPECTED_ROWS}")
    if sum(line.startswith(BATCH_PREFIX) for line in lines) != EXPECTED_BATCHES:
        fail("batch count changed")
    if sum(line.startswith(PASS_PREFIX) for line in lines) != 1:
        fail("terminal PASS count changed")

    for row_index, row in enumerate(rows):
        denominator_index, seed_index = divmod(row_index, 64)
        if int(row["denominator_index"]) != denominator_index:
            fail(f"denominator-major order changed at row {row_index}")
        if int(row["seed_index"]) != seed_index:
            fail(f"seed order changed at row {row_index}")
        if row["seed_class"] != ("production" if seed_index < 32 else "stress"):
            fail(f"seed class changed at row {row_index}")
        if int(row["c2_candidate"]) != int(row["c2_raw"]):
            fail(f"coefficient mismatch at row {row_index}")
        raw_n = int(row["n2_raw"])
        candidate_n = int(row["n2_candidate"])
        if int(row["delta_wrap"]) != (raw_n - candidate_n) % (1 << 256):
            fail(f"wrapping residual mismatch at row {row_index}")
        if int(row["delta_field"]) != (raw_n - candidate_n) % P:
            fail(f"field residual mismatch at row {row_index}")

    field_values = [int(row["delta_field"]) for row in rows]
    wrap_values = [int(row["delta_wrap"]) for row in rows]
    classes = {
        name: group_rows(rows, lambda row, name=name: row["seed_class"] == name)
        for name in ("production", "stress")
    }

    frozen_keys: list[Key] = [
        ("d",),
        ("c1",),
        ("n1",),
        ("d", "c1"),
        ("d", "n1"),
        ("c1", "n1"),
        ("d", "c1", "n1"),
        ("c2_candidate",),
        ("n2_candidate",),
        ("d", "c2_candidate"),
        ("d", "n2_candidate"),
        ("c2_candidate", "n2_candidate"),
        ("d", "c2_candidate", "n2_candidate"),
        ("d", "c2_raw", "n2_raw"),
        ("d", "c3_raw", "n3_raw"),
    ]
    diagnostic_keys: list[Key] = [
        ("sign1",),
        ("sign1", "sign2"),
        ("sign1", "c1"),
        ("sign1", "sign2", "c1"),
        ("sign1", "sign2", "c1", "n1"),
    ]

    formula_values = [signed_half_xor_difference(row) for row in rows]
    formula_errors = [
        (actual - predicted) % P
        for actual, predicted in zip(field_values, formula_values, strict=True)
    ]
    formula_error_counter = collections.Counter(formula_errors)
    signed_formula_errors = {
        str(value if value <= P // 2 else value - P): count
        for value, count in sorted(formula_error_counter.items())
    }

    zero_if_sign1_zero = all(
        (value == 0) == (int(row["sign1"]) == 0)
        for row, value in zip(rows, field_values, strict=True)
    )

    summary: dict[str, object] = {
        "schema": "teddy-x010-residual-analysis-v1",
        "normalized_records_sha256": records_digest,
        "rows": len(rows),
        "batches": EXPECTED_BATCHES,
        "field_residual": residual_stats(field_values),
        "wrapping_residual": residual_stats(wrap_values),
        "field_equals_wrap_rows": sum(
            field == wrap for field, wrap in zip(field_values, wrap_values, strict=True)
        ),
        "field_differs_wrap_rows": sum(
            field != wrap for field, wrap in zip(field_values, wrap_values, strict=True)
        ),
        "class_stats": {
            name: residual_stats([int(row["delta_field"]) for row in class_rows])
            for name, class_rows in classes.items()
        },
        "sign_stats": {
            f"sign1={sign1},sign2={sign2}": residual_stats(
                [
                    int(row["delta_field"])
                    for row in rows
                    if int(row["sign1"]) == sign1 and int(row["sign2"]) == sign2
                ]
            )
            for sign1, sign2 in itertools.product((0, 1), repeat=2)
        },
        "frozen_key_fibers": {
            "+".join(key): fiber_stats(rows, key) for key in frozen_keys
        },
        "diagnostic_key_fibers": {
            "+".join(key): fiber_stats(rows, key) for key in diagnostic_keys
        },
        "formula_checks": {
            "constant": len(set(field_values)) == 1,
            "zero_exactly_iff_sign1_zero": zero_if_sign1_zero,
            "sign1_conditioned_constant": len(
                {
                    value
                    for row, value in zip(rows, field_values, strict=True)
                    if int(row["sign1"]) == 1
                }
            )
            == 1,
            "affine_xor": {
                "+".join(fields): affine_consistency(rows, fields)
                for fields in (
                    ("sign1",),
                    ("sign1", "sign2"),
                    ("c1",),
                    ("sign1", "c1"),
                    ("sign1", "sign2", "c1"),
                )
            },
            "signed_half_raw_minus_normalized_matches": sum(
                actual == predicted
                for actual, predicted in zip(field_values, formula_values, strict=True)
            ),
            "signed_half_raw_minus_normalized_mismatches": sum(
                actual != predicted
                for actual, predicted in zip(field_values, formula_values, strict=True)
            ),
            "signed_half_correction_values": signed_formula_errors,
            "signed_half_correction_table_sha256": table_sha256(formula_error_counter),
        },
    }

    canonical = json.dumps(summary, sort_keys=True, separators=(",", ":")).encode("ascii")
    wrapper = {
        "canonical_payload_sha256": hashlib.sha256(canonical).hexdigest(),
        "input_log_sha256": digest,
        "analysis": summary,
    }
    print(json.dumps(wrapper, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
