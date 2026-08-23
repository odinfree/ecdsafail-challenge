#!/usr/bin/env python3
"""Compare the target-bound model with inherited and frozen H64 oracles."""

from __future__ import annotations

import concurrent.futures
import hashlib
import os
import pathlib
import re
import subprocess


REPO = pathlib.Path(__file__).resolve().parents[3]
ROOT = pathlib.Path("/Users/olifreuler/ecdsa-ops/q1271-target0-sign-alias-590cb55d")
OPS = ROOT / "target/ops.bin"
PPCPU = ROOT / "model/ppcpu-combined"
ORACLES = ROOT / "h64-oracle"
OUT = ROOT / "h64-model-v1"
NONCE_FILE = REPO / ".lane/q1271-target0-predictor/H64.nonces"
EXPECTED = {
    OPS: "590cb55deb75af4ab9356fce97308b4ca4dc10ac031d4fd6d16464e8515972fa",
    PPCPU: "5c2dc3f4c2be8df9a88d60448e17b65ae3073c285e68f41feaccec96f6f74021",
    ROOT / "model/phase-meta.tsv":
        "665e64bb22d87ba629a133f7c67813c284a7fca47d1b6212914c83abe0f5fa1e",
    ROOT / "model/pp_phase_schedule.h":
        "49f82e4effec2c110fed73974df306cbcae9ac456043cb329bb15a7b5e97f4e8",
    NONCE_FILE: "17443162349d50e521b0c9a20904de5a0212a668e6f3ae7ea0e2702b2f79c4b9",
    REPO / ".lane/q1271-target0-predictor/src/pp_model.h":
        "46e227f7920f43e8d233791dfefd01858cff39c24807d17ed2b390befa0bb390",
    REPO / ".lane/q1271-target0-predictor/src/pp_host.h":
        "7d432431c1d27854f6dff6b0ff807da0241deabf3b3dccc63c53b09e8b7fee8b",
    REPO / ".lane/q1271-target0-predictor/src/ppcpu.cpp":
        "0e10386e356f0a21e7a89bdf8445309d14641a94fe707fe788dd777727f796ba",
}
EXPECTED_ORACLE_ROWS_SHA256 = "4ee3022cac1798c1d50e871db2518c7142750e6bd272e56b08e8b3bf05e1553e"
EXPECTED_ORACLE_MANIFEST_SHA256 = "0faa6512fc6240c71fd42c82ef8ddaf6c77f1990f0887604283e838e8b6c1072"
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


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"qualify-h64: {message}")


def parse_indices(lines: list[str], prefix: str) -> list[int]:
    values = []
    for line in lines:
        if line.startswith(prefix):
            value = line[len(prefix):]
            if not value.isdecimal():
                fail(f"malformed index row {line!r}")
            values.append(int(value))
    if values != sorted(set(values)) or any(value >= 9024 for value in values):
        fail(f"non-canonical index set for {prefix!r}")
    return values


def parse_oracle(nonce: int, directory: pathlib.Path) -> tuple[list[int], list[int], int]:
    lines = (directory / "oracle.stdout").read_text(encoding="ascii").splitlines()
    summary = [line for line in lines if line.startswith("MIRROR ")]
    if len(summary) != 1 or (match := MIRROR_RE.match(summary[0])) is None:
        fail(f"nonce {nonce}: malformed oracle summary")
    got_nonce, qubits, shots, cls, _batches, raw_phase, ancilla = map(int, match.groups())
    if (got_nonce, qubits, shots, ancilla) != (nonce, 1271, 9024, 0):
        fail(f"nonce {nonce}: oracle geometry mismatch")
    classical = parse_indices(lines, "CLASSICAL_SHOT ")
    phase = parse_indices(lines, "CLEAN_PHASE_SHOT ")
    if len(classical) != cls or len(phase) > raw_phase or set(classical) & set(phase):
        fail(f"nonce {nonce}: oracle mask/summary mismatch")
    return classical, phase, raw_phase


def verify_h64_oracles(nonces: tuple[int, ...]) -> None:
    actual = tuple(sorted(int(path.name) for path in ORACLES.iterdir() if path.is_dir()))
    if actual != nonces:
        fail("H64 oracle directory set differs from frozen list")
    canonical_rows = []
    manifest_rows = []
    for nonce in nonces:
        directory = ORACLES / str(nonce)
        declared = {}
        for line in (directory / "SHA256SUMS").read_text(encoding="ascii").splitlines():
            digest, name = line.split(None, 1)
            name = name.strip()
            if sha256(directory / name) != digest:
                fail(f"nonce {nonce}: oracle artifact drift: {name}")
            declared[name] = digest
            manifest_rows.append(f"{nonce}\t{name}\t{digest}\n")
        if set(declared) != {"attrib.tsv", "oracle.stderr", "oracle.stdout"}:
            fail(f"nonce {nonce}: incomplete oracle manifest")
        if (directory / "oracle.stderr").read_bytes():
            fail(f"nonce {nonce}: oracle stderr is non-empty")
        classical, phase, raw_phase = parse_oracle(nonce, directory)
        canonical_rows.append(
            f"{nonce}\tq=1271\tshots=9024\tcls={','.join(map(str, classical))}"
            f"\traw_phase_total={raw_phase}\tcond_phase={','.join(map(str, phase))}"
            "\tanc=0\n"
        )
    if sha256_bytes("".join(canonical_rows).encode()) != EXPECTED_ORACLE_ROWS_SHA256:
        fail("H64 canonical oracle digest mismatch")
    if sha256_bytes("".join(manifest_rows).encode()) != EXPECTED_ORACLE_MANIFEST_SHA256:
        fail("H64 oracle artifact-manifest digest mismatch")


def run_model(nonce: int, oracle_dir: pathlib.Path, output_dir: pathlib.Path) -> tuple[int, int, int, str]:
    oracle_classical, oracle_phase, raw_phase = parse_oracle(nonce, oracle_dir)
    output_dir.mkdir()
    env = dict(os.environ, PPF_OPS=str(OPS))
    classical = subprocess.run(
        [str(PPCPU), "faultshots", str(nonce)], cwd=REPO, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
    )
    phase = subprocess.run(
        [str(PPCPU), "phasefaultshots", str(nonce)], cwd=REPO, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
    )
    outputs = {
        "model-classical.stdout": classical.stdout,
        "model-classical.stderr": classical.stderr,
        "model-phase.stdout": phase.stdout,
        "model-phase.stderr": phase.stderr,
    }
    for name, data in outputs.items():
        (output_dir / name).write_bytes(data)
    model_classical = []
    for line in classical.stdout.decode("ascii").splitlines():
        fields = line.split()
        if len(fields) != 2 or any(not field.isdecimal() for field in fields):
            fail(f"nonce {nonce}: malformed model classical output")
        model_classical.append(int(fields[0]))
    phase_lines = phase.stdout.decode("ascii").splitlines()
    if any(not line.isdecimal() for line in phase_lines):
        fail(f"nonce {nonce}: malformed model phase output")
    model_phase = [int(line) for line in phase_lines]
    if model_classical != oracle_classical:
        fail(f"nonce {nonce}: complete classical mask mismatch")
    if model_phase != oracle_phase:
        fail(f"nonce {nonce}: complete conditional-phase mask mismatch")
    rows = [f"{sha256(output_dir / name)}  {name}" for name in sorted(outputs)]
    sums = output_dir / "SHA256SUMS"
    sums.write_text("\n".join(rows) + "\n", encoding="ascii", newline="\n")
    return nonce, len(oracle_classical), raw_phase, len(oracle_phase), sha256(sums)


def main() -> None:
    for path, expected in EXPECTED.items():
        if not path.is_file() or sha256(path) != expected:
            fail(f"immutable input missing or drifted: {path}")
    lines = NONCE_FILE.read_text(encoding="ascii").splitlines()
    if len(lines) != 64 or any(not line.isdecimal() for line in lines):
        fail("H64 list is malformed")
    nonces = tuple(map(int, lines))
    if nonces != tuple(range(444_000_000_000, 444_000_000_064)):
        fail("H64 list is not the frozen ordered range")
    verify_h64_oracles(nonces)
    if OUT.exists():
        fail(f"output already exists: {OUT}")
    OUT.mkdir()

    inherited = run_model(65700024945645, ROOT / "inherited", OUT / "inherited")
    if inherited[1:4] != (11, 10, 4):
        fail(f"inherited totals drifted: {inherited[1:4]}")
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(
                run_model, nonce, ORACLES / str(nonce), OUT / str(nonce)
            ): nonce
            for nonce in nonces
        }
        for future in concurrent.futures.as_completed(futures):
            row = future.result()
            rows.append(row)
            print(
                f"qualify-h64: PASS nonce={row[0]} classical={row[1]} "
                f"raw_phase={row[2]} conditional_phase={row[3]}",
                flush=True,
            )
    rows.sort()
    if tuple(row[0] for row in rows) != nonces:
        fail("H64 result set differs from frozen order")
    totals = tuple(sum(row[index] for row in rows) for index in (1, 2, 3))
    if totals != (1093, 843, 298):
        fail(f"H64 aggregate drift: {totals}")
    manifest = ["nonce\tclassical\traw_phase\tconditional_phase\tartifact_manifest_sha256"]
    manifest.extend("\t".join(map(str, row)) for row in rows)
    results = OUT / "RESULTS.tsv"
    results.write_text("\n".join(manifest) + "\n", encoding="ascii", newline="\n")
    print(
        f"qualify-h64: PASS inherited=1/1 h64=64/64 "
        f"totals_classical_raw_conditional={totals} results_sha256={sha256(results)}",
        flush=True,
    )


if __name__ == "__main__":
    main()
