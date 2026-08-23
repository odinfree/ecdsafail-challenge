#!/usr/bin/env python3
"""Generate the exact target0/sign-alias R/Hmr phase schedule header."""

from __future__ import annotations

import hashlib
import pathlib
import sys


EXPECTED_META_SHA256 = "665e64bb22d87ba629a133f7c67813c284a7fca47d1b6212914c83abe0f5fa1e"
EXPECTED_OPS = 12_919_161
EXPECTED_RHMR = 1_941_386
EXPECTED_COUNTS = (2_579, 694, 694, 3)
SOURCE_LINES = (1577, 1846, 2006, 1501)


def fail(message: str) -> None:
    raise SystemExit(f"generate-phase-schedule: {message}")


def chunks(values: list[int], width: int) -> list[list[int]]:
    return [values[i : i + width] for i in range(0, len(values), width)]


def main() -> None:
    if len(sys.argv) != 4:
        fail("usage: generate_phase_schedule.py PHASE_META.tsv HEADER LEDGER")
    source, header, ledger = map(pathlib.Path, sys.argv[1:])
    raw = source.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_META_SHA256:
        fail(f"meta SHA-256 {digest} != {EXPECTED_META_SHA256}")
    if not raw.endswith(b"\n"):
        fail("meta is not LF-terminated")

    rows: list[tuple[int, int, int, int]] = []
    for number, line in enumerate(raw.decode("ascii").splitlines(), 1):
        fields = line.split("\t")
        if len(fields) != 4 or any(not field.isdecimal() for field in fields):
            fail(f"malformed row {number}")
        op_index, ordinal, source_line, family = map(int, fields)
        if family >= 4 or source_line != SOURCE_LINES[family]:
            fail(f"source-family mismatch at row {number}")
        if op_index >= EXPECTED_OPS or ordinal >= EXPECTED_RHMR:
            fail(f"out-of-range row {number}")
        if rows and (op_index <= rows[-1][0] or ordinal <= rows[-1][1]):
            fail(f"non-monotonic row {number}")
        rows.append((op_index, ordinal, source_line, family))
    counts = tuple(sum(row[3] == family for row in rows) for family in range(4))
    if counts != EXPECTED_COUNTS:
        fail(f"family counts {counts} != {EXPECTED_COUNTS}")

    out = [
        "#pragma once\n\n",
        "// Generated from the exact Q1271 target0/sign-alias stream.\n",
        "// source: a22090374a957d29a3331d6c876ad12ff45fea31\n",
        "// ops.bin sha256: 590cb55deb75af4ab9356fce97308b4ca4dc10ac031d4fd6d16464e8515972fa\n",
        f"// phase-meta sha256: {EXPECTED_META_SHA256}\n",
        f"#define PP_PHASE_SITE_COUNT {len(rows)}\n",
        f"#define PP_PHASE_RHMR_COUNT {EXPECTED_RHMR}\n",
        f'#define PP_PHASE_META_SHA256 "{EXPECTED_META_SHA256}"\n',
        "static const u32 PP_PHASE_ORDINALS[PP_PHASE_SITE_COUNT] = {\n",
    ]
    for group in chunks([row[1] for row in rows], 12):
        out.append("    " + ", ".join(f"{value}u" for value in group) + ",\n")
    out.append("};\n")
    out.append("static const u8 PP_PHASE_FAMILIES[PP_PHASE_SITE_COUNT] = {\n")
    for group in chunks([row[3] for row in rows], 32):
        out.append("    " + ", ".join(map(str, group)) + ",\n")
    out.append("};\n")
    header.parent.mkdir(parents=True, exist_ok=True)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    header.write_text("".join(out), encoding="ascii", newline="\n")
    ledger.write_bytes(raw)
    print(
        f"generate-phase-schedule: PASS sites={len(rows)} rhmr={EXPECTED_RHMR} "
        f"counts={counts} meta_sha256={digest}"
    )


if __name__ == "__main__":
    main()
