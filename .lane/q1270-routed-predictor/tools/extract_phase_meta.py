#!/usr/bin/env python3
"""Extract the exact Q1270 conditional-phase schedule from a zstd op trace."""

from __future__ import annotations

import hashlib
import pathlib
import subprocess
import sys


EXPECTED_COMPRESSED_SHA256 = "069ae8682265a831a69bb7861e210fc58e62b7e76422bc66d0ed2f3a81ad4173"
EXPECTED_RAW_SHA256 = "766a9b06009560333d3d2790001dfdda18e419123a9c3234732ee045373af36b"
EXPECTED_TRACED_OPS = 12_953_540
EXPECTED_RHMR = 1_947_720
EXPECTED_COUNTS = (3_267, 694, 694, 3)
FAMILIES = (
    ("point_add/pingpong_div.rs", 1585),
    ("point_add/pingpong_div.rs", 1854),
    ("point_add/pingpong_div.rs", 2031),
    ("point_add/trailmix_ludicrous/arith.rs", 1501),
)


def fail(message: str) -> None:
    raise SystemExit(f"extract-phase-meta: {message}")


def main() -> None:
    if len(sys.argv) != 3:
        fail("usage: extract_phase_meta.py OP_SITES.tsv.zst PHASE_META.tsv")
    source = pathlib.Path(sys.argv[1])
    output = pathlib.Path(sys.argv[2])
    compressed_digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if compressed_digest != EXPECTED_COMPRESSED_SHA256:
        fail(f"compressed SHA-256 {compressed_digest} != {EXPECTED_COMPRESSED_SHA256}")

    proc = subprocess.Popen(
        ["/opt/homebrew/bin/zstd", "-q", "-dc", str(source)],
        stdout=subprocess.PIPE,
    )
    assert proc.stdout is not None
    raw_hasher = hashlib.sha256()
    rows: list[tuple[int, int, int, int]] = []
    counts = [0] * len(FAMILIES)
    last_site_index = -1
    last_rhmr = -1
    line_count = 0
    try:
        for number, raw_line in enumerate(proc.stdout, 1):
            raw_hasher.update(raw_line)
            line_count += 1
            try:
                line = raw_line.decode("ascii")
            except UnicodeDecodeError as exc:
                fail(f"row {number} is not ASCII: {exc}")
            if not line.endswith("\n"):
                fail(f"row {number} is not LF-terminated")
            fields = line[:-1].split("\t")
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
                    if index <= last_site_index:
                        fail(f"phase family row {number} is not monotone")
                    last_site_index = index
                    counts[family] += 1
                    rows.append((index, ordinal, line_no, family))
                    break
    finally:
        proc.stdout.close()
    if proc.wait() != 0:
        fail("zstd decoder failed")

    raw_digest = raw_hasher.hexdigest()
    if raw_digest != EXPECTED_RAW_SHA256:
        fail(f"raw SHA-256 {raw_digest} != {EXPECTED_RAW_SHA256}")
    if line_count != EXPECTED_TRACED_OPS:
        fail(f"trace rows {line_count} != {EXPECTED_TRACED_OPS}")
    if last_rhmr + 1 != EXPECTED_RHMR:
        fail(f"R/Hmr count {last_rhmr + 1} != {EXPECTED_RHMR}")
    if tuple(counts) != EXPECTED_COUNTS:
        fail(f"family counts {tuple(counts)} != {EXPECTED_COUNTS}")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "".join(
            f"{index}\t{ordinal}\t{line}\t{family}\n"
            for index, ordinal, line, family in rows
        ),
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
