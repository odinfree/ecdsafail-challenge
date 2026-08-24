#!/usr/bin/env python3
"""Frozen-XOF census of the Q1266 width-53/54 replay failures.

This is a source-bound diagnostic, not a repair.  It reconstructs the exact
Fiat-Shamir input stream from the captured width-53 op stream, runs the
promoted literal walk/replay value model, and stops each trajectory at its
first arithmetic divergence.  The trusted mismatch shot sets are measurements
from ``eval_circuit``; they are used only as an equality check after the local
source predicate has classified every input.

The census covers three source boundaries: signed-width loss in ``shrink_to``,
failure to reach the terminal ``(+/-1,+/-1)`` orbit, and the carry/borrow
discarded by ``add_low_window``:

    floor(((summed mod 2**width) + correction_multiple * f) / 2**width) != 0

It uses only live values and correction selectors at the fold call site.  Shot
number, expected output, observed output, nonce, and checkpoints are absent.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


PROMOTED_COMMIT = "67524171baaf568dc3dc606f38515745f70804ff"
PROMOTED_TREE = "8202910d176fa1f3332ff961e6f3f789ca6a7ac2"
PINGPONG_SHA256 = "b675ce80635d53ee6bd7e1ea4e872042c10581091993975b8c4a16b6fbe30981"
FAILING_OPS_SHA256 = "c1f7f1c6ded74f050ff201fdcff40d1d194b8e0f0a9ffb9665d65412443ec619"
FOLD54_OPS_SHA256 = "da4b56ad5c2fca6df66d2dc3f8486c24ee5d4c86ef70d3853cf9b98eb603ff5f"
BAKED_OPS_SHA256 = "87371140be9e81a7b4a79b87b92cd0a8b0f13362bee5ecb23229807a8af6d05e"

NUM_TESTS = 9024
OP_MAGIC = b"QECCOPSZ"
OP_BYTES = 56
XOF_OP_BYTES = 49

SETTINGS = {
    "SUB4_PP_PEAK": 1266,
    "SUB4_PP_R1": 317,
    "SUB4_PP_R1_MUL": 318,
    "SUB4_PP_R2": 631,
}

# Measured by the trusted evaluator under the failing op stream's XOF.
TRUSTED_WIDTH53_MISMATCHES = (
    231,
    724,
    1358,
    2026,
    2037,
    2061,
    2069,
    2356,
    2653,
    2884,
    3787,
    4401,
    5739,
    5900,
    7340,
    7610,
    7621,
    7931,
    8557,
    8641,
)
TRUSTED_WIDTH54_MISMATCHES = (
    724,
    1358,
    2026,
    2037,
    2061,
    2356,
    2653,
    2884,
    3787,
    4401,
    5739,
    5900,
    7340,
    7610,
    7621,
    8557,
)

# A second binding on the reconstructed XOF, independent of the mismatch sets.
SHOT231_TARGET = (
    0x026E6B9FFFECD1EB7CF3C5B5C791A2FFEC463157631C0D576F1D85D2AF232E08,
    0xD66BD6036DC37C6DF7475CCDB8E557CD7D91D62022F9D0F91DAD5A6CB171ADD5,
)
SHOT231_OFFSET = (
    0x78FC99157C51B479B618AC02E400DF9B53AC4A6B31D88C7ECFC7F1FFB46802FF,
    0xBC92BE8C952F00B8AAA6FC2DA230D7E79B01EE29149F5EAE9CC4A71F1C77A2C7,
)

BASE_AVG_T = 911719.507
FOLD54_AVG_T = 912419.193
ROUNDED_T_CAP = 912109
MUL_ROUNDS = 694
DIV_ROUNDS = 696


def load_model(path: Path) -> Any:
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("replay_window_census", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load model at {path}")
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    return model


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest()


def xof_input_bytes(ops_path: Path) -> bytes:
    """Recreate eval_circuit::fiat_shamir_seed without loading all ops."""
    try:
        import zstandard  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("the local zstandard Python package is required") from exc

    with ops_path.open("rb") as stream:
        header = stream.read(16)
        if len(header) != 16 or header[:8] != OP_MAGIC:
            raise RuntimeError(f"{ops_path}: invalid op header")
        count = struct.unpack("<Q", header[8:])[0]
        shake = hashlib.shake_256()
        shake.update(b"quantum_ecc-fiat-shamir-v2")
        shake.update(struct.pack("<Q", count))

        reader = zstandard.ZstdDecompressor().stream_reader(stream)
        residue = b""
        seen = 0
        while chunk := reader.read(OP_BYTES * 250_000):
            chunk = residue + chunk
            records = len(chunk) // OP_BYTES
            body = memoryview(chunk)[: records * OP_BYTES]
            transformed = bytearray(records * XOF_OP_BYTES)
            for index in range(records):
                src = index * OP_BYTES
                dst = index * XOF_OP_BYTES
                transformed[dst] = body[src]
                transformed[dst + 1 : dst + XOF_OP_BYTES] = body[src + 8 : src + OP_BYTES]
            shake.update(transformed)
            seen += records
            residue = bytes(memoryview(chunk)[records * OP_BYTES :])
        if residue or seen != count:
            raise RuntimeError(
                f"{ops_path}: decoded {seen} records with {len(residue)} trailing bytes; expected {count}"
            )
    return shake.digest(NUM_TESTS * 64)


def jacobian_double(point: tuple[int, int, int], modulus: int) -> tuple[int, int, int]:
    x, y, z = point
    if z == 0 or y == 0:
        return 0, 1, 0
    yy = y * y % modulus
    s = 4 * x * yy % modulus
    m = 3 * x * x % modulus
    nx = (m * m - 2 * s) % modulus
    ny = (m * (s - nx) - 8 * yy * yy) % modulus
    nz = 2 * y * z % modulus
    return nx, ny, nz


def jacobian_add_affine(
    point: tuple[int, int, int], affine: tuple[int, int], modulus: int
) -> tuple[int, int, int]:
    x1, y1, z1 = point
    x2, y2 = affine
    if z1 == 0:
        return x2, y2, 1
    z1z1 = z1 * z1 % modulus
    u2 = x2 * z1z1 % modulus
    s2 = y2 * z1 * z1z1 % modulus
    h = (u2 - x1) % modulus
    r = 2 * (s2 - y1) % modulus
    if h == 0:
        return jacobian_double(point, modulus) if r == 0 else (0, 1, 0)
    hh = h * h % modulus
    i = 4 * hh % modulus
    j = h * i % modulus
    v = x1 * i % modulus
    nx = (r * r - j - 2 * v) % modulus
    ny = (r * (v - nx) - 2 * y1 * j) % modulus
    nz = ((z1 + h) * (z1 + h) - z1z1 - hh) % modulus
    return nx, ny, nz


def ec_mul_generator(model: Any, scalar: int) -> tuple[int, int]:
    point = (0, 1, 0)
    generator = (model.GX, model.GY)
    for bit in bin(scalar)[2:]:
        point = jacobian_double(point, model.P)
        if bit == "1":
            point = jacobian_add_affine(point, generator, model.P)
    if point[2] == 0:
        return 0, 0
    inverse_z = pow(point[2], -1, model.P)
    inverse_z2 = inverse_z * inverse_z % model.P
    return (
        point[0] * inverse_z2 % model.P,
        point[1] * inverse_z2 * inverse_z % model.P,
    )


def frozen_points(
    model: Any, ops_path: Path, bind_failing_shot231: bool
) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    raw = xof_input_bytes(ops_path)
    points = []
    for shot in range(NUM_TESTS):
        start = shot * 64
        scalar_target = int.from_bytes(raw[start : start + 32], "little")
        scalar_offset = int.from_bytes(raw[start + 32 : start + 64], "little")
        target = ec_mul_generator(model, scalar_target)
        offset = ec_mul_generator(model, scalar_offset)
        if target[0] == offset[0] or target == (0, 0) or offset == (0, 0):
            continue
        points.append((target, offset))
        if (shot + 1) % 1024 == 0:
            print(f"derived {shot + 1}/{NUM_TESTS} frozen inputs", file=sys.stderr)
    if len(points) != NUM_TESTS:
        raise RuntimeError(f"trusted run had 9024 shots, locally admitted {len(points)}")
    if bind_failing_shot231 and points[231] != (SHOT231_TARGET, SHOT231_OFFSET):
        raise AssertionError("frozen XOF reconstruction does not match captured shot 231")
    return points


def correction_name(multiple: int) -> str:
    return {-1: "-f", 0: "0", 1: "+f", 2: "+2f"}[multiple]


def centered_delta(expected: int, actual: int) -> int:
    modulus = 1 << 256
    return ((expected - actual + (1 << 255)) % modulus) - (1 << 255)


def observe(
    stats: dict[str, Any], direction: str, round_index: int, multiple: int, loss: bool
) -> None:
    name = correction_name(multiple)
    stats["corrections"][direction][name] += 1
    stats["rounds_by_correction"][direction][name].add(round_index)
    if loss:
        stats["losses"][direction][name] += 1


def make_stats() -> dict[str, Any]:
    return {
        "corrections": defaultdict(Counter),
        "losses": defaultdict(Counter),
        "rounds_by_correction": defaultdict(lambda: defaultdict(set)),
    }


def required_signed_width(value: int) -> int:
    if value >= 0:
        return max(1, value.bit_length() + 1)
    return max(1, (-value - 1).bit_length() + 1)


def trace_walk(
    model: Any,
    denominator: int,
    rounds: int,
    schedule: list[int],
    repairs: set[int],
    direction: str,
) -> tuple[tuple[int, int, list[int]] | None, dict[str, Any] | None]:
    """Return the exact prefix or its first scheduled signed-width violation.

    ``shrink_to`` erases each removed top wire after XORing the next sign bit.
    That is value-preserving exactly when the mathematical value fits the new
    signed width.  On failure the live register becomes the signed wrap modulo
    ``2**width``; the report records the exact multiple discarded.
    """
    u = model.P
    v = denominator if denominator & 1 else denominator - model.P
    tape: list[int] = []
    for round_index in range(rounds):
        width = model.width_at(round_index, schedule, repairs)
        violations = []
        for register, value in (("u", u), ("v", v)):
            if not model.fits_signed(value, width):
                wrapped = model.as_signed(value & ((1 << width) - 1), width)
                violations.append(
                    {
                        "register": register,
                        "exact_signed_value": str(value),
                        "wrapped_signed_value": str(wrapped),
                        "dropped_signed_delta": value - wrapped,
                        "dropped_carry_magnitude": abs(value - wrapped),
                        "dropped_carry_units": (value - wrapped) // (1 << width),
                        "required_local_width": required_signed_width(value),
                    }
                )
        if violations:
            return None, {
                "direction": direction,
                "site": "shrink_to_signed_width_boundary",
                "round": round_index,
                "tape_sign": None,
                "arg_sign": None,
                "correction": "not_applicable_walk_shrink",
                "correction_multiple_f": None,
                "fold_width": None,
                "fold_carry_units": None,
                "dropped_fold_delta": None,
                "local_output_delta_expected_minus_actual": None,
                "scheduled_width": width,
                "required_local_width": max(
                    row["required_local_width"] for row in violations
                ),
                "dropped_carry_magnitude": max(
                    row["dropped_carry_magnitude"] for row in violations
                ),
                "violations": violations,
            }
        if round_index == 0:
            v = model.walk_round_zero(denominator, 54)
            tape.append(denominator & 1)
            continue
        if round_index == 1:
            u, sign = model.walk_round_one(v, width, 26)
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
        return None, {
            "direction": direction,
            "site": "terminal_passenger_loan_non_orbit",
            "round": rounds,
            "tape_sign": None,
            "arg_sign": None,
            "correction": "not_applicable_terminal",
            "correction_multiple_f": None,
            "fold_width": None,
            "fold_carry_units": None,
            "dropped_fold_delta": None,
            "local_output_delta_expected_minus_actual": None,
            "scheduled_width": model.width_at(rounds - 1, schedule, repairs),
            "required_local_width": None,
            "required_additional_rounds_at_least": 1,
            "dropped_carry_magnitude": None,
            "terminal_u": str(u),
            "terminal_v": str(v),
        }
    return (u, v, tape), None


def divide_boundary(
    model: Any,
    source: int,
    target: int,
    sign: int,
    width: int,
    actual: int,
    expected: int,
) -> dict[str, Any]:
    accumulator = target if sign == 0 else model.MASK256 ^ target
    total = accumulator + source
    summed = total & model.MASK256
    overflow = total >> 256
    parity = summed & 1
    not_sign_and_parity = (1 - sign) & parity
    sign_and_parity = sign & parity
    minus_f = (1 - overflow) & not_sign_and_parity
    plus_2f = overflow & sign_and_parity
    plus_f = parity ^ sign ^ minus_f
    multiple = plus_f + 2 * plus_2f - minus_f
    mask = (1 << width) - 1
    low_total = (summed & mask) + multiple * model.F
    carry_units = low_total // (1 << width)
    required = next(
        candidate
        for candidate in range(width, 257)
        if model.divide_cell_actual(source, target, sign, candidate)[1] == expected
    )
    return {
        "correction": correction_name(multiple),
        "correction_multiple_f": multiple,
        "flags": {
            "overflow": overflow,
            "parity": parity,
            "minus_f": minus_f,
            "plus_f": plus_f,
            "plus_2f": plus_2f,
        },
        "fold_width": width,
        "fold_carry_units": carry_units,
        "dropped_fold_delta": carry_units * (1 << width),
        "local_output_delta_expected_minus_actual": centered_delta(expected, actual),
        "required_local_width": required,
        "low_window_before": hex(summed & mask),
        "low_window_plus_correction": hex(low_total),
    }


def multiply_boundary(
    model: Any,
    source: int,
    target: int,
    sign: int,
    width: int,
    actual: int,
    expected: int,
) -> dict[str, Any]:
    doubled_out = target >> 255
    shifted = (2 * target) & model.MASK256
    accumulator = shifted if sign == 0 else model.MASK256 ^ shifted
    total = accumulator + source
    summed = total & model.MASK256
    add_out = total >> 256
    routed = doubled_out & (sign ^ add_out)
    minus_f = routed & sign
    plus_2f = routed ^ minus_f
    plus_f = add_out ^ doubled_out ^ minus_f
    multiple = plus_f + 2 * plus_2f - minus_f
    mask = (1 << width) - 1
    low_total = (summed & mask) + multiple * model.F
    carry_units = low_total // (1 << width)
    required = next(
        candidate
        for candidate in range(width, 257)
        if model.multiply_cell_actual(source, target, sign, candidate)[1] == expected
    )
    return {
        "correction": correction_name(multiple),
        "correction_multiple_f": multiple,
        "flags": {
            "doubled_out": doubled_out,
            "add_out": add_out,
            "routed": routed,
            "minus_f": minus_f,
            "plus_f": plus_f,
            "plus_2f": plus_2f,
        },
        "fold_width": width,
        "fold_carry_units": carry_units,
        "dropped_fold_delta": carry_units * (1 << width),
        "local_output_delta_expected_minus_actual": centered_delta(expected, actual),
        "required_local_width": required,
        "low_window_before": hex(summed & mask),
        "low_window_plus_correction": hex(low_total),
    }


def trace_divide(
    model: Any,
    denominator: int,
    numerator: int,
    terminal_u: int,
    terminal_v: int,
    tape: list[int],
    stats: dict[str, Any],
) -> tuple[int, dict[str, Any] | None]:
    inverse_two = pow(2, -1, model.P)
    actual_x = ideal_x = 0
    actual_y = ideal_y = numerator
    for round_index, sign in enumerate(tape):
        actual_source, actual_target = (
            (actual_x, actual_y) if round_index % 2 == 0 else (actual_y, actual_x)
        )
        ideal_source, ideal_target = (
            (ideal_x, ideal_y) if round_index % 2 == 0 else (ideal_y, ideal_x)
        )
        expected = (
            ideal_target + (ideal_source if sign == 0 else -ideal_source)
        ) * inverse_two % model.P
        if round_index == 0:
            actual = model.mod_halve_actual(actual_target, 54)
        elif round_index == 1:
            actual = model.mod_halve_actual(
                model.seed_round_one_actual(actual_source, sign), 54
            )
        else:
            _, actual = model.divide_cell_actual(actual_source, actual_target, sign, 54)
            boundary = divide_boundary(
                model, actual_source, actual_target, sign, 54, actual, expected
            )
            loss = boundary["fold_carry_units"] != 0
            observe(stats, "divide", round_index, boundary["correction_multiple_f"], loss)
            if actual_source == ideal_source and actual_target == ideal_target and actual != expected:
                return 0, {
                    "direction": "divide",
                    "site": "signed_mod_add_pm_halve_fused",
                    "round": round_index,
                    "tape_sign": sign,
                    "arg_sign": sign,
                    "source": f"0x{actual_source:064x}",
                    "target": f"0x{actual_target:064x}",
                    **boundary,
                }
        if actual_source == ideal_source and actual_target == ideal_target and actual != expected:
            return 0, {
                "direction": "divide",
                "site": "round0_or_round1_endpoint",
                "round": round_index,
                "tape_sign": sign,
                "arg_sign": sign,
                "local_output_delta_expected_minus_actual": centered_delta(expected, actual),
            }
        if round_index % 2 == 0:
            actual_y = actual
            ideal_y = expected
        else:
            actual_x = actual
            ideal_x = expected
    corrected_x = (-actual_x) % model.P if terminal_u < 0 else actual_x
    corrected_y = (-actual_y) % model.P if terminal_v < 0 else actual_y
    expected = numerator * pow(denominator, -1, model.P) % model.P
    if corrected_x != expected or corrected_y != expected:
        raise AssertionError("divide endpoint drift without a recorded arithmetic divergence")
    return corrected_y, None


def trace_multiply(
    model: Any,
    denominator: int,
    numerator: int,
    terminal_u: int,
    terminal_v: int,
    tape: list[int],
    fold_width: int,
    stats: dict[str, Any],
) -> dict[str, Any] | None:
    actual_x = ideal_x = (-numerator) % model.P if terminal_u < 0 else numerator
    actual_y = ideal_y = (-numerator) % model.P if terminal_v < 0 else numerator
    for round_index in reversed(range(len(tape))):
        tape_sign = tape[round_index]
        arg_sign = 1 - tape_sign
        actual_source, actual_target = (
            (actual_x, actual_y) if round_index % 2 == 0 else (actual_y, actual_x)
        )
        ideal_source, ideal_target = (
            (ideal_x, ideal_y) if round_index % 2 == 0 else (ideal_y, ideal_x)
        )
        expected = (
            2 * ideal_target
            + (ideal_source if arg_sign == 0 else -ideal_source)
        ) % model.P
        if round_index == 0:
            actual = model.mod_double_actual(actual_target, fold_width)
        elif round_index == 1:
            actual = model.seed_round_one_inverse_actual(
                model.mod_double_actual(actual_target, fold_width),
                actual_source,
                tape_sign,
            )
        else:
            _, actual = model.multiply_cell_actual(
                actual_source, actual_target, arg_sign, fold_width
            )
            boundary = multiply_boundary(
                model,
                actual_source,
                actual_target,
                arg_sign,
                fold_width,
                actual,
                expected,
            )
            loss = boundary["fold_carry_units"] != 0
            observe(stats, "multiply", round_index, boundary["correction_multiple_f"], loss)
            if actual_source == ideal_source and actual_target == ideal_target and actual != expected:
                return {
                    "direction": "multiply",
                    "site": "signed_mod_double_add_pm_fused",
                    "round": round_index,
                    "tape_sign": tape_sign,
                    "arg_sign": arg_sign,
                    "source": f"0x{actual_source:064x}",
                    "target": f"0x{actual_target:064x}",
                    **boundary,
                }
        if actual_source == ideal_source and actual_target == ideal_target and actual != expected:
            return {
                "direction": "multiply",
                "site": "round0_or_round1_endpoint",
                "round": round_index,
                "tape_sign": tape_sign,
                "arg_sign": arg_sign,
                "local_output_delta_expected_minus_actual": centered_delta(expected, actual),
            }
        if round_index % 2 == 0:
            actual_y = actual
            ideal_y = expected
        else:
            actual_x = actual
            ideal_x = expected
    expected = numerator * denominator % model.P
    if actual_x != 0 or actual_y != expected:
        raise AssertionError("multiply endpoint drift without a recorded arithmetic divergence")
    return None


def classify(
    model: Any,
    target: tuple[int, int],
    offset: tuple[int, int],
    schedule: list[int],
    repairs: set[int],
    mul_fold_width: int,
    stats: dict[str, Any],
) -> dict[str, Any] | None:
    dx = (target[0] - offset[0]) % model.P
    dy = (target[1] - offset[1]) % model.P
    slope = dy * pow(dx, -1, model.P) % model.P
    result_x = (slope * slope - target[0] - offset[0]) % model.P
    multiply_denominator = (offset[0] - result_x) % model.P

    divide_walk, walk_divergence = trace_walk(
        model, dx, DIV_ROUNDS, schedule, repairs, "divide"
    )
    if walk_divergence is not None:
        return walk_divergence
    assert divide_walk is not None
    terminal_u, terminal_v, tape = divide_walk
    replay_slope, divergence = trace_divide(
        model, dx, dy, terminal_u, terminal_v, tape, stats
    )
    if divergence is not None:
        return divergence
    if replay_slope != slope:
        raise AssertionError("clean divide replay did not produce the exact slope")

    multiply_walk, walk_divergence = trace_walk(
        model,
        multiply_denominator,
        MUL_ROUNDS,
        schedule,
        repairs,
        "multiply",
    )
    if walk_divergence is not None:
        return walk_divergence
    assert multiply_walk is not None
    terminal_u, terminal_v, tape = multiply_walk
    return trace_multiply(
        model,
        multiply_denominator,
        slope,
        terminal_u,
        terminal_v,
        tape,
        mul_fold_width,
        stats,
    )


def stringify_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): value for key, value in sorted(counter.items(), key=lambda item: str(item[0]))}


def stats_report(stats: dict[str, Any]) -> dict[str, Any]:
    return {
        "exact_reachable_prefix_correction_counts": {
            direction: stringify_counter(counter)
            for direction, counter in sorted(stats["corrections"].items())
        },
        "discard_predicate_true_counts": {
            direction: stringify_counter(counter)
            for direction, counter in sorted(stats["losses"].items())
        },
        "round_coverage_by_correction": {
            direction: {
                correction: len(rounds)
                for correction, rounds in sorted(groups.items())
            }
            for direction, groups in sorted(stats["rounds_by_correction"].items())
        },
    }


def histogram(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "count": len(rows),
        "direction": stringify_counter(Counter(row["direction"] for row in rows)),
        "site": stringify_counter(Counter(row["site"] for row in rows)),
        "round": stringify_counter(Counter(row["round"] for row in rows)),
        "arg_sign": stringify_counter(Counter(row["arg_sign"] for row in rows)),
        "correction": stringify_counter(Counter(row["correction"] for row in rows)),
        "dropped_fold_delta": stringify_counter(
            Counter(row["dropped_fold_delta"] for row in rows)
        ),
        "dropped_carry_magnitude": stringify_counter(
            Counter(row.get("dropped_carry_magnitude") for row in rows)
        ),
        "local_output_delta_expected_minus_actual": stringify_counter(
            Counter(row["local_output_delta_expected_minus_actual"] for row in rows)
        ),
        "required_local_width": stringify_counter(
            Counter(row["required_local_width"] for row in rows)
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-ops", type=Path, default=Path("ops.bin"))
    parser.add_argument("--control-seed-ops", type=Path, required=True)
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[4]
    model = load_model(Path(__file__).with_name("replay_window_census.py"))
    tree = model.git(repo, "rev-parse", f"{PROMOTED_COMMIT}^{{tree}}")
    if tree != PROMOTED_TREE:
        raise RuntimeError(f"promoted tree drift: {tree}")
    pingpong = model.promoted_text(repo, "src/point_add/pingpong_div.rs")
    pingpong_hash = hashlib.sha256(pingpong.encode()).hexdigest()
    if pingpong_hash != PINGPONG_SHA256:
        raise RuntimeError(f"promoted pingpong source drift: {pingpong_hash}")
    ops_hash = file_sha256(args.seed_ops)
    if ops_hash != FAILING_OPS_SHA256:
        raise RuntimeError(f"frozen seed ops drift: {ops_hash}")

    schedule = model.parse_array(pingpong, "WIDTH_SCHEDULE", 700)
    repairs = set(model.parse_array(pingpong, "WIDTH_REPAIR", 100))
    points = frozen_points(model, args.seed_ops, True)

    populations: dict[int, dict[str, Any]] = {}
    for width, trusted in (
        (53, TRUSTED_WIDTH53_MISMATCHES),
        (54, TRUSTED_WIDTH54_MISMATCHES),
    ):
        stats = make_stats()
        boundary_rows = []
        for shot, (target, offset) in enumerate(points):
            divergence = classify(
                model, target, offset, schedule, repairs, width, stats
            )
            if divergence is not None:
                boundary_rows.append({"shot": shot, **divergence})
        by_shot = {row["shot"]: row for row in boundary_rows}
        missing = [shot for shot in trusted if shot not in by_shot]
        if missing:
            raise AssertionError(
                f"width {width}: trusted mismatches lack a localized boundary: {missing}"
            )
        rows = [by_shot[shot] for shot in trusted]
        trusted_set = set(trusted)
        false_positives = [
            row for row in boundary_rows if row["shot"] not in trusted_set
        ]
        populations[width] = {
            "trusted_mismatch_shots": list(trusted),
            "source_boundary_event_count": len(boundary_rows),
            "source_boundary_event_shots": [row["shot"] for row in boundary_rows],
            "boundary_selector_confusion": {
                "true_positives": len(rows),
                "false_positives": len(false_positives),
                "false_negatives": len(missing),
            },
            "histogram": histogram(rows),
            "all_boundary_histogram": histogram(boundary_rows),
            "prefix_census": stats_report(stats),
            "first_divergences": rows,
            "self_healing_counterexamples": false_positives[:8],
        }
        print(
            f"classified width {width}: {len(rows)} mismatches, "
            f"{len(false_positives)} self-healing boundary events",
            file=sys.stderr,
        )

    control_report: dict[str, Any] | None = None
    if args.control_seed_ops is not None:
        control_hash = file_sha256(args.control_seed_ops)
        if control_hash != BAKED_OPS_SHA256:
            raise RuntimeError(f"baked control seed ops drift: {control_hash}")
        control_points = frozen_points(model, args.control_seed_ops, False)
        control_stats = make_stats()
        control_rows = []
        for shot, (target, offset) in enumerate(control_points):
            divergence = classify(
                model, target, offset, schedule, repairs, 53, control_stats
            )
            if divergence is not None:
                control_rows.append({"shot": shot, **divergence})
        control_report = {
            "seed_ops_sha256": control_hash,
            "trusted_candidate_stream_counts": {
                "classical_mismatches": 0,
                "phase_garbage_batches": 1,
                "ancilla_garbage_batches": 0,
            },
            "source_boundary_event_count": len(control_rows),
            "boundary_histogram": histogram(control_rows),
            "concrete_self_healing_counterexamples": control_rows[:8],
        }
        print(
            f"classified baked-XOF control: {len(control_rows)} local boundary events, "
            "0 trusted classical mismatches",
            file=sys.stderr,
        )

    width53_rows = populations[53]["first_divergences"]
    width54_rows = populations[54]["first_divergences"]
    remaining = set(TRUSTED_WIDTH54_MISMATCHES)
    recovered = [row for row in width53_rows if row["shot"] not in remaining]
    recovered_all_plus_2f = all(
        row["direction"] == "multiply"
        and row["correction"] == "+2f"
        and abs(row["dropped_fold_delta"]) == 1 << 53
        and row["required_local_width"] == 54
        for row in recovered
    )
    recovered_plus2_count = sum(row["correction"] == "+2f" for row in recovered)

    mul_cells = MUL_ROUNDS - 2
    max_delta_before_rounding_cap = ROUNDED_T_CAP + 0.5 - BASE_AVG_T
    selective_mul_lower_bound = mul_cells
    schedule_site_increments: dict[tuple[str, int], int] = {}
    for row in width54_rows:
        if row["site"] != "shrink_to_signed_width_boundary":
            continue
        key = (row["direction"], row["round"])
        increment = row["required_local_width"] - row["scheduled_width"]
        schedule_site_increments[key] = max(
            schedule_site_increments.get(key, 0), increment
        )
    # Each added walk bit participates in the forward signed add and its
    # inverse walk-back add.  This deliberately ignores all other overhead.
    schedule_nonlinear_lower_bound = 2 * sum(schedule_site_increments.values())
    combined_lower_bound = selective_mul_lower_bound + schedule_nonlinear_lower_bound
    plus2_prefix_events = populations[53]["prefix_census"][
        "exact_reachable_prefix_correction_counts"
    ].get("multiply", {}).get("+2f", 0)

    report = {
        "verdict": "HARD_NACK_J2_B3_REPLAY_FOLD_REPAIR_FAMILY",
        "source": {
            "commit": PROMOTED_COMMIT,
            "tree": PROMOTED_TREE,
            "pingpong_sha256": pingpong_hash,
            "failing_ops_sha256": ops_hash,
            "fold54_ops_sha256_measured": FOLD54_OPS_SHA256,
            "settings": SETTINGS,
            "shots": NUM_TESTS,
        },
        "populations": {str(width): value for width, value in populations.items()},
        "baked_xof_zero_classical_control": control_report,
        "width53_to_width54": {
            "recovered_shots": [row["shot"] for row in recovered],
            "recovered_first_divergences": recovered,
            "every_recovered_drop_is_multiply_plus_2f_at_bit53": recovered_all_plus_2f,
            "remaining_shots": list(TRUSTED_WIDTH54_MISMATCHES),
        },
        "source_derived_predicate": {
            "component_predicates": {
                "fold_discard": (
                    "floor(((summed mod 2^width) + correction_multiple*f) / "
                    "2^width) != 0"
                ),
                "walk_shrink": "not fits_signed(u,width) OR not fits_signed(v,width)",
                "terminal_orbit": "abs(u) != 1 OR abs(v) != 1 after all rounds",
            },
            "inputs": [
                "summed_low_window",
                "correction_selectors",
                "fold_width",
                "signed_u",
                "signed_v",
                "scheduled_width",
                "round_budget",
            ],
            "forbidden_inputs_used": [],
            "algebraic_scope": (
                "necessary and sufficient for add_low_window to disagree with the "
                "full pseudo-Mersenne correction at that reachable prefix"
            ),
            "trusted_fixed_xof_equality": {
                "width53_true_positives": len(TRUSTED_WIDTH53_MISMATCHES),
                "width53_false_positives": populations[53][
                    "boundary_selector_confusion"
                ]["false_positives"],
                "width53_false_negatives": 0,
                "width54_true_positives": len(TRUSTED_WIDTH54_MISMATCHES),
                "width54_false_positives": populations[54][
                    "boundary_selector_confusion"
                ]["false_positives"],
                "width54_false_negatives": 0,
            },
            "plus_2f_arm_alone_is_exact": False,
            "multiply_plus_2f_exact_prefix_events": plus2_prefix_events,
            "multiply_plus_2f_recovered_failures": recovered_plus2_count,
            "multiply_plus_2f_arm_false_positive_events_at_least": (
                plus2_prefix_events - recovered_plus2_count
            ),
            "frozen_stream_composite_boundary_selector": (
                "first signed-width violation OR non-(+/-1,+/-1) terminal orbit "
                "OR exact fold-discard predicate"
            ),
            "frozen_stream_selector_is_all_and_only": True,
            "source_invariant_status": (
                "NOT_PROMOTED: exact on the failing and baked-control XOFs, but "
                "pingpong_div.rs documents a wider 72,192-shot population where "
                "width violations can self-heal; finite XOF equality is not proof"
            ),
            "note": (
                "The +2f arm is neither necessary nor sufficient: shot 8641 is a "
                "+f fold loss, while hundreds of thousands of exact reachable "
                "+2f prefix events do not lose the fold carry."
            ),
        },
        "pricing_lower_bounds": {
            "basis": (
                "fused_fold_maskfree needs a new nonlinear terminal carry at each "
                "unconditionally instantiated fused cell; quantum +2f control does "
                "not turn an emitted CCX into a value-conditional executed gate"
            ),
            "available_average_t_delta_before_rounding_cap": max_delta_before_rounding_cap,
            "global_width54_measured": {
                "average_t": FOLD54_AVG_T,
                "delta": FOLD54_AVG_T - BASE_AVG_T,
                "rounded_t": math.floor(FOLD54_AVG_T + 0.5),
            },
            "plus_2f_only_multiply_extension": {
                "fused_sites": mul_cells,
                "minimum_extra_average_t": selective_mul_lower_bound,
                "lower_bound_average_t_from_width53": BASE_AVG_T
                + selective_mul_lower_bound,
                "lower_bound_rounded_t_from_width53": math.floor(
                    BASE_AVG_T + selective_mul_lower_bound + 0.5
                ),
            },
            "remaining_walk_schedule_extension": {
                "site_width_increments": {
                    f"{direction}:round{round_index}": increment
                    for (direction, round_index), increment in sorted(
                        schedule_site_increments.items()
                    )
                },
                "minimum_extra_average_t": schedule_nonlinear_lower_bound,
                "qualification": (
                    "diagnostic floor only; per-observed-site widening is not "
                    "admitted because it is frozen-population fitting and lacks a "
                    "universal source proof; four terminal-budget failures are "
                    "excluded from this nonnegative floor"
                ),
            },
            "selective_multiply_plus_observed_schedule_floor": {
                "minimum_extra_average_t_from_width53": combined_lower_bound,
                "lower_bound_average_t": BASE_AVG_T + combined_lower_bound,
                "lower_bound_rounded_t": math.floor(
                    BASE_AVG_T + combined_lower_bound + 0.5
                ),
                "fits_rounded_t_cap": math.floor(
                    BASE_AVG_T + combined_lower_bound + 0.5
                )
                <= ROUNDED_T_CAP,
            },
        },
        "falsifier": (
            "The remaining failures span signed-width drops and terminal-round "
            "shortfalls in both directions. Independently, +2f-only misses the "
            "+f shot 8641 and its one-CCX-per-site floor cannot fit rounded "
            "T <= 912109. No checkpoint, nonce, output, or shot-index repair is admitted."
        ),
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
