#!/usr/bin/env python3
"""Fail-closed local parity gate for the frozen Q1272 reversible program."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import os
import pathlib
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass


REPO = pathlib.Path(__file__).resolve().parents[3]
LANE = REPO / ".lane/q1272-combined-unit-parity"
CLASSICAL = REPO / ".lane/q1272-promoted-predictor"
COMBINED = REPO / ".lane/q1272-live-phase"
OPS = pathlib.Path(
    "/Users/olifreuler/Documents/Codex/2026-08-21/par/work/"
    "q1272-live-phase-screen/ops.bin"
)
FIXTURE_ROOT = pathlib.Path("/Users/olifreuler/ecdsa-ops/q1272-live-phase-ea19759d")
SITES = FIXTURE_ROOT / "op-sites.tsv"
SCHEDULE = FIXTURE_ROOT / "pp_phase_schedule.h"
MIRROR_SOURCE = pathlib.Path("/private/tmp/phase_mirror/src/main.rs")
MIRROR = pathlib.Path("/private/tmp/phase_mirror/target/release/phase_mirror")

SOURCE_COMMIT = "73422709ed70ba9725b3cb592770bcf197df4cdb"
STATE_DIGEST = "e9b2d20ecd1169a8"
SHOTS = 9024
WORDS = (SHOTS + 63) // 64
MAX_NONCE = 1 << 48

EXPECTED_HASHES = {
    OPS: "ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1",
    SITES: "f2f0f99d096027299460d9a82c16d3714c9684564d10f13f6dcbbac2b3e92833",
    SCHEDULE: "de37d6004427082c345004d1225d0f877abfe9597ac969df228b77eb915fe42f",
    MIRROR_SOURCE: "26d2a045d048025ce086b099b41fdfc7c42a2657426c59d5fdb95be9cacd8d98",
    MIRROR: "90e4db8669c03b259c13b259018134b754faa94adfbc1e491a601f1052cd6402",
    CLASSICAL / "src/pp_model.h":
        "d417865bcc119686dc2d9a3d45ca8e801332cf824c8ed95aefb5e0195f1318b2",
    CLASSICAL / "src/pp_host.h":
        "b635c95deb5bab2b89ea65de4dafdba22ea4184a647c82d4bb5680450f976435",
    CLASSICAL / "src/ppcpu.cpp":
        "37550fe3d8d1f1130cdc03a746ed5b4ea6bdb619475eebcddaeb087342457352",
    COMBINED / "src/pp_model.h":
        "0d4c9a812892b9dac598cb59a8345c443b9e21663ac29743578f4e651b39b92a",
    COMBINED / "src/pp_host.h":
        "aa546788a823268cf311d88f028b80dd12826162fe220848ae46ec165b6190a2",
    COMBINED / "src/ppcpu.cpp":
        "dd05545d33911e7e0ab44b0e373f03a759ae8ee4b990f20f2cc40ca6ee2063af",
    CLASSICAL / "H64.nonces":
        "17443162349d50e521b0c9a20904de5a0212a668e6f3ae7ea0e2702b2f79c4b9",
    CLASSICAL / "D32.nonces":
        "45838602350ecabd4c95d900602d440692e57bffd2581160e1f151ccdb4cc79c",
    CLASSICAL / "V64.nonces":
        "9db8b3a0fc0f277f8cea77cac181cc6133a667c96d5e73a97397a7116a6ec1bd",
    CLASSICAL / "W64.nonces":
        "db43f935ec97561cdab7f1e0c86d11ea439f9b75f0da815a7a92b999bc5575a0",
    LANE / "F32.nonces":
        "8d93cbf5e871f1ec8cab5768835c5c60a78a94fbc71611a96248a4248dc450ec",
    FIXTURE_ROOT / "inherited-oracle.txt":
        "230ce787840da6838ae7632851d4a7109d4ab1fda4e802c872eed38c91e1c3b2",
    FIXTURE_ROOT / "h64/RESULTS.tsv":
        "0b05b359ac2f9fc23e81163adcf8047aa28fd514c5ecd581a0416a07ee1b9ccc",
}

CORPUS_LENGTHS = {"inherited": 1, "H64": 64, "D32": 32, "V64": 64, "F32": 32}
SUMMARY_RE = re.compile(
    r"^MIRROR nonce=(\d+) qubits=(\d+) shots=(\d+) cls=(\d+) "
    r"phase_batches=(\d+) phase_shots=(\d+) ancilla=(\d+) "
)


def fail(message: str) -> None:
    raise RuntimeError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_hashes() -> None:
    for path, expected in EXPECTED_HASHES.items():
        if not path.is_file():
            fail(f"missing immutable input: {path}")
        actual = sha256(path)
        if actual != expected:
            fail(f"input drift: {path}: {actual} != {expected}")


def read_canonical_nonces(path: pathlib.Path, expected: int) -> tuple[int, ...]:
    raw = path.read_bytes()
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        fail(f"non-ASCII corpus {path}: {exc}")
    if not text.endswith("\n") or "\r" in text:
        fail(f"corpus is not canonical LF text: {path}")
    lines = text.splitlines()
    if len(lines) != expected:
        fail(f"corpus length drift: {path}: {len(lines)} != {expected}")
    if any(not row.isdecimal() or (row.startswith("0") and row != "0") for row in lines):
        fail(f"malformed nonce in {path}")
    values = tuple(map(int, lines))
    if values != tuple(sorted(set(values))) or any(value >= MAX_NONCE for value in values):
        fail(f"corpus is duplicate, unordered, or outside 48 bits: {path}")
    return values


def load_corpora() -> dict[str, tuple[int, ...]]:
    corpora = {
        "inherited": (65700024945645,),
        "H64": read_canonical_nonces(CLASSICAL / "H64.nonces", 64),
        "D32": read_canonical_nonces(CLASSICAL / "D32.nonces", 32),
        "V64": read_canonical_nonces(CLASSICAL / "V64.nonces", 64),
        "F32": read_canonical_nonces(LANE / "F32.nonces", 32),
    }
    owner: dict[int, str] = {}
    for name, values in corpora.items():
        if len(values) != CORPUS_LENGTHS[name]:
            fail(f"internal corpus size mismatch: {name}")
        for value in values:
            if value in owner:
                fail(f"corpus overlap: nonce {value} in {owner[value]} and {name}")
            owner[value] = name
    prior_w64 = read_canonical_nonces(CLASSICAL / "W64.nonces", 64)
    if set(corpora["F32"]) & set(prior_w64):
        fail("fresh F32 overlaps prior W64")
    return corpora


def run(argv: list[str], *, env: dict[str, str] | None = None,
        check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        argv, cwd=REPO, env=env, check=check,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )


def build_binaries(out: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path, pathlib.Path]:
    compiler = shutil.which("clang++")
    if compiler is None:
        fail("clang++ is unavailable")
    include = out / "include"
    include.mkdir()
    shutil.copyfile(SCHEDULE, include / "pp_phase_schedule.h")
    binary_dir = out / "bin"
    binary_dir.mkdir()
    classical = binary_dir / "ppcpu-classical"
    combined = binary_dir / "ppcpu-combined"
    bad_schedule = binary_dir / "ppcpu-bad-schedule"
    run([
        compiler, "-O3", "-std=c++17", "-pthread",
        f"-I{CLASSICAL / 'src'}", str(CLASSICAL / "src/ppcpu.cpp"),
        "-o", str(classical),
    ])
    common = [
        compiler, "-O3", "-std=c++17", f"-I{COMBINED / 'src'}", f"-I{include}",
        str(COMBINED / "src/ppcpu.cpp"),
    ]
    run([*common, "-o", str(combined)])
    run([*common, "-DPP_PHASE_FORCE_BAD_SCHEDULE", "-o", str(bad_schedule)])
    return classical, combined, bad_schedule


def model_env(ops: pathlib.Path = OPS) -> dict[str, str]:
    return dict(os.environ, PPF_OPS=str(ops))


def verify_build_identity(classical: pathlib.Path, combined: pathlib.Path) -> None:
    for binary in (classical, combined):
        digest = run([str(binary), "statedigest"], env=model_env()).stdout.decode("ascii").strip()
        if digest != STATE_DIGEST:
            fail(f"state digest mismatch for {binary.name}: {digest}")
    identity = run([str(combined), "identity"], env=model_env()).stdout.decode("ascii")
    required = (
        f"source_commit={SOURCE_COMMIT}", "ops_count=12904643",
        f"ops_sha256={EXPECTED_HASHES[OPS]}", f"predictor_digest={STATE_DIGEST}",
        "phase_sites=3964", "phase_rhmr=1938616", "shots=9024",
        "contract=phase&~classical",
    )
    if any(token not in identity for token in required):
        fail("combined identity is incomplete or drifted")
    kat = run([str(combined), "shaketest"])
    kat_text = kat.stderr.decode("ascii")
    if "46b9dd2b0ba88d13233b3feb743eeb243fcd52ea62b81b82b50c27646ed5762f" not in kat_text:
        fail("SHAKE256 empty-string KAT missing")
    if "483366601360a8771c6863080cc4114d8db44530f8f1e1ee4f94ea37e78b5739" not in kat_text:
        fail("SHAKE256 abc KAT missing")


def parse_classical(data: bytes, source: str) -> tuple[tuple[int, int], ...]:
    rows: list[tuple[int, int]] = []
    for line in data.decode("ascii").splitlines():
        fields = line.split()
        if len(fields) != 2 or not all(field.isdecimal() for field in fields):
            fail(f"malformed classical row from {source}: {line!r}")
        index, cause = map(int, fields)
        if index >= SHOTS or cause <= 0 or cause >= 32:
            fail(f"out-of-range classical row from {source}: {line!r}")
        rows.append((index, cause))
    if rows != sorted(set(rows)):
        fail(f"non-canonical classical output from {source}")
    return tuple(rows)


def parse_phase(data: bytes, source: str) -> tuple[int, ...]:
    lines = data.decode("ascii").splitlines()
    if any(not line.isdecimal() for line in lines):
        fail(f"malformed phase output from {source}")
    values = tuple(map(int, lines))
    if values != tuple(sorted(set(values))) or any(value >= SHOTS for value in values):
        fail(f"non-canonical phase output from {source}")
    return values


def parse_oracle(data: bytes, nonce: int) -> tuple[tuple[int, ...], tuple[int, ...], int]:
    text = data.decode("ascii")
    classical: list[int] = []
    phase: list[int] = []
    summaries = []
    for line in text.splitlines():
        if line.startswith("CLASSICAL_SHOT "):
            value = line.removeprefix("CLASSICAL_SHOT ")
            if not value.isdecimal():
                fail(f"malformed oracle classical row for {nonce}")
            classical.append(int(value))
        elif line.startswith("CLEAN_PHASE_SHOT "):
            value = line.removeprefix("CLEAN_PHASE_SHOT ")
            if not value.isdecimal():
                fail(f"malformed oracle phase row for {nonce}")
            phase.append(int(value))
        elif line.startswith("MIRROR "):
            summaries.append(line)
    if classical != sorted(set(classical)) or phase != sorted(set(phase)):
        fail(f"non-canonical oracle sets for {nonce}")
    if any(value >= SHOTS for value in (*classical, *phase)):
        fail(f"oracle index outside shot range for {nonce}")
    if set(classical) & set(phase):
        fail(f"conditional phase overlaps classical dirt for {nonce}")
    if len(summaries) != 1:
        fail(f"expected one mirror summary for {nonce}")
    match = SUMMARY_RE.match(summaries[0])
    if match is None:
        fail(f"malformed mirror summary for {nonce}")
    got_nonce, qubits, shots, cls, _batches, raw_phase, ancilla = map(int, match.groups())
    if (got_nonce, qubits, shots, ancilla) != (nonce, 1272, SHOTS, 0):
        fail(f"geometry or ancilla mismatch for {nonce}")
    if cls != len(classical) or len(phase) > raw_phase:
        fail(f"oracle summary/set mismatch for {nonce}")
    return tuple(classical), tuple(phase), raw_phase


def canonical_mask(indices: tuple[int, ...]) -> bytes:
    words = [0] * WORDS
    for index in indices:
        words[index // 64] |= 1 << (index % 64)
    return "".join(f"{word:016x}" for word in words).encode("ascii") + b"\n"


def verify_cached_h64(nonces: tuple[int, ...]) -> None:
    results_path = FIXTURE_ROOT / "h64/RESULTS.tsv"
    rows = results_path.read_text(encoding="ascii").splitlines()
    if not rows or rows[0] != "nonce\tclassical\traw_phase\tclean_phase\tartifact_manifest_sha256":
        fail("cached H64 result header drift")
    parsed: dict[int, str] = {}
    for row in rows[1:]:
        fields = row.split("\t")
        if len(fields) != 5 or not all(field.isdecimal() for field in fields[:4]):
            fail("malformed cached H64 result row")
        parsed[int(fields[0])] = fields[4]
    if tuple(sorted(parsed)) != nonces:
        fail("cached H64 nonce set drift")
    for nonce in nonces:
        root = FIXTURE_ROOT / "h64" / str(nonce)
        sums = root / "SHA256SUMS"
        if sha256(sums) != parsed[nonce]:
            fail(f"cached H64 manifest drift for {nonce}")
        for line in sums.read_text(encoding="ascii").splitlines():
            digest, name = line.split("  ", 1)
            if sha256(root / name) != digest:
                fail(f"cached H64 artifact drift for {nonce}/{name}")


def oracle_bytes(corpus: str, nonce: int, row_dir: pathlib.Path) -> bytes:
    if corpus == "inherited":
        return (FIXTURE_ROOT / "inherited-oracle.txt").read_bytes()
    if corpus == "H64":
        return (FIXTURE_ROOT / "h64" / str(nonce) / "oracle.stdout").read_bytes()
    attrib = row_dir / "attrib.tsv"
    result = run([str(MIRROR), str(OPS), str(SITES), str(nonce), str(attrib)])
    if result.stderr:
        fail(f"mirror emitted stderr for {corpus}/{nonce}")
    return result.stdout


@dataclass(frozen=True)
class Row:
    corpus: str
    nonce: int
    classical: int
    raw_phase: int
    clean_phase: int
    classical_mask_sha256: str
    phase_mask_sha256: str
    cause_sha256: str
    artifact_manifest_sha256: str


def evaluate_row(corpus: str, nonce: int, root: pathlib.Path,
                 classical_bin: pathlib.Path, combined_bin: pathlib.Path) -> Row:
    row_dir = root / corpus / str(nonce)
    row_dir.mkdir(parents=True)
    classical = run([str(classical_bin), "faultshots", str(nonce)], env=model_env())
    combined_classical = run([str(combined_bin), "faultshots", str(nonce)], env=model_env())
    combined_phase = run([str(combined_bin), "phasefaultshots", str(nonce)], env=model_env())
    oracle = oracle_bytes(corpus, nonce, row_dir)
    artifacts = {
        "classical.stdout": classical.stdout,
        "classical.stderr": classical.stderr,
        "combined-classical.stdout": combined_classical.stdout,
        "combined-classical.stderr": combined_classical.stderr,
        "combined-phase.stdout": combined_phase.stdout,
        "combined-phase.stderr": combined_phase.stderr,
        "oracle.stdout": oracle,
    }
    for name, data in artifacts.items():
        (row_dir / name).write_bytes(data)

    c_rows = parse_classical(classical.stdout, f"qualified/{corpus}/{nonce}")
    cc_rows = parse_classical(combined_classical.stdout, f"combined/{corpus}/{nonce}")
    if c_rows != cc_rows:
        fail(f"qualified/combined complete classical mismatch for {corpus}/{nonce}")
    phase_rows = parse_phase(combined_phase.stdout, f"combined-phase/{corpus}/{nonce}")
    oracle_classical, oracle_phase, raw_phase = parse_oracle(oracle, nonce)
    if tuple(index for index, _ in c_rows) != oracle_classical:
        fail(f"complete classical mask mismatch for {corpus}/{nonce}")
    if phase_rows != oracle_phase:
        fail(f"complete conditional-phase mask mismatch for {corpus}/{nonce}")

    c_mask = canonical_mask(oracle_classical)
    p_mask = canonical_mask(oracle_phase)
    (row_dir / "classical.mask").write_bytes(c_mask)
    (row_dir / "conditional-phase.mask").write_bytes(p_mask)
    manifest_rows = []
    for path in sorted(row_dir.iterdir()):
        if path.is_file():
            manifest_rows.append(f"{sha256(path)}  {path.name}")
    manifest = "\n".join(manifest_rows).encode("ascii") + b"\n"
    (row_dir / "SHA256SUMS").write_bytes(manifest)
    return Row(
        corpus, nonce, len(oracle_classical), raw_phase, len(oracle_phase),
        sha256_bytes(c_mask), sha256_bytes(p_mask), sha256_bytes(classical.stdout),
        sha256_bytes(manifest),
    )


def verify_negatives(out: pathlib.Path, combined: pathlib.Path,
                     bad_schedule: pathlib.Path) -> str:
    rows = []

    def reject(name: str, argv: list[str], env: dict[str, str] | None = None) -> None:
        result = run(argv, env=env, check=False)
        if result.returncode == 0 or result.stdout:
            fail(f"negative did not fail closed: {name}")
        rows.append(f"{name}\t{result.returncode}\t{sha256_bytes(result.stderr)}")

    reject("scan-disabled", [str(combined), "scan", "0", "1"], model_env())
    reject("unknown-mode", [str(combined), "unknown"], model_env())
    reject("missing-ops", [str(combined), "statedigest"], model_env(out / "missing.bin"))
    for label, nonce in (
        ("empty", ""), ("leading-zero", "00"), ("negative", "-1"),
        ("positive", "+1"), ("overflow", str(MAX_NONCE)), ("alpha", "abc"),
    ):
        reject(f"nonce-{label}", [str(combined), "faultshots", nonce], model_env())

    corrupt = out / "corrupt-ops.bin"
    shutil.copyfile(OPS, corrupt)
    with corrupt.open("r+b") as stream:
        stream.seek(32)
        byte = stream.read(1)
        if len(byte) != 1:
            fail("unable to make corrupt operation fixture")
        stream.seek(32)
        stream.write(bytes([byte[0] ^ 1]))
    reject("corrupt-ops", [str(combined), "statedigest"], model_env(corrupt))
    corrupt.unlink()
    reject(
        "bad-phase-schedule",
        [str(bad_schedule), "phasefaultshots", "65700024945645"], model_env(),
    )
    data = ("name\trc\tstderr_sha256\n" + "\n".join(rows) + "\n").encode("ascii")
    path = out / "NEGATIVES.tsv"
    path.write_bytes(data)
    return sha256(path)


def deterministic_repeat(root: pathlib.Path, corpus: str, nonce: int,
                         classical_bin: pathlib.Path, combined_bin: pathlib.Path) -> str:
    first = root / corpus / str(nonce)
    repeat_root = root / "repeats"
    repeated = evaluate_row(corpus, nonce, repeat_root, classical_bin, combined_bin)
    second = repeat_root / corpus / str(nonce)
    names = (
        "classical.stdout", "classical.stderr", "combined-classical.stdout",
        "combined-classical.stderr", "combined-phase.stdout", "combined-phase.stderr",
        "oracle.stdout", "classical.mask", "conditional-phase.mask",
    )
    for name in names:
        if (first / name).read_bytes() != (second / name).read_bytes():
            fail(f"deterministic repeat mismatch: {corpus}/{nonce}/{name}")
    return repeated.artifact_manifest_sha256


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=pathlib.Path)
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()
    if args.jobs < 1 or args.jobs > 8:
        fail("jobs must be in 1..8")
    if args.out.exists():
        fail(f"output already exists: {args.out}")
    status = run(["git", "status", "--porcelain"]).stdout
    if status:
        fail("worktree must be clean before qualification")
    if run([
        "git", "merge-base", "--is-ancestor", "517f32a", "HEAD"
    ], check=False).returncode != 0:
        fail("sealed predeclaration is not an ancestor of HEAD")
    if run(["git", "rev-parse", "HEAD"]).stdout.decode("ascii").strip() == "f308df4f1ab054b204dec050bc8b9f452e7c49ee":
        fail("combined donor is not integrated")
    verify_hashes()
    corpora = load_corpora()
    verify_cached_h64(corpora["H64"])
    args.out.mkdir(parents=True)
    classical_bin, combined_bin, bad_schedule = build_binaries(args.out)
    verify_build_identity(classical_bin, combined_bin)

    rows = []
    jobs = [(name, nonce) for name, nonces in corpora.items() for nonce in nonces]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures = {
            executor.submit(
                evaluate_row, name, nonce, args.out, classical_bin, combined_bin
            ): (name, nonce)
            for name, nonce in jobs
        }
        for future in concurrent.futures.as_completed(futures):
            name, nonce = futures[future]
            row = future.result()
            rows.append(row)
            print(
                f"PASS corpus={name} nonce={nonce} classical={row.classical} "
                f"raw_phase={row.raw_phase} clean_phase={row.clean_phase}",
                flush=True,
            )
    order = {name: index for index, name in enumerate(corpora)}
    rows.sort(key=lambda row: (order[row.corpus], row.nonce))
    if len(rows) != sum(CORPUS_LENGTHS.values()):
        fail("result row count mismatch")

    negative_sha = verify_negatives(args.out, combined_bin, bad_schedule)
    inherited_repeat = deterministic_repeat(
        args.out, "inherited", corpora["inherited"][0], classical_bin, combined_bin
    )
    f32_repeat = deterministic_repeat(
        args.out, "F32", corpora["F32"][-1], classical_bin, combined_bin
    )
    result_lines = [
        "corpus\tnonce\tclassical\traw_phase\tclean_phase\t"
        "classical_mask_sha256\tphase_mask_sha256\tcause_sha256\t"
        "artifact_manifest_sha256"
    ]
    for row in rows:
        result_lines.append(
            f"{row.corpus}\t{row.nonce}\t{row.classical}\t{row.raw_phase}\t"
            f"{row.clean_phase}\t{row.classical_mask_sha256}\t"
            f"{row.phase_mask_sha256}\t{row.cause_sha256}\t"
            f"{row.artifact_manifest_sha256}"
        )
    results = args.out / "RESULTS.tsv"
    results.write_text("\n".join(result_lines) + "\n", encoding="ascii", newline="\n")
    totals = {
        name: (
            sum(row.classical for row in rows if row.corpus == name),
            sum(row.raw_phase for row in rows if row.corpus == name),
            sum(row.clean_phase for row in rows if row.corpus == name),
        )
        for name in corpora
    }
    terminal = args.out / "TERMINAL_GO"
    terminal.write_text(
        "status=TERMINAL_GO_LOCAL_ONLY\n"
        f"rows={len(rows)}\nshots={len(rows) * SHOTS}\n"
        f"results_sha256={sha256(results)}\nnegative_sha256={negative_sha}\n"
        f"inherited_repeat_manifest_sha256={inherited_repeat}\n"
        f"f32_repeat_manifest_sha256={f32_repeat}\n"
        + "".join(
            f"{name}_totals_classical_raw_clean={value[0]},{value[1]},{value[2]}\n"
            for name, value in totals.items()
        )
        + "classical_complete_masks_equal=1\n"
        + "conditional_phase_complete_masks_equal=1\n"
        + "ancilla_zero_all_rows=1\n"
        + "cuda_range_provider_hunt_submission_authority=0\n",
        encoding="ascii",
    )
    print(
        f"TERMINAL GO rows={len(rows)} results_sha256={sha256(results)} "
        f"terminal_sha256={sha256(terminal)}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"TERMINAL KILL: {exc}", file=sys.stderr)
        raise SystemExit(2)
