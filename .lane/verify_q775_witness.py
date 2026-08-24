#!/usr/bin/env python3
"""Independently verify that candidate ops equal baseline ops minus one zero-control CCX."""

from __future__ import annotations

import argparse
import struct
import subprocess
from pathlib import Path


MAGIC = b"QECCOPSZ"
HEADER_BYTES = 16
RECORD_BYTES = 56
NO_WIRE = (1 << 64) - 1
RESET_INDEX = 14_686
CUT_INDEX = 15_461
ZERO_CONTROL = 775

X = 6
CX = 8
SWAP = 10
R = 11
HMR = 12
CCX = 13
PUSH_CONDITION = 15
POP_CONDITION = 16


class OpStream:
    def __init__(self, path: Path) -> None:
        self.path = path
        # Unbuffered I/O is required because the decompressor inherits this
        # descriptor after the 16-byte header; buffered read-ahead would move
        # the underlying descriptor past the zstd frame.
        self.file = path.open("rb", buffering=0)
        header = self.file.read(HEADER_BYTES)
        if header[:8] != MAGIC or len(header) != HEADER_BYTES:
            raise AssertionError(f"{path}: invalid operation-stream header")
        self.count = int.from_bytes(header[8:16], "little")
        self.proc = subprocess.Popen(
            ["zstd", "-q", "-d", "-c"],
            stdin=self.file,
            stdout=subprocess.PIPE,
        )
        assert self.proc.stdout is not None

    def read_record(self) -> bytes:
        chunks: list[bytes] = []
        remaining = RECORD_BYTES
        while remaining:
            chunk = self.proc.stdout.read(remaining)
            if not chunk:
                raise AssertionError(f"{self.path}: truncated operation stream")
            chunks.append(chunk)
            remaining -= len(chunk)
        return b"".join(chunks)

    def finish(self) -> None:
        assert self.proc.stdout is not None
        if self.proc.stdout.read(1):
            raise AssertionError(f"{self.path}: trailing decompressed bytes")
        if self.proc.wait() != 0:
            raise AssertionError(f"{self.path}: zstd decompression failed")
        self.file.close()


def fields(record: bytes) -> tuple[int, int, int, int, int, int, int]:
    return struct.unpack("<I4xQQQQQQ", record)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()

    baseline = OpStream(args.baseline)
    candidate = OpStream(args.candidate)
    assert baseline.count == 12_593_858
    assert candidate.count == baseline.count - 1

    condition_depth = 0
    for index in range(baseline.count):
        baseline_record = baseline.read_record()
        kind, q2, q1, target, _ctarget, condition, _rtarget = fields(baseline_record)

        if index == RESET_INDEX:
            assert condition_depth == 0
            assert (kind, target, condition) == (R, ZERO_CONTROL, NO_WIRE)

        if RESET_INDEX < index < CUT_INDEX:
            writes_zero = (
                (kind in {X, CX, CCX, R, HMR} and target == ZERO_CONTROL)
                or (kind == SWAP and (target == ZERO_CONTROL or q1 == ZERO_CONTROL))
            )
            assert not writes_zero, f"intervening q775 write at baseline op {index}"

        if index == CUT_INDEX:
            assert condition_depth == 0
            assert (kind, q2, q1, target, condition) == (
                CCX,
                513,
                ZERO_CONTROL,
                776,
                NO_WIRE,
            )
        else:
            candidate_record = candidate.read_record()
            assert candidate_record == baseline_record, (
                f"candidate differs from deletion-only baseline at baseline op {index}"
            )

        if kind == PUSH_CONDITION:
            condition_depth += 1
        elif kind == POP_CONDITION:
            assert condition_depth > 0
            condition_depth -= 1

    assert condition_depth == 0
    baseline.finish()
    candidate.finish()
    print(
        "PASS baseline=12593858 candidate=12593857 "
        "reset=14686 cut=15461 q775_no_write=true deletion_only=true"
    )


if __name__ == "__main__":
    main()
