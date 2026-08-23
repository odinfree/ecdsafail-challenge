#!/bin/bash
# Qualify source-build, tail-patch, and unchanged full-evaluator equivalence
# for the exact Q1276 stream on the reserved CPU host. This does no GPU work.
set -euo pipefail

SRC=/workspace/q1276-fullconfirm-c639abe
CAND=/workspace/ev-g1000-q1276-0b6ac181
INC=/workspace/ev-cc20
OUT=/workspace/q1276-fullconfirm-c639abe-artifacts
BUILD=$SRC/target/release/build_circuit
EVAL=$SRC/target/release/eval_circuit
PATCH=$INC/tail_patch

test "$(git -C "$SRC" rev-parse HEAD)" = \
  c639abedfee8931d84fad282b6d128865b597bc4
test "$(git -C "$SRC" rev-parse HEAD^{tree})" = \
  7f2d009cf1332380e15e13756773f6a66afc7cb7
test "$(sha256sum "$SRC/src/point_add/pingpong_div.rs" | awk '{print $1}')" = \
  ef9dd2d570c5826f0739509c45a082927985f68109c4dcbc53c36d9add2bb6d6
test "$(sha256sum "$SRC/src/point_add/trailmix_ludicrous/square/product_register.rs" | awk '{print $1}')" = \
  d2ee51194594123d982be3f135fbc087d24bf1cd645d8346c986f8d5dce3724d
test "$(sha256sum "$SRC/src/bin/eval_circuit.rs" | awk '{print $1}')" = \
  b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b
test "$(sha256sum "$CAND/ops.bin" | awk '{print $1}')" = \
  d1461959eac52b19b644f1f97a3b44a3ea249a109f14a406d19e872cd17c5422
test "$(sha256sum "$PATCH" | awk '{print $1}')" = \
  e1c5174ae456ea2ac3aa3b1a6377744c1617b81de4060734adf7dc7d80eee313
test "$(sha256sum "$CAND/ppcpu" | awk '{print $1}')" = \
  73f09fb8f5d84bdd595c730e0be34a8a8abb5d78184c8f431987708b4d2cc61b
test "$(sha256sum "$CAND/ppgpu" | awk '{print $1}')" = \
  672a47004f1f0a4a3ebc0d0a3e4a41e2dd903b1e1493bf493757fefed355cf2d
grep -Fqx 'state_digest=5a0a4564563a201a' "$CAND/FINGERPRINTS"
test -x "$BUILD"
test -x "$EVAL"

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

assert_gpu_idle
test "$(pending_confirms)" -eq 0
test "$(ps -eo args | grep -c '^/workspace/ev-cc20/eval_circuit --note cf-' || true)" -eq 0
test "$(readlink /proc/590322/cwd)" = /workspace/ev-cc20
kill -0 590322
test ! -e "$OUT"
mkdir "$OUT"
mkdir "$OUT/root-write-sentinel"
set +e
(: > "$OUT/root-write-sentinel") 2> "$OUT/root-write-sentinel.stderr"
sentinel_rc=$?
set -e
test "$sentinel_rc" -ne 0
rmdir "$OUT/root-write-sentinel"
printf 'root_file_write_to_directory=blocked rc=%s\n' "$sentinel_rc" \
  > "$OUT/root-write-sentinel.complete"

for nonce in 135608492183 0 7 2500069332; do
  mkdir "$OUT/source-$nonce" "$OUT/patch-$nonce"
  (
    cd "$OUT/source-$nonce"
    env -i PATH=/root/.cargo/bin:/usr/local/bin:/usr/bin:/bin \
      SUB4_PINGPONG_TAIL_NONCE="$nonce" "$BUILD"
  ) > "$OUT/build-$nonce.log" 2>&1
  (
    cd "$CAND"
    "$PATCH" "$nonce" "$OUT/patch-$nonce"
  ) > "$OUT/patch-$nonce.log" 2>&1

  case "$nonce" in
    135608492183) expected=d1461959eac52b19b644f1f97a3b44a3ea249a109f14a406d19e872cd17c5422 ;;
    0) expected=c3028fbdca51b01ead6940634ed4818e0cfa69421125970108bd8d754366b7a0 ;;
    7) expected=68b1cc12a9f9cd8a2f38d6f8c1bb4810b377b65bcb568bad45697a7edb15bbae ;;
    2500069332) expected=bb681cbe6c2913bd5eeae3c642a5ae080aef63f34b84c5186d1e94c9662017f5 ;;
  esac
  test "$(sha256sum "$OUT/source-$nonce/ops.bin" | awk '{print $1}')" = "$expected"
  test "$(sha256sum "$OUT/patch-$nonce/ops.bin" | awk '{print $1}')" = "$expected"
  cmp "$OUT/source-$nonce/ops.bin" "$OUT/patch-$nonce/ops.bin"
done

RESULTS=$SRC/results.tsv
RESULTS_SHA=$(sha256sum "$RESULTS" | awk '{print $1}')
test ! -e "$SRC/score.json"
# The host runs as root, so mode bits alone cannot protect the evaluator's
# compile-time sinks. Replace each path with a directory sentinel: opening it
# as a file fails even for root. Keep the tracked file recoverably in OUT.
mv "$RESULTS" "$OUT/results.original.tsv"
mkdir "$RESULTS" "$SRC/score.json"
restore_results() {
  if test -d "$RESULTS"; then
    rmdir "$RESULTS"
  fi
  if test -f "$OUT/results.original.tsv"; then
    mv "$OUT/results.original.tsv" "$RESULTS"
  fi
  if test -d "$SRC/score.json"; then
    rmdir "$SRC/score.json"
  fi
}
trap restore_results EXIT

for nonce in 135608492183 0 7 2500069332; do
  set +e
  (
    cd "$OUT/patch-$nonce"
    timeout 600 "$EVAL" --note "q1276-fullconfirm-path-$nonce"
  ) > "$OUT/eval-$nonce.log" 2>&1
  rc=$?
  set -e
  test "$rc" -eq 1
  cls=$(sed -n 's/.*classical mismatches  *: *\([0-9][0-9]*\).*/\1/p' "$OUT/eval-$nonce.log" | tail -1)
  phase=$(sed -n 's/.*phase-garbage batches  *: *\([0-9][0-9]*\).*/\1/p' "$OUT/eval-$nonce.log" | tail -1)
  anc=$(sed -n 's/.*ancilla-garbage batches  *: *\([0-9][0-9]*\).*/\1/p' "$OUT/eval-$nonce.log" | tail -1)
  first=$(sed -n 's/.*CLASSICAL MISMATCH shot \([0-9][0-9]*\).*/\1/p' "$OUT/eval-$nonce.log" | head -1)
  case "$nonce" in
    135608492183) test "$cls:$phase:$anc:$first" = 15:5:0:32 ;;
    0) test "$cls:$phase:$anc:$first" = 18:11:0:521 ;;
    7) test "$cls:$phase:$anc:$first" = 20:11:0:594 ;;
    2500069332) test "$cls:$phase:$anc:$first" = 17:10:0:266 ;;
  esac
  printf '%s\t%s\t%s\t%s\t%s\n' "$nonce" "$cls" "$phase" "$anc" "$first" \
    >> "$OUT/full.tsv"
done

test -d "$RESULTS"
test -z "$(find "$RESULTS" -mindepth 1 -maxdepth 1 -print -quit)"
test -d "$SRC/score.json"
restore_results
trap - EXIT
test "$(sha256sum "$RESULTS" | awk '{print $1}')" = "$RESULTS_SHA"
test ! -e "$SRC/score.json"
test "$(pending_confirms)" -eq 0
test "$(ps -eo args | grep -c '^/workspace/ev-cc20/eval_circuit --note cf-' || true)" -eq 0
kill -0 590322
assert_gpu_idle

BUILD_SHA=$(sha256sum "$BUILD" | awk '{print $1}')
EVAL_SHA=$(sha256sum "$EVAL" | awk '{print $1}')
{
  printf 'source_commit=c639abedfee8931d84fad282b6d128865b597bc4\n'
  printf 'source_tree=7f2d009cf1332380e15e13756773f6a66afc7cb7\n'
  printf 'ops_sha256=d1461959eac52b19b644f1f97a3b44a3ea249a109f14a406d19e872cd17c5422\n'
  printf 'state_digest=5a0a4564563a201a\n'
  printf 'patcher_sha256=e1c5174ae456ea2ac3aa3b1a6377744c1617b81de4060734adf7dc7d80eee313\n'
  printf 'build_sha256=%s\n' "$BUILD_SHA"
  printf 'eval_sha256=%s\n' "$EVAL_SHA"
  printf 'fixtures=135608492183,0,7,2500069332 source_build=tail_patch full9024=exact\n'
  printf 'incumbent_pending_before=0 incumbent_pending_after=0 confirmer_preserved=590322 gpu_apps=0\n'
} > "$OUT/FULLCONFIRM-PATH.complete.tmp"
mv "$OUT/FULLCONFIRM-PATH.complete.tmp" "$OUT/FULLCONFIRM-PATH.complete"
printf 'FULLCONFIRM_PATH_COMPLETE build_sha256=%s eval_sha256=%s\n' \
  "$BUILD_SHA" "$EVAL_SHA"
