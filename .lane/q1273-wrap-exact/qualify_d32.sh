#!/bin/bash
set -euo pipefail

repo=$(cd "$(dirname "$0")/../.." && pwd)
packet=/Users/olifreuler/ecdsa-ops/q1273-predictor-093d85d
nonce_file="$repo/.lane/q1273-wrap-exact/D32.nonces"
builder="$packet/builder-target/release/build_circuit"
evaluator="$packet/evaluator-target/release/eval_circuit"
base_ops="$packet/ops.bin"
bin=${PP_WRAP_BIN:-/private/tmp/ppcpu-q1273-wrap-exact}
out=${PP_WRAP_D32_OUT:-/Users/olifreuler/ecdsa-ops/q1273-wrap-exact-ea6a02f/d32}

die() { printf 'FATAL: %s\n' "$*" >&2; exit 2; }
hash() { sha256sum "$1" | awk '{print $1}'; }
one_field() {
  local pattern=$1 field=$2 file=$3 values count
  values=$(awk -v p="$pattern" -v f="$field" 'index($0,p)==1 {print $f}' "$file")
  count=$(printf '%s\n' "$values" | awk 'NF {n++} END {print n+0}')
  [[ "$count" == 1 ]] || die "expected one '$pattern' field in $file, got $count"
  printf '%s\n' "$values"
}

[[ $(hash "$nonce_file") == \
  62bca2420f684c718e52b516dc850f05d72c33f64798002fe2afd215642a0f90 ]] || \
  die 'D32 nonce ledger drift'
[[ $(wc -l <"$nonce_file" | tr -d '[:space:]') == 32 ]] || die 'D32 count drift'
[[ $(sort -u "$nonce_file" | wc -l | tr -d '[:space:]') == 32 ]] || die 'D32 duplicate'
[[ $(hash "$repo/.lane/q1273-predictor/src/pp_model.h") == \
  da56cb95e2c423e67e8d400b423117cc54d007505aa7281e7725bcadd2ea19ab ]] || \
  die 'predictor source drift'
[[ $(hash "$base_ops") == \
  ee6448dbb23aa877123733724b109266e584f1ba14abf5c38b43b9ab6aa26cd1 ]] || \
  die 'base ops SHA drift'
[[ $(hash "$bin") == \
  79e3a2962d9ff365622fff656d8c985ff29511ae9e4eba5f84ead7407ea0b097 ]] || \
  die 'predictor binary drift'
[[ $(hash "$builder") == \
  67c8720188d26fe464c3552bba02a2ec011fe7f5c40b0517c4b1c71a55977995 ]] || \
  die 'builder binary drift'
[[ $(hash "$evaluator") == \
  37081d949bf34f185023098e74393a9014b96853633646288a90f1538663580e ]] || \
  die 'evaluator binary drift'
[[ $(hash "$packet/evaluator-instrumented/instrumentation.patch") == \
  15943baf5815f36188a8406b7a080c8b446f856a9337d8046eafe363752c6e4f ]] || \
  die 'evaluator instrumentation drift'

mkdir -p "$out"

run_one() {
  local nonce=$1 dir count ops_sha eval_rc loaded qubits shots cls phase anc
  local eval_mask_sha pred_mask_sha pred_repeat_sha
  dir="$out/$nonce"
  [[ $(grep -Fxc "$nonce" "$nonce_file") == 1 ]] || die "nonce $nonce is not uniquely frozen"
  mkdir -p "$dir"
  [[ ! -e "$dir/receipt.tsv" ]] || return 0
  (
    cd "$dir"
    SUB4_PINGPONG_TAIL_NONCE="$nonce" "$builder" >build.log 2>&1
  )
  [[ -s "$dir/ops.bin" ]] || die "missing ops for $nonce"
  count=$(od -An -tu8 -j8 -N8 "$dir/ops.bin" | tr -d '[:space:]')
  [[ "$count" == 12933805 ]] || die "op count $count for $nonce"
  ops_sha=$(hash "$dir/ops.bin")

  set +e
  (
    cd "$dir"
    EVAL_CLASSICAL_SHOTS=1 EVAL_NO_WRITE=1 "$evaluator" --note "q1273-wrap-d32-$nonce" \
      >eval.log 2>&1
  )
  eval_rc=$?
  set -e
  [[ "$eval_rc" == 0 || "$eval_rc" == 1 ]] || die "evaluator rc $eval_rc for $nonce"
  loaded=$(one_field '  loaded ops  : ' 4 "$dir/eval.log")
  qubits=$(one_field '  qubits      : ' 3 "$dir/eval.log")
  shots=$(one_field '  tested shots            : ' 4 "$dir/eval.log")
  cls=$(one_field '  classical mismatches    : ' 4 "$dir/eval.log")
  phase=$(one_field '  phase-garbage batches   : ' 4 "$dir/eval.log")
  anc=$(one_field '  ancilla-garbage batches : ' 4 "$dir/eval.log")
  [[ "$loaded" == 12933805 && "$qubits" == 1273 && "$shots" == 9024 && "$anc" == 0 ]] || \
    die "evaluator identity failure for $nonce"
  if [[ "$cls" == 0 ]]; then
    [[ "$eval_rc" == 0 || "$phase" != 0 ]] || die "clean-classical rc mismatch for $nonce"
  else
    [[ "$eval_rc" == 1 ]] || die "dirty-classical rc mismatch for $nonce"
  fi
  awk '$1 == "CLASSICAL_SHOT" && $2 ~ /^[0-9]+$/ && NF == 2 {print $2}' \
    "$dir/eval.log" >"$dir/evaluator.shots"
  [[ $(wc -l <"$dir/evaluator.shots" | tr -d '[:space:]') == "$cls" ]] || \
    die "evaluator complete-mask length mismatch for $nonce"

  PPF_OPS="$base_ops" "$bin" faultshots "$nonce" \
    >"$dir/predictor.raw" 2>"$dir/predictor.stderr"
  awk 'NF != 2 || $1 !~ /^[0-9]+$/ || $2 !~ /^(1|2|4|8|16)$/ {exit 2}
       $1 < 0 || $1 >= 9024 || (NR > 1 && $1 <= prev) {exit 2}
       {print $1; prev=$1}' "$dir/predictor.raw" >"$dir/predictor.shots" || \
    die "malformed predictor mask for $nonce"
  cmp -s "$dir/evaluator.shots" "$dir/predictor.shots" || \
    die "complete-mask mismatch for $nonce"

  PPF_OPS="$base_ops" "$bin" faultshots "$nonce" \
    >"$dir/predictor.repeat.raw" 2>"$dir/predictor.repeat.stderr"
  cmp -s "$dir/predictor.raw" "$dir/predictor.repeat.raw" || \
    die "nondeterministic predictor output for $nonce"
  eval_mask_sha=$(hash "$dir/evaluator.shots")
  pred_mask_sha=$(hash "$dir/predictor.shots")
  pred_repeat_sha=$(hash "$dir/predictor.repeat.raw")
  [[ "$eval_mask_sha" == "$pred_mask_sha" ]] || die "mask SHA mismatch for $nonce"

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$nonce" "$ops_sha" "$loaded" "$qubits" "$shots" "$cls" "$phase" "$anc" \
    "$eval_rc" "$eval_mask_sha" "$(hash "$dir/predictor.raw")" "$pred_repeat_sha" \
    >"$dir/receipt.tsv.tmp"
  mv "$dir/receipt.tsv.tmp" "$dir/receipt.tsv"
  rm -f "$dir/ops.bin"
}

while read -r nonce; do run_one "$nonce"; done <"$nonce_file"

ledger="$out/fixtures.tsv.tmp"
printf 'nonce\tops_sha256\tops\tqubits\tshots\tclassical\tphase\tancilla\teval_rc\tmask_sha256\tpredictor_raw_sha256\trepeat_raw_sha256\n' >"$ledger"
while read -r nonce; do
  [[ -f "$out/$nonce/receipt.tsv" ]] || die "missing receipt for $nonce"
  cat "$out/$nonce/receipt.tsv" >>"$ledger"
done <"$nonce_file"
[[ $(($(wc -l <"$ledger") - 1)) == 32 ]] || die 'D32 receipt count failure'
mv "$ledger" "$out/fixtures.tsv"
(
  cd "$out"
  find . -mindepth 2 -type f -print0 | sort -z | xargs -0 sha256sum
  sha256sum fixtures.tsv
) >"$out/MANIFEST.sha256.tmp"
mv "$out/MANIFEST.sha256.tmp" "$out/MANIFEST.sha256"
sha256sum "$out/fixtures.tsv" "$out/MANIFEST.sha256"
