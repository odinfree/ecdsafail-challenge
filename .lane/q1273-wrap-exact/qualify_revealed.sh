#!/bin/bash
set -euo pipefail

repo=$(cd "$(dirname "$0")/../../.." && pwd)
packet=/Users/olifreuler/ecdsa-ops/q1273-predictor-093d85d
ops="$packet/ops.bin"
bin=${PP_WRAP_BIN:-/private/tmp/ppcpu-q1273-wrap-exact}
out=${PP_WRAP_OUT:-/Users/olifreuler/ecdsa-ops/q1273-wrap-exact-ea6a02f/revealed}

die() { printf 'FATAL: %s\n' "$*" >&2; exit 2; }
hash() { sha256sum "$1" | awk '{print $1}'; }

[[ $(hash "$repo/.lane/q1273-predictor/src/pp_model.h") == \
  da56cb95e2c423e67e8d400b423117cc54d007505aa7281e7725bcadd2ea19ab ]] || \
  die 'predictor source drift'
[[ $(hash "$ops") == \
  ee6448dbb23aa877123733724b109266e584f1ba14abf5c38b43b9ab6aa26cd1 ]] || \
  die 'ops SHA drift'
[[ $(od -An -tu8 -j8 -N8 "$ops" | tr -d '[:space:]') == 12933805 ]] || \
  die 'ops count drift'
[[ $(hash "$bin") == \
  79e3a2962d9ff365622fff656d8c985ff29511ae9e4eba5f84ead7407ea0b097 ]] || \
  die 'predictor binary drift'
[[ $(hash "$packet/h64/fixtures.tsv") == \
  7918937a30d562a2dd26cf59374cdb702c11ce0f08d42789f9ef42da8264b5f4 ]] || \
  die 'H64 evaluator ledger drift'
[[ $(hash "$packet/h64/evaluator-index-mask.tsv") == \
  9c1c9cfb0dc7057e8ea1aafbd55c42382e9c4eeabab0d13fe80d18d98c899f46 ]] || \
  die 'H64 evaluator mask drift'
[[ $(hash "$packet/original-d16/MANIFEST.sha256") == \
  bf8f73cd6570bcf1c6dc2eddcf227ba40f4f0fe5bc3b4877bc119e01a5bf9e41 ]] || \
  die 'D16 evaluator manifest drift'
[[ $(hash /private/tmp/q1273-phase/corpus17.nonces) == \
  e72d277e87af6c2d01687df89c4254405e98313742e0af51e2004de953db55d2 ]] || \
  die 'D16 nonce ledger drift'

mkdir -p "$out"/inherited "$out"/h64 "$out"/d16
summary="$out/summary.tsv.tmp"
printf 'corpus\tnonce\texpected_count\tpredicted_count\tmask_sha256\tstatus\n' >"$summary"

run_one() {
  local corpus=$1 nonce=$2 expected=$3 dir="$out/$corpus/$nonce"
  local expected_count predicted_count expected_hash predicted_hash
  mkdir -p "$dir"
  PPF_OPS="$ops" "$bin" faultshots "$nonce" >"$dir/predictor.raw" 2>"$dir/predictor.stderr"
  awk 'NF != 2 || $1 !~ /^[0-9]+$/ || $2 !~ /^(1|2|4|8|16)$/ {exit 2}
       $1 < 0 || $1 >= 9024 || (NR > 1 && $1 <= prev) {exit 2}
       {print $1; prev=$1}' "$dir/predictor.raw" >"$dir/predictor.shots" || \
    die "malformed predictor mask for $corpus/$nonce"
  expected_count=$(wc -l <"$expected" | tr -d '[:space:]')
  predicted_count=$(wc -l <"$dir/predictor.shots" | tr -d '[:space:]')
  expected_hash=$(hash "$expected")
  predicted_hash=$(hash "$dir/predictor.shots")
  [[ "$predicted_count" == "$expected_count" ]] || \
    die "count mismatch for $corpus/$nonce: $predicted_count != $expected_count"
  [[ "$predicted_hash" == "$expected_hash" ]] || \
    die "complete-mask mismatch for $corpus/$nonce"
  printf '%s\t%s\t%s\t%s\t%s\tPASS\n' "$corpus" "$nonce" "$expected_count" \
    "$predicted_count" "$predicted_hash" >>"$summary"
}

run_one inherited 100000045835813 "$packet/inherited.evaluator.shots"
for i in $(seq 0 63); do
  nonce=$((444000000000 + i))
  run_one h64 "$nonce" "$packet/h64/$nonce/evaluator.shots"
done
tail -n +2 /private/tmp/q1273-phase/corpus17.nonces | while read -r nonce; do
  run_one d16 "$nonce" "$packet/original-d16/$nonce/evaluator.shots"
done

[[ $(($(wc -l <"$summary") - 1)) == 81 ]] || die 'revealed fixture count is not 81'
mv "$summary" "$out/summary.tsv"
(
  cd "$out"
  find inherited h64 d16 -type f -print0 | sort -z | xargs -0 sha256sum
  sha256sum summary.tsv
) >"$out/MANIFEST.sha256.tmp"
mv "$out/MANIFEST.sha256.tmp" "$out/MANIFEST.sha256"
sha256sum "$out/summary.tsv" "$out/MANIFEST.sha256"
