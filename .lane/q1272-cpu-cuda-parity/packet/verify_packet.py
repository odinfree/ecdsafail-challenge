#!/usr/bin/env python3
"""Strict offline verifier for the fixed-only Q1272 CUDA parity packet."""

from __future__ import annotations

import hashlib
import pathlib
import re
import sys


EXPECTED = {
    "format": "q1272-fixed8-cpu-cuda-parity-v1",
    "terminal_commit": "32943c9589097312e78692122c72566f834355ef",
    "repair_commit": "6cdcbedcb201bad289dd1381ae60429f0691d6fd",
    "source_commit": "73422709ed70ba9725b3cb592770bcf197df4cdb",
    "ops_count": "12904643",
    "ops_sha256": "ea19759d80a4bc1492a5e98c966e70ee79d5aa40211e6cc480b08cf032c8a0f1",
    "state_digest": "e9b2d20ecd1169a8",
    "model_sha256": "9eab10bd8cf1c3510f4dcada4f08f8eb93d2efb749cc8496a88b7f68401bb90b",
    "host_sha256": "aa546788a823268cf311d88f028b80dd12826162fe220848ae46ec165b6190a2",
    "cpu_driver_sha256": "71031a56d921056d41c845b4d933d5fcd020c563a98ec1d7f8407ab57c3962e1",
    "phase_meta_sha256": "61e28111ff655bed39d5bc7dd8ccf0912274c112a34dfcc11ec01369725010b6",
    "phase_schedule_sha256": "2135746c16dc4deb4e608cd2e7e1d9907fe167d76854ba2420279f6164efca82",
    "fixed8_sha256": "6830df61133fdd99ade11e4c2aa3b450f14dfe9331a7b64ae61817346e0a960c",
    "fixtures": "8",
    "shots_per_fixture": "9024",
    "classical_rows": "150",
    "clean_phase_rows": "32",
    "cuda_interface": "fixed8-no-arguments",
    "cuda_execution": "not-performed",
}
FIXED8 = (
    3306946714859,
    37754156253796,
    51170368051453,
    65700024945645,
    147428349223424,
    154123680082395,
    202374768790705,
    279811539530441,
)
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


def fail(message: str) -> None:
    raise SystemExit(f"verify-packet: {message}")


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_meta(path: pathlib.Path) -> dict[str, str]:
    raw = path.read_bytes()
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        fail(f"PACKET.meta is not ASCII: {exc}")
    if not text.endswith("\n") or "\r" in text:
        fail("PACKET.meta is not canonical LF text")
    result: dict[str, str] = {}
    for number, line in enumerate(text.splitlines(), 1):
        if line.count("=") != 1:
            fail(f"malformed PACKET.meta line {number}")
        key, value = line.split("=", 1)
        if not key or not value or key in result:
            fail(f"duplicate or empty PACKET.meta line {number}")
        result[key] = value
    return result


def read_manifest(root: pathlib.Path) -> dict[str, str]:
    path = root / "MANIFEST.sha256"
    raw = path.read_bytes()
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        fail(f"manifest is not ASCII: {exc}")
    if not text.endswith("\n") or "\r" in text:
        fail("manifest is not canonical LF text")
    result: dict[str, str] = {}
    for number, line in enumerate(text.splitlines(), 1):
        if "  " not in line:
            fail(f"malformed manifest line {number}")
        digest, name = line.split("  ", 1)
        if not SHA_RE.fullmatch(digest) or not name or name in result:
            fail(f"bad digest, name, or duplicate at manifest line {number}")
        rel = pathlib.PurePosixPath(name)
        if rel.is_absolute() or ".." in rel.parts or str(rel) != name:
            fail(f"unsafe manifest path {name!r}")
        result[name] = digest
    if tuple(result) != tuple(sorted(result)):
        fail("manifest paths are not sorted")
    return result


def read_fixed(path: pathlib.Path) -> tuple[int, ...]:
    raw = path.read_bytes()
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        fail(f"FIXED8 is not ASCII: {exc}")
    if not text.endswith("\n") or "\r" in text:
        fail("FIXED8 is not canonical LF text")
    rows = text.splitlines()
    if any(not row.isdecimal() or row.startswith("0") for row in rows):
        fail("FIXED8 has a malformed nonce")
    values = tuple(map(int, rows))
    if values != FIXED8 or values != tuple(sorted(set(values))):
        fail("FIXED8 identity, order, or uniqueness mismatch")
    if any(value >= 1 << 48 for value in values):
        fail("FIXED8 contains a nonce outside 48 bits")
    return values


def read_expected(path: pathlib.Path, width: int, allowed: set[int]) -> int:
    raw = path.read_bytes()
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        fail(f"{path.name} is not ASCII: {exc}")
    if not text.endswith("\n") or "\r" in text:
        fail(f"{path.name} is not canonical LF text")
    parsed = []
    for number, line in enumerate(text.splitlines(), 1):
        fields = line.split("\t")
        if len(fields) != width or any(not field.isdecimal() for field in fields):
            fail(f"malformed {path.name} row {number}")
        values = tuple(map(int, fields))
        nonce, shot = values[:2]
        if nonce not in allowed or shot >= 9024:
            fail(f"out-of-scope {path.name} row {number}")
        if width == 3 and not (0 < values[2] < 32):
            fail(f"bad cause in {path.name} row {number}")
        parsed.append(values)
    if parsed != sorted(set(parsed)):
        fail(f"{path.name} rows are not canonical and unique")
    return len(parsed)


def verify_cuda_interface(path: pathlib.Path) -> None:
    try:
        source = path.read_text(encoding="ascii")
    except UnicodeDecodeError as exc:
        fail(f"CUDA source is not ASCII: {exc}")
    match = re.search(
        r"static const u64 FIXED8\[\] = \{(.*?)\};", source, re.DOTALL
    )
    if match is None:
        fail("CUDA source has no fixed corpus declaration")
    compiled = tuple(map(int, re.findall(r"([0-9]+)ULL", match.group(1))))
    if compiled != FIXED8:
        fail("CUDA compile-time FIXED8 differs from packet fixture identity")
    forbidden = ("argv[", "getenv(", "strtoull(", "system(", "popen(", "socket(")
    if any(token in source for token in forbidden):
        fail("CUDA source exposes a dynamic input or external-command surface")
    if "if (argc != 1)" not in source:
        fail("CUDA source does not reject all arguments")


def main() -> None:
    if len(sys.argv) != 1:
        fail("this verifier accepts no arguments")
    root = pathlib.Path(__file__).resolve().parent
    if root.is_symlink():
        fail("packet root may not be a symlink")
    meta = read_meta(root / "PACKET.meta")
    if set(meta) != set(EXPECTED) | {
        "implementation_commit", "cuda_source_sha256",
        "expected_classical_sha256", "expected_phase_sha256",
    }:
        fail("PACKET.meta key set mismatch")
    for key, expected in EXPECTED.items():
        if meta.get(key) != expected:
            fail(f"PACKET.meta {key} mismatch")
    if not COMMIT_RE.fullmatch(meta["implementation_commit"]):
        fail("PACKET.meta implementation_commit is not a full Git identity")
    for key in (
        "cuda_source_sha256", "expected_classical_sha256",
        "expected_phase_sha256",
    ):
        if not SHA_RE.fullmatch(meta[key]):
            fail(f"PACKET.meta {key} is not a SHA-256 identity")

    manifest = read_manifest(root)
    actual_files = sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path.name != "MANIFEST.sha256"
    )
    if actual_files != list(manifest):
        fail("manifest coverage mismatch or unexpected packet file")
    for name, expected in manifest.items():
        path = root / name
        if path.is_symlink() or not path.is_file():
            fail(f"manifest target is missing or a symlink: {name}")
        actual = sha256(path)
        if actual != expected:
            fail(f"manifest hash mismatch for {name}")

    fixed = read_fixed(root / "FIXED8.nonces")
    if sha256(root / "FIXED8.nonces") != EXPECTED["fixed8_sha256"]:
        fail("FIXED8 SHA-256 mismatch")
    if sha256(root / "ops.bin") != EXPECTED["ops_sha256"]:
        fail("operation stream SHA-256 mismatch")
    if sha256(root / "src/pp_model.h") != EXPECTED["model_sha256"]:
        fail("model SHA-256 mismatch")
    if sha256(root / "src/pp_host.h") != EXPECTED["host_sha256"]:
        fail("host SHA-256 mismatch")
    if sha256(root / "src/ppcpu.cpp") != EXPECTED["cpu_driver_sha256"]:
        fail("CPU driver SHA-256 mismatch")
    if sha256(root / "include/pp_phase_schedule.h") != EXPECTED["phase_schedule_sha256"]:
        fail("phase schedule SHA-256 mismatch")
    if sha256(root / "src/ppcuda_fixed.cu") != meta["cuda_source_sha256"]:
        fail("CUDA source SHA-256 mismatch")
    verify_cuda_interface(root / "src/ppcuda_fixed.cu")
    if sha256(root / "expected/classical.tsv") != meta["expected_classical_sha256"]:
        fail("expected classical SHA-256 mismatch")
    if sha256(root / "expected/phase.tsv") != meta["expected_phase_sha256"]:
        fail("expected phase SHA-256 mismatch")

    allowed = set(fixed)
    if read_expected(root / "expected/classical.tsv", 3, allowed) != 150:
        fail("expected classical row count mismatch")
    if read_expected(root / "expected/phase.tsv", 2, allowed) != 32:
        fail("expected phase row count mismatch")
    print(
        "Q1272_FIXED8_PACKET_OK fixtures=8 shots=72192 "
        "classical_rows=150 clean_phase_rows=32 cuda_execution=not-performed"
    )


if __name__ == "__main__":
    main()
