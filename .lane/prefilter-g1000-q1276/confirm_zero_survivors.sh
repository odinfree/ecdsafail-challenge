#!/bin/bash
# Confirm every retained row from the fixed Q1276 zero calibration through the
# exact CPU model and unchanged full evaluator. No GPU or range work occurs.
set -euo pipefail

CAND=/workspace/ev-g1000-q1276-0b6ac181
SRC=/workspace/q1276-fullconfirm-c639abe
INC=/workspace/ev-cc20
PATCH=$INC/tail_patch
CPU=$CAND/ppcpu
EVAL=$SRC/target/release/eval_circuit
RUN=/workspace/q1276-zero-confirm-270000000000-270128000000
INPUT=$RUN/counts.tsv
EXPECTED_COUNTS_SHA=eaf57509b143bd58a7dfcf167e942cf283d99c786a403d3bd0cf1cc964e96cf0
EXPECTED_ROWS=2
JOBS=16

test "$(git -C "$SRC" rev-parse HEAD)" = \
  c639abedfee8931d84fad282b6d128865b597bc4
test "$(git -C "$SRC" rev-parse HEAD^{tree})" = \
  7f2d009cf1332380e15e13756773f6a66afc7cb7
test "$(sha256sum "$SRC/src/bin/eval_circuit.rs" | awk '{print $1}')" = \
  b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b
test "$(sha256sum "$CAND/ops.bin" | awk '{print $1}')" = \
  d1461959eac52b19b644f1f97a3b44a3ea249a109f14a406d19e872cd17c5422
test "$(sha256sum "$CAND/FINGERPRINTS" | awk '{print $1}')" = \
  b78f07dc879a9eb6c1f5ef3248ced3a373b7d31d7a92d6d98ae741ed47964310
grep -Fqx 'state_digest=5a0a4564563a201a' "$CAND/FINGERPRINTS"
test "$(sha256sum "$PATCH" | awk '{print $1}')" = \
  e1c5174ae456ea2ac3aa3b1a6377744c1617b81de4060734adf7dc7d80eee313
test "$(sha256sum "$CPU" | awk '{print $1}')" = \
  73f09fb8f5d84bdd595c730e0be34a8a8abb5d78184c8f431987708b4d2cc61b
test "$(sha256sum "$EVAL" | awk '{print $1}')" = \
  7e146f04e9147be2b5403f613ddc553fb3ddda7054256f14e7d95fc9d3556d40
test "$(readlink /proc/590322/cwd)" = /workspace/ev-cc20
test "$(awk '{print $22}' /proc/590322/stat)" = 125595502
kill -0 590322

pending_confirms() {
  comm -23 \
    <(grep '^[0-9]' "$INC/survivors.tsv" | cut -d ' ' -f 1 | sort -u) \
    <(grep '^[0-9]' "$INC/confirmed.txt" | sort -u) | wc -l | tr -d ' '
}

test "$(pending_confirms)" -eq 0
test "$(ps -eo args | grep -c '^/workspace/ev-cc20/eval_circuit --note cf-' || true)" -eq 0
test -f "$INPUT"
test ! -e "$RUN/ZERO-CONFIRM.complete"
test ! -e "$RUN/cpu.tsv"
test ! -e "$RUN/full"
test "$(sha256sum "$INPUT" | awk '{print $1}')" = "$EXPECTED_COUNTS_SHA"
test "$EXPECTED_ROWS" -gt 0
test "$(wc -l < "$INPUT" | tr -d ' ')" = "$EXPECTED_ROWS"
awk '
  NF != 2 || $1 !~ /^[0-9]+$/ || $2 != "pred_cls=0" ||
  $1+0 < 270000000000 || $1+0 >= 270128000000 || seen[$1]++ { bad=1 }
  END { exit bad }
' "$INPUT"

mapfile -t NONCES < <(awk '{print $1}' "$INPUT")
test "${#NONCES[@]}" -eq "$EXPECTED_ROWS"
PPF_OPS="$CAND/ops.bin" "$CPU" counts "${NONCES[@]}" \
  > "$RUN/cpu.tsv.tmp" 2> "$RUN/cpu.stderr"
awk '
  NF != 5 || $1 != "nonce" || $2 !~ /^[0-9]+$/ ||
  $3 != "pred_cls=0" || $4 != "shots=9024" || $5 != "first=-1" ||
  seen[$2]++ { bad=1 }
  END { exit bad }
' "$RUN/cpu.tsv.tmp"
test "$(wc -l < "$RUN/cpu.tsv.tmp" | tr -d ' ')" = "$EXPECTED_ROWS"
awk '{print $1, $2}' "$INPUT" | sort -n > "$RUN/gpu.normalized.tmp"
awk '{print $2, $3}' "$RUN/cpu.tsv.tmp" | sort -n > "$RUN/cpu.normalized.tmp"
cmp "$RUN/gpu.normalized.tmp" "$RUN/cpu.normalized.tmp"
mv "$RUN/cpu.tsv.tmp" "$RUN/cpu.tsv"

RESULTS=$SRC/results.tsv
RESULTS_SHA=$(sha256sum "$RESULTS" | awk '{print $1}')
test "$RESULTS_SHA" = eea840222afd2424445550252f25795d63eb4bc3904b8c87f0213b5f22abc810
test ! -e "$SRC/score.json"
mv "$RESULTS" "$RUN/results.original.tsv"
mkdir "$RESULTS" "$SRC/score.json" "$RUN/full"
restore_results() {
  if test -d "$RESULTS"; then
    rmdir "$RESULTS"
  fi
  if test -f "$RUN/results.original.tsv"; then
    mv "$RUN/results.original.tsv" "$RESULTS"
  fi
  if test -d "$SRC/score.json"; then
    rmdir "$SRC/score.json"
  fi
}
trap restore_results EXIT

confirm_one() {
  local nonce=$1
  local d=$RUN/full/$nonce
  local rc cls phase anc first status tof ops_sha
  mkdir "$d"
  (
    cd "$CAND"
    "$PATCH" "$nonce" "$d"
  ) > "$d/patch.log" 2>&1
  ops_sha=$(sha256sum "$d/ops.bin" | awk '{print $1}')
  set +e
  (
    cd "$d"
    timeout 600 "$EVAL" --note "q1276-zero-confirm-$nonce"
  ) > "$d/eval.log" 2>&1
  rc=$?
  set -e
  case "$rc" in 0|1) ;; *) return 80 ;; esac
  cls=$(sed -n 's/.*classical mismatches  *: *\([0-9][0-9]*\).*/\1/p' "$d/eval.log" | tail -1)
  phase=$(sed -n 's/.*phase-garbage batches  *: *\([0-9][0-9]*\).*/\1/p' "$d/eval.log" | tail -1)
  anc=$(sed -n 's/.*ancilla-garbage batches  *: *\([0-9][0-9]*\).*/\1/p' "$d/eval.log" | tail -1)
  first=$(sed -n 's/.*CLASSICAL MISMATCH shot \([0-9][0-9]*\).*/\1/p' "$d/eval.log" | head -1)
  test -n "$cls" && test -n "$phase" && test -n "$anc"
  if test "$cls" != 0 || test -n "$first"; then
    printf 'nonce=%s cls=%s phase=%s anc=%s first=%s rc=%s\n' \
      "$nonce" "$cls" "$phase" "$anc" "${first:--1}" "$rc" > "$d/FALSIFIER"
    return 90
  fi
  if test "$phase" = 0 && test "$anc" = 0; then
    test "$rc" -eq 0
    status=clean
    tof=$(sed -n 's/.*avg executed Toffoli  *: *\([0-9.][0-9.]*\).*/\1/p' "$d/eval.log" | tail -1)
    test -n "$tof"
  else
    test "$rc" -eq 1
    status=dirty
    tof=-
  fi
  printf '%s\t0\t%s\t%s\t-1\t%s\t%s\t%s\n' \
    "$nonce" "$phase" "$anc" "$status" "$tof" "$ops_sha" > "$d/summary.tsv"
}

failure=0
pids=()
for nonce in "${NONCES[@]}"; do
  confirm_one "$nonce" &
  pids+=("$!")
  if test "${#pids[@]}" -eq "$JOBS"; then
    for pid in "${pids[@]}"; do
      wait "$pid" || failure=1
    done
    pids=()
  fi
done
for pid in "${pids[@]}"; do
  wait "$pid" || failure=1
done
test "$failure" -eq 0

find "$RUN/full" -mindepth 2 -maxdepth 2 -name summary.tsv -exec awk '1' {} + \
  | sort -n > "$RUN/full.tsv.tmp"
test "$(wc -l < "$RUN/full.tsv.tmp" | tr -d ' ')" = "$EXPECTED_ROWS"
awk 'NF != 8 || $1 !~ /^[0-9]+$/ || $2 != 0 || $3 !~ /^[0-9]+$/ ||
     $4 !~ /^[0-9]+$/ || $5 != -1 || ($6 != "clean" && $6 != "dirty") ||
     length($8) != 64 || $8 !~ /^[0-9a-f]+$/ || seen[$1]++ { bad=1 }
     END { exit bad }' "$RUN/full.tsv.tmp"

test -d "$RESULTS"
test -z "$(find "$RESULTS" -mindepth 1 -maxdepth 1 -print -quit)"
test -d "$SRC/score.json"
restore_results
trap - EXIT
test "$(sha256sum "$RESULTS" | awk '{print $1}')" = "$RESULTS_SHA"
test ! -e "$SRC/score.json"
test "$(git -C "$SRC" status --short)" = ""
test "$(pending_confirms)" -eq 0
test "$(ps -eo args | grep -c '^/workspace/ev-cc20/eval_circuit --note cf-' || true)" -eq 0
kill -0 590322

mv "$RUN/full.tsv.tmp" "$RUN/full.tsv"
clean=$(awk '$6 == "clean" {n++} END {print n+0}' "$RUN/full.tsv")
{
  printf 'interval=270000000000-270128000000 max_faults=0\n'
  printf 'counts_sha256=%s rows=%s\n' "$EXPECTED_COUNTS_SHA" "$EXPECTED_ROWS"
  printf 'ops_sha256=d1461959eac52b19b644f1f97a3b44a3ea249a109f14a406d19e872cd17c5422\n'
  printf 'state_digest=5a0a4564563a201a\n'
  printf 'cpu_sha256=73f09fb8f5d84bdd595c730e0be34a8a8abb5d78184c8f431987708b4d2cc61b\n'
  printf 'patcher_sha256=e1c5174ae456ea2ac3aa3b1a6377744c1617b81de4060734adf7dc7d80eee313\n'
  printf 'eval_sha256=7e146f04e9147be2b5403f613ddc553fb3ddda7054256f14e7d95fc9d3556d40\n'
  printf 'gpu=cpu=full_classical_zero rows=%s clean_0_0_0=%s\n' "$EXPECTED_ROWS" "$clean"
  printf 'results_sha256=%s confirmer_preserved=590322 pending=0\n' "$RESULTS_SHA"
} > "$RUN/ZERO-CONFIRM.complete.tmp"
mv "$RUN/ZERO-CONFIRM.complete.tmp" "$RUN/ZERO-CONFIRM.complete"
printf 'ZERO_CONFIRM_COMPLETE rows=%s clean=%s\n' "$EXPECTED_ROWS" "$clean"
