#!/usr/bin/env python3
"""Seal the exact live-source Q1272 R/Hmr phase schedule."""

from __future__ import annotations

import hashlib
import pathlib
import sys


EXPECTED_META_SHA256 = "59c177b5b43bf27eba1ee6758a7c1cea07f0eef5aa9b0c2a27dfe05301c6657d"
EXPECTED_OPS = 12_904_643
EXPECTED_RHMR = 1_938_616
EXPECTED_COUNTS = (2_573, 694, 694, 3)
SOURCE_LINES = (1558, 1813, 1928, 1501)


def fail(message: str) -> None:
    raise SystemExit(f"generate-phase-schedule: {message}")


def chunks(values: list[int], width: int) -> list[list[int]]:
    return [values[i : i + width] for i in range(0, len(values), width)]


def main() -> None:
    if len(sys.argv) != 4:
        fail("usage: generate_phase_schedule.py PHASE_META_TSV HEADER LEDGER")
    source = pathlib.Path(sys.argv[1])
    header = pathlib.Path(sys.argv[2])
    ledger = pathlib.Path(sys.argv[3])
    raw = source.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_META_SHA256:
        fail(f"meta SHA-256 {digest} != {EXPECTED_META_SHA256}")
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        fail(f"meta is not ASCII: {exc}")
    if not text.endswith("\n"):
        fail("meta is not LF-terminated")

    rows: list[tuple[int, int, int, int]] = []
    for number, line in enumerate(text.splitlines(), 1):
        fields = line.split("\t")
        if len(fields) != 4 or any(not field.isdecimal() for field in fields):
            fail(f"malformed row {number}")
        op_index, ordinal, source_line, family = map(int, fields)
        if family >= len(SOURCE_LINES) or source_line != SOURCE_LINES[family]:
            fail(f"source-family mismatch at row {number}")
        if op_index >= EXPECTED_OPS or ordinal >= EXPECTED_RHMR:
            fail(f"out-of-range row {number}")
        if rows and (op_index <= rows[-1][0] or ordinal <= rows[-1][1]):
            fail(f"non-monotonic row {number}")
        rows.append((op_index, ordinal, source_line, family))

    counts = tuple(sum(row[3] == family for row in rows) for family in range(4))
    if counts != EXPECTED_COUNTS:
        fail(f"family counts {counts} != {EXPECTED_COUNTS}")

    ordinals = [row[1] for row in rows]
    families = [row[3] for row in rows]
    out = [
        "#pragma once\n\n",
        "// Generated from the exact live-source Q1272 source/stream trace.\n",
        "// source: 73422709ed70ba9725b3cb592770bcf197df4cdb\n",
        "// ops.bin sha256: ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1\n",
        f"// phase-meta sha256: {EXPECTED_META_SHA256}\n",
        f"#define PP_PHASE_SITE_COUNT {len(rows)}\n",
        f"#define PP_PHASE_RHMR_COUNT {EXPECTED_RHMR}\n",
        f'#define PP_PHASE_META_SHA256 "{EXPECTED_META_SHA256}"\n',
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
    ledger.write_bytes(raw)
    print(
        "generate-phase-schedule: PASS "
        f"sites={len(rows)} rhmr={EXPECTED_RHMR} counts={counts} meta_sha256={digest}"
    )


if __name__ == "__main__":
    main()
