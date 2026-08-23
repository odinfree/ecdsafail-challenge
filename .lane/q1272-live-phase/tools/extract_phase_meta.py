#!/usr/bin/env python3
"""Extract the exact Q1272 conditional-phase schedule from an op-site trace."""

from __future__ import annotations

import hashlib
import pathlib
import sys


EXPECTED_TRACE_SHA256 = "f2f0f99d096027299460d9a82c16d3714c9684564d10f13f6dcbbac2b3e92833"
EXPECTED_TRACED_OPS = 12_904_547
EXPECTED_RHMR = 1_938_616
EXPECTED_COUNTS = (2_573, 694, 694, 3)
FAMILIES = (
    ("point_add/pingpong_div.rs", 1558),
    ("point_add/pingpong_div.rs", 1813),
    ("point_add/pingpong_div.rs", 1928),
    ("point_add/trailmix_ludicrous/arith.rs", 1501),
)


def fail(message: str) -> None:
    raise SystemExit(f"extract-phase-meta: {message}")


def main() -> None:
    if len(sys.argv) != 3:
        fail("usage: extract_phase_meta.py OP_SITES.tsv PHASE_META.tsv")
    source = pathlib.Path(sys.argv[1])
    output = pathlib.Path(sys.argv[2])
    raw = source.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_TRACE_SHA256:
        fail(f"trace SHA-256 {digest} != {EXPECTED_TRACE_SHA256}")
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        fail(f"trace is not ASCII: {exc}")
    if not text.endswith("\n"):
        fail("trace is not LF-terminated")

    rows: list[tuple[int, int, int, int]] = []
    counts = [0] * len(FAMILIES)
    last_index = -1
    last_rhmr = -1
    line_count = 0
    for number, line in enumerate(text.splitlines(), 1):
        line_count += 1
        fields = line.split("\t")
        if len(fields) != 6:
            fail(f"row {number} has {len(fields)} fields")
        index_s, file_s, line_s, context_s, kind_s, ordinal_s = fields
        if not (index_s.isdecimal() and line_s.isdecimal() and context_s.isdecimal()
                and kind_s.isdecimal()):
            fail(f"row {number} has malformed numeric fields")
        index = int(index_s)
        if index != number - 1:
            fail(f"row {number} index {index} is not contiguous")
        line_no = int(line_s)
        kind = int(kind_s)
        if ordinal_s == "-":
            ordinal = None
        elif ordinal_s.isdecimal():
            ordinal = int(ordinal_s)
            if ordinal != last_rhmr + 1:
                fail(f"row {number} R/Hmr ordinal is not contiguous")
            last_rhmr = ordinal
        else:
            fail(f"row {number} has malformed ordinal")
        if (kind in (11, 12)) != (ordinal is not None):
            fail(f"row {number} kind/ordinal mismatch")

        for family, (suffix, expected_line) in enumerate(FAMILIES):
            if file_s.endswith(suffix) and line_no == expected_line:
                if kind != 12 or ordinal is None:
                    fail(f"phase family row {number} is not Hmr")
                if index <= last_index:
                    fail(f"phase family row {number} is not monotone")
                last_index = index
                counts[family] += 1
                rows.append((index, ordinal, line_no, family))
                break

    if line_count != EXPECTED_TRACED_OPS:
        fail(f"trace rows {line_count} != {EXPECTED_TRACED_OPS}")
    if last_rhmr + 1 != EXPECTED_RHMR:
        fail(f"R/Hmr count {last_rhmr + 1} != {EXPECTED_RHMR}")
    if tuple(counts) != EXPECTED_COUNTS:
        fail(f"family counts {tuple(counts)} != {EXPECTED_COUNTS}")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "".join(f"{index}\t{ordinal}\t{line}\t{family}\n" for index, ordinal, line, family in rows),
        encoding="ascii",
        newline="\n",
    )
    out_sha = hashlib.sha256(output.read_bytes()).hexdigest()
    print(
        f"extract-phase-meta: PASS sites={len(rows)} rhmr={EXPECTED_RHMR} "
        f"counts={tuple(counts)} meta_sha256={out_sha}"
    )


if __name__ == "__main__":
    main()
