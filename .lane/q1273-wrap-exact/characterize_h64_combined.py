#!/usr/bin/env python3
"""Run the predeclared fixed-H64 combined CPU density characterization."""

from __future__ import annotations

import concurrent.futures
import hashlib
import json
import math
import os
import pathlib
import re
import statistics
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
OPS_ROOT = pathlib.Path("/Users/olifreuler/ecdsa-ops")
PACKET = OPS_ROOT / "q1273-predictor-093d85d"
OPS = PACKET / "ops.bin"
BINARY = pathlib.Path("/private/tmp/ppcpu-q1273-combined-final")
OUT = OPS_ROOT / "q1273-wrap-exact-ea6a02f/h64-combined-density"
NONCES = tuple(444_000_000_000 + i for i in range(64))
MAX_WORKERS = 4

HASHES = {
    ROOT / ".lane/q1273-predictor/src/pp_model.h":
        "14fc9230b55d2b2a84721e50d860933764a18d1357ad30331e5999280f764261",
    ROOT / ".lane/q1273-predictor/src/ppcpu.cpp":
        "1d93d46803670324401443ed9f625ee641c6fa8ef77ba4a920baebff83ea24ce",
    ROOT / ".lane/q1273-phase/src/pp_phase_schedule.h":
        "4249864aca9e2928a33865ea086b99ef8ecccc9eb596ba4c3e57468ba88d25e5",
    PACKET / "h64/fixtures.tsv":
        "7918937a30d562a2dd26cf59374cdb702c11ce0f08d42789f9ef42da8264b5f4",
    OPS_ROOT / "q1273-wrap-exact-ea6a02f/combined-cpu/MANIFEST.sha256":
        "c1088ca0e3bf0d9215f63b6823bf490d408ba46e2cf3271d35c40b449d5fe847",
    OPS: "ee6448dbb23aa877123733724b109266e584f1ba14abf5c38b43b9ab6aa26cd1",
    BINARY: "2234a6cfc61dfb996fdfe757b506dcc5a4917662477cbcdc7894659ce6c098c7",
}


def sha(raw_or_path: bytes | pathlib.Path) -> str:
    raw = raw_or_path if isinstance(raw_or_path, bytes) else raw_or_path.read_bytes()
    return hashlib.sha256(raw).hexdigest()


def parse_classical(raw: bytes) -> tuple[tuple[int, int], ...]:
    rows: list[tuple[int, int]] = []
    for line in raw.decode("ascii").splitlines():
        fields = line.split()
        if len(fields) != 2 or not all(field.isdecimal() for field in fields):
            raise ValueError(f"malformed classical row: {line!r}")
        shot, mask = map(int, fields)
        if shot >= 9024 or mask not in (1, 2, 4, 8, 16):
            raise ValueError(f"out-of-contract classical row: {line!r}")
        if rows and shot <= rows[-1][0]:
            raise ValueError("classical shots are not strictly increasing")
        rows.append((shot, mask))
    return tuple(rows)


def parse_phase(raw: bytes) -> tuple[int, ...]:
    rows: list[int] = []
    for line in raw.decode("ascii").splitlines():
        if not line.isdecimal():
            raise ValueError(f"malformed phase row: {line!r}")
        shot = int(line)
        if shot >= 9024 or (rows and shot <= rows[-1]):
            raise ValueError(f"out-of-contract phase row: {line!r}")
        rows.append(shot)
    return tuple(rows)


def run_selector(selector: str, nonce: int) -> tuple[bytes, bytes]:
    env = os.environ.copy()
    env["PPF_OPS"] = str(OPS)
    result = subprocess.run(
        [str(BINARY), selector, str(nonce)], env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise RuntimeError(f"{selector}/{nonce} returned {result.returncode}")
    return result.stdout, result.stderr


def run_one(nonce: int, scratch: pathlib.Path) -> dict[str, object]:
    row_dir = scratch / str(nonce)
    row_dir.mkdir()
    classical_raw, classical_stderr = run_selector("faultshots", nonce)
    phase_raw, phase_stderr = run_selector("phasefaultshots", nonce)
    classical = parse_classical(classical_raw)
    phase = parse_phase(phase_raw)

    expected_path = PACKET / f"h64/{nonce}/evaluator.shots"
    expected = tuple(int(line) for line in expected_path.read_text().splitlines())
    actual = tuple(shot for shot, _ in classical)
    if actual != expected:
        raise RuntimeError(f"trusted classical set mismatch for {nonce}")
    stderr_text = phase_stderr.decode("utf-8")
    if "source=093d85d64de87aa5006a94868172f642daacf136" not in stderr_text:
        raise RuntimeError(f"missing source bind for {nonce}")
    if "contract=phase&~classical raw_phase=not-claimed cuda_phase=not-claimed" not in stderr_text:
        raise RuntimeError(f"missing conditional contract for {nonce}")
    match = re.search(r" classical=(\d+) clean_phase=(\d+) ", stderr_text)
    if not match or tuple(map(int, match.groups())) != (len(classical), len(phase)):
        raise RuntimeError(f"stderr count bind mismatch for {nonce}")

    artifacts = {
        "classical.raw": classical_raw,
        "classical.stderr": classical_stderr,
        "phase.raw": phase_raw,
        "phase.stderr": phase_stderr,
    }
    for name, raw in artifacts.items():
        (row_dir / name).write_bytes(raw)
    c = len(classical)
    p = len(phase)
    receipt = {
        "nonce": nonce,
        "classical_faults": c,
        "conditional_phase_faults": p,
        "joint_faults": c + p,
        "classical_zero": c == 0,
        "phase_zero_among_classical_zero": c == 0 and p == 0,
        "joint_zero": c == 0 and p == 0,
        "classical_stdout_sha256": sha(classical_raw),
        "phase_stdout_sha256": sha(phase_raw),
        "classical_stderr_sha256": sha(classical_stderr),
        "phase_stderr_sha256": sha(phase_stderr),
    }
    (row_dir / "receipt.json").write_text(
        json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n"
    )
    return receipt


def main() -> None:
    if OUT.exists():
        raise SystemExit(f"characterize-h64: output already exists: {OUT}")
    for path, expected in HASHES.items():
        actual = sha(path)
        if actual != expected:
            raise SystemExit(f"characterize-h64: hash drift {path}: {actual}")
    if int.from_bytes(OPS.read_bytes()[8:16], "little") != 12_933_805:
        raise SystemExit("characterize-h64: ops count drift")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    scratch = pathlib.Path(tempfile.mkdtemp(prefix="h64-combined.tmp.", dir=OUT.parent))
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = {pool.submit(run_one, nonce, scratch): nonce for nonce in NONCES}
            rows = [future.result() for future in concurrent.futures.as_completed(futures)]
        rows.sort(key=lambda row: int(row["nonce"]))
        if tuple(int(row["nonce"]) for row in rows) != NONCES:
            raise RuntimeError("nonce set/order drift")

        # Determinism is checked only on the first frozen nonce; no extra nonce
        # is touched.  Compare all selector output streams byte-for-byte.
        repeat_dir = scratch / "repeat-444000000000"
        repeat_dir.mkdir()
        for selector, stem in (("faultshots", "classical"),
                               ("phasefaultshots", "phase")):
            stdout, stderr = run_selector(selector, NONCES[0])
            (repeat_dir / f"{stem}.raw").write_bytes(stdout)
            (repeat_dir / f"{stem}.stderr").write_bytes(stderr)
            if stdout != (scratch / str(NONCES[0]) / f"{stem}.raw").read_bytes():
                raise RuntimeError(f"{stem} stdout nondeterminism")
            if stderr != (scratch / str(NONCES[0]) / f"{stem}.stderr").read_bytes():
                raise RuntimeError(f"{stem} stderr nondeterminism")

        c_values = [int(row["classical_faults"]) for row in rows]
        p_values = [int(row["conditional_phase_faults"]) for row in rows]
        j_values = [int(row["joint_faults"]) for row in rows]
        lambda_c = statistics.mean(c_values)
        lambda_p = statistics.mean(p_values)
        lambda_j = statistics.mean(j_values)
        sd_j = statistics.stdev(j_values)
        lambda_upper = lambda_j + 2.0 * sd_j / math.sqrt(len(rows))
        p0_lower = math.exp(-lambda_upper)
        n95 = math.ceil(math.log(20.0) / p0_lower)
        n95_power2 = 1 << (n95 - 1).bit_length()
        summary = {
            "nonce_from": NONCES[0],
            "nonce_to": NONCES[-1],
            "rows": len(rows),
            "classical_faults_total": sum(c_values),
            "conditional_phase_faults_total": sum(p_values),
            "joint_faults_total": sum(j_values),
            "lambda_classical_mean": lambda_c,
            "lambda_conditional_phase_mean": lambda_p,
            "lambda_joint_mean": lambda_j,
            "joint_row_sample_sd": sd_j,
            "lambda_joint_upper_2se": lambda_upper,
            "poisson_p0_lower": p0_lower,
            "poisson_n95": n95,
            "poisson_n95_next_power_of_two": n95_power2,
            "classical_zero_count": sum(bool(row["classical_zero"]) for row in rows),
            "phase_zero_among_classical_zero_count": sum(
                bool(row["phase_zero_among_classical_zero"]) for row in rows
            ),
            "joint_predicted_zero_count": sum(bool(row["joint_zero"]) for row in rows),
            "phase_h64_truth_status": "model-prediction-only",
            "provider_range_hunt_submission": "none",
        }

        header = (
            "nonce\tclassical_faults\tconditional_phase_faults\tjoint_faults\t"
            "classical_zero\tphase_zero_among_classical_zero\tjoint_zero\t"
            "classical_stdout_sha256\tphase_stdout_sha256\t"
            "classical_stderr_sha256\tphase_stderr_sha256\n"
        )
        with (scratch / "rows.tsv").open("w") as stream:
            stream.write(header)
            for row in rows:
                stream.write("\t".join(str(row[key]) for key in (
                    "nonce", "classical_faults", "conditional_phase_faults",
                    "joint_faults", "classical_zero",
                    "phase_zero_among_classical_zero", "joint_zero",
                    "classical_stdout_sha256", "phase_stdout_sha256",
                    "classical_stderr_sha256", "phase_stderr_sha256",
                )) + "\n")
        (scratch / "summary.json").write_text(
            json.dumps(summary, sort_keys=True, indent=2) + "\n"
        )
        files = sorted(path for path in scratch.rglob("*") if path.is_file())
        with (scratch / "MANIFEST.sha256").open("w") as manifest:
            for path in files:
                manifest.write(f"{sha(path)}  {path.relative_to(scratch)}\n")
        os.replace(scratch, OUT)
    except BaseException:
        raise

    print(f"rows_sha256={sha(OUT / 'rows.tsv')}")
    print(f"summary_sha256={sha(OUT / 'summary.json')}")
    print(f"manifest_sha256={sha(OUT / 'MANIFEST.sha256')}")
    print((OUT / "summary.json").read_text(), end="")


if __name__ == "__main__":
    main()
