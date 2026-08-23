#!/usr/bin/env python3
"""Derive Q1270 recurrence inputs from the exact target source and probes."""

from __future__ import annotations

import hashlib
import os
import pathlib
import re
import subprocess


REPO = pathlib.Path(__file__).resolve().parents[3]
ROOT = pathlib.Path(
    "/Users/olifreuler/ecdsa-ops/q1270-routed-combined-ec4fadc0/"
    "model-derivation-4aaf5b8"
)
PINGPONG = REPO / "src/point_add/pingpong_div.rs"
SQUARE = REPO / "src/point_add/trailmix_ludicrous/square/product_register.rs"
BINARY = pathlib.Path("/private/tmp/q1270-native-derive-target/release/build_circuit")
EXPECTED = {
    PINGPONG: "9b1e5e8540a01584e1238c27328481ba67db3b167aa199db4113e846f1eb6295",
    SQUARE: "864d31454c5279632652cf48aeda038d481a504b09e4f7a8c0f266e10a24b81c",
    BINARY: "1011f82a46a034fff7c82307354e83b1d4a24d2c3c740bc3caa3449f93f555a4",
}
REQUIRED_SNIPPETS = (
    "const ROUNDS_DEFAULT: usize = 704;",
    'tuned_window("SUB4_PP_ROUNDS_MUL", &SLOT, 696)',
    'tuned_window("SUB4_PP_ROUNDS", &SLOT, 696)',
    "round * (ROUNDS_DEFAULT - 1) / (r - 1)",
    'tuned_window("SUB4_PP_REPLAY_CHUNK", &SLOT, 96)',
    'tuned_window("SUB4_PP_REPLAY_CHUNK_COMPARE", &SLOT, 20)',
    'tuned_window("SUB4_PP_REPLAY_FOLD_WINDOW", &SLOT, 54)',
    'tuned_window("SUB4_PP_ENDPOINT_FOLD_WINDOW", &SLOT, 20)',
    'tuned_window("SUB4_PP_REPLAY_FLAG_COMPARE", &SLOT, 22)',
    'let r1 = env("SUB4_PP_R1", 340).min(rounds);',
    'let r2 = env("SUB4_PP_R2", 628).min(rounds.saturating_sub(1));',
    'let peak = env("SUB4_PP_PEAK", 1273);',
    "if false && r <= u16::MAX as usize",
    'std::env::var("SUB4_PP_FOLD_SELECTOR_EVICT")',
    'std::env::var("SUB4_PP_EVICT_SIGN_XOR_ADD")',
    'std::env::var("SUB4_PP_ALIAS_TARGET0_SIGN")',
    'std::env::var_os("SUB4_PP_EVICT_DOUBLED_OUT")',
)


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"derive-native-inputs: {message}")


def require_inputs() -> str:
    for path, expected in EXPECTED.items():
        if not path.is_file():
            fail(f"missing input: {path}")
        actual = sha256(path)
        if actual != expected:
            fail(f"input drift: {path}: {actual} != {expected}")
    source = PINGPONG.read_text(encoding="utf-8")
    for snippet in REQUIRED_SNIPPETS:
        if source.count(snippet) != 1:
            fail(f"required source binding is not unique: {snippet!r}")
    square = SQUARE.read_text(encoding="utf-8")
    if square.count('std::env::var("SUB4_SQUARE_LADDER")') != 1:
        fail("square-ladder source binding is not unique")
    return source


def parse_width_table(source: str) -> tuple[int, ...]:
    match = re.search(
        r"const WIDTH_SCHEDULE: \[u16; 700\] = \[(.*?)\];",
        source,
        re.DOTALL,
    )
    if match is None:
        fail("missing 700-entry width table")
    values = tuple(int(value) for value in re.findall(r"\d+", match.group(1)))
    if len(values) != 700:
        fail(f"width table has {len(values)} entries")
    if any(right > left for left, right in zip(values, values[1:])):
        fail("source width table is not non-increasing")
    return values


def expected_width(table: tuple[int, ...], round_index: int, rescale: bool) -> int:
    if round_index == 0:
        return 259
    index = round_index * 703 // 695 if rescale else round_index
    return table[index] if index < len(table) else 8


def run_probe() -> tuple[tuple[int, int, int], ...]:
    stdout_path = ROOT / "width-probe.stdout"
    stderr_path = ROOT / "width-probe.stderr"
    empty_ops = ROOT / "ops.bin"
    for path in (stdout_path, stderr_path, empty_ops):
        if path.exists():
            fail(f"probe output already exists: {path}")
    environment = {
        "PATH": "/usr/bin:/bin:/opt/homebrew/bin",
        "SUB4_DUMP_WSCHED": "1",
    }
    process = subprocess.run(
        [str(BINARY)],
        cwd=ROOT,
        env=environment,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout_path.write_bytes(process.stdout)
    stderr_path.write_bytes(process.stderr)
    if process.returncode != 0:
        fail(f"width probe returned {process.returncode}")
    try:
        lines = process.stdout.decode("ascii").splitlines()
    except UnicodeDecodeError as error:
        fail(f"width probe output is not ASCII: {error}")
    positions = [index for index, line in enumerate(lines) if line == "round,base,rescale"]
    if len(positions) != 1:
        fail(f"expected one width header, got {len(positions)}")
    start = positions[0] + 1
    rows: list[tuple[int, int, int]] = []
    for expected_round, line in enumerate(lines[start : start + 700]):
        fields = line.split(",")
        if len(fields) != 3 or any(not field.isdecimal() for field in fields):
            fail(f"malformed width row {expected_round}: {line!r}")
        row = tuple(int(field) for field in fields)
        if row[0] != expected_round:
            fail(f"non-contiguous width row {expected_round}: {row[0]}")
        rows.append(row)
    if len(rows) != 700:
        fail(f"width probe emitted {len(rows)} rows")
    if not empty_ops.is_file():
        fail("diagnostic builder did not emit framed empty operation file")
    framing = empty_ops.read_bytes()
    if len(framing) < 16 or framing[:8] != b"QECCOPSZ" or int.from_bytes(framing[8:16], "little") != 0:
        fail("diagnostic operation framing is not empty")
    return tuple(rows)


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    source = require_inputs()
    table = parse_width_table(source)
    rows = run_probe()
    for round_index, base, rescale in rows:
        expected_base = expected_width(table, round_index, False)
        expected_rescale = expected_width(table, round_index, True)
        if (base, rescale) != (expected_base, expected_rescale):
            fail(
                f"width row {round_index}: {(base, rescale)} != "
                f"{(expected_base, expected_rescale)}"
            )

    width_path = ROOT / "width-schedule.tsv"
    active_path = ROOT / "active-widths.tsv"
    inputs_path = ROOT / "native-inputs.txt"
    for path in (width_path, active_path, inputs_path):
        if path.exists():
            fail(f"derived output already exists: {path}")
    width_path.write_text(
        "round\tbase\trescale\n"
        + "".join(f"{round_index}\t{base}\t{rescale}\n" for round_index, base, rescale in rows),
        encoding="ascii",
        newline="\n",
    )
    active_path.write_text(
        "direction\tround\twidth\n"
        + "".join(
            f"divide\t{round_index}\t{rows[round_index][2]}\n"
            for round_index in range(696)
        )
        + "".join(
            f"multiply\t{round_index}\t{rows[round_index][2]}\n"
            for round_index in range(696)
        ),
        encoding="ascii",
        newline="\n",
    )
    inputs = (
        "source_commit=90770b10664fc89065b1d05ac792370efed4c629\n"
        f"pingpong_sha256={EXPECTED[PINGPONG]}\n"
        f"square_sha256={EXPECTED[SQUARE]}\n"
        f"probe_binary_sha256={EXPECTED[BINARY]}\n"
        "divide_rounds=696\nmultiply_rounds=696\nrounds_default=704\n"
        "width_map=floor(round*703/695)\nwidth_repair=disabled_literal_false\n"
        "replay_chunk_default=96\nreplay_compare=20\nreplay_fold=54\n"
        "endpoint_fold=20\nreplay_flag_compare=22\n"
        "plan_r1=340\nplan_r2=628\ndivide_peak=1270\nmultiply_peak=1271\n"
        "square_ladder=240\nfold_selector_evict=1\ndoubled_out_evict=1\n"
        "target0_sign_alias=1\nsign_xor_add_evict=1\n"
        f"width_schedule_sha256={sha256(width_path)}\n"
        f"active_widths_sha256={sha256(active_path)}\n"
    )
    inputs_path.write_text(inputs, encoding="ascii", newline="\n")
    print(
        "derive-native-inputs: PASS "
        f"rows={len(rows)} active=696+696 width_sha256={sha256(width_path)} "
        f"active_sha256={sha256(active_path)} inputs_sha256={sha256(inputs_path)}"
    )


if __name__ == "__main__":
    main()
