#!/usr/bin/env python3
"""Qualify the exact Q1271 combined CPU model's fail-closed boundary."""

from __future__ import annotations

import hashlib
import os
import pathlib
import shutil
import struct
import subprocess


REPO = pathlib.Path(__file__).resolve().parents[3]
LANE = REPO / ".lane/q1271-target0-predictor"
ROOT = pathlib.Path("/Users/olifreuler/ecdsa-ops/q1271-target0-sign-alias-590cb55d")
OUT = ROOT / "negatives-v1"
OPS = ROOT / "target/ops.bin"
PPCPU = ROOT / "model/ppcpu-combined"
PHASE_HEADER = ROOT / "model/pp_phase_schedule.h"
SOURCE = LANE / "src/ppcpu.cpp"
MODEL_SOURCE = LANE / "src/pp_model.h"
HOST_SOURCE = LANE / "src/pp_host.h"
D32_SEAL = "18bb4547c0889410440e9f3cb00df02819cb7327"
NONCE = "65700024945645"
EXPECTED_STATE = "a05fe6ce236b1bfc"
EXPECTED_OPS_COUNT = 12_919_161
EXPECTED = {
    OPS: "590cb55deb75af4ab9356fce97308b4ca4dc10ac031d4fd6d16464e8515972fa",
    PPCPU: "5c2dc3f4c2be8df9a88d60448e17b65ae3073c285e68f41feaccec96f6f74021",
    PHASE_HEADER: "49f82e4effec2c110fed73974df306cbcae9ac456043cb329bb15a7b5e97f4e8",
    ROOT / "model/phase-meta.tsv":
        "665e64bb22d87ba629a133f7c67813c284a7fca47d1b6212914c83abe0f5fa1e",
    MODEL_SOURCE: "46e227f7920f43e8d233791dfefd01858cff39c24807d17ed2b390befa0bb390",
    HOST_SOURCE: "7d432431c1d27854f6dff6b0ff807da0241deabf3b3dccc63c53b09e8b7fee8b",
    SOURCE: "0e10386e356f0a21e7a89bdf8445309d14641a94fe707fe788dd777727f796ba",
    ROOT / "d32-v1/RESULTS.tsv":
        "b95a6aa454329b6f85a37e88859b755c961e3502e981c4dc6aec34fbd652b8d3",
}


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"qualify-negatives: {message}")


def write_bytes(path: pathlib.Path, data: bytes) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def compile_negative(output: pathlib.Path, define: str) -> None:
    command = [
        "c++", "-std=c++17", "-O3", define, "-I", str(ROOT / "model"),
        str(SOURCE), "-o", str(output),
    ]
    result = subprocess.run(
        command, cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        timeout=300,
    )
    if result.returncode != 0 or result.stdout:
        fail(
            f"negative binary compile failed for {output.name}: "
            f"rc={result.returncode} stdout={result.stdout!r} stderr={result.stderr!r}"
        )
    write_bytes(output.with_suffix(".compile.stderr"), result.stderr)
    write_bytes(
        output.with_suffix(".compile.argv"),
        ("\n".join(command) + "\n").encode("utf-8"),
    )


def main() -> None:
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=REPO, check=True,
        stdout=subprocess.PIPE,
    ).stdout
    if status:
        fail("worktree is not clean before the fixed negative matrix")
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", D32_SEAL, "HEAD"], cwd=REPO,
    )
    if ancestor.returncode != 0:
        fail("sealed D32 evidence is not an ancestor")
    for path, expected in EXPECTED.items():
        if not path.is_file() or sha256(path) != expected:
            fail(f"immutable input missing or drifted: {path}")
    if OUT.exists():
        fail(f"output already exists: {OUT}")

    OUT.mkdir()
    compiler = subprocess.run(
        ["c++", "--version"], check=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    ).stdout
    write_bytes(OUT / "COMPILER.txt", compiler)

    bad_magic = OUT / "bad-magic.bin"
    wrong_count = OUT / "wrong-count.bin"
    wrong_sha = OUT / "wrong-sha.bin"
    for target in (bad_magic, wrong_count, wrong_sha):
        shutil.copyfile(OPS, target)
    with bad_magic.open("r+b") as stream:
        stream.write(b"X")
    with wrong_count.open("r+b") as stream:
        stream.seek(8)
        stream.write(struct.pack("<Q", EXPECTED_OPS_COUNT + 1))
    with wrong_sha.open("r+b") as stream:
        stream.seek(-1, os.SEEK_END)
        final = stream.read(1)
        stream.seek(-1, os.SEEK_END)
        stream.write(bytes((final[0] ^ 1,)))

    wrong_state_binary = OUT / "ppcpu-wrong-state"
    bad_schedule_binary = OUT / "ppcpu-bad-schedule"
    compile_negative(
        wrong_state_binary,
        "-DPP_EXPECTED_STATE_DIGEST_VALUE=0xa05fe6ce236b1bfdULL",
    )
    compile_negative(bad_schedule_binary, "-DPP_PHASE_FORCE_BAD_SCHEDULE=1")

    identities = []
    for path in sorted((*EXPECTED, bad_magic, wrong_count, wrong_sha,
                        wrong_state_binary, bad_schedule_binary)):
        identities.append(f"{sha256(path)}  {path}")
    identity_path = OUT / "IDENTITIES.sha256"
    write_bytes(identity_path, ("\n".join(identities) + "\n").encode("ascii"))

    env = dict(os.environ, PPF_OPS=str(OPS))
    positive = subprocess.run(
        [str(PPCPU), "statedigest"], cwd=REPO, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300,
    )
    write_bytes(OUT / "positive-state.stdout", positive.stdout)
    write_bytes(OUT / "positive-state.stderr", positive.stderr)
    if positive.returncode != 0 or positive.stdout != (EXPECTED_STATE + "\n").encode():
        fail("positive state/checkpoint control did not reproduce exactly")

    cases: list[tuple[str, pathlib.Path, list[str], str]] = [
        ("bad-magic", bad_magic, ["identity"], "ppgpu: bad ops magic"),
        (
            "wrong-count", wrong_count, ["identity"],
            "ppcpu: FATAL: ops stream op count 12919162 != expected 12919161",
        ),
        (
            "same-count-wrong-sha", wrong_sha, ["identity"],
            "ppgpu: FATAL: ops stream sha256",
        ),
        (
            "wrong-state", OPS, ["identity"],
            "ppcpu: FATAL: ops stream state digest a05fe6ce236b1bfc != expected "
            "a05fe6ce236b1bfd",
        ),
        (
            "bad-phase-schedule", OPS, ["phasefaultshots", NONCE],
            "ppcpu: FATAL: phase schedule mismatch at shot",
        ),
        (
            "missing-stream", OUT / "definitely-missing-ops.bin", ["identity"],
            "ppgpu: cannot open ops file",
        ),
    ]

    parser_cases: list[tuple[str, list[str], str]] = [
        ("scan-mode", ["scan", "0", "1"],
         "ppcpu: scan mode disabled in bounded qualification build"),
        ("range-mode", ["range", "0", "1"], "unknown mode range"),
        ("unknown-mode", ["frobnicate"], "unknown mode frobnicate"),
        ("missing-mode-argument", ["faultshots"],
         "ppcpu: expected one canonical 48-bit nonce"),
        ("extra-mode-argument", ["faultshots", NONCE, "extra"],
         "ppcpu: expected one canonical 48-bit nonce"),
        ("extra-identity-argument", ["identity", "extra"],
         "ppcpu: unexpected arguments for identity"),
        ("nonce-empty", ["faultshots", ""],
         "ppcpu: expected one canonical 48-bit nonce"),
        ("nonce-leading-zero", ["faultshots", "01"],
         "ppcpu: expected one canonical 48-bit nonce"),
        ("nonce-signed", ["faultshots", "-1"],
         "ppcpu: expected one canonical 48-bit nonce"),
        ("nonce-2pow48", ["faultshots", "281474976710656"],
         "ppcpu: expected one canonical 48-bit nonce"),
        ("nonce-u64-overflow", ["faultshots", "18446744073709551616"],
         "ppcpu: expected one canonical 48-bit nonce"),
        ("nonce-alphabetic", ["faultshots", "not-a-nonce"],
         "ppcpu: expected one canonical 48-bit nonce"),
        ("shot-missing", ["shot", NONCE],
         "ppcpu: expected a canonical 48-bit nonce and shot index"),
        ("shot-9024", ["shot", NONCE, "9024"],
         "ppcpu: expected a canonical 48-bit nonce and shot index"),
        ("shot-leading-zero", ["shot", NONCE, "01"],
         "ppcpu: expected a canonical 48-bit nonce and shot index"),
        ("shot-signed", ["shot", NONCE, "-1"],
         "ppcpu: expected a canonical 48-bit nonce and shot index"),
        ("shot-alphabetic", ["shot", NONCE, "x"],
         "ppcpu: expected a canonical 48-bit nonce and shot index"),
    ]
    if len(cases) + len(parser_cases) != 23:
        fail("internal case-count drift")

    rows = ["case\treturncode\tstdout_sha256\tstderr_sha256\tguard\tstatus"]

    def run_case(
        name: str, binary: pathlib.Path, ops: pathlib.Path, argv: list[str], guard: str,
    ) -> None:
        case_env = dict(os.environ, PPF_OPS=str(ops))
        result = subprocess.run(
            [str(binary), *argv], cwd=REPO, env=case_env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300,
        )
        stdout_path = OUT / f"{name}.stdout"
        stderr_path = OUT / f"{name}.stderr"
        write_bytes(stdout_path, result.stdout)
        write_bytes(stderr_path, result.stderr)
        decoded = result.stderr.decode("utf-8", errors="replace")
        if result.returncode == 0:
            fail(f"{name} unexpectedly returned zero")
        if result.stdout:
            fail(f"{name} violated empty-stdout fail-closed contract")
        if decoded.count(guard) != 1:
            fail(f"{name} did not emit its required guard exactly once: {decoded!r}")
        rows.append(
            "\t".join((name, str(result.returncode), sha256(stdout_path),
                        sha256(stderr_path), guard, "PASS"))
        )

    for name, case_ops, argv, guard in cases:
        binary = PPCPU
        if name == "wrong-state":
            binary = wrong_state_binary
        elif name == "bad-phase-schedule":
            binary = bad_schedule_binary
        run_case(name, binary, case_ops, argv, guard)
    for name, argv, guard in parser_cases:
        run_case(name, PPCPU, OPS, argv, guard)

    receipt = OUT / "receipt.tsv"
    write_bytes(receipt, ("\n".join(rows) + "\n").encode("utf-8"))
    if len(rows) != 24:
        fail("terminal receipt does not contain exactly 23 negatives")

    for path, expected in EXPECTED.items():
        if sha256(path) != expected:
            fail(f"immutable source/input changed during matrix: {path}")
    if subprocess.run(
        ["git", "status", "--porcelain"], cwd=REPO, check=True,
        stdout=subprocess.PIPE,
    ).stdout:
        fail("worktree changed during negative matrix")

    manifest_rows = []
    for path in sorted(OUT.iterdir()):
        if path.is_file() and path.name not in {"MANIFEST.sha256", "PASS"}:
            manifest_rows.append(f"{sha256(path)}  {path.name}")
    manifest = OUT / "MANIFEST.sha256"
    write_bytes(manifest, ("\n".join(manifest_rows) + "\n").encode("ascii"))
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO, check=True,
        stdout=subprocess.PIPE, text=True,
    ).stdout.strip()
    marker = (
        "PASS_23_OF_23_NEGATIVES\n"
        f"head={head}\n"
        f"receipt_sha256={sha256(receipt)}\n"
        f"identities_sha256={sha256(identity_path)}\n"
        f"manifest_sha256={sha256(manifest)}\n"
    )
    write_bytes(OUT / "PASS", marker.encode("ascii"))
    print(
        "qualify-negatives: PASS 23/23 "
        f"receipt_sha256={sha256(receipt)} "
        f"identities_sha256={sha256(identity_path)} "
        f"manifest_sha256={sha256(manifest)} "
        f"marker_sha256={sha256(OUT / 'PASS')}",
        flush=True,
    )


if __name__ == "__main__":
    main()
