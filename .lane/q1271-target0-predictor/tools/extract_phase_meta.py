#!/usr/bin/env python3
"""Extract the target-bound conditional-phase schedule from ops plus trace."""

from __future__ import annotations

import collections
import hashlib
import pathlib
import struct
import subprocess
import sys


EXPECTED_OPS_SHA256 = "590cb55deb75af4ab9356fce97308b4ca4dc10ac031d4fd6d16464e8515972fa"
EXPECTED_TRACE_SHA256 = "56e084c152701707310c6822f7b914652a5d17d2352efd2255fd513492a0b4ce"
EXPECTED_OPS = 12_919_161
EXPECTED_TRACED_OPS = 12_919_065
EXPECTED_RHMR = 1_941_386
EXPECTED_COUNTS = (2_579, 694, 694, 3)
FAMILIES = {
    ("src/bin/../point_add/pingpong_div.rs", 1577): 0,
    ("src/bin/../point_add/pingpong_div.rs", 1846): 1,
    ("src/bin/../point_add/pingpong_div.rs", 2006): 2,
    ("src/bin/../point_add/trailmix_ludicrous/arith.rs", 1501): 3,
}


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"extract-phase-meta: {message}")


def main() -> None:
    if len(sys.argv) != 4:
        fail("usage: extract_phase_meta.py OPS.bin OP_SITES.tsv PHASE_META.tsv")
    ops, trace, output = map(pathlib.Path, sys.argv[1:])
    if sha256(ops) != EXPECTED_OPS_SHA256:
        fail("operation SHA-256 mismatch")
    if sha256(trace) != EXPECTED_TRACE_SHA256:
        fail("trace SHA-256 mismatch")
    with ops.open("rb") as stream:
        header = stream.read(16)
    if header[:8] != b"QECCOPSZ" or struct.unpack("<Q", header[8:])[0] != EXPECTED_OPS:
        fail("operation framing mismatch")

    with trace.open("rb") as stream:
        traced_rows = sum(1 for _ in stream)
    if traced_rows != EXPECTED_TRACED_OPS or EXPECTED_OPS - traced_rows != 96:
        fail("trace length or nonce-tail length mismatch")

    compressed = ops.open("rb")
    compressed.seek(16)
    process = subprocess.Popen(
        ["zstd", "-dc"], stdin=compressed, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert process.stdout is not None and process.stderr is not None
    rows: list[tuple[int, int, int, int]] = []
    counts: collections.Counter[int] = collections.Counter()
    rhmr = 0
    try:
        with trace.open("rt", encoding="ascii", newline="") as sites:
            for index in range(EXPECTED_TRACED_OPS):
                record = process.stdout.read(56)
                if len(record) != 56:
                    fail(f"short operation record at {index}")
                kind = struct.unpack_from("<I", record)[0]
                fields = sites.readline().rstrip("\n").split("\t")
                if len(fields) != 4 or not fields[0].isdecimal() or int(fields[0]) != index:
                    fail(f"malformed or non-contiguous trace row {index}")
                if kind in (11, 12):
                    ordinal = rhmr
                    rhmr += 1
                    if kind == 12:
                        key = (fields[1], int(fields[2]))
                        family = FAMILIES.get(key)
                        if family is not None:
                            rows.append((index, ordinal, key[1], family))
                            counts[family] += 1
            if sites.readline() != "":
                fail("trace has trailing rows")
        for index in range(EXPECTED_TRACED_OPS, EXPECTED_OPS):
            record = process.stdout.read(56)
            if len(record) != 56 or struct.unpack_from("<I", record)[0] != 6:
                fail(f"nonce tail row {index} is not X")
        if process.stdout.read(1) != b"":
            fail("operation stream has trailing bytes")
    finally:
        compressed.close()
    stderr = process.stderr.read()
    status = process.wait()
    if status != 0:
        fail(f"zstd failed with {status}: {stderr.decode(errors='replace')}")
    if rhmr != EXPECTED_RHMR:
        fail(f"R/Hmr count {rhmr} != {EXPECTED_RHMR}")
    got_counts = tuple(counts[i] for i in range(4))
    if got_counts != EXPECTED_COUNTS:
        fail(f"family counts {got_counts} != {EXPECTED_COUNTS}")

    raw = "".join(
        f"{index}\t{ordinal}\t{line}\t{family}\n"
        for index, ordinal, line, family in rows
    ).encode("ascii")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(raw)
    print(
        f"extract-phase-meta: PASS sites={len(rows)} rhmr={rhmr} "
        f"counts={got_counts} meta_sha256={hashlib.sha256(raw).hexdigest()}"
    )


if __name__ == "__main__":
    main()
