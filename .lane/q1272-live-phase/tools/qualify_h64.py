#!/usr/bin/env python3
"""Run the frozen Q1272 H64 trusted/model complete-mask qualification."""

from __future__ import annotations

import concurrent.futures
import hashlib
import os
import pathlib
import re
import subprocess


REPO = pathlib.Path(__file__).resolve().parents[3]
ROOT = pathlib.Path("/Users/olifreuler/ecdsa-ops/q1272-live-phase-ea19759d")
OUT = ROOT / "h64"
OPS = REPO / "ops.bin"
SITES = ROOT / "op-sites.tsv"
MIRROR_SOURCE = pathlib.Path("/private/tmp/phase_mirror/src/main.rs")
MIRROR = pathlib.Path("/private/tmp/phase_mirror/target/release/phase_mirror")
PPCPU = ROOT / "ppcpu-combined"
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
}
NONCES = tuple(range(444_000_000_000, 444_000_000_064))
MIRROR_RE = re.compile(
    r"^MIRROR nonce=(\d+) qubits=(\d+) shots=(\d+) cls=(\d+) "
    r"phase_batches=(\d+) phase_shots=(\d+) ancilla=(\d+) "
)


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"qualify-h64: {message}")


def run_checked(argv: list[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(argv, cwd=REPO, check=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)


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


def run_nonce(nonce: int) -> tuple[int, int, int, int, list[str]]:
    work = OUT / str(nonce)
    work.mkdir()
    attrib = work / "attrib.tsv"
    oracle = run_checked([str(MIRROR), str(OPS), str(SITES), str(nonce), str(attrib)])
    (work / "oracle.stdout").write_bytes(oracle.stdout)
    (work / "oracle.stderr").write_bytes(oracle.stderr)
    oracle_lines = oracle.stdout.decode("ascii").splitlines()
    summary = [line for line in oracle_lines if line.startswith("MIRROR ")]
    if len(summary) != 1:
        fail(f"nonce {nonce}: expected one MIRROR row, got {len(summary)}")
    match = MIRROR_RE.match(summary[0])
    if not match or match.group(0) != summary[0].split(" bareR_clean_mask=", 1)[0] + " ":
        # The anchored prefix must parse uniquely; the remaining attribution
        # fields are retained verbatim and hashed below.
        if not match:
            fail(f"nonce {nonce}: malformed MIRROR row")
    got_nonce, qubits, shots, cls, _phase_batches, raw_phase, ancilla = map(
        int, match.groups()
    )
    if (got_nonce, qubits, shots, ancilla) != (nonce, 1272, 9024, 0):
        fail(
            f"nonce {nonce}: geometry {(got_nonce, qubits, shots, ancilla)} "
            "!= expected"
        )
    oracle_classical = parse_indices(oracle_lines, "CLASSICAL_SHOT ")
    oracle_phase = parse_indices(oracle_lines, "CLEAN_PHASE_SHOT ")
    if len(oracle_classical) != cls:
        fail(f"nonce {nonce}: oracle classical count mismatch")

    env = dict(os.environ, PPF_OPS=str(OPS))
    classical = subprocess.run(
        [str(PPCPU), "faultshots", str(nonce)], cwd=REPO, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
    )
    phase = subprocess.run(
        [str(PPCPU), "phasefaultshots", str(nonce)], cwd=REPO, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
    )
    (work / "model-classical.stdout").write_bytes(classical.stdout)
    (work / "model-classical.stderr").write_bytes(classical.stderr)
    (work / "model-phase.stdout").write_bytes(phase.stdout)
    (work / "model-phase.stderr").write_bytes(phase.stderr)

    model_classical = []
    for line in classical.stdout.decode("ascii").splitlines():
        fields = line.split()
        if len(fields) != 2 or not all(field.isdecimal() for field in fields):
            fail(f"nonce {nonce}: malformed model classical row {line!r}")
        model_classical.append(int(fields[0]))
    model_phase_lines = phase.stdout.decode("ascii").splitlines()
    if any(not line.isdecimal() for line in model_phase_lines):
        fail(f"nonce {nonce}: malformed model phase output")
    model_phase = [int(line) for line in model_phase_lines]
    if model_classical != oracle_classical:
        fail(f"nonce {nonce}: complete classical set mismatch")
    if model_phase != oracle_phase:
        fail(f"nonce {nonce}: complete conditional-phase set mismatch")
    if len(model_phase) > raw_phase:
        fail(f"nonce {nonce}: conditional phase exceeds raw phase")

    artifact_rows = []
    for path in sorted(work.iterdir()):
        if path.is_file():
            artifact_rows.append(f"{sha256(path)}  {path.name}")
    (work / "SHA256SUMS").write_text("\n".join(artifact_rows) + "\n", encoding="ascii")
    return nonce, cls, raw_phase, len(oracle_phase), artifact_rows


def main() -> None:
    for path, expected in EXPECTED.items():
        if not path.is_file():
            fail(f"missing immutable input: {path}")
        actual = sha256(path)
        if actual != expected:
            fail(f"input drift: {path}: {actual} != {expected}")
    if OUT.exists():
        fail(f"output already exists: {OUT}")
    OUT.mkdir(parents=True)

    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(run_nonce, nonce): nonce for nonce in NONCES}
        for future in concurrent.futures.as_completed(futures):
            nonce, cls, raw_phase, clean_phase, artifacts = future.result()
            rows.append((nonce, cls, raw_phase, clean_phase, artifacts))
            print(
                f"qualify-h64: PASS nonce={nonce} classical={cls} "
                f"raw_phase={raw_phase} clean_phase={clean_phase}",
                flush=True,
            )

    rows.sort()
    if tuple(row[0] for row in rows) != NONCES:
        fail("result nonce set differs from frozen H64")
    manifest = ["nonce\tclassical\traw_phase\tclean_phase\tartifact_manifest_sha256"]
    for nonce, cls, raw_phase, clean_phase, _ in rows:
        sums = OUT / str(nonce) / "SHA256SUMS"
        manifest.append(f"{nonce}\t{cls}\t{raw_phase}\t{clean_phase}\t{sha256(sums)}")
    manifest_path = OUT / "RESULTS.tsv"
    manifest_path.write_text("\n".join(manifest) + "\n", encoding="ascii", newline="\n")
    totals = tuple(sum(row[index] for row in rows) for index in (1, 2, 3))
    print(
        f"qualify-h64: PASS exact=64/64 totals_classical_raw_clean={totals} "
        f"results_sha256={sha256(manifest_path)}",
        flush=True,
    )


if __name__ == "__main__":
    main()
