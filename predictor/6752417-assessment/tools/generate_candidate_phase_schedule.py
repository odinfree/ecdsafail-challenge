#!/usr/bin/env python3
"""Generate the exact Q1266 candidate conditional-phase schedule."""

from __future__ import annotations

import hashlib
import pathlib
import sys


EXPECTED_TRACE_SHA256 = "c5f2f732577914bee1ad52a446af5edd0c14fd3962c7c29fdf1273d888e9ae9c"
EXPECTED_TRACED_OPS = 12_596_343
EXPECTED_TOTAL_OPS = 12_596_439
EXPECTED_RHMR = 1_919_152
EXPECTED_COUNTS = (3_016, 694, 692, 3)
EXPECTED_OPS_SHA256 = "5f39b385c693a3f9179d7ba6d674c13676c0bb489bf2b07e208048b0e6ed561c"
FAMILIES = (
    ("point_add/pingpong_div.rs", 2165),
    ("point_add/pingpong_div.rs", 2435),
    ("point_add/pingpong_div.rs", 2774),
    ("point_add/trailmix_ludicrous/arith.rs", 1491),
)


def fail(message: str) -> None:
    raise SystemExit(f"generate-candidate-phase-schedule: {message}")


def chunks(values: list[int], width: int) -> list[list[int]]:
    return [values[i : i + width] for i in range(0, len(values), width)]


def main() -> None:
    if len(sys.argv) != 4:
        fail("usage: generate_candidate_phase_schedule.py TRACE HEADER LEDGER")
    trace = pathlib.Path(sys.argv[1])
    header = pathlib.Path(sys.argv[2])
    ledger = pathlib.Path(sys.argv[3])
    raw = trace.read_bytes()
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
    last_rhmr = -1
    line_count = 0
    for number, line in enumerate(text.splitlines(), 1):
        line_count += 1
        fields = line.split("\t")
        if len(fields) != 6:
            fail(f"row {number} has {len(fields)} fields")
        index_s, file_s, line_s, context_s, kind_s, ordinal_s = fields
        if not (
            index_s.isdecimal()
            and line_s.isdecimal()
            and context_s.isdecimal()
            and kind_s.isdecimal()
        ):
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
                counts[family] += 1
                rows.append((index, ordinal, line_no, family))
                break

    if line_count != EXPECTED_TRACED_OPS:
        fail(f"trace rows {line_count} != {EXPECTED_TRACED_OPS}")
    if last_rhmr + 1 != EXPECTED_RHMR:
        fail(f"R/Hmr count {last_rhmr + 1} != {EXPECTED_RHMR}")
    if tuple(counts) != EXPECTED_COUNTS:
        fail(f"family counts {tuple(counts)} != {EXPECTED_COUNTS}")
    if any(
        rows[index][0] >= rows[index + 1][0]
        or rows[index][1] >= rows[index + 1][1]
        for index in range(len(rows) - 1)
    ):
        fail("selected phase rows are not strictly monotone")

    meta = "".join(
        f"{index}\t{ordinal}\t{line_no}\t{family}\n"
        for index, ordinal, line_no, family in rows
    ).encode("ascii")
    meta_sha = hashlib.sha256(meta).hexdigest()
    ordinals = [row[1] for row in rows]
    families = [row[3] for row in rows]
    out = [
        "#pragma once\n\n",
        "// Generated from the exact Q1266 odd-passenger source/stream trace.\n",
        "// source: 57ee207abe9f648dbc443bfb329e051707327d46\n",
        f"// ops.bin sha256: {EXPECTED_OPS_SHA256}\n",
        f"// phase-meta sha256: {meta_sha}\n",
        f"#define PP_PHASE_SITE_COUNT {len(rows)}\n",
        f"#define PP_PHASE_RHMR_COUNT {EXPECTED_RHMR}\n",
        f'#define PP_PHASE_META_SHA256 "{meta_sha}"\n',
        "static const u32 PP_PHASE_ORDINALS[PP_PHASE_SITE_COUNT] = {\n",
    ]
    for group in chunks(ordinals, 12):
        out.append("    " + ", ".join(f"{value}u" for value in group) + ",\n")
    out.append("};\n")
    out.append("static const u8 PP_PHASE_FAMILIES[PP_PHASE_SITE_COUNT] = {\n")
    for group in chunks(families, 32):
        out.append("    " + ", ".join(str(value) for value in group) + ",\n")
    out.append("};\n")

    header.parent.mkdir(parents=True, exist_ok=True)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    header.write_text("".join(out), encoding="ascii", newline="\n")
    ledger.write_bytes(meta)
    print(
        "generate-candidate-phase-schedule: PASS "
        f"ops={EXPECTED_TOTAL_OPS} sites={len(rows)} rhmr={EXPECTED_RHMR} "
        f"counts={tuple(counts)} trace_sha256={digest} meta_sha256={meta_sha}"
    )


if __name__ == "__main__":
    main()
