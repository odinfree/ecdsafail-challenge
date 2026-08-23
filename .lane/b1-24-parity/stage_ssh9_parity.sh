#!/bin/bash
# Isolated, no-hunt Linux/CUDA parity gate for the predeclared B1=24 fixture
# set. The source checkout is pinned to the source-packet commit below. This
# script never launches a range scan and never touches the incumbent confirmer.
set -euo pipefail

ROOT=/workspace/ev-b523-b1-24-90a27e1
SRC=$ROOT/source
ART=$ROOT/artifacts
PROTECTED=/workspace/ev-g1000-q1276-0b6ac181
INC=/workspace/ev-cc20
QSRC=/workspace/q1276-fullconfirm-c639abe
QART=/workspace/q1276-fullconfirm-c639abe-artifacts
SOURCE_COMMIT=90a27e1480e064ed2d020e0bf2b63be1c926cfa5
SOURCE_TREE=b33f4e96c6186eb3e76d159830be8622532a2230
SEMANTIC_COMMIT=8a3c06e57f169d842fdb33722415dc66236a0b02
SEMANTIC_TREE=b49fd5ef8bf42be563f9defa2f2a3282b27aa834
OPS_COUNT=12822408
OPS_SHA=af28dbc49471651c3e856c62c1fd97cb429469cde4b66fe7fe082a0d23fe1ad7
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
      "$QART/FULLCONFIRM-PATH.complete"
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

PRE=/workspace/.b1-24-protected-before.$$
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
assert_sha "$SRC/src/bin/build_circuit.rs" \
  ac013f1d851156a117c7d41ddb16cb5bb014ed4e6ed4679df143207b46852f33
assert_sha "$SRC/src/bin/eval_circuit.rs" \
  b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b
assert_sha "$SRC/src/bin/pingpong_filter.rs" \
  23ab339c466a41dbba4da65f2d4ab8bd70f8d504708a8e9135f12e48cead4658
assert_sha "$SRC/.lane/b1-24-parity/pingpong_filter.cu" \
  49989f9f5801005ac5ca478f24cddbda7c7ce99ee9287c876864435243014571

mkdir "$ART"
(
  cd "$SRC"
  cargo build --release --locked --offline --bin build_circuit --bin pingpong_filter
) > "$ART/cargo.stdout" 2> "$ART/cargo.stderr"
test "$(git -C "$SRC" status --short)" = ""

(
  cd "$ART"
  env -i PATH=/usr/local/bin:/usr/bin:/bin \
    "$SRC/target/release/build_circuit"
) > "$ART/build.stdout" 2> "$ART/build.stderr"
grep -Fqx '  emitted ops : 12822408' "$ART/build.stdout"
grep -Fqx '  wrote       : ops.bin (50931262 bytes on disk, 718054864 uncompressed, 14.1x)' \
  "$ART/build.stdout"
test "$(stat -c %s "$ART/ops.bin")" -eq 50931262
assert_sha "$ART/ops.bin" "$OPS_SHA"

env -i PATH=/usr/local/bin:/usr/bin:/bin \
  "$SRC/target/release/pingpong_filter" \
  --dump-checkpoint "$ART/checkpoint.bin" \
  > "$ART/checkpoint.stdout" 2> "$ART/checkpoint.stderr"
grep -Fqx 'wrote Fiat-Shamir checkpoint for 12822408 ops to /workspace/ev-b523-b1-24-90a27e1/artifacts/checkpoint.bin' \
  "$ART/checkpoint.stderr"
test "$(stat -c %s "$ART/checkpoint.bin")" -eq 5064
test "$(head -c 8 "$ART/checkpoint.bin")" = PPFSCKP1
test "$(od -An -tu8 -j8 -N8 "$ART/checkpoint.bin" | tr -d ' \n')" = "$OPS_COUNT"

env -i PATH=/usr/local/bin:/usr/bin:/bin \
  "$SRC/target/release/pingpong_filter" \
  --from "$FIXTURE_FROM" --to "$FIXTURE_TO" --jobs 32 \
  > "$ART/cpu.tsv" 2> "$ART/cpu.stderr"
test "$(wc -l < "$ART/cpu.tsv" | tr -d ' ')" -eq 32
awk -v s="$FIXTURE_FROM" '
  NF != 2 || $1 !~ /^[0-9]+$/ || $2 !~ /^[0-9]+$/ ||
  $1+0 != s+NR-1 || seen[$1]++ { bad=1 }
  END { exit bad }
' "$ART/cpu.tsv"
sed -n '1p' "$ART/cpu.tsv" | grep -Fqx '81327465284 17'
sed -n '2p' "$ART/cpu.tsv" | grep -Fqx '81327465285 24'
sed -n '3p' "$ART/cpu.tsv" | grep -Fqx '81327465286 17'
sed -n '4p' "$ART/cpu.tsv" | grep -Fqx '81327465287 21'
test "$(grep -c 'WARNING\|FALSE NEGATIVE' "$ART/cpu.stderr" || true)" -eq 0

/usr/local/cuda/bin/nvcc -arch=sm_89 -O3 -lineinfo \
  -Xptxas -v -Xptxas -O3 -allow-unsupported-compiler \
  -o "$ART/pingpong_gpu" "$SRC/.lane/b1-24-parity/pingpong_filter.cu" \
  > "$ART/nvcc.stdout" 2> "$ART/nvcc.stderr"
test "$(/usr/local/cuda/bin/cuobjdump --list-elf "$ART/pingpong_gpu" | grep -Fc sm_89)" -ge 1

assert_gpu_idle
set +e
env -i PATH=/usr/local/cuda/bin:/usr/local/bin:/usr/bin:/bin \
  "$ART/pingpong_gpu" --checkpoint "$ART/checkpoint.bin" \
  --ops 12822407 --from "$FIXTURE_FROM" --to "$FIXTURE_FROM" \
  > "$ART/wrong-ops.stdout" 2> "$ART/wrong-ops.stderr"
wrong_rc=$?
set -e
test "$wrong_rc" -eq 4
grep -Fq 'REFUSING TO RUN' "$ART/wrong-ops.stderr"

env -i PATH=/usr/local/cuda/bin:/usr/local/bin:/usr/bin:/bin \
  "$ART/pingpong_gpu" --checkpoint "$ART/checkpoint.bin" \
  --ops "$OPS_COUNT" --selftest \
  > "$ART/selftest.stdout" 2> "$ART/selftest.stderr"
grep -Fqx 'gx OK' "$ART/selftest.stderr"
grep -Fqx 'gy OK' "$ART/selftest.stderr"

env -i PATH=/usr/local/cuda/bin:/usr/local/bin:/usr/bin:/bin \
  "$ART/pingpong_gpu" --checkpoint "$ART/checkpoint.bin" \
  --ops "$OPS_COUNT" --from "$FIXTURE_FROM" --to "$FIXTURE_TO" \
  --batch 32 --window 512 --verbose \
  > "$ART/gpu.tsv" 2> "$ART/gpu.stderr"
test "$(wc -l < "$ART/gpu.tsv" | tr -d ' ')" -eq 32
awk -v s="$FIXTURE_FROM" '
  NF != 2 || $1 !~ /^[0-9]+$/ || $2 !~ /^[0-9]+$/ ||
  $1+0 != s+NR-1 || seen[$1]++ { bad=1 }
  END { exit bad }
' "$ART/gpu.tsv"
grep -Fq 'checkpoint: 12822408 ops' "$ART/gpu.stderr"
grep -Fq 'model windows: rounds_div=700 rounds_mul=696 replay_fold=53 endpoint_fold=20' \
  "$ART/gpu.stderr"
cmp "$ART/cpu.tsv" "$ART/gpu.tsv"
assert_gpu_idle
test "$(git -C "$SRC" status --short)" = ""

assert_protected "$ROOT/protected.after"
cmp "$ROOT/protected.before" "$ROOT/protected.after"

{
  printf 'semantic_commit=%s semantic_tree=%s\n' "$SEMANTIC_COMMIT" "$SEMANTIC_TREE"
  printf 'source_commit=%s source_tree=%s\n' "$SOURCE_COMMIT" "$SOURCE_TREE"
  printf 'ops_count=%s ops_sha256=%s\n' "$OPS_COUNT" "$OPS_SHA"
  printf 'fixtures=%s-%s inclusive rows=32 cpu=gpu exact_counts\n' \
    "$FIXTURE_FROM" "$FIXTURE_TO"
  sha256sum \
    "$SRC/src/point_add/pingpong_div.rs" \
    "$SRC/src/bin/pingpong_filter.rs" \
    "$SRC/.lane/b1-24-parity/pingpong_filter.cu" \
    "$SRC/target/release/build_circuit" \
    "$SRC/target/release/pingpong_filter" \
    "$ART/ops.bin" \
    "$ART/checkpoint.bin" \
    "$ART/pingpong_gpu" \
    "$ART/cpu.tsv" \
    "$ART/gpu.tsv" \
    "$ROOT/protected.before" \
    "$0"
} > "$ROOT/FINGERPRINTS.tmp"
mv "$ROOT/FINGERPRINTS.tmp" "$ROOT/FINGERPRINTS"

{
  printf 'verdict=PASS_COUNT_PARITY_HOLD_MASK_PARITY\n'
  printf 'semantic_commit=%s source_commit=%s\n' "$SEMANTIC_COMMIT" "$SOURCE_COMMIT"
  printf 'ops_count=%s ops_sha256=%s\n' "$OPS_COUNT" "$OPS_SHA"
  printf 'checkpoint_sha256=%s\n' "$(sha "$ART/checkpoint.bin")"
  printf 'cpu_sha256=%s cuda_sha256=%s\n' \
    "$(sha "$SRC/target/release/pingpong_filter")" "$(sha "$ART/pingpong_gpu")"
  printf 'fixture_sha256=%s rows=32 cpu=cuda wrong_ops_rc=4 selftest=pass\n' \
    "$(sha "$ART/cpu.tsv")"
  printf 'protected_manifest_sha256=%s confirmer_preserved=590322 pending=0 gpu_apps=0\n' \
    "$(sha "$ROOT/protected.before")"
} > "$ROOT/PARITY.complete.tmp"
mv "$ROOT/PARITY.complete.tmp" "$ROOT/PARITY.complete"
printf 'B1_24_PARITY_COMPLETE rows=32 fixture_sha256=%s\n' "$(sha "$ART/cpu.tsv")"
