#!/bin/bash
set -euo pipefail

repo=$(cd "$(dirname "$0")/../.." && pwd)
corpus="$repo/.lane/q1272-promoted-predictor/H64.nonces"
predictor="$repo/target/release/pingpong_filter"
builder="$repo/target/release/build_circuit"
evaluator=/Users/olifreuler/ecdsa-ops/q1273-predictor-093d85d/evaluator-instrumented/target/release/eval_circuit

die() { printf 'FATAL: %s\n' "$*" >&2; exit 2; }
hash() { sha256sum "$1" | awk '{print $1}'; }
assert_hash() { [[ -f $1 && $(hash "$1") == "$2" ]] || die "hash drift: $1"; }

check_identity() {
  git -C "$repo" merge-base --is-ancestor \
    01e06d605c1de3cea4571b033e1d16dc820bfbdf HEAD || \
    die 'inherited classical checkpoint is not an ancestor of HEAD'
  assert_hash "$corpus" \
    17443162349d50e521b0c9a20904de5a0212a668e6f3ae7ea0e2702b2f79c4b9
  assert_hash "$repo/src/bin/pingpong_filter.rs" \
    2d016070a93a5966c5a163a6242b27ef8264176c76c72448ba50027b70465890
  assert_hash "$repo/src/bin/eval_circuit.rs" \
    b35314bc47a5f8eecbf60459e6c76c9b43aa034eeb9b7ec3421655d74f9e890b
  assert_hash "$repo/src/point_add/pingpong_div.rs" \
    6e7cce578663d8419c032190a9caa405ca0d84e0512104b766b9c68540f01994
  assert_hash "$repo/src/point_add/mod.rs" \
    0c9e9a920d9078f2390028009895f03d495096fdac9d2b596c7913c064e03e63
  assert_hash "$repo/src/point_add/trailmix_ludicrous/square/product_register.rs" \
    864d31454c5279632652cf48aeda038d481a504b09e4f7a8c0f266e10a24b81c
  assert_hash "$predictor" \
    1ce7b22c1ed1a4d55620ccf5daeed110cdb7b0f6de3ce85b5de93fcc86cb7ba8
  assert_hash "$builder" \
    02c94aed131c5558aa40f91cc9bdccda8248c8dccbe4390138afd4a3901311a5
  assert_hash "$evaluator" \
    37081d949bf34f185023098e74393a9014b96853633646288a90f1538663580e
  [[ $(wc -l <"$corpus" | tr -d '[:space:]') == 64 ]] || die 'H64 row count drift'
  awk 'NF != 1 || $1 !~ /^[0-9]+$/ || (NR > 1 && $1 <= prev) {exit 2} {prev=$1}' \
    "$corpus" || die 'H64 nonce framing drift'
}

predict() {
  local out=$1 tmp rows
  check_identity
  [[ ! -e $out/evaluator ]] || die 'evaluator output exists before prediction seal'
  mkdir -p "$out"
  tmp=$(mktemp "$out/prediction.raw.tmp.XXXXXX")
  env -i PATH="$PATH" LC_ALL=C \
    SUB4_PP_FOLD_SELECTOR_EVICT=1 SUB4_PP_PEAK=1272 SUB4_SQUARE_LADDER=242 \
    "$predictor" --nonces "$corpus" --jobs 4 --faultshots >"$tmp"
  rows=$(wc -l <"$tmp" | tr -d '[:space:]')
  [[ $rows == 64 ]] || die "prediction rows $rows != 64"
  awk 'NF != 3 || $1 !~ /^[0-9]+$/ || $2 !~ /^[0-9]+$/ ||
       length($3) != 2256 || $3 !~ /^[0-9a-f]+$/ ||
       (NR > 1 && $1 <= prev) {exit 2} {prev=$1}' "$tmp" || \
    die 'prediction framing drift'
  mv "$tmp" "$out/prediction.tsv"
  {
    printf 'status=PREDICTION_SEALED_EVALUATOR_UNOPENED\n'
    printf 'source_commit=01e06d605c1de3cea4571b033e1d16dc820bfbdf\n'
    printf 'source_sha256=2d016070a93a5966c5a163a6242b27ef8264176c76c72448ba50027b70465890\n'
    printf 'corpus_sha256=%s\n' "$(hash "$corpus")"
    printf 'prediction_sha256=%s\n' "$(hash "$out/prediction.tsv")"
    printf 'rows=64\n'
  } >"$out/PREDICTION.seal.tmp"
  mv "$out/PREDICTION.seal.tmp" "$out/PREDICTION.seal"
  sha256sum "$out/prediction.tsv" "$out/PREDICTION.seal"
}

decode_mask() {
  local encoded=$1 output=$2
  python3 -c 'import sys
h=sys.argv[1]
assert len(h)==141*16 and all(c in "0123456789abcdef" for c in h)
for wi in range(141):
    word=int(h[wi*16:(wi+1)*16],16)
    for bit in range(64):
        shot=wi*64+bit
        if shot < 9024 and ((word >> bit) & 1): print(shot)' "$encoded" >"$output"
}

worker() {
  local out=$1 nonce=$2 final stage pred_row expected_count encoded eval_rc
  local q shots classical phase ancilla first ops_sha mask_sha
  check_identity
  final="$out/evaluator/$nonce"
  [[ ! -e $final ]] || die "worker output already exists: $final"
  mkdir -p "$out/evaluator" "$out/staging"
  stage=$(mktemp -d "$out/staging/$nonce.XXXXXX")

  pred_row=$(awk -v n="$nonce" '$1 == n {print; found++} END {if (found != 1) exit 2}' \
    "$out/prediction.tsv") || die "missing prediction row $nonce"
  expected_count=$(printf '%s\n' "$pred_row" | awk '{print $2}')
  encoded=$(printf '%s\n' "$pred_row" | awk '{print $3}')
  decode_mask "$encoded" "$stage/predictor.shots"
  [[ $(wc -l <"$stage/predictor.shots" | tr -d '[:space:]') == "$expected_count" ]] || \
    die "prediction count/mask disagreement $nonce"

  (
    cd "$stage"
    env -i PATH="$PATH" LC_ALL=C \
      SUB4_PP_FOLD_SELECTOR_EVICT=1 SUB4_PP_PEAK=1272 SUB4_SQUARE_LADDER=242 \
      SUB4_PINGPONG_TAIL_NONCE="$nonce" \
      "$builder" >build.stdout 2>build.stderr
  )
  [[ -f $stage/ops.bin ]] || die "builder did not emit ops.bin for $nonce"
  [[ $(od -An -tu8 -j8 -N8 "$stage/ops.bin" | tr -d '[:space:]') == 12904643 ]] || \
    die "operation count drift $nonce"
  ops_sha=$(hash "$stage/ops.bin")

  set +e
  (
    cd "$stage"
    env -i PATH="$PATH" LC_ALL=C EVAL_CLASSICAL_SHOTS=1 EVAL_NO_WRITE=1 \
      "$evaluator" --note q1272-promoted-h64 \
      >eval.stdout 2>eval.stderr
  )
  eval_rc=$?
  set -e
  [[ $eval_rc == 0 || $eval_rc == 1 ]] || die "evaluator rc $eval_rc for $nonce"

  q=$(awk -F: '/^[[:space:]]*qubits[[:space:]]*:/{gsub(/[[:space:]]/,"",$2); print $2}' \
    "$stage/eval.stdout")
  shots=$(awk -F: '/^[[:space:]]*tested shots[[:space:]]*:/{gsub(/[[:space:]]/,"",$2); print $2}' \
    "$stage/eval.stdout")
  classical=$(awk -F: '/^[[:space:]]*classical mismatches[[:space:]]*:/{gsub(/[[:space:]]/,"",$2); print $2}' \
    "$stage/eval.stdout")
  phase=$(awk -F: '/^[[:space:]]*phase-garbage batches[[:space:]]*:/{gsub(/[[:space:]]/,"",$2); print $2}' \
    "$stage/eval.stdout")
  ancilla=$(awk -F: '/^[[:space:]]*ancilla-garbage batches[[:space:]]*:/{gsub(/[[:space:]]/,"",$2); print $2}' \
    "$stage/eval.stdout")
  [[ $q == 1272 && $shots == 9024 && $classical == "$expected_count" && $ancilla == 0 ]] || \
    die "trusted summary mismatch $nonce q=$q shots=$shots cl=$classical/$expected_count anc=$ancilla"
  awk '/^CLASSICAL_SHOT / {print $2}' "$stage/eval.stdout" >"$stage/evaluator.shots"
  cmp -s "$stage/predictor.shots" "$stage/evaluator.shots" || \
    die "complete classical mask mismatch $nonce"
  first=$(head -1 "$stage/evaluator.shots" 2>/dev/null || true)
  [[ -n $first ]] || first=none
  mask_sha=$(hash "$stage/evaluator.shots")
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\tPASS\n' \
    "$nonce" "$ops_sha" "$q" "$shots" "$classical" "$phase" "$ancilla" \
    "$first" "$mask_sha" >"$stage/row.tsv"
  {
    printf 'status=PASS\nnonce=%s\nops_sha256=%s\n' "$nonce" "$ops_sha"
    printf 'row_sha256=%s\nmask_sha256=%s\n' "$(hash "$stage/row.tsv")" "$mask_sha"
  } >"$stage/WORKER.complete"
  mv "$stage" "$final"
}

evaluate() {
  local out=$1 jobs=${2:-4} sealed actual nonce tmp rows faults
  check_identity
  [[ -f $out/PREDICTION.seal && -f $out/prediction.tsv ]] || die 'prediction is not sealed'
  sealed=$(awk -F= '$1 == "prediction_sha256" {print $2}' "$out/PREDICTION.seal")
  actual=$(hash "$out/prediction.tsv")
  [[ -n $sealed && $sealed == "$actual" ]] || die 'prediction seal drift'
  [[ $jobs =~ ^[1-9][0-9]*$ && $jobs -le 6 ]] || die 'jobs must be 1..6'
  while read -r nonce; do
    printf '%s\n' "$nonce"
  done <"$corpus" | xargs -P "$jobs" -n 1 bash "$0" worker "$out"

  tmp=$(mktemp "$out/summary.tsv.tmp.XXXXXX")
  printf 'nonce\tops_sha256\tqubits\tshots\tclassical\tphase_batches\tancilla_batches\tfirst\tmask_sha256\tstatus\n' \
    >"$tmp"
  while read -r nonce; do
    [[ -f $out/evaluator/$nonce/WORKER.complete ]] || die "missing worker $nonce"
    cat "$out/evaluator/$nonce/row.tsv" >>"$tmp"
  done <"$corpus"
  rows=$(($(wc -l <"$tmp") - 1))
  faults=$(awk 'NR > 1 {n += $5} END {print n+0}' "$tmp")
  [[ $rows == 64 ]] || die "summary rows $rows != 64"
  mv "$tmp" "$out/summary.tsv"
  (
    cd "$out"
    find evaluator -type f ! -name ops.bin -print0 | sort -z | xargs -0 sha256sum
    sha256sum prediction.tsv PREDICTION.seal summary.tsv
  ) >"$out/MANIFEST.sha256.tmp"
  mv "$out/MANIFEST.sha256.tmp" "$out/MANIFEST.sha256"
  {
    printf 'status=H64_CLASSICAL_PASS\nrows=64\nclassical_faults=%s\n' "$faults"
    printf 'prediction_sha256=%s\nsummary_sha256=%s\nmanifest_sha256=%s\n' \
      "$sealed" "$(hash "$out/summary.tsv")" "$(hash "$out/MANIFEST.sha256")"
  } >"$out/H64.complete.tmp"
  mv "$out/H64.complete.tmp" "$out/H64.complete"
  sha256sum "$out/summary.tsv" "$out/MANIFEST.sha256" "$out/H64.complete"
}

mode=${1:-}
case "$mode" in
  predict)
    [[ $# == 2 ]] || die 'usage: qualify_h64_local.sh predict OUT'
    predict "$2"
    ;;
  evaluate)
    [[ $# == 2 || $# == 3 ]] || die 'usage: qualify_h64_local.sh evaluate OUT [JOBS]'
    evaluate "$2" "${3:-4}"
    ;;
  worker)
    [[ $# == 3 ]] || die 'internal worker usage'
    worker "$2" "$3"
    ;;
  *)
    die 'usage: qualify_h64_local.sh predict OUT | evaluate OUT [JOBS]'
    ;;
esac
