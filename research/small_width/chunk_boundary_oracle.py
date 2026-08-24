#!/usr/bin/env python3
"""Exhaustively audit truncated chunk-boundary carry oracles.

Research motivation: Justin Drake proposed using smaller adders to expose
hidden Pareto steps before lifting mechanisms to 256 bits.  This probe tests a
specific mechanism in the promoted 6752417 ping-pong replay adder: preserving
the carry entering the top comparison window during measured boundary erasure.

The circuit currently approximates a chunk carry with ``sum_top < addend_top``.
When the lower slice sends a carry into the top window, the exact relation is
``sum_top < addend_top or (window_cin and sum_top == addend_top)``.
"""

from __future__ import annotations

import argparse
import json


def audit(chunk_width: int, top_width: int) -> dict[str, int | float]:
    if not 1 <= top_width <= chunk_width:
        raise ValueError("require 1 <= top_width <= chunk_width")

    mask = (1 << chunk_width) - 1
    top_mask = (1 << top_width) - 1
    shift = chunk_width - top_width
    total = 0
    no_cin_errors = 0
    with_cin_errors = 0
    entry_carry_cases = 0
    equality_cases = 0

    for addend in range(mask + 1):
        addend_top = addend >> shift
        for accumulator in range(mask + 1):
            for chunk_cin in (0, 1):
                full = addend + accumulator + chunk_cin
                exact = int(full > mask)
                result = full & mask
                result_top = (result >> shift) & top_mask

                if shift:
                    low_mask = (1 << shift) - 1
                    window_cin = int(
                        (addend & low_mask)
                        + (accumulator & low_mask)
                        + chunk_cin
                        > low_mask
                    )
                else:
                    window_cin = chunk_cin

                approximate = int(result_top < addend_top)
                repaired = int(
                    result_top < addend_top
                    or (window_cin and result_top == addend_top)
                )

                total += 1
                entry_carry_cases += window_cin
                equality_cases += int(window_cin and result_top == addend_top)
                no_cin_errors += int(approximate != exact)
                with_cin_errors += int(repaired != exact)

    return {
        "chunk_width": chunk_width,
        "top_width": top_width,
        "total_cases": total,
        "entry_carry_cases": entry_carry_cases,
        "equality_cases": equality_cases,
        "no_cin_errors": no_cin_errors,
        "with_cin_errors": with_cin_errors,
        "no_cin_error_rate": no_cin_errors / total,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-chunk-width", type=int, default=10)
    parser.add_argument("--min-top-width", type=int, default=1)
    args = parser.parse_args()

    if not 1 <= args.max_chunk_width <= 12:
        parser.error("max chunk width must be in 1..12 for exhaustive search")

    for chunk_width in range(args.min_top_width, args.max_chunk_width + 1):
        for top_width in range(args.min_top_width, chunk_width + 1):
            row = audit(chunk_width, top_width)
            if row["with_cin_errors"] != 0:
                raise AssertionError(f"with-cin oracle failed: {row}")
            print(json.dumps(row, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
