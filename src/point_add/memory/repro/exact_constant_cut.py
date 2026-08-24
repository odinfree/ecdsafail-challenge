#!/usr/bin/env python3
"""Independently certify exact constant-zero nonlinear gates in promoted ops.bin.

The verifier streams the compressed artifact and implements the evaluator's
state transitions with the conservative lattice {0, 1, unknown}. It assumes
only the frozen four-register point-add ABI: q0..q511 and b0..b511 are unknown
inputs; all other state begins zero. The declarations at the end of the stream
are checked against that ABI before PASS is printed.
"""

from __future__ import annotations

import argparse
import hashlib
import struct
import subprocess
import unittest
from pathlib import Path


MAGIC = b"QECCOPSZ"
HEADER_BYTES = 16
RECORD_BYTES = 56
NO_WIRE = (1 << 64) - 1

ZERO = 0
ONE = 1
UNKNOWN = 2

NEG = 0
REGISTER = 1
APPEND = 2
BIT_INVERT = 3
BIT_STORE0 = 4
BIT_STORE1 = 5
X = 6
Z = 7
CX = 8
CZ = 9
SWAP = 10
R = 11
HMR = 12
CCX = 13
CCZ = 14
PUSH_CONDITION = 15
POP_CONDITION = 16
DEBUG_PRINT = 17

EXPECTED_SHA256 = "87371140be9e81a7b4a79b87b92cd0a8b0f13362bee5ecb23229807a8af6d05e"
EXPECTED_COUNT = 12_593_858
EXPECTED_BASE_HITS = (
    (15_461, CCX, 513, 775, 776),
    (15_464, CCX, 514, 776, 777),
    (5_836_416, CCX, 513, 781, 782),
    (5_836_417, CCX, 514, 782, 1055),
    (5_913_066, CCX, 582, 710, 773),
    (5_935_732, CCX, 582, 512, 773),
    (6_003_685, CCX, 709, 731, 1060),
    (6_021_218, CCX, 709, 771, 1060),
    (6_089_324, CCX, 732, 708, 773),
    (6_121_152, CCX, 732, 512, 773),
    (6_281_357, CCX, 581, 512, 1112),
    (6_340_361, CCX, 581, 1099, 1112),
    (6_515_872, CCX, 584, 521, 771),
    (6_533_956, CCX, 584, 772, 771),
    (6_602_891, CCX, 520, 540, 781),
    (6_618_347, CCX, 520, 778, 781),
    (6_688_557, CCX, 541, 519, 776),
    (6_715_372, CCX, 541, 775, 776),
    (6_758_096, CCX, 515, 775, 776),
    (6_758_099, CCX, 513, 776, 777),
    (12_571_629, CCX, 515, 1055, 784),
    (12_571_630, CCX, 513, 784, 785),
)


def tri_and(a: int, b: int) -> int:
    if a == ZERO or b == ZERO:
        return ZERO
    if a == ONE and b == ONE:
        return ONE
    return UNKNOWN


def tri_xor(a: int, b: int) -> int:
    if a == UNKNOWN or b == UNKNOWN:
        return UNKNOWN
    return a ^ b


def store_zero_if(value: int, condition: int) -> int:
    if condition == ZERO:
        return value
    if condition == ONE or value == ZERO:
        return ZERO
    return UNKNOWN


def store_one_if(value: int, condition: int) -> int:
    if condition == ZERO:
        return value
    if condition == ONE or value == ONE:
        return ONE
    return UNKNOWN


def ensure(values: list[int], index: int, fill: int = ZERO) -> None:
    if index >= len(values):
        values.extend([fill] * (index + 1 - len(values)))


class OpStream:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.file = path.open("rb", buffering=0)
        header = self.file.read(HEADER_BYTES)
        if len(header) != HEADER_BYTES or header[:8] != MAGIC:
            raise AssertionError(f"{path}: invalid operation-stream header")
        self.count = int.from_bytes(header[8:16], "little")
        self.proc = subprocess.Popen(
            ["zstd", "-q", "-d", "-c"],
            stdin=self.file,
            stdout=subprocess.PIPE,
        )
        assert self.proc.stdout is not None

    def __iter__(self):
        assert self.proc.stdout is not None
        for _ in range(self.count):
            chunks: list[bytes] = []
            remaining = RECORD_BYTES
            while remaining:
                chunk = self.proc.stdout.read(remaining)
                if not chunk:
                    raise AssertionError(f"{self.path}: truncated operation stream")
                chunks.append(chunk)
                remaining -= len(chunk)
            record = b"".join(chunks)
            yield struct.unpack("<I4xQQQQQQ", record)
        if self.proc.stdout.read(1):
            raise AssertionError(f"{self.path}: trailing decompressed bytes")
        if self.proc.wait() != 0:
            raise AssertionError(f"{self.path}: zstd decompression failed")
        self.file.close()


def scan(path: Path) -> tuple[tuple[int, int, int, int, int], ...]:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256:
        raise AssertionError(f"baseline SHA drift: {digest}")

    stream = OpStream(path)
    if stream.count != EXPECTED_COUNT:
        raise AssertionError(f"baseline count drift: {stream.count}")

    qubits = [UNKNOWN] * 512 + [ZERO] * 1024
    bits = [UNKNOWN] * 512
    registers: dict[int, list[tuple[str, int]]] = {}
    base = ONE
    stack: list[int] = []
    hits: list[tuple[int, int, int, int, int]] = []

    for index, (kind, q2, q1, target, ctarget, ccondition, rtarget) in enumerate(stream):
        for q in (q2, q1, target):
            if q != NO_WIRE:
                ensure(qubits, q)
        for bit in (ctarget, ccondition):
            if bit != NO_WIRE:
                ensure(bits, bit)

        condition = base if ccondition == NO_WIRE else tri_and(base, bits[ccondition])

        if kind in (CCX, CCZ):
            phase_factor = qubits[target] if kind == CCZ else ONE
            predicate = tri_and(tri_and(tri_and(condition, qubits[q2]), qubits[q1]), phase_factor)
            if predicate == ZERO and (
                qubits[q2] == ZERO or qubits[q1] == ZERO or (kind == CCZ and qubits[target] == ZERO)
            ):
                hits.append((index, kind, q2, q1, target))
            if kind == CCX:
                delta = tri_and(tri_and(condition, qubits[q2]), qubits[q1])
                qubits[target] = tri_xor(qubits[target], delta)
        elif kind == CX:
            qubits[target] = tri_xor(qubits[target], tri_and(condition, qubits[q1]))
        elif kind == SWAP:
            a, b = qubits[q1], qubits[target]
            if condition == ONE:
                qubits[q1], qubits[target] = b, a
            elif condition == UNKNOWN and not (a == b and a != UNKNOWN):
                qubits[q1] = qubits[target] = UNKNOWN
        elif kind == X:
            qubits[target] = tri_xor(qubits[target], condition)
        elif kind in (R, HMR):
            qubits[target] = store_zero_if(qubits[target], condition)
            if kind == HMR and condition != ZERO:
                bits[ctarget] = UNKNOWN
        elif kind == BIT_INVERT:
            bits[ctarget] = tri_xor(bits[ctarget], condition)
        elif kind == BIT_STORE0:
            bits[ctarget] = store_zero_if(bits[ctarget], condition)
        elif kind == BIT_STORE1:
            bits[ctarget] = store_one_if(bits[ctarget], condition)
        elif kind == PUSH_CONDITION:
            stack.append(base)
            base = tri_and(base, bits[ccondition])
        elif kind == POP_CONDITION:
            if not stack:
                raise AssertionError(f"unbalanced condition stack at op {index}")
            base = stack.pop()
        elif kind == APPEND:
            if rtarget == NO_WIRE:
                raise AssertionError(f"append without register at op {index}")
            wire = ("q", target) if target != NO_WIRE else ("b", ctarget)
            registers.setdefault(rtarget, []).append(wire)
        elif kind not in (NEG, REGISTER, Z, CZ, DEBUG_PRINT):
            raise AssertionError(f"unknown operation kind {kind} at op {index}")

    if stack:
        raise AssertionError("unbalanced condition stack at stream end")
    expected_registers = {
        0: [("q", q) for q in range(256)],
        1: [("q", q) for q in range(256, 512)],
        2: [("b", b) for b in range(256)],
        3: [("b", b) for b in range(256, 512)],
    }
    if registers != expected_registers:
        raise AssertionError("four-register ABI drift")
    return tuple(hits)


def verify_deletion_only(baseline_path: Path, candidate_path: Path) -> tuple[int, str]:
    baseline = OpStream(baseline_path)
    candidate = OpStream(candidate_path)
    if baseline.count != EXPECTED_COUNT:
        raise AssertionError(f"baseline count drift: {baseline.count}")
    if candidate.count != EXPECTED_COUNT - len(EXPECTED_BASE_HITS):
        raise AssertionError(f"candidate count drift: {candidate.count}")

    deleted = {hit[0] for hit in EXPECTED_BASE_HITS}
    baseline_iter = iter(baseline)
    candidate_iter = iter(candidate)
    for index in range(baseline.count):
        baseline_record = next(baseline_iter)
        if index in deleted:
            expected = EXPECTED_BASE_HITS[sorted(deleted).index(index)]
            kind, q2, q1, target, _ctarget, _condition, _register = baseline_record
            if (index, kind, q2, q1, target) != expected:
                raise AssertionError(f"deletion operand drift at baseline op {index}")
            continue
        candidate_record = next(candidate_iter)
        if candidate_record != baseline_record:
            raise AssertionError(f"candidate differs beyond deletions at baseline op {index}")

    try:
        next(baseline_iter)
        raise AssertionError("baseline iterator has trailing records")
    except StopIteration:
        pass
    try:
        next(candidate_iter)
        raise AssertionError("candidate iterator has trailing records")
    except StopIteration:
        pass
    return candidate.count, hashlib.sha256(candidate_path.read_bytes()).hexdigest()


class LatticeTests(unittest.TestCase):
    def test_fail_closed(self) -> None:
        self.assertEqual(tri_and(ZERO, UNKNOWN), ZERO)
        self.assertEqual(tri_and(ONE, UNKNOWN), UNKNOWN)
        self.assertEqual(tri_xor(UNKNOWN, UNKNOWN), UNKNOWN)

    def test_conditional_store(self) -> None:
        self.assertEqual(store_zero_if(ZERO, UNKNOWN), ZERO)
        self.assertEqual(store_zero_if(ONE, UNKNOWN), UNKNOWN)
        self.assertEqual(store_one_if(ONE, UNKNOWN), ONE)
        self.assertEqual(store_one_if(ZERO, UNKNOWN), UNKNOWN)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("ops", type=Path)
    parser.add_argument("candidate", nargs="?", type=Path)
    args = parser.parse_args()
    hits = scan(args.ops)
    if hits != EXPECTED_BASE_HITS:
        missing = sorted(set(EXPECTED_BASE_HITS) - set(hits))
        extra = sorted(set(hits) - set(EXPECTED_BASE_HITS))
        raise AssertionError(f"constant-cut set drift: missing={missing} extra={extra}")
    candidate_suffix = ""
    if args.candidate is not None:
        candidate_count, candidate_sha = verify_deletion_only(args.ops, args.candidate)
        candidate_suffix = (
            f" candidate_ops={candidate_count} candidate_sha256={candidate_sha} deletion_only=true"
        )
    print(
        f"PASS sha256={EXPECTED_SHA256} ops={EXPECTED_COUNT} "
        f"nonlinear_identities={len(hits)} q775=true abi=frozen{candidate_suffix}"
    )


if __name__ == "__main__":
    main()
