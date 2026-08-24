#!/usr/bin/env python3
"""Source-bound census of ping-pong replay carry-cleanup predicates.

This is a falsifier, not a correctness proof.  It reconstructs the promoted
canonical-frame replay on deterministic, EC-derived affine-add inputs and
records two different carry families:

* the exact carry from bits 0..233 into the final 22-bit overflow-cleanup
  comparator; and
* the exact carry entering each interior chunk's top comparison window, plus
  the boundary carry that comparator must reconstruct.

Only trajectories that fit the promoted signed-walk width schedule, reach the
documented (+/-1,+/-1) terminal orbit, and pass the coefficient endpoint
identities are admitted.  A finite census can falsify fixed/affine candidates;
it cannot establish a new invariant for deleting gates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable, Iterable, Sequence


PROMOTED_COMMIT = "67524171baaf568dc3dc606f38515745f70804ff"
PROMOTED_TREE = "8202910d176fa1f3332ff961e6f3f789ca6a7ac2"

P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
MASK256 = (1 << 256) - 1
F = (1 << 32) + 977
ROUND1_H = (1 << 31) + 488

DIR_DIV = 0
DIR_MUL = 1

# final tuple fields
F_DIR, F_SAMPLE, F_ROUND, F_ARG, F_TAPE = range(5)
F_SOURCE, F_TARGET, F_ACC, F_SUM, F_OVERFLOW, F_WINDOW_CARRY = range(5, 11)

# interior tuple fields
(
    I_DIR,
    I_SAMPLE,
    I_ROUND,
    I_CHUNK,
    I_WIDTH,
    I_ARG,
    I_TAPE,
    I_CARRY_IN,
    I_WINDOW_CARRY,
    I_CARRY_OUT,
    I_PREDICTED,
    I_ADDEND,
    I_ACC,
    I_SUM,
) = range(14)


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def promoted_text(repo: Path, relative: str) -> str:
    return git(repo, "show", f"{PROMOTED_COMMIT}:{relative}")


def parse_array(source: str, name: str, expected_len: int) -> list[int]:
    match = re.search(
        rf"const {re.escape(name)}: \[u16; {expected_len}\] = \[(.*?)\];",
        source,
        re.S,
    )
    if match is None:
        raise RuntimeError(f"could not bind {name} at {PROMOTED_COMMIT}")
    values = [int(value) for value in re.findall(r"\d+", match.group(1))]
    if len(values) != expected_len:
        raise RuntimeError(f"{name}: expected {expected_len}, got {len(values)}")
    return values


def parse_route_defaults(source: str) -> dict[str, int]:
    wanted = {
        "SUB4_PP_ROUNDS",
        "SUB4_PP_ROUNDS_MUL",
        "SUB4_PP_R1",
        "SUB4_PP_R1_MUL",
        "SUB4_PP_R2",
        "SUB4_PP_PEAK",
        "SUB4_PP_REPLAY_CHUNK_COMPARE",
        "SUB4_PP_REPLAY_FLAG_COMPARE",
        "SUB4_PP_REPLAY_FOLD_WINDOW",
        "SUB4_PP_REPLAY_FOLD_WINDOW_MUL",
        "SUB4_PP_ENDPOINT_FOLD_WINDOW",
        "SUB4_PP_SIGNED_FRAME",
    }
    found = {
        name: int(value)
        for name, value in re.findall(
            r'set_default_env\("([A-Z0-9_]+)", "([0-9]+)"\);', source
        )
        if name in wanted
    }
    missing = wanted - found.keys()
    if missing:
        raise RuntimeError(f"missing promoted route defaults: {sorted(missing)}")
    return found


def ec_add(
    left: tuple[int, int] | None, right: tuple[int, int] | None
) -> tuple[int, int] | None:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2:
        if (y1 + y2) % P == 0:
            return None
        slope = 3 * x1 * x1 * pow(2 * y1, -1, P) % P
    else:
        slope = (y2 - y1) * pow((x2 - x1) % P, -1, P) % P
    x3 = (slope * slope - x1 - x2) % P
    return x3, (slope * (x1 - x3) - y1) % P


def ec_mul(scalar: int) -> tuple[int, int]:
    result = None
    point = (GX, GY)
    while scalar:
        if scalar & 1:
            result = ec_add(result, point)
        point = ec_add(point, point)
        scalar >>= 1
    if result is None:
        raise RuntimeError("deterministic scalar unexpectedly produced infinity")
    return result


def deterministic_scalar(sample: int, role: bytes) -> int:
    digest = hashlib.shake_256(
        b"ecdsa.fail/67524171/replay-window-census/v1/"
        + role
        + sample.to_bytes(8, "little")
    ).digest(32)
    return int.from_bytes(digest, "little") % (ORDER - 1) + 1


def width_at(round_index: int, schedule: Sequence[int], repairs: set[int]) -> int:
    if round_index == 0:
        return 259
    # width_round_index uses rounds(), not rounds_for(direction).
    sampled = round_index * (704 - 1) // (696 - 1)
    if sampled >= len(schedule):
        return 8
    return max(8, min(259, schedule[sampled] + int(sampled in repairs)))


def fits_signed(value: int, width: int) -> bool:
    return -(1 << (width - 1)) <= value < (1 << (width - 1))


def as_signed(bits: int, width: int) -> int:
    return bits - (1 << width) if bits >> (width - 1) else bits


def add_low_window(value: int, delta: int, width: int) -> int:
    mask = (1 << width) - 1
    return (value & ~mask) | ((value + delta) & mask)


def walk_round_zero(denominator: int, fold_window: int) -> int:
    """Literal value action of fused_lift_round0_forward_sparse."""
    a0 = denominator & 1
    a1 = (denominator >> 1) & 1
    not_a1 = 1 - a1
    half_f_minus_one = (F - 1) >> 1
    magnitude = (
        (not_a1 & (1 - a0)) * F
        + a0 * half_f_minus_one
        + (not_a1 & a0)
    )
    low = denominator >> 1
    if a1:
        low ^= MASK256
    # cadd_per_position_controls_trunc(last=fold_window-2) updates through
    # position last+1, hence exactly fold_window low bits.
    low = add_low_window(low, magnitude, fold_window)
    if a1:
        low ^= MASK256
    low ^= a0 << 255
    bits = low | (not_a1 << 256) | (not_a1 << 257) | (not_a1 << 258)
    return as_signed(bits, 259)


def walk_round_one(value_v: int, width: int, endpoint_window: int) -> tuple[int, int]:
    """Literal value action of fused_round1_forward."""
    modulus = 1 << width
    v_bits = value_v % modulus
    sign = (((P % modulus) >> 1) ^ (v_bits >> 1)) & 1
    shifted = (v_bits >> 1) | (((v_bits >> (width - 1)) & 1) << (width - 1))
    if sign:
        shifted ^= modulus - 1
    shifted = add_low_window(shifted, -ROUND1_H, 32 + endpoint_window)
    high_width = width - 255
    high_mask = ((1 << high_width) - 1) << 255
    high = ((shifted >> 255) + 1) & ((1 << high_width) - 1)
    shifted = (shifted & ~high_mask) | (high << 255)
    return as_signed(shifted, width), sign


def walk_transcript(
    denominator: int,
    rounds: int,
    schedule: Sequence[int],
    repairs: set[int],
    fold_window: int,
    endpoint_window: int,
) -> tuple[int, int, list[int]] | None:
    """Promoted walk value action, gated at every scheduled width."""
    u = P
    v = denominator if denominator & 1 else denominator - P
    tape: list[int] = []
    for round_index in range(rounds):
        width = width_at(round_index, schedule, repairs)
        if not fits_signed(u, width) or not fits_signed(v, width):
            return None
        if round_index == 0:
            v = walk_round_zero(denominator, fold_window)
            tape.append(denominator & 1)
            continue
        if round_index == 1:
            u, sign = walk_round_one(v, width, endpoint_window)
            tape.append(sign)
            continue
        source, target = (u, v) if round_index % 2 == 0 else (v, u)
        modulus = 1 << width
        sign = (((source % modulus) >> 1) ^ ((target % modulus) >> 1)) & 1
        updated = (target + (source if sign == 0 else -source)) // 2
        if round_index % 2 == 0:
            v = updated
        else:
            u = updated
        tape.append(sign)
    if abs(u) != 1 or abs(v) != 1:
        return None
    return u, v, tape


def chunk_bounds(width: int, chunk: int) -> list[tuple[int, int]]:
    chunks = max(1, (width + max(1, chunk) - 1) // max(1, chunk))
    base, extra = divmod(width, chunks)
    output = []
    low = 0
    for index in range(chunks):
        size = base + int(index < extra)
        output.append((low, low + size))
        low += size
    return output


def layout_ladder(sizes: Sequence[int], final_carry: bool = True) -> int:
    count = len(sizes)
    return max(
        int(index > 0)
        + int(index + 1 < count or final_carry)
        + max(0, width - 1)
        for index, width in enumerate(sizes)
    )


def chunk_layout(width: int, target: int, compare: int) -> list[tuple[int, int]]:
    """Literal port of pingpong_div.rs::chunk_layout for final_carry=true."""
    for wide in range(13):
        count = wide + 1
        equal = chunk_bounds(width, (width + count - 1) // count)
        sizes = [high - low for low, high in equal]
        if layout_ladder(sizes) <= target:
            return equal

        count = wide + 2
        capacity = [
            max(
                0,
                target
                + 1
                # final_carry=true makes every chunk pay the output-carry cost.
                - (int(index > 0) + 1),
            )
            for index in range(count)
        ]
        capacity[0] = min(capacity[0], compare)
        if any(value == 0 for value in capacity) or sum(capacity) < width:
            continue
        excess = sum(capacity) - width
        for index in [0, *reversed(range(1, count))]:
            if excess == 0:
                break
            cut = min(excess, capacity[index] - 1)
            capacity[index] -= cut
            excess -= cut
        if excess == 0 and layout_ladder(capacity) <= target:
            output = []
            low = 0
            for size in capacity:
                output.append((low, low + size))
                low += size
            return output
    raise RuntimeError(f"no promoted chunk layout for target={target}")


def ladder_budget(
    direction: int,
    round_index: int,
    route: dict[str, int],
    schedule: Sequence[int],
    repairs: set[int],
) -> int:
    if direction == DIR_DIV:
        rounds = route["SUB4_PP_ROUNDS"]
        r1 = route["SUB4_PP_R1"]
        extra = 0
    else:
        rounds = route["SUB4_PP_ROUNDS_MUL"]
        r1 = route["SUB4_PP_R1_MUL"]
        extra = 1
    r2 = route["SUB4_PP_R2"]
    if round_index < r1:
        tape_len = r1
        walk_width = width_at(r1, schedule, repairs)
    elif round_index <= r2:
        tape_len = round_index + 1
        walk_width = width_at(round_index + 1, schedule, repairs)
    else:
        tape_len = rounds
        walk_width = 1
    allowance = max(
        0,
        route["SUB4_PP_PEAK"]
        - (tape_len + 2 * 256 + 2 * walk_width),
    )
    return max(0, allowance - extra)


def record_add(
    final_events: list[tuple[int, ...]],
    interior_events: list[tuple[int, ...]],
    direction: int,
    sample: int,
    round_index: int,
    tape_sign: int,
    arg_sign: int,
    source: int,
    target: int,
    acc: int,
    bounds: Sequence[tuple[int, int]],
    final_compare: int,
    chunk_compare: int,
) -> None:
    total = acc + source
    summed = total & MASK256
    overflow = total >> 256
    cutoff = 256 - final_compare
    low_mask = (1 << cutoff) - 1
    window_carry = ((acc & low_mask) + (source & low_mask)) >> cutoff
    final_events.append(
        (
            direction,
            sample,
            round_index,
            arg_sign,
            tape_sign,
            source,
            target,
            acc,
            summed,
            overflow,
            window_carry,
        )
    )

    carry_in = 0
    for chunk, (low, high) in enumerate(bounds):
        width = high - low
        mask = (1 << width) - 1
        addend = (source >> low) & mask
        accumulator = (acc >> low) & mask
        chunk_total = addend + accumulator + carry_in
        chunk_sum = chunk_total & mask
        carry_out = chunk_total >> width
        compare = min(chunk_compare, width)
        prefix = width - compare
        if prefix == 0:
            entering = carry_in
        else:
            prefix_mask = (1 << prefix) - 1
            entering = (
                (addend & prefix_mask)
                + (accumulator & prefix_mask)
                + carry_in
            ) >> prefix
        predicted = int(
            (chunk_sum >> (width - compare))
            < (addend >> (width - compare))
        )
        if chunk + 1 < len(bounds):
            interior_events.append(
                (
                    direction,
                    sample,
                    round_index,
                    chunk,
                    width,
                    arg_sign,
                    tape_sign,
                    carry_in,
                    entering,
                    carry_out,
                    predicted,
                    addend,
                    accumulator,
                    chunk_sum,
                )
            )
        carry_in = carry_out
    if carry_in != overflow:
        raise AssertionError("chunk recurrence disagrees with exact 256-bit carry")


def mod_halve_actual(target: int, fold_window: int) -> int:
    parity = target & 1
    corrected = add_low_window(target, -parity * F, fold_window)
    if corrected & 1:
        raise AssertionError("mod_halve_pm correction did not make the value even")
    return (corrected >> 1) | (parity << 255)


def mod_double_actual(target: int, fold_window: int) -> int:
    overflow = target >> 255
    shifted = (2 * target) & MASK256
    return add_low_window(shifted, overflow * F, fold_window)


def seed_round_one_actual(source: int, sign: int) -> int:
    target = source ^ (MASK256 if sign else 0)
    # f-1 has top bit 32.  The helper's last borrow is 32+window=64
    # and updates sum bit 65, so the literal truncated value window is 66.
    return add_low_window(target, -sign * (F - 1), 66)


def seed_round_one_inverse_actual(target: int, source: int, sign: int) -> int:
    target = add_low_window(target, sign * (F - 1), 66)
    return target ^ (MASK256 if sign else 0) ^ source


def divide_cell_actual(
    source: int, target: int, sign: int, fold_window: int
) -> tuple[int, int]:
    """Return (pre-add accumulator, literal promoted value output)."""
    acc = target if sign == 0 else MASK256 ^ target
    total = acc + source
    summed = total & MASK256
    overflow = total >> 256
    parity = summed & 1
    not_sign_and_parity = (1 - sign) & parity
    sign_and_parity = sign & parity
    minus_f = (1 - overflow) & not_sign_and_parity
    plus_2f = overflow & sign_and_parity
    plus_f = parity ^ sign ^ minus_f
    corrected = add_low_window(
        summed, (plus_f + 2 * plus_2f - minus_f) * F, fold_window
    )
    parity_state = parity ^ overflow ^ sign
    if sign:
        corrected ^= MASK256
    if corrected & 1:
        raise AssertionError("signed halve correction did not make the value even")
    return acc, (corrected >> 1) | (parity_state << 255)


def multiply_cell_actual(
    source: int, target: int, sign: int, fold_window: int
) -> tuple[int, int]:
    """Return (pre-add accumulator, literal promoted value output)."""
    doubled_out = target >> 255
    shifted = (2 * target) & MASK256
    acc = shifted if sign == 0 else MASK256 ^ shifted
    total = acc + source
    summed = total & MASK256
    add_out = total >> 256
    routed = doubled_out & (sign ^ add_out)
    minus_f = routed & sign
    plus_2f = routed ^ minus_f
    plus_f = add_out ^ doubled_out ^ minus_f
    corrected = add_low_window(
        summed, (plus_f + 2 * plus_2f - minus_f) * F, fold_window
    )
    if sign:
        corrected ^= MASK256
    return acc, corrected


def replay_divide(
    sample: int,
    denominator: int,
    numerator: int,
    terminal_u: int,
    terminal_v: int,
    tape: Sequence[int],
    layouts: dict[tuple[int, int], list[tuple[int, int]]],
    route: dict[str, int],
) -> tuple[list[tuple[int, ...]], list[tuple[int, ...]]] | None:
    final_events: list[tuple[int, ...]] = []
    interior_events: list[tuple[int, ...]] = []
    x, y = 0, numerator
    for round_index, tape_sign in enumerate(tape):
        source, target = (x, y) if round_index % 2 == 0 else (y, x)
        if round_index == 0:
            updated = mod_halve_actual(target, route["SUB4_PP_REPLAY_FOLD_WINDOW"])
        elif round_index == 1:
            seeded = seed_round_one_actual(source, tape_sign)
            updated = mod_halve_actual(seeded, route["SUB4_PP_REPLAY_FOLD_WINDOW"])
        else:
            acc, updated = divide_cell_actual(
                source,
                target,
                tape_sign,
                route["SUB4_PP_REPLAY_FOLD_WINDOW"],
            )
            record_add(
                final_events,
                interior_events,
                DIR_DIV,
                sample,
                round_index,
                tape_sign,
                tape_sign,
                source,
                target,
                acc,
                layouts[(DIR_DIV, round_index)],
                route["SUB4_PP_REPLAY_FLAG_COMPARE"],
                route["SUB4_PP_REPLAY_CHUNK_COMPARE"],
            )
        if round_index % 2 == 0:
            y = updated
        else:
            x = updated
    corrected_x = (-x) % P if terminal_u < 0 else x
    corrected_y = (-y) % P if terminal_v < 0 else y
    expected = numerator * pow(denominator, -1, P) % P
    if corrected_x != expected or corrected_y != expected:
        return None
    return final_events, interior_events


def replay_multiply(
    sample: int,
    denominator: int,
    numerator: int,
    terminal_u: int,
    terminal_v: int,
    tape: Sequence[int],
    layouts: dict[tuple[int, int], list[tuple[int, int]]],
    route: dict[str, int],
) -> tuple[list[tuple[int, ...]], list[tuple[int, ...]]] | None:
    final_events: list[tuple[int, ...]] = []
    interior_events: list[tuple[int, ...]] = []
    x = (-numerator) % P if terminal_u < 0 else numerator
    y = (-numerator) % P if terminal_v < 0 else numerator
    for round_index in reversed(range(len(tape))):
        tape_sign = tape[round_index]
        source, target = (x, y) if round_index % 2 == 0 else (y, x)
        if round_index == 0:
            updated = mod_double_actual(
                target, route["SUB4_PP_REPLAY_FOLD_WINDOW_MUL"]
            )
        elif round_index == 1:
            doubled = mod_double_actual(
                target, route["SUB4_PP_REPLAY_FOLD_WINDOW_MUL"]
            )
            updated = seed_round_one_inverse_actual(doubled, source, tape_sign)
        else:
            arg_sign = 1 - tape_sign
            acc, updated = multiply_cell_actual(
                source,
                target,
                arg_sign,
                route["SUB4_PP_REPLAY_FOLD_WINDOW_MUL"],
            )
            record_add(
                final_events,
                interior_events,
                DIR_MUL,
                sample,
                round_index,
                tape_sign,
                arg_sign,
                source,
                target,
                acc,
                layouts[(DIR_MUL, round_index)],
                route["SUB4_PP_REPLAY_FLAG_COMPARE"],
                route["SUB4_PP_REPLAY_CHUNK_COMPARE"],
            )
        if round_index % 2 == 0:
            y = updated
        else:
            x = updated
    if x != 0 or y != numerator * denominator % P:
        return None
    return final_events, interior_events


def gf2_rank(rows: Iterable[int]) -> int:
    basis: dict[int, int] = {}
    for original in rows:
        row = original
        while row:
            pivot = row.bit_length() - 1
            if pivot in basis:
                row ^= basis[pivot]
            else:
                basis[pivot] = row
                break
    return len(basis)


def affine_ranks(
    rows: Sequence[tuple[int, ...]],
    features: Callable[[tuple[int, ...]], int],
    label: Callable[[tuple[int, ...]], int],
    feature_count: int,
) -> dict[str, int | bool]:
    feature_rows = [features(row) for row in rows]
    rank = gf2_rank(feature_rows)
    augmented = gf2_rank(
        value | (label(row) << feature_count)
        for value, row in zip(feature_rows, rows, strict=True)
    )
    return {
        "rows": len(rows),
        "feature_count": feature_count,
        "rank": rank,
        "augmented_rank": augmented,
        "affine_fit": rank == augmented,
    }


def witness(row: tuple[int, ...]) -> dict[str, int | str]:
    return {
        "direction": "divide" if row[F_DIR] == DIR_DIV else "multiply",
        "sample": row[F_SAMPLE],
        "round": row[F_ROUND],
        "arg_sign": row[F_ARG],
        "tape_sign": row[F_TAPE],
        "window_carry": row[F_WINDOW_CARRY],
        "overflow": row[F_OVERFLOW],
        "source": f"0x{row[F_SOURCE]:064x}",
        "target": f"0x{row[F_TARGET]:064x}",
        "pre_add_acc": f"0x{row[F_ACC]:064x}",
        "sum": f"0x{row[F_SUM]:064x}",
    }


def summarize_final(rows: Sequence[tuple[int, ...]], compare: int) -> dict[str, object]:
    output: dict[str, object] = {}
    for direction, name in [(DIR_DIV, "divide"), (DIR_MUL, "multiply")]:
        selected = [row for row in rows if row[F_DIR] == direction]
        by_round: dict[int, set[int]] = defaultdict(set)
        overflow_by_round: dict[int, set[int]] = defaultdict(set)
        for row in selected:
            by_round[row[F_ROUND]].add(row[F_WINDOW_CARRY])
            overflow_by_round[row[F_ROUND]].add(row[F_OVERFLOW])
        mismatches = sum(
            int((row[F_SUM] >> (256 - compare)) < (row[F_SOURCE] >> (256 - compare)))
            != row[F_OVERFLOW]
            for row in selected
        )
        affine = {}
        for arg_sign in (0, 1):
            group = [row for row in selected if row[F_ARG] == arg_sign]
            # Constant, ten static round bits, then all 512 exact add-input bits.
            feature_count = 1 + 10 + 256 + 256
            affine[str(arg_sign)] = affine_ranks(
                group,
                lambda row: 1
                | (row[F_ROUND] << 1)
                | (row[F_ACC] << 11)
                | (row[F_SOURCE] << (11 + 256)),
                lambda row: row[F_WINDOW_CARRY],
                feature_count,
            )
        output[name] = {
            "cells": len(selected),
            "window_carry_counts": dict(sorted(Counter(row[F_WINDOW_CARRY] for row in selected).items())),
            "overflow_counts": dict(sorted(Counter(row[F_OVERFLOW] for row in selected).items())),
            "rounds_with_fixed_window_carry_0": sum(values == {0} for values in by_round.values()),
            "rounds_with_fixed_window_carry_1": sum(values == {1} for values in by_round.values()),
            "rounds_with_variable_window_carry": sum(len(values) == 2 for values in by_round.values()),
            "rounds_with_variable_overflow": sum(
                len(values) == 2 for values in overflow_by_round.values()
            ),
            "observed_cleanup_mismatches": mismatches,
            "affine_full_inputs_by_arg_sign": affine,
        }

    first_one = next(row for row in rows if row[F_WINDOW_CARRY] == 1)
    first_zero = next(row for row in rows if row[F_WINDOW_CARRY] == 0)
    first_not_arg = next(row for row in rows if row[F_WINDOW_CARRY] != row[F_ARG])

    # Same local shell, opposite answer: this falsifies every predicate (not
    # merely affine ones) over these context and boundary-bit features.
    seen: dict[tuple[int, ...], tuple[int, ...]] = {}
    collision = None
    for row in rows:
        key = (
            row[F_DIR],
            row[F_ARG],
            row[F_ROUND] & 1,
            row[F_ACC] & 1,
            row[F_SOURCE] & 1,
            (row[F_ACC] >> (256 - compare - 1)) & 1,
            (row[F_SOURCE] >> (256 - compare - 1)) & 1,
            (row[F_ACC] >> (256 - compare)) & 1,
            (row[F_SOURCE] >> (256 - compare)) & 1,
            (row[F_ACC] >> 255) & 1,
            (row[F_SOURCE] >> 255) & 1,
        )
        prior = seen.get(key)
        if prior is not None and prior[F_WINDOW_CARRY] != row[F_WINDOW_CARRY]:
            collision = {"feature_tuple": list(key), "left": witness(prior), "right": witness(row)}
            break
        seen[key] = row
    if collision is None:
        raise AssertionError("expected a local-feature collision falsifier")

    output["falsifiers"] = {
        "fixed_zero": witness(first_one),
        "fixed_one": witness(first_zero),
        "equals_arg_sign": witness(first_not_arg),
        "same_local_features_opposite_carry": collision,
    }
    return output


def summarize_interior(rows: Sequence[tuple[int, ...]]) -> dict[str, object]:
    output: dict[str, object] = {}
    for direction, name in [(DIR_DIV, "divide"), (DIR_MUL, "multiply")]:
        selected = [row for row in rows if row[I_DIR] == direction]
        sites: dict[tuple[int, int], list[tuple[int, ...]]] = defaultdict(list)
        for row in selected:
            sites[(row[I_ROUND], row[I_CHUNK])].append(row)
        whole_window = [
            row for row in selected if row[I_CHUNK] == 0 and row[I_WIDTH] <= 22
        ]
        whole_sites: dict[tuple[int, int], list[tuple[int, ...]]] = defaultdict(list)
        for row in whole_window:
            whole_sites[(row[I_ROUND], row[I_CHUNK])].append(row)

        pooled_affine = {}
        for width in sorted({row[I_WIDTH] for row in whole_window}):
            group = [row for row in whole_window if row[I_WIDTH] == width]
            feature_count = 1 + 10 + 1 + 2 * width
            pooled_affine[str(width)] = affine_ranks(
                group,
                lambda row, width=width: 1
                | (row[I_ROUND] << 1)
                | (row[I_ARG] << 11)
                | (row[I_ADDEND] << 12)
                | (row[I_ACC] << (12 + width)),
                lambda row: row[I_CARRY_OUT],
                feature_count,
            )

        output[name] = {
            "cleanup_events": len(selected),
            "cleanup_sites_per_trajectory": len(sites),
            "window_carry_counts": dict(sorted(Counter(row[I_WINDOW_CARRY] for row in selected).items())),
            "boundary_carry_counts": dict(sorted(Counter(row[I_CARRY_OUT] for row in selected).items())),
            "observed_cleanup_mismatches": sum(
                row[I_PREDICTED] != row[I_CARRY_OUT] for row in selected
            ),
            "whole_window_leading_sites": len(whole_sites),
            "whole_window_entry_carry_nonzero": sum(
                row[I_WINDOW_CARRY] != 0 for row in whole_window
            ),
            "whole_window_sites_fixed_boundary_0": sum(
                {row[I_CARRY_OUT] for row in group} == {0}
                for group in whole_sites.values()
            ),
            "whole_window_sites_fixed_boundary_1": sum(
                {row[I_CARRY_OUT] for row in group} == {1}
                for group in whole_sites.values()
            ),
            "whole_window_sites_variable_boundary": sum(
                len({row[I_CARRY_OUT] for row in group}) == 2
                for group in whole_sites.values()
            ),
            "whole_window_boundary_affine_by_width": pooled_affine,
        }

    # Concrete same-shell witness for the fixed-input leading family: carry
    # entering its full comparator is zero in both rows, but its output differs.
    leading = [row for row in rows if row[I_CHUNK] == 0 and row[I_WIDTH] <= 22]
    seen: dict[tuple[int, ...], tuple[int, ...]] = {}
    collision = None
    for row in leading:
        key = (
            row[I_DIR],
            row[I_WIDTH],
            row[I_ARG],
            row[I_ROUND] & 1,
            row[I_ADDEND] & 3,
            row[I_ACC] & 3,
        )
        prior = seen.get(key)
        if prior is not None and prior[I_CARRY_OUT] != row[I_CARRY_OUT]:
            collision = {
                "feature_tuple": list(key),
                "left": {
                    "sample": prior[I_SAMPLE],
                    "round": prior[I_ROUND],
                    "width": prior[I_WIDTH],
                    "window_carry": prior[I_WINDOW_CARRY],
                    "boundary_carry": prior[I_CARRY_OUT],
                    "addend": hex(prior[I_ADDEND]),
                    "acc": hex(prior[I_ACC]),
                },
                "right": {
                    "sample": row[I_SAMPLE],
                    "round": row[I_ROUND],
                    "width": row[I_WIDTH],
                    "window_carry": row[I_WINDOW_CARRY],
                    "boundary_carry": row[I_CARRY_OUT],
                    "addend": hex(row[I_ADDEND]),
                    "acc": hex(row[I_ACC]),
                },
            }
            break
        seen[key] = row
    if collision is None:
        raise AssertionError("expected a leading-boundary collision falsifier")
    output["fixed_entry_does_not_delete_comparator"] = collision
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=64)
    args = parser.parse_args()
    if args.samples < 2:
        raise SystemExit("--samples must be at least 2")

    repo = Path(__file__).resolve().parents[4]
    tree = git(repo, "rev-parse", f"{PROMOTED_COMMIT}^{{tree}}")
    if tree != PROMOTED_TREE:
        raise RuntimeError(f"promoted tree drift: {tree}")
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", PROMOTED_COMMIT, "HEAD"],
        cwd=repo,
        check=True,
    )
    pingpong = promoted_text(repo, "src/point_add/pingpong_div.rs")
    point_add = promoted_text(repo, "src/point_add/mod.rs")
    schedule = parse_array(pingpong, "WIDTH_SCHEDULE", 700)
    repairs = set(parse_array(pingpong, "WIDTH_REPAIR", 100))
    route = parse_route_defaults(point_add)
    expected_route = {
        "SUB4_PP_ROUNDS": 696,
        "SUB4_PP_ROUNDS_MUL": 694,
        "SUB4_PP_R1": 335,
        "SUB4_PP_R1_MUL": 315,
        "SUB4_PP_R2": 645,
        "SUB4_PP_PEAK": 1267,
        "SUB4_PP_REPLAY_CHUNK_COMPARE": 22,
        "SUB4_PP_REPLAY_FLAG_COMPARE": 22,
        "SUB4_PP_REPLAY_FOLD_WINDOW": 54,
        "SUB4_PP_REPLAY_FOLD_WINDOW_MUL": 53,
        "SUB4_PP_ENDPOINT_FOLD_WINDOW": 26,
        "SUB4_PP_SIGNED_FRAME": 0,
    }
    if route != expected_route:
        raise RuntimeError(f"unexpected promoted route: {route}")

    layouts: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for direction, rounds in [
        (DIR_DIV, route["SUB4_PP_ROUNDS"]),
        (DIR_MUL, route["SUB4_PP_ROUNDS_MUL"]),
    ]:
        for round_index in range(2, rounds):
            budget = ladder_budget(direction, round_index, route, schedule, repairs)
            layouts[(direction, round_index)] = chunk_layout(
                256, budget, route["SUB4_PP_REPLAY_CHUNK_COMPARE"]
            )

    final_events: list[tuple[int, ...]] = []
    interior_events: list[tuple[int, ...]] = []
    admitted = Counter()
    rejected = Counter()
    for sample in range(args.samples):
        target_point = ec_mul(deterministic_scalar(sample, b"target"))
        offset_point = ec_mul(deterministic_scalar(sample, b"offset"))
        if target_point[0] == offset_point[0]:
            rejected["degenerate_ec_pair"] += 1
            continue
        dx = (target_point[0] - offset_point[0]) % P
        dy = (target_point[1] - offset_point[1]) % P
        slope = dy * pow(dx, -1, P) % P
        result_x = (slope * slope - target_point[0] - offset_point[0]) % P
        multiply_denominator = (offset_point[0] - result_x) % P

        for direction, denominator, numerator, rounds in [
            (DIR_DIV, dx, dy, route["SUB4_PP_ROUNDS"]),
            (DIR_MUL, multiply_denominator, slope, route["SUB4_PP_ROUNDS_MUL"]),
        ]:
            transcript = walk_transcript(
                denominator,
                rounds,
                schedule,
                repairs,
                route["SUB4_PP_REPLAY_FOLD_WINDOW"],
                route["SUB4_PP_ENDPOINT_FOLD_WINDOW"],
            )
            name = "divide" if direction == DIR_DIV else "multiply"
            if transcript is None:
                rejected[f"{name}_walk_gate"] += 1
                continue
            terminal_u, terminal_v, tape = transcript
            replay = (
                replay_divide(
                    sample,
                    denominator,
                    numerator,
                    terminal_u,
                    terminal_v,
                    tape,
                    layouts,
                    route,
                )
                if direction == DIR_DIV
                else replay_multiply(
                    sample,
                    denominator,
                    numerator,
                    terminal_u,
                    terminal_v,
                    tape,
                    layouts,
                    route,
                )
            )
            if replay is None:
                rejected[f"{name}_coefficient_endpoint"] += 1
                continue
            local_final, local_interior = replay
            final_events.extend(local_final)
            interior_events.extend(local_interior)
            admitted[name] += 1

    if admitted["divide"] < 2 or admitted["multiply"] < 2:
        raise RuntimeError("too few admitted trajectories for a census")

    report = {
        "verdict": "HARD_NACK_FIXED_OR_AFFINE_FAMILY_DELETION",
        "scope": {
            "base_commit": PROMOTED_COMMIT,
            "base_tree": PROMOTED_TREE,
            "head": git(repo, "rev-parse", "HEAD"),
            "pingpong_sha256": hashlib.sha256(pingpong.encode()).hexdigest(),
            "point_add_mod_sha256": hashlib.sha256(point_add.encode()).hexdigest(),
            "route": route,
            "requested_ec_pairs": args.samples,
            "admitted_trajectories": dict(admitted),
            "rejected_trajectories": dict(rejected),
            "model_boundary": (
                "literal promoted value arithmetic for fused walk rounds 0/1, signed walk, "
                "chunked adds, truncated folds, and canonical replay; width/terminal/"
                "coefficient endpoints gated; measurement-conditioned phase not simulated"
            ),
        },
        "final_top_cleanup": summarize_final(
            final_events, route["SUB4_PP_REPLAY_FLAG_COMPARE"]
        ),
        "interior_chunk_cleanup": summarize_interior(interior_events),
        "interpretation": {
            "holds": (
                "For leading chunk 0 with width <= 22, the comparison window spans "
                "the whole chunk and its exact entering carry is source-proven 0."
            ),
            "falsified": (
                "The final-window entering carry is neither fixed nor affine over the "
                "complete observed add inputs; the fixed-entry leading boundary output "
                "is also variable and has no pooled affine fit at any observed width."
            ),
            "family_priority": (
                "Do not implement an entire final or interior comparator/carry-family "
                "deletion from this lane. Fixed input carry makes 547 leading repairs "
                "exact, but does not make their cleanup predicate removable."
            ),
            "next_gate": (
                "One reduced-width symbolic miter for the highest-volume divide width-2 "
                "leading-boundary family; require a source-level affine output identity "
                "before any production edit or count gate."
            ),
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
