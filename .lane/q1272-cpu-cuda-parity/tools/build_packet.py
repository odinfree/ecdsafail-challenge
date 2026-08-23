#!/usr/bin/env python3
"""Assemble the immutable fixed-only Q1272 CPU/CUDA parity packet."""

from __future__ import annotations

import csv
import hashlib
import os
import pathlib
import shutil
import subprocess


REPO = pathlib.Path(__file__).resolve().parents[3]
LANE = REPO / ".lane/q1272-cpu-cuda-parity"
OUT = pathlib.Path("/Users/olifreuler/ecdsa-ops/q1272-cpu-cuda-parity-packet-32943c9")
TERMINAL = pathlib.Path("/Users/olifreuler/ecdsa-ops/q1272-phase8833-repair-6cdcbed")
OPS = pathlib.Path(
    "/Users/olifreuler/Documents/Codex/2026-08-21/par/work/"
    "q1272-live-phase-screen/ops.bin"
)
SCHEDULE = pathlib.Path(
    "/Users/olifreuler/ecdsa-ops/q1272-phase8833-repair-generated/"
    "pp_phase_schedule.h"
)
EXPECTED = {
    REPO / ".lane/q1272-live-phase/src/pp_model.h":
        "9eab10bd8cf1c3510f4dcada4f08f8eb93d2efb749cc8496a88b7f68401bb90b",
    REPO / ".lane/q1272-live-phase/src/pp_host.h":
        "aa546788a823268cf311d88f028b80dd12826162fe220848ae46ec165b6190a2",
    REPO / ".lane/q1272-live-phase/src/ppcpu.cpp":
        "71031a56d921056d41c845b4d933d5fcd020c563a98ec1d7f8407ab57c3962e1",
    LANE / "FIXED8.nonces":
        "6830df61133fdd99ade11e4c2aa3b450f14dfe9331a7b64ae61817346e0a960c",
    OPS: "ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1",
    SCHEDULE: "2135746c16dc4deb4e608cd2e7e1d9907fe167d76854ba2420279f6164efca82",
    TERMINAL / "RESULTS.tsv":
        "90ba8719ba2e082e6646726ac6a15a8ab19659d33de055d0ab5cd2faaa241fb9",
    TERMINAL / "TERMINAL_GO":
        "21d5a7507335069b4b8c0999fe26356d9e449327b4f347390a2a341975248b14",
}


def fail(message: str) -> None:
    raise RuntimeError(message)


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(*argv: str) -> str:
    return subprocess.run(
        argv, cwd=REPO, check=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True,
    ).stdout.strip()


def verify_row_manifest(row_dir: pathlib.Path, expected: str) -> None:
    sums = row_dir / "SHA256SUMS"
    if sha256(sums) != expected:
        fail(f"row manifest drift: {row_dir}")
    for line in sums.read_text(encoding="ascii").splitlines():
        digest, name = line.split("  ", 1)
        if sha256(row_dir / name) != digest:
            fail(f"row artifact drift: {row_dir / name}")


def main() -> None:
    if OUT.exists():
        fail(f"output already exists: {OUT}")
    if run("git", "status", "--porcelain"):
        fail("worktree must be clean")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", "d09d541", "HEAD"],
        cwd=REPO,
    ).returncode != 0:
        fail("sealed predeclaration is not an ancestor of HEAD")
    for path, expected in EXPECTED.items():
        if not path.is_file() or sha256(path) != expected:
            fail(f"immutable input drift: {path}")

    nonces = tuple(map(int, (LANE / "FIXED8.nonces").read_text().split()))
    if len(nonces) != 8 or nonces != tuple(sorted(set(nonces))):
        fail("FIXED8 shape drift")
    results = list(csv.DictReader((TERMINAL / "RESULTS.tsv").open(), delimiter="\t"))
    by_nonce = {int(row["nonce"]): row for row in results}
    if len(by_nonce) != 257:
        fail("terminal result identity drift")

    classical_lines: list[str] = []
    phase_lines: list[str] = []
    for nonce in nonces:
        row = by_nonce.get(nonce)
        if row is None:
            fail(f"FIXED8 nonce absent from terminal results: {nonce}")
        row_dir = TERMINAL / row["corpus"] / str(nonce)
        verify_row_manifest(row_dir, row["artifact_manifest_sha256"])
        classical = (row_dir / "classical.stdout").read_text(encoding="ascii")
        phase = (row_dir / "combined-phase.stdout").read_text(encoding="ascii")
        for line in classical.splitlines():
            fields = line.split()
            if len(fields) != 2:
                fail(f"malformed classical fixture row for {nonce}")
            classical_lines.append(f"{nonce}\t{fields[0]}\t{fields[1]}")
        for line in phase.splitlines():
            if not line.isdecimal():
                fail(f"malformed phase fixture row for {nonce}")
            phase_lines.append(f"{nonce}\t{line}")
    if len(classical_lines) != 150 or len(phase_lines) != 32:
        fail("FIXED8 expected transcript counts drift")

    (OUT / "src").mkdir(parents=True)
    (OUT / "include").mkdir()
    (OUT / "expected").mkdir()
    shutil.copyfile(REPO / ".lane/q1272-live-phase/src/pp_model.h", OUT / "src/pp_model.h")
    shutil.copyfile(REPO / ".lane/q1272-live-phase/src/pp_host.h", OUT / "src/pp_host.h")
    shutil.copyfile(REPO / ".lane/q1272-live-phase/src/ppcpu.cpp", OUT / "src/ppcpu.cpp")
    shutil.copyfile(LANE / "src/ppcuda_fixed.cu", OUT / "src/ppcuda_fixed.cu")
    shutil.copyfile(SCHEDULE, OUT / "include/pp_phase_schedule.h")
    shutil.copyfile(OPS, OUT / "ops.bin")
    shutil.copyfile(LANE / "FIXED8.nonces", OUT / "FIXED8.nonces")
    shutil.copyfile(LANE / "packet/verify_packet.py", OUT / "verify_packet.py")
    shutil.copyfile(LANE / "packet/run_one_gpu_parity.sh", OUT / "run_one_gpu_parity.sh")
    shutil.copyfile(LANE / "packet/selftest_failclosed.sh", OUT / "selftest_failclosed.sh")
    (OUT / "expected/classical.tsv").write_text(
        "\n".join(classical_lines) + "\n", encoding="ascii", newline="\n"
    )
    (OUT / "expected/phase.tsv").write_text(
        "\n".join(phase_lines) + "\n", encoding="ascii", newline="\n"
    )

    implementation = run("git", "rev-parse", "HEAD")
    meta = {
        "format": "q1272-fixed8-cpu-cuda-parity-v1",
        "terminal_commit": "32943c9589097312e78692122c72566f834355ef",
        "repair_commit": "6cdcbedcb201bad289dd1381ae60429f0691d6fd",
        "implementation_commit": implementation,
        "source_commit": "73422709ed70ba9725b3cb592770bcf197df4cdb",
        "ops_count": "12904643",
        "ops_sha256": EXPECTED[OPS],
        "state_digest": "e9b2d20ecd1169a8",
        "model_sha256": EXPECTED[REPO / ".lane/q1272-live-phase/src/pp_model.h"],
        "host_sha256": EXPECTED[REPO / ".lane/q1272-live-phase/src/pp_host.h"],
        "cpu_driver_sha256": EXPECTED[REPO / ".lane/q1272-live-phase/src/ppcpu.cpp"],
        "cuda_source_sha256": sha256(LANE / "src/ppcuda_fixed.cu"),
        "phase_meta_sha256": "61e28111ff655bed39d5bc7dd8ccf0912274c112a34dfcc11ec01369725010b6",
        "phase_schedule_sha256": EXPECTED[SCHEDULE],
        "fixed8_sha256": EXPECTED[LANE / "FIXED8.nonces"],
        "expected_classical_sha256": sha256(OUT / "expected/classical.tsv"),
        "expected_phase_sha256": sha256(OUT / "expected/phase.tsv"),
        "fixtures": "8",
        "shots_per_fixture": "9024",
        "classical_rows": "150",
        "clean_phase_rows": "32",
        "cuda_interface": "fixed8-no-arguments",
        "cuda_execution": "not-performed",
    }
    (OUT / "PACKET.meta").write_text(
        "".join(f"{key}={value}\n" for key, value in meta.items()),
        encoding="ascii", newline="\n",
    )

    files = sorted(
        path for path in OUT.rglob("*")
        if path.is_file() and path.name != "MANIFEST.sha256"
    )
    (OUT / "MANIFEST.sha256").write_text(
        "".join(f"{sha256(path)}  {path.relative_to(OUT).as_posix()}\n" for path in files),
        encoding="ascii", newline="\n",
    )
    for path in OUT.rglob("*"):
        if path.is_file():
            mode = 0o500 if path.suffix in {".py", ".sh"} else 0o400
            os.chmod(path, mode)
    for path in sorted(OUT.rglob("*"), reverse=True):
        if path.is_dir():
            os.chmod(path, 0o500)
    os.chmod(OUT, 0o500)
    print(f"PACKET_READY path={OUT} files={len(files) + 1} implementation={implementation}")


if __name__ == "__main__":
    main()
