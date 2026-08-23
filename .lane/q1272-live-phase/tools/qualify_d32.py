#!/usr/bin/env python3
"""Reveal and qualify the frozen disjoint Q1272 D32 exactly once."""

from __future__ import annotations

import concurrent.futures
import hashlib
import os
import pathlib
import re
import subprocess


REPO = pathlib.Path(__file__).resolve().parents[3]
ROOT = pathlib.Path("/Users/olifreuler/ecdsa-ops/q1272-live-phase-ea19759d")
OUT = ROOT / "d32"
OPS = REPO / "ops.bin"
SITES = ROOT / "op-sites.tsv"
MIRROR_SOURCE = pathlib.Path("/private/tmp/phase_mirror/src/main.rs")
MIRROR = pathlib.Path("/private/tmp/phase_mirror/target/release/phase_mirror")
PPCPU = ROOT / "ppcpu-combined"
NONCE_SPEC = "3c1a49cdde48f804c4e35bd0501d7d8d7f46f15e:.lane/q1273-wrap-exact/D32.nonces"
EXPECTED_NONCE_SHA256 = "62bca2420f684c718e52b516dc850f05d72c33f64798002fe2afd215642a0f90"
EXPECTED = {
    OPS: "ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1",
    SITES: "f2f0f99d096027299460d9a82c16d3714c9684564d10f13f6dcbbac2b3e92833",
    MIRROR_SOURCE: "26d2a045d048025ce086b099b41fdfc7c42a2657426c59d5fdb95be9cacd8d98",
    MIRROR: "90e4db8669c03b259c13b259018134b754faa94adfbc1e491a601f1052cd6402",
    PPCPU: "47366b9d7d131639bb0ed9a8abc9cb87bd9c3b9aa5b746d0dcbc464ac9ba435c",
    REPO / ".lane/q1272-live-phase/src/pp_model.h":
        "0d4c9a812892b9dac598cb59a8345c443b9e21663ac29743578f4e651b39b92a",
    REPO / ".lane/q1272-live-phase/src/pp_host.h":
        "aa546788a823268cf311d88f028b80dd12826162fe220848ae46ec165b6190a2",
    REPO / ".lane/q1272-live-phase/src/ppcpu.cpp":
        "dd05545d33911e7e0ab44b0e373f03a759ae8ee4b990f20f2cc40ca6ee2063af",
    ROOT / "h64/RESULTS.tsv":
        "0b05b359ac2f9fc23e81163adcf8047aa28fd514c5ecd581a0416a07ee1b9ccc",
}
MIRROR_RE = re.compile(
    r"^MIRROR nonce=(\d+) qubits=(\d+) shots=(\d+) cls=(\d+) "
    r"phase_batches=(\d+) phase_shots=(\d+) ancilla=(\d+) "
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"qualify-d32: {message}")


def parse_indices(lines: list[str], prefix: str) -> list[int]:
    out = []
    for line in lines:
        if line.startswith(prefix):
            value = line[len(prefix):]
            if not value.isdecimal():
                fail(f"malformed oracle index: {line!r}")
            out.append(int(value))
    if out != sorted(set(out)) or any(value >= 9024 for value in out):
        fail(f"non-canonical oracle set for {prefix!r}")
    return out


def evaluate(nonce: int, work: pathlib.Path) -> tuple[int, int, int, list[int], list[int]]:
    work.mkdir()
    attrib = work / "attrib.tsv"
    oracle = subprocess.run(
        [str(MIRROR), str(OPS), str(SITES), str(nonce), str(attrib)],
        cwd=REPO, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    (work / "oracle.stdout").write_bytes(oracle.stdout)
    (work / "oracle.stderr").write_bytes(oracle.stderr)
    oracle_lines = oracle.stdout.decode("ascii").splitlines()
    summary = [line for line in oracle_lines if line.startswith("MIRROR ")]
    if len(summary) != 1:
        fail(f"nonce {nonce}: expected one MIRROR row, got {len(summary)}")
    match = MIRROR_RE.match(summary[0])
    if not match:
        fail(f"nonce {nonce}: malformed MIRROR row")
    got_nonce, qubits, shots, cls, _phase_batches, raw_phase, ancilla = map(
        int, match.groups()
    )
    if (got_nonce, qubits, shots, ancilla) != (nonce, 1272, 9024, 0):
        fail(f"nonce {nonce}: geometry/ancilla mismatch")
    oracle_classical = parse_indices(oracle_lines, "CLASSICAL_SHOT ")
    oracle_phase = parse_indices(oracle_lines, "CLEAN_PHASE_SHOT ")
    if len(oracle_classical) != cls or len(oracle_phase) > raw_phase:
        fail(f"nonce {nonce}: oracle summary/set mismatch")

    env = dict(os.environ, PPF_OPS=str(OPS))
    classical = subprocess.run(
        [str(PPCPU), "faultshots", str(nonce)], cwd=REPO, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
    )
    phase = subprocess.run(
        [str(PPCPU), "phasefaultshots", str(nonce)], cwd=REPO, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
    )
    for name, result in (("model-classical", classical), ("model-phase", phase)):
        (work / f"{name}.stdout").write_bytes(result.stdout)
        (work / f"{name}.stderr").write_bytes(result.stderr)

    model_classical = []
    for line in classical.stdout.decode("ascii").splitlines():
        fields = line.split()
        if len(fields) != 2 or not all(field.isdecimal() for field in fields):
            fail(f"nonce {nonce}: malformed model classical row")
        model_classical.append(int(fields[0]))
    phase_lines = phase.stdout.decode("ascii").splitlines()
    if any(not line.isdecimal() for line in phase_lines):
        fail(f"nonce {nonce}: malformed model phase output")
    model_phase = [int(line) for line in phase_lines]
    if model_classical != oracle_classical:
        fail(f"nonce {nonce}: complete classical set mismatch")
    if model_phase != oracle_phase:
        fail(f"nonce {nonce}: complete conditional-phase set mismatch")

    artifact_rows = []
    for path in sorted(work.iterdir()):
        if path.is_file():
            artifact_rows.append(f"{sha256(path)}  {path.name}")
    (work / "SHA256SUMS").write_text("\n".join(artifact_rows) + "\n", encoding="ascii")
    return cls, raw_phase, len(oracle_phase), oracle_classical, oracle_phase


def compare_repeat(original: pathlib.Path, repeated: pathlib.Path) -> None:
    names = (
        "attrib.tsv", "oracle.stdout", "oracle.stderr",
        "model-classical.stdout", "model-classical.stderr",
        "model-phase.stdout", "model-phase.stderr",
    )
    for name in names:
        if (original / name).read_bytes() != (repeated / name).read_bytes():
            fail(f"deterministic repeat mismatch: {original.name}/{name}")


def compare_inherited_repeat(repeated: pathlib.Path) -> None:
    mapping = {
        ROOT / "inherited-attrib.tsv": repeated / "attrib.tsv",
        ROOT / "inherited-oracle.txt": repeated / "oracle.stdout",
        ROOT / "model-inherited-classical.tsv": repeated / "model-classical.stdout",
        ROOT / "model-inherited-classical.stderr": repeated / "model-classical.stderr",
        ROOT / "model-inherited-phase.tsv": repeated / "model-phase.stdout",
        ROOT / "model-inherited-phase.stderr": repeated / "model-phase.stderr",
    }
    for original, repeat in mapping.items():
        if original.read_bytes() != repeat.read_bytes():
            fail(f"deterministic inherited repeat mismatch: {original.name}")
    if (repeated / "oracle.stderr").read_bytes():
        fail("deterministic inherited oracle emitted stderr")


def main() -> None:
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=REPO, check=True,
        stdout=subprocess.PIPE,
    ).stdout
    if status:
        fail("worktree is not clean before holdout reveal")
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", "cf16b4f", "HEAD"], cwd=REPO,
    ).returncode
    if ancestor != 0:
        fail("sealed H64 evidence commit cf16b4f is not an ancestor")
    for path, expected in EXPECTED.items():
        if not path.is_file() or sha256(path) != expected:
            fail(f"immutable input missing or drifted: {path}")
    if OUT.exists():
        fail(f"output already exists: {OUT}")

    nonce_raw = subprocess.run(
        ["git", "show", NONCE_SPEC], cwd=REPO, check=True, stdout=subprocess.PIPE,
    ).stdout
    if sha256_bytes(nonce_raw) != EXPECTED_NONCE_SHA256:
        fail("D32 nonce-list hash mismatch")
    try:
        nonce_text = nonce_raw.decode("ascii")
    except UnicodeDecodeError as exc:
        fail(f"D32 list is not ASCII: {exc}")
    if not nonce_text.endswith("\n"):
        fail("D32 list is not LF-terminated")
    lines = nonce_text.splitlines()
    if len(lines) != 32 or any(not line.isdecimal() or (line.startswith("0") and line != "0") for line in lines):
        fail("D32 list is not 32 canonical decimal rows")
    nonces = tuple(map(int, lines))
    if len(set(nonces)) != 32 or any(nonce >= (1 << 48) for nonce in nonces):
        fail("D32 list is duplicate or outside 48 bits")
    forbidden = {65700024945645, *range(444_000_000_000, 444_000_000_064)}
    if set(nonces) & forbidden:
        fail("D32 overlaps inherited or H64 corpus")

    OUT.mkdir(parents=True)
    (OUT / "D32.nonces").write_bytes(nonce_raw)
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(evaluate, nonce, OUT / str(nonce)): (index, nonce)
            for index, nonce in enumerate(nonces)
        }
        for future in concurrent.futures.as_completed(futures):
            index, nonce = futures[future]
            cls, raw_phase, clean_phase, _classical, _phase = future.result()
            sums_sha = sha256(OUT / str(nonce) / "SHA256SUMS")
            rows.append((index, nonce, cls, raw_phase, clean_phase, sums_sha))
            print(
                f"qualify-d32: PASS row={index} classical={cls} "
                f"raw_phase={raw_phase} clean_phase={clean_phase}",
                flush=True,
            )
    rows.sort()
    if tuple(row[1] for row in rows) != nonces:
        fail("D32 result order differs from sealed nonce list")

    # Two deterministic repeats after the full reveal: the original inherited
    # stream and the final ordered holdout row.  No model/source change occurs.
    repeat_root = OUT / "repeats"
    repeat_root.mkdir()
    evaluate(65700024945645, repeat_root / "inherited")
    compare_inherited_repeat(repeat_root / "inherited")
    evaluate(nonces[-1], repeat_root / "final-d32")
    compare_repeat(OUT / str(nonces[-1]), repeat_root / "final-d32")

    results = ["row\tnonce\tclassical\traw_phase\tclean_phase\tartifact_manifest_sha256"]
    results.extend("\t".join(map(str, row)) for row in rows)
    result_path = OUT / "RESULTS.tsv"
    result_path.write_text("\n".join(results) + "\n", encoding="ascii", newline="\n")
    totals = tuple(sum(row[index] for row in rows) for index in (2, 3, 4))
    repeat_rows = []
    for path in sorted(repeat_root.rglob("*")):
        if path.is_file():
            repeat_rows.append(f"{sha256(path)}  {path.relative_to(repeat_root)}")
    repeat_manifest = OUT / "REPEATS.sha256"
    repeat_manifest.write_text("\n".join(repeat_rows) + "\n", encoding="ascii")
    print(
        f"qualify-d32: PASS exact=32/32 totals_classical_raw_clean={totals} "
        f"results_sha256={sha256(result_path)} repeats_sha256={sha256(repeat_manifest)}",
        flush=True,
    )


if __name__ == "__main__":
    main()
