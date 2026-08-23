#!/bin/bash
set -euo pipefail

repo=$(cd "$(dirname "$0")/../.." && pwd)
packet=/Users/olifreuler/ecdsa-ops/q1273-predictor-093d85d
d32=/Users/olifreuler/ecdsa-ops/q1273-wrap-exact-ea6a02f/d32
ops="$packet/ops.bin"
bin=${PP_WRAP_FINAL_BIN:-/private/tmp/ppcpu-q1273-wrap-exact-final}
out=${PP_WRAP_FINAL_OUT:-/Users/olifreuler/ecdsa-ops/q1273-wrap-exact-ea6a02f/final-masks}

die() { printf 'FATAL: %s\n' "$*" >&2; exit 2; }
hash() { sha256sum "$1" | awk '{print $1}'; }

[[ $(hash "$repo/.lane/q1273-predictor/src/pp_host.h") == \
  bc2df2182beb8ebcc103a3fc498a8ca65911bf52439566dbfa1284e88407f98a ]] || \
  die 'host source drift'
[[ $(hash "$repo/.lane/q1273-predictor/src/pp_model.h") == \
  da56cb95e2c423e67e8d400b423117cc54d007505aa7281e7725bcadd2ea19ab ]] || \
  die 'model source drift'
[[ $(hash "$repo/.lane/q1273-predictor/src/ppcpu.cpp") == \
  cc93e3ea51ddcb94857452e5aa3c9cfb39327a89711f703193e494daa2585d97 ]] || \
  die 'CPU source drift'
[[ $(hash "$bin") == \
  7f9a49d25f0c487d7f35ea09beff3749d2a64050b46089fbf078dadaabb4da00 ]] || \
  die 'final CPU binary drift'
[[ $(hash "$ops") == \
  ee6448dbb23aa877123733724b109266e584f1ba14abf5c38b43b9ab6aa26cd1 ]] || \
  die 'ops drift'
[[ $(od -An -tu8 -j8 -N8 "$ops" | tr -d '[:space:]') == 12933805 ]] || \
  die 'ops count drift'
[[ $(hash "$packet/h64/fixtures.tsv") == \
  7918937a30d562a2dd26cf59374cdb702c11ce0f08d42789f9ef42da8264b5f4 ]] || \
  die 'H64 ledger drift'
[[ $(hash "$packet/original-d16/MANIFEST.sha256") == \
  bf8f73cd6570bcf1c6dc2eddcf227ba40f4f0fe5bc3b4877bc119e01a5bf9e41 ]] || \
  die 'D16 manifest drift'
[[ $(hash "$d32/fixtures.tsv") == \
  9cbd9a0e41459f43963bb6bf619b9a3561adfd16f99c9025c6e4769964405cac ]] || \
  die 'D32 fixture ledger drift'
[[ $(hash "$d32/MANIFEST.sha256") == \
  4e094b128e8bf32408d1bc28376ee6e71291130d62eaa72b63bde5d7fc354f01 ]] || \
  die 'D32 manifest drift'
[[ $(hash "$repo/.lane/q1273-wrap-exact/D32.nonces") == \
  62bca2420f684c718e52b516dc850f05d72c33f64798002fe2afd215642a0f90 ]] || \
  die 'D32 nonce drift'

mkdir -p "$out"/inherited "$out"/h64 "$out"/d16 "$out"/d32
summary="$out/summary.tsv.tmp"
printf 'corpus\tnonce\texpected_count\tpredicted_count\tmask_sha256\traw_sha256\trepeat_sha256\tstatus\n' \
  >"$summary"

run_one() {
  local corpus=$1 nonce=$2 expected=$3 dir expected_count predicted_count
  local expected_hash predicted_hash raw_hash repeat_hash
  dir="$out/$corpus/$nonce"
  mkdir -p "$dir"
  PPF_OPS="$ops" "$bin" faultshots "$nonce" >"$dir/predictor.raw" \
    2>"$dir/predictor.stderr"
  PPF_OPS="$ops" "$bin" faultshots "$nonce" >"$dir/predictor.repeat.raw" \
    2>"$dir/predictor.repeat.stderr"
  cmp -s "$dir/predictor.raw" "$dir/predictor.repeat.raw" || \
    die "nondeterministic raw output for $corpus/$nonce"
  awk 'NF != 2 || $1 !~ /^[0-9]+$/ || $2 !~ /^(1|2|4|8|16)$/ {exit 2}
       $1 < 0 || $1 >= 9024 || (NR > 1 && $1 <= prev) {exit 2}
       {print $1; prev=$1}' "$dir/predictor.raw" >"$dir/predictor.shots" || \
    die "malformed output for $corpus/$nonce"
  expected_count=$(wc -l <"$expected" | tr -d '[:space:]')
  predicted_count=$(wc -l <"$dir/predictor.shots" | tr -d '[:space:]')
  expected_hash=$(hash "$expected")
  predicted_hash=$(hash "$dir/predictor.shots")
  raw_hash=$(hash "$dir/predictor.raw")
  repeat_hash=$(hash "$dir/predictor.repeat.raw")
  [[ "$expected_count" == "$predicted_count" && "$expected_hash" == "$predicted_hash" ]] || \
    die "complete-mask mismatch for $corpus/$nonce"
  [[ "$raw_hash" == "$repeat_hash" ]] || die "repeat SHA mismatch for $corpus/$nonce"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\tPASS\n' "$corpus" "$nonce" \
    "$expected_count" "$predicted_count" "$predicted_hash" "$raw_hash" "$repeat_hash" \
    >>"$summary"
}

run_one inherited 100000045835813 "$packet/inherited.evaluator.shots"
for i in $(seq 0 63); do
  nonce=$((444000000000 + i))
  run_one h64 "$nonce" "$packet/h64/$nonce/evaluator.shots"
done
tail -n +2 /private/tmp/q1273-phase/corpus17.nonces | while read -r nonce; do
  run_one d16 "$nonce" "$packet/original-d16/$nonce/evaluator.shots"
done
while read -r nonce; do
  run_one d32 "$nonce" "$d32/$nonce/evaluator.shots"
done <"$repo/.lane/q1273-wrap-exact/D32.nonces"

[[ $(($(wc -l <"$summary") - 1)) == 113 ]] || die 'final fixture count is not 113'
mv "$summary" "$out/summary.tsv"
(
  cd "$out"
  find inherited h64 d16 d32 -type f -print0 | sort -z | xargs -0 sha256sum
  sha256sum summary.tsv
) >"$out/MANIFEST.sha256.tmp"
mv "$out/MANIFEST.sha256.tmp" "$out/MANIFEST.sha256"
sha256sum "$out/summary.tsv" "$out/MANIFEST.sha256"
