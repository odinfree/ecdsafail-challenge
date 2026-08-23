#!/usr/bin/env python3
"""Open the frozen fresh F16 and require exact complete-mask parity."""

from __future__ import annotations

import concurrent.futures
import hashlib
import os
import pathlib
import re
import subprocess


REPO = pathlib.Path(__file__).resolve().parents[3]
LANE = REPO / ".lane/q1271-target0-predictor"
ROOT = pathlib.Path("/Users/olifreuler/ecdsa-ops/q1271-target0-sign-alias-590cb55d")
OUT = ROOT / "fresh-f16-v1"
OPS = ROOT / "target/ops.bin"
SITES = ROOT / "op-sites.tsv"
PPCPU = ROOT / "model/ppcpu-combined"
MIRROR_SOURCE = pathlib.Path("/private/tmp/phase_mirror/src/main.rs")
MIRROR = pathlib.Path("/private/tmp/phase_mirror/target/release/phase_mirror")
NONCES = LANE / "F16.nonces"
EXPECTED_NONCE_SHA256 = "bbfdbf0372f73855519c100bd5aa52c39f5f1fe5e6f966e7726b2a43c008819e"
NEGATIVE_SEAL = "2cfdd9e5be17a73d08eccdc10a1dc9becf201abd"
SEALED_MODEL_COMMIT = "08a9da2093bd5fececbaebc7569de55b12243d9f"
REMOTE_REF = "refs/remotes/odinfree/research/q1271-target0-sign-alias"
DOMAIN = b"q1271-target0-sign-alias/fresh-f16/v1\0"
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
    ROOT / "d32-v1/RESULTS.tsv":
        "b95a6aa454329b6f85a37e88859b755c961e3502e981c4dc6aec34fbd652b8d3",
    ROOT / "negatives-v1/receipt.tsv":
        "9c2626f1f12ba1a7d64a25b7577a51967061f57bd5762cb35dc122f67eee8e80",
    ROOT / "negatives-v1/PASS":
        "f140cc7529d3cc4a4e3676c58d7d7a10254fca4b44aaae1672e81b3762f22b7a",
    LANE / "src/pp_model.h":
        "46e227f7920f43e8d233791dfefd01858cff39c24807d17ed2b390befa0bb390",
    LANE / "src/pp_host.h":
        "7d432431c1d27854f6dff6b0ff807da0241deabf3b3dccc63c53b09e8b7fee8b",
    LANE / "src/ppcpu.cpp":
        "0e10386e356f0a21e7a89bdf8445309d14641a94fe707fe788dd777727f796ba",
}
MIRROR_RE = re.compile(
    r"^MIRROR nonce=(\d+) qubits=(\d+) shots=(\d+) cls=(\d+) "
    r"phase_batches=(\d+) phase_shots=(\d+) ancilla=(\d+) "
)


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"qualify-f16: {message}")


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
    summaries = [line for line in lines if line.startswith("MIRROR ")]
    if len(summaries) != 1 or (match := MIRROR_RE.match(summaries[0])) is None:
        fail(f"nonce {nonce}: malformed oracle summary")
    got_nonce, qubits, shots, cls, _batches, raw_phase, ancilla = map(
        int, match.groups()
    )
    if (got_nonce, qubits, shots, ancilla) != (nonce, 1271, 9024, 0):
        fail(f"nonce {nonce}: oracle geometry mismatch")
    oracle_classical = parse_indices(lines, "CLASSICAL_SHOT ")
    oracle_phase = parse_indices(lines, "CLEAN_PHASE_SHOT ")
    if len(oracle_classical) != cls or len(oracle_phase) > raw_phase:
        fail(f"nonce {nonce}: oracle mask/summary mismatch")
    if set(oracle_classical) & set(oracle_phase):
        fail(f"nonce {nonce}: conditional phase intersects classical mask")
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
    phase_lines = phase.stdout.decode("ascii").splitlines()
    if any(not line.isdecimal() for line in phase_lines):
        fail(f"nonce {nonce}: malformed model phase output")
    model_phase = [int(line) for line in phase_lines]

    classical_fn = len(set(oracle_classical) - set(model_classical))
    classical_fp = len(set(model_classical) - set(oracle_classical))
    phase_fn = len(set(oracle_phase) - set(model_phase))
    phase_fp = len(set(model_phase) - set(oracle_phase))
    if (classical_fn, classical_fp, phase_fn, phase_fp) != (0, 0, 0, 0):
        fail(
            f"nonce {nonce}: mask mismatch "
            f"classical_fn_fp={classical_fn}/{classical_fp} "
            f"phase_fn_fp={phase_fn}/{phase_fp}"
        )
    if model_classical != oracle_classical or model_phase != oracle_phase:
        fail(f"nonce {nonce}: ordered complete-mask mismatch")

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


def derive_fresh(forbidden: set[int]) -> tuple[int, ...]:
    seed = DOMAIN + bytes.fromhex(NEGATIVE_SEAL)
    selected = []
    counter = 0
    while len(selected) < 16:
        digest = hashlib.sha256(seed + counter.to_bytes(8, "little")).digest()
        candidate = int.from_bytes(digest[:6], "little")
        if candidate not in forbidden and candidate not in selected:
            selected.append(candidate)
        counter += 1
    if counter != 16:
        fail(f"fresh derivation counter drift: {counter}")
    return tuple(selected)


def main() -> None:
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=REPO, check=True,
        stdout=subprocess.PIPE,
    ).stdout
    if status:
        fail("worktree is not clean before fresh holdout reveal")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", NEGATIVE_SEAL, "HEAD"], cwd=REPO,
    ).returncode != 0:
        fail("negative-matrix seal is not an ancestor")
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO, check=True,
        stdout=subprocess.PIPE, text=True,
    ).stdout.strip()
    remote = subprocess.run(
        ["git", "rev-parse", REMOTE_REF], cwd=REPO, check=True,
        stdout=subprocess.PIPE, text=True,
    ).stdout.strip()
    if head != remote:
        fail("fresh fixture and runner commit is not pushed")
    if subprocess.run(
        ["git", "diff", "--quiet", SEALED_MODEL_COMMIT, "--",
         ".lane/q1271-target0-predictor/src"], cwd=REPO,
    ).returncode != 0:
        fail("model semantics differ from the terminal H64 commit")
    for path, expected in EXPECTED.items():
        if not path.is_file() or sha256(path) != expected:
            fail(f"immutable input missing or drifted: {path}")
    if OUT.exists():
        fail(f"output already exists: {OUT}")

    raw = NONCES.read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED_NONCE_SHA256:
        fail("F16 nonce-list SHA-256 mismatch")
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        fail(f"F16 list is not ASCII: {exc}")
    if not text.endswith("\n"):
        fail("F16 list is not LF-terminated")
    lines = text.splitlines()
    if len(lines) != 16 or any(
        not line.isdecimal() or (line.startswith("0") and line != "0")
        for line in lines
    ):
        fail("F16 list is not 16 canonical decimal rows")
    nonces = tuple(map(int, lines))
    if len(set(nonces)) != 16 or any(nonce >= 1 << 48 for nonce in nonces):
        fail("F16 contains duplicates or a value outside 48 bits")

    d32_raw = subprocess.run(
        ["git", "show",
         "3c1a49cdde48f804c4e35bd0501d7d8d7f46f15e:.lane/q1273-wrap-exact/D32.nonces"],
        cwd=REPO, check=True, stdout=subprocess.PIPE,
    ).stdout.decode("ascii").splitlines()
    forbidden = {
        65700024945645,
        *range(444_000_000_000, 444_000_000_064),
        *map(int, d32_raw),
    }
    if set(nonces) & forbidden:
        fail("F16 overlaps inherited, H64, or D32")
    if nonces != derive_fresh(forbidden):
        fail("F16 differs from its predeclared domain-separated derivation")

    OUT.mkdir()
    (OUT / "F16.nonces").write_bytes(raw)
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
                f"qualify-f16: PASS row={index} classical={classical} "
                f"raw_phase={raw_phase} conditional_phase={conditional_phase}",
                flush=True,
            )
    rows.sort()
    if tuple(row[1] for row in rows) != nonces:
        fail("fresh result order differs from the frozen list")

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
    evaluate(nonces[-1], repeat_root / "final-f16")
    compare_exact(
        OUT / str(nonces[-1]), repeat_root / "final-f16",
        ("attrib.tsv", "oracle.stdout", "oracle.stderr",
         "model-classical.stdout", "model-classical.stderr",
         "model-phase.stdout", "model-phase.stderr"),
    )

    result_lines = [
        "row\tnonce\tclassical\traw_phase\tconditional_phase\t"
        "classical_fn\tclassical_fp\tphase_fn\tphase_fp\tartifact_manifest_sha256"
    ]
    result_lines.extend(
        "\t".join(map(str, (*row[:5], 0, 0, 0, 0, row[5]))) for row in rows
    )
    result_path = OUT / "RESULTS.tsv"
    result_path.write_text(
        "\n".join(result_lines) + "\n", encoding="ascii", newline="\n"
    )
    repeat_rows = []
    for path in sorted(repeat_root.rglob("*")):
        if path.is_file():
            repeat_rows.append(f"{sha256(path)}  {path.relative_to(repeat_root)}")
    repeat_manifest = OUT / "REPEATS.sha256"
    repeat_manifest.write_text(
        "\n".join(repeat_rows) + "\n", encoding="ascii", newline="\n"
    )
    input_rows = [f"{sha256(path)}  {path}" for path in sorted(EXPECTED)]
    input_rows.append(f"{sha256(NONCES)}  {NONCES}")
    inputs = OUT / "INPUTS.sha256"
    inputs.write_text("\n".join(input_rows) + "\n", encoding="ascii", newline="\n")

    for path, expected in EXPECTED.items():
        if sha256(path) != expected:
            fail(f"immutable input changed during F16: {path}")
    if subprocess.run(
        ["git", "status", "--porcelain"], cwd=REPO, check=True,
        stdout=subprocess.PIPE,
    ).stdout:
        fail("worktree changed during fresh holdout")
    if subprocess.run(
        ["git", "diff", "--quiet", SEALED_MODEL_COMMIT, "--",
         ".lane/q1271-target0-predictor/src"], cwd=REPO,
    ).returncode != 0:
        fail("model semantics changed during fresh holdout")

    totals = tuple(sum(row[index] for row in rows) for index in (2, 3, 4))
    marker = OUT / "PASS"
    marker.write_text(
        "PASS_FRESH_F16_16_OF_16_ZERO_FN_ZERO_FP\n"
        f"head={head}\n"
        f"results_sha256={sha256(result_path)}\n"
        f"repeats_sha256={sha256(repeat_manifest)}\n"
        f"inputs_sha256={sha256(inputs)}\n",
        encoding="ascii", newline="\n",
    )
    print(
        "qualify-f16: PASS exact=16/16 zero_fn=0 zero_fp=0 "
        f"totals_classical_raw_conditional={totals} "
        f"results_sha256={sha256(result_path)} "
        f"repeats_sha256={sha256(repeat_manifest)} "
        f"inputs_sha256={sha256(inputs)} marker_sha256={sha256(marker)}",
        flush=True,
    )


if __name__ == "__main__":
    main()
