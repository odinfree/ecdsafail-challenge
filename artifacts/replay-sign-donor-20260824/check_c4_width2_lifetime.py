#!/usr/bin/env python3
"""Exact-675 C4 lifetime gate for the n=2 boundary phase comparator."""

from __future__ import annotations

import argparse
from collections import Counter, deque
import hashlib
from pathlib import Path
import re
import struct

import zstandard


BASE = "67524171baaf568dc3dc606f38515745f70804ff"
EXPECTED = {
    "src/point_add/arith/compare.rs":
        "0d1cf305c68263cd078ec96c10b2b00135bef21492f81ff4e3d7d45d33e5191e",
    "src/point_add/pingpong_div.rs":
        "953dd851629e4d15a4f56d5061e3c0d61ea83bebab8f7aca5243636d4f240c38",
    "src/point_add/mod.rs":
        "596ed58d4d61fbb087ccf236c728efc09631632a96693d849a71c03bea866a06",
    "ops.bin":
        "87371140be9e81a7b4a79b87b92cd0a8b0f13362bee5ecb23229807a8af6d05e",
    "artifacts/replay-sign-donor-20260824/b0-replay-peak.log":
        "16f0d3102e702942d92b498c9171fd534cd982121be7f35ff46ead110cf5745f",
}
REC = struct.Struct("<II6Q")
KINDS = [12, 15, 6, 6, 8, 13, 8, 9, 9, 9, 8, 12, 9, 8, 11, 6, 6, 16, 11]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def source_array(text: str, name: str) -> list[int]:
    match = re.search(rf"const {name}: \[[^\]]+\] = \[(.*?)\];", text, re.S)
    assert match is not None, name
    return [int(value) for value in re.findall(r"\d+", match.group(1))]


def promoted_width2_rounds(pingpong: Path) -> tuple[list[int], list[int]]:
    text = pingpong.read_text()
    widths = source_array(text, "WIDTH_SCHEDULE")
    repairs = set(source_array(text, "WIDTH_REPAIR"))
    assert len(widths) == 700 and len(repairs) == 100

    # These are the build-level promoted defaults in exact-675 mod.rs.
    n = 256
    rounds = 696
    rounds_mul = 694
    r1_div = 335
    r1_mul = 315
    r2 = 645
    peak = 1267
    compare = 22

    def value_width(round_index: int) -> int:
        if round_index == 0:
            return 259
        # width_round_index uses rounds(), including in the multiply traversal.
        sampled = round_index * (704 - 1) // (rounds - 1)
        if sampled >= len(widths):
            return 8
        return max(8, min(259, widths[sampled] + int(sampled in repairs)))

    def chunk_bounds(width: int, chunk: int) -> list[int]:
        chunks = max(1, (width + max(1, chunk) - 1) // max(1, chunk))
        base, extra = divmod(width, chunks)
        return [base + int(index < extra) for index in range(chunks)]

    def layout_ladder(sizes: list[int], final_carry: bool = True) -> int:
        count = len(sizes)
        return max(
            int(index > 0)
            + int(index + 1 < count or final_carry)
            + max(0, width - 1)
            for index, width in enumerate(sizes)
        )

    def layout(target: int) -> list[int] | None:
        for wide in range(13):
            chunks = wide + 1
            equal = chunk_bounds(n, (n + chunks - 1) // chunks)
            if layout_ladder(equal) <= target:
                return equal

            chunks = wide + 2
            capacity = []
            for index in range(chunks):
                # All promoted replay cells request a final carry, so every
                # chunk has either a successor boundary or that final carry.
                overhead = int(index > 0) + 1
                capacity.append(max(0, target + 1 - overhead))
            capacity[0] = min(capacity[0], compare)
            if any(value == 0 for value in capacity) or sum(capacity) < n:
                continue
            excess = sum(capacity) - n
            for index in [0] + list(range(1, chunks))[::-1]:
                cut = min(excess, capacity[index] - 1)
                capacity[index] -= cut
                excess -= cut
            if excess == 0 and layout_ladder(capacity) <= target:
                return capacity
        return None

    div_rounds: list[int] = []
    for round_index in range(2, rounds):
        if round_index < r1_div:
            tape, walk = r1_div, value_width(r1_div)
        elif round_index <= r2:
            tape, walk = round_index + 1, value_width(round_index + 1)
        else:
            tape, walk = rounds, 1
        budget = max(0, peak - (tape + 2 * n + 2 * walk))
        sizes = layout(budget)
        if sizes is not None and sizes[0] == 2:
            assert sizes == [2, 127, 127] and budget == 128
            div_rounds.append(round_index)

    mul_rounds: list[int] = []
    for round_index in range(r2, r1_mul - 1, -1):
        # Before replaying r on walkback, the registers still have width W[r+1].
        tape, walk = round_index + 1, value_width(round_index + 1)
        budget = max(0, peak - (tape + 2 * n + 2 * walk) - 1)
        sizes = layout(budget)
        if sizes is not None and sizes[0] == 2:
            assert sizes == [2, 127, 127] and budget == 128
            mul_rounds.append(round_index)
    return div_rounds, mul_rounds


def is_width2_pattern(ops: list[tuple[int, ...]]) -> bool:
    if [op[0] for op in ops] != KINDS:
        return False
    # Fields are kind, q_control2, q_control1, q_target, c_target,
    # c_condition, r_target.
    boundary, phase = ops[0][3], ops[0][4]
    if ops[1][5] != phase:
        return False
    u0, u1, v0 = ops[2][3], ops[3][3], ops[4][3]
    if ops[4][2:4] != (u0, v0):
        return False
    carry = ops[5][3]
    if (ops[5][1], ops[5][2]) != (u0, v0):
        return False
    if ops[6][2:4] != (carry, u0):
        return False
    v1 = ops[7][3]
    if ops[7][2] != u1 or ops[8][2:4] != (u1, u0):
        return False
    if ops[9][2:4] != (v1, u0) or ops[10][2:4] != (carry, u0):
        return False
    measured = ops[11][4]
    if ops[11][3] != carry:
        return False
    if ops[12][2:4] != (u0, v0) or ops[12][5] != measured:
        return False
    return (
        ops[13][2:4] == (u0, v0)
        and ops[14][3] == carry
        and ops[15][3] == u0
        and ops[16][3] == u1
        and ops[18][3] == boundary
    )


def scan_ops(path: Path) -> tuple[int, list[int]]:
    starts: list[int] = []
    window: deque[tuple[int, tuple[int, ...]]] = deque(maxlen=len(KINDS))
    with path.open("rb") as stream:
        header = stream.read(16)
        assert header[:8] == b"QECCOPSZ"
        expected = int.from_bytes(header[8:16], "little")
        reader = zstandard.ZstdDecompressor(max_window_size=1 << 27).stream_reader(stream)
        remainder = b""
        index = 0
        while True:
            data = reader.read(56 * 16384)
            if not data:
                break
            data = remainder + data
            upto = len(data) // 56 * 56
            remainder = data[upto:]
            for offset in range(0, upto, 56):
                values = REC.unpack_from(data, offset)
                window.append((index, (values[0],) + values[2:]))
                index += 1
                if len(window) == len(KINDS):
                    rows = list(window)
                    if is_width2_pattern([row[1] for row in rows]):
                        starts.append(rows[0][0])
        assert index == expected and not remainder
    return expected, starts


def peak_rows(path: Path) -> list[tuple[int, str]]:
    rows = []
    for line in path.read_text().splitlines():
        if "ALLOC_NEAR active=1267" not in line:
            continue
        phase = re.search(r"phase='([^']*)'", line)
        index = re.search(r"ops_idx=(\d+)", line)
        assert phase is not None and index is not None
        rows.append((int(index.group(1)), phase.group(1)))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    args = parser.parse_args()
    repo = args.repo.resolve()

    for relative, expected in EXPECTED.items():
        actual = sha256(repo / relative)
        assert actual == expected, (relative, actual, expected)

    div_rounds, mul_rounds = promoted_width2_rounds(repo / "src/point_add/pingpong_div.rs")
    assert div_rounds == list(range(2, 335))
    assert mul_rounds == [325, 323, 321, 319]

    op_count, starts = scan_ops(repo / "ops.bin")
    assert len(starts) == len(div_rounds) + len(mul_rounds) == 337
    assert starts[:333] == [914687 + 4536 * index for index in range(333)]
    assert starts[333:] == [10227975, 10241463, 10254913, 10268413]

    # The pattern starts on boundary HMR. The comparator scratch allocation is
    # sampled one op later and is released after its R, 14 op positions later.
    intervals = [(start + 1, start + 15) for start in starts]
    peaks = peak_rows(repo / "artifacts/replay-sign-donor-20260824/b0-replay-peak.log")
    intersections = [
        (index, phase, lo, hi)
        for index, phase in peaks
        for lo, hi in intervals
        if lo <= index < hi
    ]
    assert not intersections
    phase_counts = Counter(phase for _, phase in peaks)
    assert phase_counts == {"pp_div_replay": 993, "pp_mul_walkback": 672}

    closest = min(
        (
            lo - index if index < lo else index - (hi - 1) if index >= hi else 0,
            lo,
            hi,
            index,
            phase,
        )
        for lo, hi in intervals
        for index, phase in peaks
    )
    assert closest == (5, 914688, 914702, 914706, "pp_div_replay")

    print(f"base={BASE}")
    print(f"op_count={op_count}")
    print(f"width2_sites={len(starts)} div={len(div_rounds)} mul={len(mul_rounds)}")
    print(f"div_rounds={div_rounds[0]}..{div_rounds[-1]}")
    print(f"mul_rounds={','.join(map(str, mul_rounds))}")
    print(f"div_intervals_first_last={intervals[0]},{intervals[332]} stride=4536")
    print(f"mul_intervals={intervals[333:]}")
    print(f"peak_events={len(peaks)} phase_counts={dict(phase_counts)}")
    print(f"peak_intersections={len(intersections)}")
    print(f"closest_peak={closest}")
    print("verdict=HARD_NACK_C4_WIDTH2_GLOBAL_Q_LIFT")


if __name__ == "__main__":
    main()
