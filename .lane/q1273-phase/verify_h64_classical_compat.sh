#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 || -z $1 || -z $2 ]]; then
    echo "usage: verify_h64_classical_compat.sh OPS_BIN EXTERNAL_H64_DIR" >&2
    exit 2
fi

script_dir=$(cd -- "$(dirname -- "$0")" && pwd -P)
ops=$(cd -- "$(dirname -- "$1")" && pwd -P)/$(basename -- "$1")
h64=$(cd -- "$2" && pwd -P)
tmp=$(mktemp -d "${TMPDIR:-/tmp}/q1273-h64-compat.XXXXXX")
trap 'rm -rf -- "$tmp"' EXIT

sha256() {
    shasum -a 256 -- "$1" | awk '{print $1}'
}

die() {
    echo "verify-q1273-h64-compat: FAIL: $*" >&2
    exit 1
}

[[ $(sha256 "$ops") == \
    ee6448dbb23aa877123733724b109266e584f1ba14abf5c38b43b9ab6aa26cd1 ]] || \
    die "wrong base ops stream"
[[ $(sha256 "$h64/fixtures.tsv") == \
    7918937a30d562a2dd26cf59374cdb702c11ce0f08d42789f9ef42da8264b5f4 ]] || \
    die "wrong H64 fixture ledger"
[[ $(sha256 "$h64/evaluator-index-mask.tsv") == \
    9c1c9cfb0dc7057e8ea1aafbd55c42382e9c4eeabab0d13fe80d18d98c899f46 ]] || \
    die "wrong H64 evaluator mask ledger"
[[ $(sha256 "$h64/predictor-index-mask.tsv") == \
    9c1c9cfb0dc7057e8ea1aafbd55c42382e9c4eeabab0d13fe80d18d98c899f46 ]] || \
    die "wrong original-predictor H64 mask ledger"
[[ $(sha256 "$h64/predictor-cause-mask.tsv") == \
    eb3193ffefa76c5572006878fec23ca83f8d83737db49cd0d4c2cbceeb99a0b6 ]] || \
    die "wrong original-predictor H64 cause ledger"

"$script_dir/build_phase_cpu.sh" "$tmp/ppcpu"

# This is exactly the already-frozen H64 qualification corpus, never an open
# range.  Four local workers reduce repeated bound-stream decompression time;
# each executable invocation still consumes one explicit nonce.
python3 - "$tmp/ppcpu" "$ops" "$h64" "$tmp" <<'PY'
import concurrent.futures
import os
import pathlib
import subprocess
import sys

binary, ops, h64, out = map(pathlib.Path, sys.argv[1:])
nonces = [444_000_000_000 + i for i in range(64)]

def run(nonce: int) -> tuple[int, bytes]:
    expected_path = h64 / str(nonce) / "predictor.raw"
    expected = expected_path.read_bytes()
    env = os.environ.copy()
    env["PPF_OPS"] = str(ops)
    result = subprocess.run(
        [str(binary), "faultshots", str(nonce)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"nonce {nonce}: predictor rc={result.returncode}")
    if result.stdout != expected:
        raise RuntimeError(f"nonce {nonce}: phase-extended predictor output drift")
    return nonce, result.stdout

outputs: dict[int, bytes] = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    futures = [pool.submit(run, nonce) for nonce in nonces]
    for future in concurrent.futures.as_completed(futures):
        nonce, stdout = future.result()
        outputs[nonce] = stdout

index_rows: list[str] = []
cause_rows: list[str] = []
total = 0
for nonce in nonces:
    previous = -1
    for raw_line in outputs[nonce].decode("ascii").splitlines():
        fields = raw_line.split(" ")
        if len(fields) != 2 or not all(field.isdecimal() for field in fields):
            raise RuntimeError(f"nonce {nonce}: malformed predictor row {raw_line!r}")
        shot, cause = map(int, fields)
        if shot <= previous or shot >= 9024 or cause not in (1, 2, 4, 8, 16):
            raise RuntimeError(f"nonce {nonce}: invalid predictor row {raw_line!r}")
        previous = shot
        index_rows.append(f"{nonce}\t{shot}\n")
        cause_rows.append(f"{nonce}\t{shot}\t{cause}\n")
        total += 1
if total != 870:
    raise RuntimeError(f"H64 predicted {total} classical rows, expected 870")
(out / "phase-predictor-index-mask.tsv").write_text("".join(index_rows), encoding="ascii")
(out / "phase-predictor-cause-mask.tsv").write_text("".join(cause_rows), encoding="ascii")
PY

cmp -s "$tmp/phase-predictor-index-mask.tsv" "$h64/evaluator-index-mask.tsv" || \
    die "phase-extended predictor differs from exact H64 evaluator masks"
cmp -s "$tmp/phase-predictor-cause-mask.tsv" "$h64/predictor-cause-mask.tsv" || \
    die "phase additions changed H64 classical cause masks"

echo "verify-q1273-h64-compat: PASS corpus=444000000000..444000000063 exact=64/64 faults=870 index_sha256=$(sha256 "$tmp/phase-predictor-index-mask.tsv") cause_sha256=$(sha256 "$tmp/phase-predictor-cause-mask.tsv") binary_sha256=$(sha256 "$tmp/ppcpu") combined_hunt=HOLD"
