#!/bin/bash
# Finalize the preserved attempt whose computation and post-guard completed but
# whose wrapper correctly refused to hash the non-file argv[0] value "bash".
set -euo pipefail

ROOT=/workspace/ev-b523-b1-24-faultshots-f376e53
SRC=$ROOT/source
ART=$ROOT/artifacts
PROTECTED=/workspace/ev-g1000-q1276-0b6ac181
INC=/workspace/ev-cc20
QSRC=/workspace/q1276-fullconfirm-c639abe
QART=/workspace/q1276-fullconfirm-c639abe-artifacts
SOURCE_COMMIT=f376e532f9e5ac293bfda8cfbd27edb6c1e97f0b
SOURCE_TREE=71598311d15f0b49f6a34360b664182cbb6be698
OPS_COUNT=12822408
OPS_SHA=af28dbc49471651c3e856c62c1fd97cb429469cde4b66fe7fe082a0d23fe1ad7
CHECKPOINT_SHA=7080f69f4aabd7be663713d57c553d1e80913a2fc1d5b4958e7ab5c4b46a8dcc
CPU_SOURCE_SHA=cba1e48b979a6f4a1c8623e12a59a17c0dda2d688213b3af5131e162883a0753
CUDA_SOURCE_SHA=2986855fd6ad3334b448f296047d30851ba051dc2d2b9204fd8da08461856bae
MASK_SHA=00a545dacb9fa68d7ffcb4d52a7a5e0edf802443bc8e3ecacd845cf181755cf9
PRE_SHA=57ae9a4e6656e33cd7cf483f26a342b58bca44544360b88095d92582e94b8e40

sha() { sha256sum "$1" | awk '{print $1}'; }
assert_sha() { test "$(sha "$1")" = "$2"; }

test -f "$0"
test -d "$ROOT"
test ! -e "$ROOT/FAULTSHOTS.complete"
test "$(git -C "$SRC" rev-parse HEAD)" = "$SOURCE_COMMIT"
test "$(git -C "$SRC" rev-parse HEAD^{tree})" = "$SOURCE_TREE"
test "$(git -C "$SRC" status --short)" = ""
assert_sha "$SRC/src/bin/pingpong_filter.rs" "$CPU_SOURCE_SHA"
assert_sha "$SRC/.lane/b1-24-parity/pingpong_filter.cu" "$CUDA_SOURCE_SHA"
assert_sha "$ART/checkpoint.bin" "$CHECKPOINT_SHA"
test "$(od -An -tu8 -j8 -N8 "$ART/checkpoint.bin" | tr -d ' \n')" = "$OPS_COUNT"
assert_sha "$ART/cpu-faultshots.tsv" "$MASK_SHA"
assert_sha "$ART/gpu-faultshots.tsv" "$MASK_SHA"
cmp "$ART/cpu-faultshots.tsv" "$ART/gpu-faultshots.tsv"
assert_sha "$ROOT/protected.before" "$PRE_SHA"
assert_sha "$ROOT/protected.after" "$PRE_SHA"
cmp "$ROOT/protected.before" "$ROOT/protected.after"

test "$(wc -l < "$ART/cpu-faultshots.tsv" | tr -d ' ')" -eq 32
python3 - "$ART/cpu-faultshots.tsv" <<'PY'
import sys

expect = 81_327_465_284
for row, line in enumerate(open(sys.argv[1], encoding="ascii")):
    nonce, count, mask = line.split()
    assert int(nonce) == expect + row
    assert len(mask) == 141 * 16
    words = [int(mask[i:i + 16], 16) for i in range(0, len(mask), 16)]
    assert sum(word.bit_count() for word in words) == int(count)
assert row == 31
PY

test ! -s "$ART/cpu-wrong-stream.stdout"
grep -Fq 'REFUSING TO RUN' "$ART/cpu-wrong-stream.stderr"
test ! -s "$ART/gpu-wrong-ops.stdout"
grep -Fq 'REFUSING TO RUN' "$ART/gpu-wrong-ops.stderr"
test ! -s "$ART/gpu-wrong-checkpoint.stdout"
grep -Fq 'source-bound B1=24 identity' "$ART/gpu-wrong-checkpoint.stderr"
test ! -s "$ART/gpu-incomplete-mask.stdout"
grep -Fq 'incompatible with incomplete --screen mode' "$ART/gpu-incomplete-mask.stderr"
grep -Fqx 'gx OK' "$ART/selftest.stderr"
grep -Fqx 'gy OK' "$ART/selftest.stderr"

# Re-establish the protected state at finalization time, not only at the end of
# the preserved computation.
test "$(readlink /proc/590322/cwd)" = "$INC"
test "$(awk '{print $22}' /proc/590322/stat)" = 125595502
test "$(ps -o ppid= -p 590322 | tr -d ' ')" = 1
test "$(tr '\0' ' ' < /proc/590322/cmdline)" = '/bin/bash ./confirm_loop.sh '
pending=$(comm -23 \
  <(grep '^[0-9]' "$INC/survivors.tsv" | cut -d ' ' -f 1 | sort -u) \
  <(grep '^[0-9]' "$INC/confirmed.txt" | sort -u) | wc -l | tr -d ' ')
active=$(ps -eo args | grep -c '^/workspace/ev-cc20/eval_circuit --note cf-' || true)
test "$pending" -eq 0
test "$active" -eq 0
test -z "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader | sed '/^$/d')"

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
test "$(git -C "$QSRC" rev-parse HEAD)" = c639abedfee8931d84fad282b6d128865b597bc4
test "$(git -C "$QSRC" status --short)" = ""
assert_sha "$QSRC/results.tsv" \
  eea840222afd2424445550252f25795d63eb4bc3904b8c87f0213b5f22abc810
assert_sha "$QART/FULLCONFIRM-PATH.complete" \
  b09d29a129f61e02a95152da747e7fbe675375bbe23e945e597f9c6c88d927ee

{
  printf 'source_commit=%s source_tree=%s\n' "$SOURCE_COMMIT" "$SOURCE_TREE"
  printf 'ops_count=%s ops_sha256=%s checkpoint_sha256=%s\n' \
    "$OPS_COUNT" "$OPS_SHA" "$CHECKPOINT_SHA"
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
    "$ROOT/protected.after" \
    "$0"
} > "$ROOT/FINGERPRINTS.final.tmp"
mv "$ROOT/FINGERPRINTS.final.tmp" "$ROOT/FINGERPRINTS"

{
  printf 'verdict=PASS_EXACT_FAULTSHOT_PARITY\n'
  printf 'source_commit=%s source_tree=%s\n' "$SOURCE_COMMIT" "$SOURCE_TREE"
  printf 'ops_count=%s ops_sha256=%s\n' "$OPS_COUNT" "$OPS_SHA"
  printf 'checkpoint_sha256=%s\n' "$CHECKPOINT_SHA"
  printf 'cpu_sha256=%s cuda_sha256=%s\n' \
    "$(sha "$SRC/target/release/pingpong_filter")" "$(sha "$ART/pingpong_gpu")"
  printf 'faultshot_sha256=%s rows=32 words_per_row=141 cpu=cuda popcount=count\n' "$MASK_SHA"
  printf 'wrong_stream_cpu_rc=4 wrong_ops_gpu_rc=4 wrong_checkpoint_gpu_rc=4 incomplete_mask_rc=2\n'
  printf 'protected_manifest_sha256=%s confirmer_preserved=590322 pending=0 gpu_apps=0\n' "$PRE_SHA"
  printf 'finalizer_sha256=%s fingerprints_sha256=%s\n' \
    "$(sha "$0")" "$(sha "$ROOT/FINGERPRINTS")"
} > "$ROOT/FAULTSHOTS.complete.tmp"
mv "$ROOT/FAULTSHOTS.complete.tmp" "$ROOT/FAULTSHOTS.complete"
printf 'B1_24_FAULTSHOTS_COMPLETE rows=32 mask_sha256=%s receipt_sha256=%s\n' \
  "$MASK_SHA" "$(sha "$ROOT/FAULTSHOTS.complete")"
