#!/usr/bin/env python3
"""Reachability gate for the ping-pong division sign tape.

This module mirrors the signed Euclid value walk at the integer level and
measures only information/support bounds.  It does not claim that a sampled
support is complete and it does not assign a reversible decoder cost.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

FIELD_MODULUS = (1 << 256) - (1 << 32) - 977
PRODUCTION_ROUNDS = 696
DEFAULT_SEED = b"pingpong-sign-tape-support-v1"
DEFAULT_OUTPUT = Path(__file__).resolve().parents[4] / ".autoresearch/measurements/pingpong-sign-tape-v1/report.json"


def fused_round_zero(modulus: int, value: int) -> tuple[int, int]:
    """Return the first sign and the fused odd signed representative."""
    if modulus <= 2 or modulus % 4 != 3:
        raise ValueError("the fused identity requires an odd modulus congruent to 3 mod 4")
    if not 0 <= value < modulus:
        raise ValueError("value must be in the canonical field range")
    a0 = value & 1
    a1 = (value >> 1) & 1
    target = value // 2 - modulus + a1 * modulus + a0 * ((modulus + 1) // 2)
    if target & 1 == 0:
        raise AssertionError("fused round zero must produce an odd representative")
    return a0, target


def signed_round(source: int, target: int) -> tuple[int, int]:
    """One exact alternating signed-Euclid update on odd integers."""
    if source & 1 == 0 or target & 1 == 0:
        raise ValueError("signed round requires two odd operands")
    sign = ((target >> 1) & 1) ^ ((source >> 1) & 1)
    numerator = target - source if sign else target + source
    if numerator % 4 != 2:
        raise AssertionError("branch must leave an odd quotient")
    return sign, numerator // 2


def signed_round_inverse(source: int, output: int, sign: int) -> int:
    if sign not in (0, 1):
        raise ValueError("sign must be a bit")
    return 2 * output + source if sign else 2 * output - source


def wrap_signed(value: int, width: int) -> int:
    if width < 2:
        raise ValueError("signed width must be at least two")
    mask = (1 << width) - 1
    value &= mask
    return value - (1 << width) if value >> (width - 1) else value


def walk_trace(
    modulus: int,
    value: int,
    rounds: int,
    widths: Sequence[int] | None = None,
) -> tuple[list[int], tuple[int, int]]:
    """Run the recurrence; optional widths mirror the circuit's truncation."""
    if rounds < 1:
        raise ValueError("rounds must be positive")
    if widths is not None and len(widths) < rounds:
        raise ValueError("width schedule is shorter than the requested walk")
    first, v = fused_round_zero(modulus, value)
    u = modulus
    trace = [first]
    for round_index in range(1, rounds):
        if widths is not None:
            width = widths[round_index]
            u = wrap_signed(u, width)
            v = wrap_signed(v, width)
        if round_index % 2 == 0:
            sign, v = signed_round(u, v)
            if widths is not None:
                v = wrap_signed(v, widths[round_index])
        else:
            sign, u = signed_round(v, u)
            if widths is not None:
                u = wrap_signed(u, widths[round_index])
        trace.append(sign)
    return trace, (u, v)


def bits_to_string(bits: Sequence[int]) -> str:
    return "".join(str(bit) for bit in bits)


def fixed_block_support(traces: Sequence[Sequence[int]], start: int, width: int) -> dict[str, int | bool]:
    if not traces:
        raise ValueError("at least one trace is required")
    if width < 1 or start < 0:
        raise ValueError("invalid block")
    if any(start + width > len(trace) for trace in traces):
        raise ValueError("block exceeds a trace")
    support = {tuple(trace[start : start + width]) for trace in traces}
    rank_bits = (len(support) - 1).bit_length()
    return {
        "start": start,
        "block_width": width,
        "samples": len(traces),
        "support": len(support),
        "rank_bits": rank_bits,
        "raw_minus_rank": width - rank_bits,
        "full_support_observed": len(support) == 1 << width,
    }


def partition_bound(traces: Sequence[Sequence[int]], block_width: int) -> dict[str, Any]:
    if not traces:
        raise ValueError("at least one trace is required")
    raw_bits = len(traces[0])
    if any(len(trace) != raw_bits for trace in traces):
        raise ValueError("traces must have equal lengths")
    blocks = [
        fixed_block_support(traces, start, min(block_width, raw_bits - start))
        for start in range(0, raw_bits, block_width)
    ]
    rank_bits = sum(int(row["rank_bits"]) for row in blocks)
    return {
        "block_width": block_width,
        "raw_bits": raw_bits,
        "rank_bits": rank_bits,
        "best_possible_saving": raw_bits - rank_bits,
        "blocks": blocks,
    }


_HEADER_RE = re.compile(r"^PINGPONG_TAPE_V1 rounds=(\d+) lanes=(\d+)$")
_ROW_RE = re.compile(r"^lane=(\d+) denominator=(0x[0-9a-fA-F]+) tape=([01]+)$")


def parse_gate_dump(text: str) -> dict[str, Any]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines or (header := _HEADER_RE.fullmatch(lines[0])) is None:
        raise ValueError("missing ping-pong tape dump header")
    rounds, lanes = map(int, header.groups())
    rows = []
    for line in lines[1:]:
        match = _ROW_RE.fullmatch(line)
        if match is None:
            raise ValueError(f"malformed tape row: {line}")
        lane, denominator, raw_tape = match.groups()
        if len(raw_tape) != rounds:
            raise ValueError("tape length does not match header")
        rows.append({
            "lane": int(lane),
            "denominator": int(denominator, 16),
            "tape": [int(bit) for bit in raw_tape],
        })
    if len(rows) != lanes or [row["lane"] for row in rows] != list(range(lanes)):
        raise ValueError("dump does not contain every lane exactly once in order")
    return {"rounds": rounds, "lanes": lanes, "rows": rows}


def deterministic_values(count: int, modulus: int, seed: bytes = DEFAULT_SEED) -> Iterable[int]:
    for index in range(count):
        digest = hashlib.sha256(seed + index.to_bytes(8, "little")).digest()
        yield int.from_bytes(digest, "little") % (modulus - 1) + 1


def _new_supports(rounds: int, widths: Sequence[int]) -> dict[int, list[set[int]]]:
    return {
        width: [set() for _ in range(0, rounds, width)]
        for width in widths
    }


def _record_trace(supports: dict[int, list[set[int]]], trace: Sequence[int]) -> None:
    for width, blocks in supports.items():
        for block_index, start in enumerate(range(0, len(trace), width)):
            word = 0
            for offset, bit in enumerate(trace[start : start + width]):
                word |= bit << offset
            blocks[block_index].add(word)


def _summarize_supports(supports: dict[int, list[set[int]]], rounds: int) -> list[dict[str, Any]]:
    partitions = []
    for width, blocks in sorted(supports.items()):
        rows = []
        rank = 0
        for block_index, support in enumerate(blocks):
            start = block_index * width
            actual_width = min(width, rounds - start)
            bits = (len(support) - 1).bit_length()
            rank += bits
            rows.append({
                "start": start,
                "width": actual_width,
                "support": len(support),
                "rank_bits": bits,
                "raw_minus_rank": actual_width - bits,
                "full_support_observed": len(support) == 1 << actual_width,
            })
        partitions.append({
            "block_width": width,
            "raw_bits": rounds,
            "rank_bits": rank,
            "best_possible_saving": rounds - rank,
            "blocks": rows,
        })
    return partitions


def analyze_domain(
    modulus: int,
    values: Iterable[int],
    samples: int,
    rounds: int,
    block_widths: Sequence[int],
) -> dict[str, Any]:
    supports = _new_supports(rounds, block_widths)
    suffix_widths = (4, 8, 12, 16, 20, 24, 28, 32)
    suffix_supports = {width: set() for width in suffix_widths if width <= rounds}
    whole_hashes: set[bytes] = set()
    terminal_counts: dict[str, int] = {}
    sample_hash = hashlib.sha256()
    seen = 0
    for value in values:
        if seen >= samples:
            break
        trace, terminal = walk_trace(modulus, value, rounds)
        _record_trace(supports, trace)
        packed = int(bits_to_string(reversed(trace)), 2).to_bytes((rounds + 7) // 8, "little")
        whole_hashes.add(hashlib.sha256(packed).digest())
        sample_hash.update(value.to_bytes((modulus.bit_length() + 7) // 8, "little"))
        for width, support in suffix_supports.items():
            word = sum(bit << offset for offset, bit in enumerate(trace[-width:]))
            support.add(word)
        key = f"{terminal[0]},{terminal[1]}"
        terminal_counts[key] = terminal_counts.get(key, 0) + 1
        seen += 1
    return {
        "modulus": modulus,
        "field_width": modulus.bit_length(),
        "rounds": rounds,
        "samples": seen,
        "sample_sha256": sample_hash.hexdigest(),
        "unique_whole_traces": len(whole_hashes),
        "whole_trace_rank_lower_bound": (len(whole_hashes) - 1).bit_length(),
        "terminal_counts": terminal_counts,
        "partitions": _summarize_supports(supports, rounds),
        "suffixes": [
            {
                "width": width,
                "support": len(support),
                "rank_bits": (len(support) - 1).bit_length(),
                "raw_minus_rank": width - (len(support) - 1).bit_length(),
            }
            for width, support in suffix_supports.items()
        ],
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    started = time.monotonic()
    toy_cases = []
    for modulus in (31, 61, 127, 251, 509, 1021, 4093):
        rounds = max(12, 3 * modulus.bit_length())
        toy_cases.append(analyze_domain(
            modulus,
            range(1, modulus),
            modulus - 1,
            rounds,
            args.block_widths,
        ))
    production = analyze_domain(
        FIELD_MODULUS,
        deterministic_values(args.samples, FIELD_MODULUS, args.seed.encode()),
        args.samples,
        PRODUCTION_ROUNDS,
        args.block_widths,
    )
    return {
        "schema": "pingpong-sign-tape-support-v1",
        "exact_toy_cases": toy_cases,
        "production_sample": production,
        "production_exhaustive": False,
        "codec_constructed": False,
        "reversible_cost_known": False,
        "elapsed_seconds": time.monotonic() - started,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=100_000)
    parser.add_argument("--seed", default=DEFAULT_SEED.decode())
    parser.add_argument("--block-widths", type=int, nargs="+", default=[4, 8, 12, 16])
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = run(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "elapsed_seconds": report["elapsed_seconds"],
        "production_partitions": [
            {key: row[key] for key in ("block_width", "rank_bits", "best_possible_saving")}
            for row in report["production_sample"]["partitions"]
        ],
        "production_suffixes": report["production_sample"]["suffixes"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
