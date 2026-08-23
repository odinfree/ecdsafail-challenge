#!/usr/bin/env python3
"""Reveal and compare the frozen disjoint D32 fixtures exactly once."""

from __future__ import annotations

import concurrent.futures
import hashlib
import os
import pathlib
import re
import subprocess


REPO = pathlib.Path(__file__).resolve().parents[3]
ROOT = pathlib.Path("/Users/olifreuler/ecdsa-ops/q1271-target0-sign-alias-590cb55d")
OUT = ROOT / "d32-v1"
OPS = ROOT / "target/ops.bin"
SITES = ROOT / "op-sites.tsv"
PPCPU = ROOT / "model/ppcpu-combined"
MIRROR_SOURCE = pathlib.Path("/private/tmp/phase_mirror/src/main.rs")
MIRROR = pathlib.Path("/private/tmp/phase_mirror/target/release/phase_mirror")
NONCE_SPEC = (
    "3c1a49cdde48f804c4e35bd0501d7d8d7f46f15e:"
    ".lane/q1273-wrap-exact/D32.nonces"
)
EXPECTED_NONCE_SHA256 = "62bca2420f684c718e52b516dc850f05d72c33f64798002fe2afd215642a0f90"
SEALED_MODEL_COMMIT = "08a9da2093bd5fececbaebc7569de55b12243d9f"
PRE_REVEAL_SEAL = "613a2320ef412d9753f0a7add7ae55e32d807fd5"
EXPECTED = {
    OPS: "590cb55deb75af4ab9356fce97308b4ca4dc10ac031d4fd6d16464e8515972fa",
    SITES: "56e084c152701707310c6822f7b914652a5d17d2352efd2255fd513492a0b4ce",
    PPCPU: "5c2dc3f4c2be8df9a88d60448e17b65ae3073c285e68f41feaccec96f6f74021",
    MIRROR_SOURCE: "26d2a045d048025ce086b099b41fdfc7c42a2657426c59d5fdb95be9cacd8d98",
    MIRROR: "90e4db8669c03b259c13b259018134b754faa94adfbc1e491a601f1052cd6402",
    ROOT / "model/phase-meta.tsv":
        "665e64bb22d87ba629a133f7c67813c284a7fca47d1b6212914c83abe0f5fa1e",
    ROOT / "model/pp_phase_schedule.h":
        "49f82e4effec2c110fed73974df306cbcae9ac456043cb329bb15a7b5e97f4e8",
    ROOT / "h64-model-v1/RESULTS.tsv":
        "3819de96a6d5351a53a8bd6b45371467cc2fa8f5ee7b5162fc34239391e2e6d7",
    REPO / ".lane/q1271-target0-predictor/src/pp_model.h":
        "46e227f7920f43e8d233791dfefd01858cff39c24807d17ed2b390befa0bb390",
    REPO / ".lane/q1271-target0-predictor/src/pp_host.h":
        "7d432431c1d27854f6dff6b0ff807da0241deabf3b3dccc63c53b09e8b7fee8b",
    REPO / ".lane/q1271-target0-predictor/src/ppcpu.cpp":
        "0e10386e356f0a21e7a89bdf8445309d14641a94fe707fe788dd777727f796ba",
}
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
    raise SystemExit(f"qualify-d32: {message}")


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


def evaluate(nonce: int, directory: pathlib.Path) -> tuple[int, int, int, str]:
    directory.mkdir()
    attrib = directory / "attrib.tsv"
    oracle = subprocess.run(
        [str(MIRROR), str(OPS), str(SITES), str(nonce), str(attrib)],
        cwd=REPO, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    (directory / "oracle.stdout").write_bytes(oracle.stdout)
    (directory / "oracle.stderr").write_bytes(oracle.stderr)
    lines = oracle.stdout.decode("ascii").splitlines()
    summary = [line for line in lines if line.startswith("MIRROR ")]
    if len(summary) != 1 or (match := MIRROR_RE.match(summary[0])) is None:
        fail(f"nonce {nonce}: malformed oracle summary")
    got_nonce, qubits, shots, cls, _batches, raw_phase, ancilla = map(int, match.groups())
    if (got_nonce, qubits, shots, ancilla) != (nonce, 1271, 9024, 0):
        fail(f"nonce {nonce}: oracle geometry mismatch")
    oracle_classical = parse_indices(lines, "CLASSICAL_SHOT ")
    oracle_phase = parse_indices(lines, "CLEAN_PHASE_SHOT ")
    if len(oracle_classical) != cls or len(oracle_phase) > raw_phase:
        fail(f"nonce {nonce}: oracle mask/summary mismatch")
    if set(oracle_classical) & set(oracle_phase):
        fail(f"nonce {nonce}: conditional-phase mask intersects classical")
    attrib_rows = attrib.read_text(encoding="ascii").splitlines()
    if any(row.split("\t", 1)[0] != str(nonce) for row in attrib_rows):
        fail(f"nonce {nonce}: attribution nonce mismatch")

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
        (directory / f"{name}.stdout").write_bytes(result.stdout)
        (directory / f"{name}.stderr").write_bytes(result.stderr)
    model_classical = []
    for line in classical.stdout.decode("ascii").splitlines():
        fields = line.split()
        if len(fields) != 2 or any(not field.isdecimal() for field in fields):
            fail(f"nonce {nonce}: malformed model classical output")
        model_classical.append(int(fields[0]))
    model_phase_lines = phase.stdout.decode("ascii").splitlines()
    if any(not line.isdecimal() for line in model_phase_lines):
        fail(f"nonce {nonce}: malformed model phase output")
    model_phase = [int(line) for line in model_phase_lines]
    if model_classical != oracle_classical:
        fail(f"nonce {nonce}: complete classical mask mismatch")
    if model_phase != oracle_phase:
        fail(f"nonce {nonce}: complete conditional-phase mask mismatch")

    names = (
        "attrib.tsv", "oracle.stdout", "oracle.stderr",
        "model-classical.stdout", "model-classical.stderr",
        "model-phase.stdout", "model-phase.stderr",
    )
    sums = directory / "SHA256SUMS"
    sums.write_text(
        "".join(f"{sha256(directory / name)}  {name}\n" for name in names),
        encoding="ascii", newline="\n",
    )
    return len(oracle_classical), raw_phase, len(oracle_phase), sha256(sums)


def compare_exact(left: pathlib.Path, right: pathlib.Path, names: tuple[str, ...]) -> None:
    for name in names:
        if (left / name).read_bytes() != (right / name).read_bytes():
            fail(f"deterministic repeat mismatch: {left.name}/{name}")


def main() -> None:
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=REPO, check=True,
        stdout=subprocess.PIPE,
    ).stdout
    if status:
        fail("worktree is not clean before holdout reveal")
    for commit in (SEALED_MODEL_COMMIT, PRE_REVEAL_SEAL):
        if subprocess.run(
            ["git", "merge-base", "--is-ancestor", commit, "HEAD"], cwd=REPO,
        ).returncode != 0:
            fail(f"required seal is not an ancestor: {commit}")
    for path, expected in EXPECTED.items():
        if not path.is_file() or sha256(path) != expected:
            fail(f"immutable input missing or drifted: {path}")
    if OUT.exists():
        fail(f"output already exists: {OUT}")

    raw = subprocess.run(
        ["git", "show", NONCE_SPEC], cwd=REPO, check=True,
        stdout=subprocess.PIPE,
    ).stdout
    if sha256_bytes(raw) != EXPECTED_NONCE_SHA256:
        fail("D32 nonce-list SHA-256 mismatch")
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        fail(f"D32 list is not ASCII: {exc}")
    if not text.endswith("\n"):
        fail("D32 list is not LF-terminated")
    lines = text.splitlines()
    if len(lines) != 32 or any(
        not line.isdecimal() or (line.startswith("0") and line != "0")
        for line in lines
    ):
        fail("D32 list is not 32 canonical decimal rows")
    nonces = tuple(map(int, lines))
    if len(set(nonces)) != 32 or any(nonce >= 1 << 48 for nonce in nonces):
        fail("D32 contains duplicates or a value outside 48 bits")
    forbidden = {65700024945645, *range(444_000_000_000, 444_000_000_064)}
    if set(nonces) & forbidden:
        fail("D32 overlaps inherited or H64")

    OUT.mkdir()
    (OUT / "D32.nonces").write_bytes(raw)
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(evaluate, nonce, OUT / str(nonce)): (index, nonce)
            for index, nonce in enumerate(nonces)
        }
        for future in concurrent.futures.as_completed(futures):
            index, nonce = futures[future]
            classical, raw_phase, conditional_phase, manifest = future.result()
            rows.append((index, nonce, classical, raw_phase, conditional_phase, manifest))
            print(
                f"qualify-d32: PASS row={index} classical={classical} "
                f"raw_phase={raw_phase} conditional_phase={conditional_phase}",
                flush=True,
            )
    rows.sort()
    if tuple(row[1] for row in rows) != nonces:
        fail("D32 result order differs from frozen list")

    repeat_root = OUT / "repeats"
    repeat_root.mkdir()
    evaluate(65700024945645, repeat_root / "inherited")
    compare_exact(
        ROOT / "inherited", repeat_root / "inherited",
        ("attrib.tsv", "oracle.stdout"),
    )
    compare_exact(
        ROOT / "h64-model-v1/inherited", repeat_root / "inherited",
        ("model-classical.stdout", "model-classical.stderr",
         "model-phase.stdout", "model-phase.stderr"),
    )
    evaluate(nonces[-1], repeat_root / "final-d32")
    compare_exact(
        OUT / str(nonces[-1]), repeat_root / "final-d32",
        ("attrib.tsv", "oracle.stdout", "oracle.stderr",
         "model-classical.stdout", "model-classical.stderr",
         "model-phase.stdout", "model-phase.stderr"),
    )

    results = [
        "row\tnonce\tclassical\traw_phase\tconditional_phase\tartifact_manifest_sha256"
    ]
    results.extend("\t".join(map(str, row)) for row in rows)
    result_path = OUT / "RESULTS.tsv"
    result_path.write_text("\n".join(results) + "\n", encoding="ascii", newline="\n")
    repeat_rows = []
    for path in sorted(repeat_root.rglob("*")):
        if path.is_file():
            repeat_rows.append(f"{sha256(path)}  {path.relative_to(repeat_root)}")
    repeat_manifest = OUT / "REPEATS.sha256"
    repeat_manifest.write_text("\n".join(repeat_rows) + "\n", encoding="ascii", newline="\n")
    totals = tuple(sum(row[index] for row in rows) for index in (2, 3, 4))
    print(
        f"qualify-d32: PASS exact=32/32 totals_classical_raw_conditional={totals} "
        f"results_sha256={sha256(result_path)} "
        f"repeats_sha256={sha256(repeat_manifest)}",
        flush=True,
    )


if __name__ == "__main__":
    main()
