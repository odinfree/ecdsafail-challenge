#!/bin/bash
# Fail-closed, no-range-hunt per-shot mask parity gate for the frozen B1=24
# fixtures. It reuses only the already-qualified checkpoint, writes into a new
# isolated workspace, and leaves the protected Q1276 confirmer untouched.
set -euo pipefail

ROOT=/workspace/ev-b523-b1-24-faultshots-f376e53
SRC=$ROOT/source
ART=$ROOT/artifacts
COUNT_ROOT=/workspace/ev-b523-b1-24-90a27e1
PROTECTED=/workspace/ev-g1000-q1276-0b6ac181
INC=/workspace/ev-cc20
QSRC=/workspace/q1276-fullconfirm-c639abe
QART=/workspace/q1276-fullconfirm-c639abe-artifacts
SOURCE_COMMIT=f376e532f9e5ac293bfda8cfbd27edb6c1e97f0b
SOURCE_TREE=71598311d15f0b49f6a34360b664182cbb6be698
SEMANTIC_COMMIT=8a3c06e57f169d842fdb33722415dc66236a0b02
SEMANTIC_TREE=b49fd5ef8bf42be563f9defa2f2a3282b27aa834
OPS_COUNT=12822408
OPS_SHA=af28dbc49471651c3e856c62c1fd97cb429469cde4b66fe7fe082a0d23fe1ad7
CHECKPOINT_SHA=7080f69f4aabd7be663713d57c553d1e80913a2fc1d5b4958e7ab5c4b46a8dcc
CPU_SOURCE_SHA=cba1e48b979a6f4a1c8623e12a59a17c0dda2d688213b3af5131e162883a0753
CUDA_SOURCE_SHA=2986855fd6ad3334b448f296047d30851ba051dc2d2b9204fd8da08461856bae
COUNT_RECEIPT_SHA=24de81effc820a65033c79879e75d8ebc1586587a8ab6cece8f0796eae86efb3
COUNT_FIXTURE_SHA=6411fd885aab5ddd19f673217c4c2cb5a51a7230b70bf91d143b71f1c2d1c920
FIXTURE_FROM=81327465284
FIXTURE_TO=81327465315
PATH=/root/.cargo/bin:/usr/local/cuda/bin:/usr/local/bin:/usr/bin:/bin
export PATH

sha() {
  sha256sum "$1" | awk '{print $1}'
}

assert_sha() {
  local path=$1 expected=$2
  test "$(sha "$path")" = "$expected"
}

assert_gpu_idle() {
  local apps
  apps=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader | sed '/^$/d')
  test -z "$apps"
}

pending_confirms() {
  comm -23 \
    <(grep '^[0-9]' "$INC/survivors.tsv" | cut -d ' ' -f 1 | sort -u) \
    <(grep '^[0-9]' "$INC/confirmed.txt" | sort -u) | wc -l | tr -d ' '
}

assert_protected() {
  local out=$1 pending active cmd
  test "$(readlink /proc/590322/cwd)" = /workspace/ev-cc20
  test "$(awk '{print $22}' /proc/590322/stat)" = 125595502
  test "$(ps -o ppid= -p 590322 | tr -d ' ')" = 1
  kill -0 590322
  cmd=$(tr '\0' ' ' < /proc/590322/cmdline)
  test "$cmd" = '/bin/bash ./confirm_loop.sh '
  pending=$(pending_confirms)
  active=$(ps -eo args | grep -c '^/workspace/ev-cc20/eval_circuit --note cf-' || true)
  test "$pending" -eq 0
  test "$active" -eq 0
  assert_gpu_idle

  assert_sha "$PROTECTED/ops.bin" \
    d1461959eac52b19b644f1f97a3b44a3ea249a109f14a406d19e872cd17c5422
  assert_sha "$PROTECTED/ppcpu" \
    73f09fb8f5d84bdd595c730e0be34a8a8abb5d78184c8f431987708b4d2cc61b
  assert_sha "$PROTECTED/ppgpu" \
    672a47004f1f0a4a3ebc0d0a3e4a41e2dd903b1e1493bf493757fefed355cf2d
  assert_sha "$PROTECTED/FINGERPRINTS" \
    b78f07dc879a9eb6c1f5ef3248ced3a373b7d31d7a92d6d98ae741ed47964310
  assert_sha "$PROTECTED/PARITY.complete" \
    92f8ac280ecd0dd2710190a01e98e1fd59198d7e9142c567ff5acfa027a78cc1
  assert_sha "$PROTECTED/BORROW.complete" \
    b63248390e7e49a2d6a33782c3f457eefb5fdcdfe03a904cd6a25aa7e31d562f
  assert_sha "$PROTECTED/DRAINED_AT" \
    0bd58d73f2252d0c459cbf055b9407215ca2416bb12ab3d95a6e5c087dfafb3b
  test ! -e "$PROTECTED/DEDICATED.complete"
  test ! -e "$PROTECTED/runs"

  test "$(git -C "$QSRC" rev-parse HEAD)" = \
    c639abedfee8931d84fad282b6d128865b597bc4
  test "$(git -C "$QSRC" rev-parse HEAD^{tree})" = \
    7f2d009cf1332380e15e13756773f6a66afc7cb7
  test "$(git -C "$QSRC" status --short)" = ""
  assert_sha "$QSRC/results.tsv" \
    eea840222afd2424445550252f25795d63eb4bc3904b8c87f0213b5f22abc810
  test ! -e "$QSRC/score.json"
  assert_sha "$QSRC/target/release/build_circuit" \
    16a17befc03e9a2394a1e385167720a79428f84783bcddd10b1bf2e8655bb4d5
  assert_sha "$QSRC/target/release/eval_circuit" \
    7e146f04e9147be2b5403f613ddc553fb3ddda7054256f14e7d95fc9d3556d40
  assert_sha "$QART/FULLCONFIRM-PATH.complete" \
    b09d29a129f61e02a95152da747e7fbe675375bbe23e945e597f9c6c88d927ee

  assert_sha "$COUNT_ROOT/PARITY.complete" "$COUNT_RECEIPT_SHA"
  assert_sha "$COUNT_ROOT/artifacts/cpu.tsv" "$COUNT_FIXTURE_SHA"
  assert_sha "$COUNT_ROOT/artifacts/gpu.tsv" "$COUNT_FIXTURE_SHA"
  assert_sha "$COUNT_ROOT/artifacts/ops.bin" "$OPS_SHA"
  assert_sha "$COUNT_ROOT/artifacts/checkpoint.bin" "$CHECKPOINT_SHA"

  {
    printf 'confirmer_pid=590322 ppid=1 start=125595502 cwd=/workspace/ev-cc20\n'
    printf 'confirmer_cmd=%s pending=%s active=%s gpu_apps=0\n' \
      "$cmd" "$pending" "$active"
    sha256sum \
      "$PROTECTED/ops.bin" \
      "$PROTECTED/ppcpu" \
      "$PROTECTED/ppgpu" \
      "$PROTECTED/FINGERPRINTS" \
      "$PROTECTED/PARITY.complete" \
      "$PROTECTED/BORROW.complete" \
      "$PROTECTED/DRAINED_AT" \
      "$QSRC/results.tsv" \
      "$QSRC/target/release/build_circuit" \
      "$QSRC/target/release/eval_circuit" \
      "$QART/FULLCONFIRM-PATH.complete" \
      "$COUNT_ROOT/PARITY.complete" \
      "$COUNT_ROOT/artifacts/cpu.tsv" \
      "$COUNT_ROOT/artifacts/gpu.tsv" \
      "$COUNT_ROOT/artifacts/ops.bin" \
      "$COUNT_ROOT/artifacts/checkpoint.bin"
    printf 'qsource_head=c639abedfee8931d84fad282b6d128865b597bc4\n'
    printf 'qsource_tree=7f2d009cf1332380e15e13756773f6a66afc7cb7\n'
    printf 'qsource_clean=1 score_absent=1 dedicated_absent=1 runs_absent=1\n'
  } > "$out.tmp"
  mv "$out.tmp" "$out"
}

test ! -e "$ROOT"
test "$(nvidia-smi --query-gpu=name --format=csv,noheader | tr -d '\r')" = \
  'NVIDIA GeForce RTX 4090'
test "$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader | tr -d '\r')" = 8.9
test "$(/usr/local/cuda/bin/nvcc --list-gpu-code | grep -Fc sm_89)" -ge 1

PRE=/workspace/.b1-24-faultshots-protected-before.$$
trap 'test ! -e "$PRE" || rm -f "$PRE"' EXIT
assert_protected "$PRE"
mkdir "$ROOT"
mv "$PRE" "$ROOT/protected.before"
trap - EXIT

git clone --branch research/b523-b1-24-gpu-parity --single-branch \
  https://github.com/odinfree/ecdsafail-challenge.git "$SRC" \
  > "$ROOT/clone.stdout" 2> "$ROOT/clone.stderr"
git -C "$SRC" checkout --detach "$SOURCE_COMMIT" \
  > "$ROOT/checkout.stdout" 2> "$ROOT/checkout.stderr"
test "$(git -C "$SRC" rev-parse HEAD)" = "$SOURCE_COMMIT"
test "$(git -C "$SRC" rev-parse HEAD^{tree})" = "$SOURCE_TREE"
test "$(git -C "$SRC" rev-parse "$SEMANTIC_COMMIT^{tree}")" = "$SEMANTIC_TREE"
git -C "$SRC" diff --quiet "$SEMANTIC_COMMIT" "$SOURCE_COMMIT" -- src/point_add
test "$(git -C "$SRC" status --short)" = ""
assert_sha "$SRC/Cargo.toml" \
  29efe8d7da9c7879bf5bd85d1dfb240db3282bf73d80e3f92ba136381068b3b0
assert_sha "$SRC/Cargo.lock" \
  42ff16919e551891ad1b21821329b116d133194245a0e0734a33573dfe598e07
assert_sha "$SRC/src/point_add/pingpong_div.rs" \
  92ffe2f17886334e9db863e81683ef31911c46b759b7b7acac65017591e6c66d
assert_sha "$SRC/src/bin/pingpong_filter.rs" "$CPU_SOURCE_SHA"
assert_sha "$SRC/.lane/b1-24-parity/pingpong_filter.cu" "$CUDA_SOURCE_SHA"

mkdir "$ART"
seq "$FIXTURE_FROM" "$FIXTURE_TO" > "$ART/fixtures.txt"
cp "$COUNT_ROOT/artifacts/checkpoint.bin" "$ART/checkpoint.bin"
assert_sha "$ART/checkpoint.bin" "$CHECKPOINT_SHA"
test "$(head -c 8 "$ART/checkpoint.bin")" = PPFSCKP1
test "$(od -An -tu8 -j8 -N8 "$ART/checkpoint.bin" | tr -d ' \n')" = "$OPS_COUNT"

(
  cd "$SRC"
  cargo build --release --locked --offline --bin pingpong_filter
) > "$ART/cargo.stdout" 2> "$ART/cargo.stderr"
test "$(git -C "$SRC" status --short)" = ""

env -i PATH=/usr/local/bin:/usr/bin:/bin \
  "$SRC/target/release/pingpong_filter" \
  --nonces "$ART/fixtures.txt" --jobs 32 --faultshots \
  > "$ART/cpu-faultshots.tsv" 2> "$ART/cpu-faultshots.stderr"
test "$(wc -l < "$ART/cpu-faultshots.tsv" | tr -d ' ')" -eq 32
awk -v s="$FIXTURE_FROM" '
  NF != 3 || $1 !~ /^[0-9]+$/ || $2 !~ /^[0-9]+$/ ||
  $3 !~ /^[0-9a-f]+$/ || length($3) != 2256 ||
  $1+0 != s+NR-1 || seen[$1]++ { bad=1 }
  END { exit bad }
' "$ART/cpu-faultshots.tsv"
test "$(grep -c 'WARNING\|FALSE NEGATIVE' "$ART/cpu-faultshots.stderr" || true)" -eq 0
awk '{print $1, $2}' "$ART/cpu-faultshots.tsv" > "$ART/cpu-counts.tsv"
cmp "$ART/cpu-counts.tsv" "$COUNT_ROOT/artifacts/cpu.tsv"

python3 - "$ART/cpu-faultshots.tsv" <<'PY'
import sys

for line in open(sys.argv[1], encoding="ascii"):
    nonce, count, mask = line.split()
    words = [int(mask[i:i + 16], 16) for i in range(0, len(mask), 16)]
    assert len(words) == 141
    assert sum(word.bit_count() for word in words) == int(count)
PY

# CPU wrong-stream negative: a different round count changes the emitted
# circuit identity and must hit the source-bound operation guard before output.
set +e
env -i PATH=/usr/local/bin:/usr/bin:/bin SUB4_PP_ROUNDS=699 \
  "$SRC/target/release/pingpong_filter" \
  --nonces "$ART/fixtures.txt" --jobs 1 --faultshots \
  > "$ART/cpu-wrong-stream.stdout" 2> "$ART/cpu-wrong-stream.stderr"
cpu_wrong_rc=$?
set -e
test "$cpu_wrong_rc" -eq 4
grep -Fq 'REFUSING TO RUN' "$ART/cpu-wrong-stream.stderr"
test ! -s "$ART/cpu-wrong-stream.stdout"

/usr/local/cuda/bin/nvcc -arch=sm_89 -O3 -lineinfo \
  -Xptxas -v -Xptxas -O3 -allow-unsupported-compiler \
  -o "$ART/pingpong_gpu" "$SRC/.lane/b1-24-parity/pingpong_filter.cu" \
  > "$ART/nvcc.stdout" 2> "$ART/nvcc.stderr"
test "$(/usr/local/cuda/bin/cuobjdump --list-elf "$ART/pingpong_gpu" | grep -Fc sm_89)" -ge 1

assert_gpu_idle
set +e
env -i PATH=/usr/local/cuda/bin:/usr/local/bin:/usr/bin:/bin \
  "$ART/pingpong_gpu" --checkpoint "$ART/checkpoint.bin" \
  --ops 12822407 --from "$FIXTURE_FROM" --to "$FIXTURE_FROM" --faultshots \
  > "$ART/gpu-wrong-ops.stdout" 2> "$ART/gpu-wrong-ops.stderr"
gpu_wrong_ops_rc=$?
set -e
test "$gpu_wrong_ops_rc" -eq 4
grep -Fq 'REFUSING TO RUN' "$ART/gpu-wrong-ops.stderr"

python3 - "$ART/checkpoint.bin" "$ART/wrong-checkpoint.bin" <<'PY'
import struct
import sys

data = bytearray(open(sys.argv[1], "rb").read())
data[8:16] = struct.pack("<Q", 12_822_407)
open(sys.argv[2], "wb").write(data)
PY
set +e
env -i PATH=/usr/local/cuda/bin:/usr/local/bin:/usr/bin:/bin \
  "$ART/pingpong_gpu" --checkpoint "$ART/wrong-checkpoint.bin" \
  --ops 12822407 --from "$FIXTURE_FROM" --to "$FIXTURE_FROM" --faultshots \
  > "$ART/gpu-wrong-checkpoint.stdout" 2> "$ART/gpu-wrong-checkpoint.stderr"
gpu_wrong_checkpoint_rc=$?
set -e
test "$gpu_wrong_checkpoint_rc" -eq 4
grep -Fq 'source-bound B1=24 identity' "$ART/gpu-wrong-checkpoint.stderr"

set +e
env -i PATH=/usr/local/cuda/bin:/usr/local/bin:/usr/bin:/bin \
  "$ART/pingpong_gpu" --checkpoint "$ART/checkpoint.bin" \
  --ops "$OPS_COUNT" --from "$FIXTURE_FROM" --to "$FIXTURE_FROM" \
  --screen --faultshots \
  > "$ART/gpu-incomplete-mask.stdout" 2> "$ART/gpu-incomplete-mask.stderr"
gpu_incomplete_rc=$?
set -e
test "$gpu_incomplete_rc" -eq 2
grep -Fq 'incompatible with incomplete --screen mode' "$ART/gpu-incomplete-mask.stderr"

env -i PATH=/usr/local/cuda/bin:/usr/local/bin:/usr/bin:/bin \
  "$ART/pingpong_gpu" --checkpoint "$ART/checkpoint.bin" \
  --ops "$OPS_COUNT" --selftest \
  > "$ART/selftest.stdout" 2> "$ART/selftest.stderr"
grep -Fqx 'gx OK' "$ART/selftest.stderr"
grep -Fqx 'gy OK' "$ART/selftest.stderr"

env -i PATH=/usr/local/cuda/bin:/usr/local/bin:/usr/bin:/bin \
  "$ART/pingpong_gpu" --checkpoint "$ART/checkpoint.bin" \
  --ops "$OPS_COUNT" --from "$FIXTURE_FROM" --to "$FIXTURE_TO" \
  --batch 32 --window 512 --faultshots --verbose \
  > "$ART/gpu-faultshots.tsv" 2> "$ART/gpu-faultshots.stderr"
test "$(wc -l < "$ART/gpu-faultshots.tsv" | tr -d ' ')" -eq 32
awk -v s="$FIXTURE_FROM" '
  NF != 3 || $1 !~ /^[0-9]+$/ || $2 !~ /^[0-9]+$/ ||
  $3 !~ /^[0-9a-f]+$/ || length($3) != 2256 ||
  $1+0 != s+NR-1 || seen[$1]++ { bad=1 }
  END { exit bad }
' "$ART/gpu-faultshots.tsv"
grep -Fq 'checkpoint: 12822408 ops' "$ART/gpu-faultshots.stderr"
grep -Fq 'model windows: rounds_div=700 rounds_mul=696 replay_fold=53 endpoint_fold=20' \
  "$ART/gpu-faultshots.stderr"
cmp "$ART/cpu-faultshots.tsv" "$ART/gpu-faultshots.tsv"
assert_gpu_idle
test "$(git -C "$SRC" status --short)" = ""

assert_protected "$ROOT/protected.after"
cmp "$ROOT/protected.before" "$ROOT/protected.after"

{
  printf 'semantic_commit=%s semantic_tree=%s\n' "$SEMANTIC_COMMIT" "$SEMANTIC_TREE"
  printf 'source_commit=%s source_tree=%s\n' "$SOURCE_COMMIT" "$SOURCE_TREE"
  printf 'ops_count=%s ops_sha256=%s checkpoint_sha256=%s\n' \
    "$OPS_COUNT" "$OPS_SHA" "$CHECKPOINT_SHA"
  printf 'fixtures=%s-%s inclusive rows=32 cpu=gpu exact_fault_masks\n' \
    "$FIXTURE_FROM" "$FIXTURE_TO"
  sha256sum \
    "$SRC/src/point_add/pingpong_div.rs" \
    "$SRC/src/bin/pingpong_filter.rs" \
    "$SRC/.lane/b1-24-parity/pingpong_filter.cu" \
    "$SRC/target/release/pingpong_filter" \
    "$ART/checkpoint.bin" \
    "$ART/pingpong_gpu" \
    "$ART/cpu-faultshots.tsv" \
    "$ART/gpu-faultshots.tsv" \
    "$ROOT/protected.before" \
    "$0"
} > "$ROOT/FINGERPRINTS.tmp"
mv "$ROOT/FINGERPRINTS.tmp" "$ROOT/FINGERPRINTS"

{
  printf 'verdict=PASS_EXACT_FAULTSHOT_PARITY\n'
  printf 'semantic_commit=%s source_commit=%s\n' "$SEMANTIC_COMMIT" "$SOURCE_COMMIT"
  printf 'ops_count=%s ops_sha256=%s\n' "$OPS_COUNT" "$OPS_SHA"
  printf 'checkpoint_sha256=%s\n' "$CHECKPOINT_SHA"
  printf 'cpu_sha256=%s cuda_sha256=%s\n' \
    "$(sha "$SRC/target/release/pingpong_filter")" "$(sha "$ART/pingpong_gpu")"
  printf 'faultshot_sha256=%s rows=32 words_per_row=141 cpu=cuda popcount=count\n' \
    "$(sha "$ART/cpu-faultshots.tsv")"
  printf 'wrong_stream_cpu_rc=4 wrong_ops_gpu_rc=4 wrong_checkpoint_gpu_rc=4 incomplete_mask_rc=2\n'
  printf 'protected_manifest_sha256=%s confirmer_preserved=590322 pending=0 gpu_apps=0\n' \
    "$(sha "$ROOT/protected.before")"
} > "$ROOT/FAULTSHOTS.complete.tmp"
mv "$ROOT/FAULTSHOTS.complete.tmp" "$ROOT/FAULTSHOTS.complete"
printf 'B1_24_FAULTSHOTS_COMPLETE rows=32 mask_sha256=%s\n' \
  "$(sha "$ART/cpu-faultshots.tsv")"
