#!/usr/bin/env python3
"""Freeze Q1270 inherited or H64 masks with the current-source oracle only."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import os
import pathlib
import re
import struct
import subprocess


REPO = pathlib.Path(__file__).resolve().parents[3]
ROOT = pathlib.Path("/Users/olifreuler/ecdsa-ops/q1270-routed-combined-ec4fadc0")
OPS = ROOT / "calibration/ops.bin"
CHECKPOINT = ROOT / "trace/checkpoint.bin"
SCHEDULE = ROOT / "trace/phase_schedule.h"
BINARY_A = pathlib.Path("/private/tmp/q1270-oracle-target-a/release/q1270_trusted_masks")
BINARY_B = pathlib.Path("/private/tmp/q1270-oracle-target-b/release/q1270_trusted_masks")
BASE = "90770b10664fc89065b1d05ac792370efed4c629"
FULL_RECEIPT = "953acb44fbcbb32ab097a52be31ae365db41bd92"
OPS_SHA256 = "ec4fadc0b5cd1c26ee5d81001b7a72692678b61a94c4091032dd93b8b62eb63a"
CHECKPOINT_SHA256 = "75deeae0d80122a3ce30a7337b34128af5dc964bc26ba0b77c2d6599abdb937f"
SCHEDULE_SHA256 = "17720a6855002f12f0b90ce8598139bfa4f5d2ec0e1ed72d6579177da9a43d35"
ORACLE_SOURCE_SHA256 = "4059969b3cca026a637e7fc735acc8c214d23a5172344d25463dff0ecf128b60"
EVALUATOR_SOURCE_SHA256 = "b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b"
BINARY_SHA256 = "de84cf864bd80b7acf934259fa5435e4103d9b387167456091d85ca34ce9acfd"
TRANSFORM_ID = b"paired-x-tail-v1"
EXPECTED = {
    OPS: OPS_SHA256,
    CHECKPOINT: CHECKPOINT_SHA256,
    SCHEDULE: SCHEDULE_SHA256,
    BINARY_A: BINARY_SHA256,
    BINARY_B: BINARY_SHA256,
    REPO / "src/bin/q1270_trusted_masks.rs": ORACLE_SOURCE_SHA256,
    REPO / "src/bin/eval_circuit.rs": EVALUATOR_SOURCE_SHA256,
    REPO / "Cargo.toml": "3c80178b08d29a158abb29a7dcb8eefc67c66f60f2c3bd14483b65eeca0740dc",
    REPO / "Cargo.lock": "42ff16919e551891ad1b21821329b116d133194245a0e0734a33573dfe598e07",
    REPO / "src/circuit.rs": "ac2255f6bcb6895c9da2dfe21c3a051a0ef8fc4e0af9598634fec0035dbf35c6",
    REPO / "src/sim.rs": "f0c72f2a280cd68acee1dbf8282098f72d6b3bf4311e0abf96d122fe002256d7",
    REPO / "src/weierstrass_elliptic_curve.rs":
        "ecfca15ee3b831c243fbea559ff4b8937be47fe591a4f14786ec2b9bfb30bded",
    REPO / "src/point_add/mod.rs":
        "3fbe6baa8bb4638217f7416b858f4ddd57906fdaaecc500d860f1ca96f1ed60f",
    REPO / "src/point_add/pingpong_div.rs":
        "9b1e5e8540a01584e1238c27328481ba67db3b167aa199db4113e846f1eb6295",
}
CORPORA = {
    "inherited": (
        REPO / ".lane/q1270-routed-predictor/INHERITED.nonces",
        "dabc177103443bede607625489337794ac828e25b60e787a67f7789bfa1627f1",
        (65_700_024_945_645,),
    ),
    "h64": (
        REPO / ".lane/q1270-routed-predictor/H64.nonces",
        "87fb300f0f1aa12cb4c6e70c24f0cae7899313c1cc5bd6f92ab70c06848314bd",
        tuple(range(770_000_000_000, 770_000_000_064)),
    ),
}
SUMMARY_RE = re.compile(
    r"^MASKS nonce=(\d+) qubits=(\d+) bits=(\d+) ops=(\d+) shots=(\d+) "
    r"total_toffoli=(\d+) total_clifford=(\d+) classical=(\d+) "
    r"raw_phase=(\d+) raw_phase_batches=(\d+) clean_phase=(\d+) "
    r"ancilla_shots=(\d+) ancilla_batches=(\d+)$"
)
WORD_RE = re.compile(
    r"^WORD (\d{3}) ([0-9a-f]{16}) ([0-9a-f]{16}) "
    r"([0-9a-f]{16}) ([0-9a-f]{16})$"
)
CORE_PATHS = (
    "Cargo.toml",
    "Cargo.lock",
    "src/circuit.rs",
    "src/sim.rs",
    "src/weierstrass_elliptic_curve.rs",
    "src/bin/eval_circuit.rs",
    "src/point_add/mod.rs",
    "src/point_add/pingpong_div.rs",
)


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"freeze-trusted-masks: {message}")


def parse_nonce_list(path: pathlib.Path) -> tuple[int, ...]:
    raw = path.read_bytes()
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as error:
        fail(f"non-ASCII nonce list: {error}")
    if not text.endswith("\n") or "\r" in text:
        fail("nonce list is not canonical LF framing")
    lines = text.splitlines()
    if any(not line.isdecimal() or (len(line) > 1 and line.startswith("0")) for line in lines):
        fail("nonce list contains a non-canonical decimal")
    nonces = tuple(int(line) for line in lines)
    if nonces != tuple(sorted(set(nonces))) or any(nonce >= 1 << 48 for nonce in nonces):
        fail("nonce list is not sorted, unique, and below 2^48")
    return nonces


def parse_oracle(stdout: bytes, nonce: int) -> tuple[tuple[int, ...], tuple[tuple[int, ...], ...]]:
    try:
        lines = stdout.decode("ascii").splitlines()
    except UnicodeDecodeError as error:
        fail(f"nonce {nonce}: non-ASCII oracle output: {error}")
    summaries = [line for line in lines if line.startswith("MASKS ")]
    if len(summaries) != 1:
        fail(f"nonce {nonce}: expected one MASKS row, got {len(summaries)}")
    match = SUMMARY_RE.fullmatch(summaries[0])
    if match is None:
        fail(f"nonce {nonce}: malformed MASKS row")
    summary = tuple(int(value) for value in match.groups())
    if summary[:5] != (nonce, 1270, 961_070, 12_953_636, 9024):
        fail(f"nonce {nonce}: geometry drift: {summary[:5]}")

    words: list[tuple[int, ...]] = []
    for line in lines:
        if not line.startswith("WORD "):
            continue
        word_match = WORD_RE.fullmatch(line)
        if word_match is None:
            fail(f"nonce {nonce}: malformed WORD row")
        index = int(word_match.group(1))
        values = tuple(int(value, 16) for value in word_match.groups()[1:])
        if index != len(words):
            fail(f"nonce {nonce}: non-canonical word index {index}")
        words.append(values)
    if len(words) != 141:
        fail(f"nonce {nonce}: expected 141 words, got {len(words)}")
    columns = tuple(tuple(row[index] for row in words) for index in range(4))
    classical, raw_phase, clean_phase, ancilla = columns
    if any(clean != (raw & ~classical_word & ((1 << 64) - 1))
           for classical_word, raw, clean in zip(classical, raw_phase, clean_phase)):
        fail(f"nonce {nonce}: clean-phase derivation mismatch")

    counts = (
        sum(word.bit_count() for word in classical),
        sum(word.bit_count() for word in raw_phase),
        sum(word != 0 for word in raw_phase),
        sum(word.bit_count() for word in clean_phase),
        sum(word.bit_count() for word in ancilla),
        sum(word != 0 for word in ancilla),
    )
    if counts != summary[7:13]:
        fail(f"nonce {nonce}: summary/mask count mismatch: {counts} != {summary[7:13]}")
    if counts[4:] != (0, 0):
        fail(f"nonce {nonce}: ancilla is not clean: {counts[4:]}")
    return summary, columns


def canonical_row(summary: tuple[int, ...], columns: tuple[tuple[int, ...], ...]) -> bytes:
    header_values = summary[:13]
    payload = bytearray(struct.pack("<8sI" + "Q" * 13, b"Q1270MSK", 1, *header_values))
    payload.extend(bytes.fromhex(BASE))
    payload.extend(bytes.fromhex(FULL_RECEIPT))
    for identity in (
        OPS_SHA256,
        CHECKPOINT_SHA256,
        SCHEDULE_SHA256,
        ORACLE_SOURCE_SHA256,
        EVALUATOR_SOURCE_SHA256,
        hashlib.sha256(TRANSFORM_ID).hexdigest(),
        BINARY_SHA256,
    ):
        payload.extend(bytes.fromhex(identity))
    for column in columns:
        payload.extend(struct.pack("<" + "Q" * 141, *column))
    return bytes(payload)


def run_process(nonce: int) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [str(BINARY_A), str(OPS), str(nonce)],
        cwd=REPO,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def run_nonce(root: pathlib.Path, corpus: str, nonce: int) -> tuple[int, ...]:
    work = root / str(nonce)
    work.mkdir()
    process = run_process(nonce)
    (work / "oracle.stdout").write_bytes(process.stdout)
    (work / "oracle.stderr").write_bytes(process.stderr)
    if process.returncode != 0:
        fail(f"nonce {nonce}: oracle rc={process.returncode}")
    summary, columns = parse_oracle(process.stdout, nonce)

    if corpus == "inherited":
        repeat = run_process(nonce)
        (work / "repeat.stdout").write_bytes(repeat.stdout)
        (work / "repeat.stderr").write_bytes(repeat.stderr)
        if repeat.returncode != 0:
            fail(f"nonce {nonce}: repeat rc={repeat.returncode}")
        repeat_summary, repeat_columns = parse_oracle(repeat.stdout, nonce)
        if (repeat.stdout, repeat.stderr, repeat_summary, repeat_columns) != (
            process.stdout, process.stderr, summary, columns
        ):
            fail(f"nonce {nonce}: calibration repeat differs")
        if summary[7] != 23 or summary[9] != 14:
            fail(f"nonce {nonce}: inherited validity counts drift: {summary[7:10]}")
        first_classical = next(
            (batch * 64 + (word & -word).bit_length() - 1
             for batch, word in enumerate(columns[0]) if word),
            None,
        )
        if first_classical != 373:
            fail(f"nonce {nonce}: first classical shot {first_classical} != 373")
        if f"{summary[5] / 9024:.3f}" != "916366.972":
            fail(f"nonce {nonce}: inherited Toffoli average drift")
        if f"{summary[6] / 9024:.3f}" != "10731503.349":
            fail(f"nonce {nonce}: inherited Clifford average drift")

    row = canonical_row(summary, columns)
    (work / "row.bin").write_bytes(row)
    row_digest = hashlib.sha256(row).hexdigest()
    text = (
        f"nonce={nonce}\nsource_commit={BASE}\nfull_receipt_commit={FULL_RECEIPT}\n"
        f"base_ops_sha256={OPS_SHA256}\ncheckpoint_sha256={CHECKPOINT_SHA256}\n"
        f"schedule_sha256={SCHEDULE_SHA256}\noracle_source_sha256={ORACLE_SOURCE_SHA256}\n"
        f"evaluator_source_sha256={EVALUATOR_SOURCE_SHA256}\n"
        f"nonce_transform={TRANSFORM_ID.decode('ascii')}\n"
        f"nonce_transform_sha256={hashlib.sha256(TRANSFORM_ID).hexdigest()}\n"
        f"oracle_binary_sha256={BINARY_SHA256}\nrow_sha256={row_digest}\n"
        f"summary={','.join(str(value) for value in summary)}\n"
    )
    (work / "row.txt").write_text(text, encoding="ascii", newline="\n")
    artifact_rows = []
    for path in sorted(work.iterdir()):
        if path.is_file():
            artifact_rows.append(f"{sha256(path)}  {path.name}")
    sums = work / "SHA256SUMS"
    sums.write_text("\n".join(artifact_rows) + "\n", encoding="ascii", newline="\n")
    return (*summary, row_digest, sha256(sums))


def validate_inputs(list_path: pathlib.Path, list_hash: str) -> None:
    for path, expected in {**EXPECTED, list_path: list_hash}.items():
        if not path.is_file():
            fail(f"missing immutable input: {path}")
        actual = sha256(path)
        if actual != expected:
            fail(f"input drift: {path}: {actual} != {expected}")
    if BINARY_A.read_bytes() != BINARY_B.read_bytes():
        fail("independent release binaries differ")
    source_diff = subprocess.run(
        ["git", "diff", "--quiet", BASE, "--", *CORE_PATHS],
        cwd=REPO,
        check=False,
    )
    if source_diff.returncode != 0:
        fail("trusted core differs from exact circuit source")
    with OPS.open("rb") as stream:
        header = stream.read(16)
    if header[:8] != b"QECCOPSZ" or int.from_bytes(header[8:], "little") != 12_953_636:
        fail("operation framing or count drift")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", choices=tuple(CORPORA), required=True)
    parser.add_argument("--jobs", type=int, default=2)
    arguments = parser.parse_args()
    if not 1 <= arguments.jobs <= 2:
        fail("jobs must be in [1,2]")
    list_path, list_hash, expected_nonces = CORPORA[arguments.corpus]
    validate_inputs(list_path, list_hash)
    nonces = parse_nonce_list(list_path)
    if nonces != expected_nonces:
        fail(f"{arguments.corpus} nonce set differs from frozen declaration")

    output = ROOT / f"trusted-{arguments.corpus}"
    partial = ROOT / f".trusted-{arguments.corpus}.partial-{os.getpid()}"
    if output.exists() or partial.exists():
        fail(f"output already exists: {output if output.exists() else partial}")
    partial.mkdir(parents=True)

    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=arguments.jobs) as executor:
        futures = {
            executor.submit(run_nonce, partial, arguments.corpus, nonce): nonce
            for nonce in nonces
        }
        for future in concurrent.futures.as_completed(futures):
            row = future.result()
            rows.append(row)
            print(
                f"freeze-trusted-masks: PASS corpus={arguments.corpus} nonce={row[0]} "
                f"classical={row[7]} raw_phase={row[8]} clean_phase={row[10]}",
                flush=True,
            )
    rows.sort()
    if tuple(row[0] for row in rows) != nonces:
        fail("terminal nonce set differs from frozen declaration")

    header = (
        "nonce\tqubits\tbits\tops\tshots\ttotal_toffoli\ttotal_clifford\t"
        "classical\traw_phase\traw_phase_batches\tclean_phase\tancilla_shots\t"
        "ancilla_batches\trow_sha256\tartifact_manifest_sha256"
    )
    result_lines = [header] + ["\t".join(str(value) for value in row) for row in rows]
    results_path = partial / "RESULTS.tsv"
    results_path.write_text("\n".join(result_lines) + "\n", encoding="ascii", newline="\n")
    manifest_rows = []
    for path in sorted(partial.rglob("*")):
        if path.is_file():
            manifest_rows.append(f"{sha256(path)}  {path.relative_to(partial)}")
    manifest_path = partial / "SHA256SUMS"
    manifest_path.write_text("\n".join(manifest_rows) + "\n", encoding="ascii", newline="\n")
    complete = partial / "COMPLETE"
    complete.write_text(
        f"corpus={arguments.corpus}\nrows={len(rows)}\n"
        f"results_sha256={sha256(results_path)}\nmanifest_sha256={sha256(manifest_path)}\n",
        encoding="ascii",
        newline="\n",
    )
    partial.rename(output)
    print(
        f"freeze-trusted-masks: PASS corpus={arguments.corpus} exact={len(rows)}/{len(rows)} "
        f"results_sha256={sha256(output / 'RESULTS.tsv')} "
        f"manifest_sha256={sha256(output / 'SHA256SUMS')}",
        flush=True,
    )


if __name__ == "__main__":
    main()
