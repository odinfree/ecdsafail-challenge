#!/bin/bash
set -euo pipefail

repo=$(cd "$(dirname "$0")/../.." && pwd)
packet=/Users/olifreuler/ecdsa-ops/q1273-predictor-093d85d
d32=/Users/olifreuler/ecdsa-ops/q1273-wrap-exact-ea6a02f/d32
ops="$packet/ops.bin"
bin=${PP_COMBINED_BIN:-/private/tmp/ppcpu-q1273-combined-final}
out=${PP_COMBINED_OUT:-/Users/olifreuler/ecdsa-ops/q1273-wrap-exact-ea6a02f/combined-cpu}
phase_fixture="$repo/.lane/q1273-phase/Q1273_PHASE_FIXTURES.tsv"

die() { printf 'FATAL: %s\n' "$*" >&2; exit 2; }
hash() { sha256sum "$1" | awk '{print $1}'; }
assert_hash() { [[ $(hash "$1") == "$2" ]] || die "hash drift: $1"; }

assert_hash "$repo/.lane/q1273-predictor/src/pp_model.h" \
  14fc9230b55d2b2a84721e50d860933764a18d1357ad30331e5999280f764261
assert_hash "$repo/.lane/q1273-predictor/src/pp_host.h" \
  bc2df2182beb8ebcc103a3fc498a8ca65911bf52439566dbfa1284e88407f98a
assert_hash "$repo/.lane/q1273-predictor/src/ppcpu.cpp" \
  1d93d46803670324401443ed9f625ee641c6fa8ef77ba4a920baebff83ea24ce
assert_hash "$repo/.lane/q1273-phase/src/pp_phase_schedule.h" \
  4249864aca9e2928a33865ea086b99ef8ecccc9eb596ba4c3e57468ba88d25e5
assert_hash "$repo/.lane/q1273-phase/Q1273_PHASE_SCHEDULE.tsv" \
  a4043530337b91e97d7a42dde2aff7e5a967a0b820ad1a9a120b3c366d7a5294
assert_hash "$phase_fixture" \
  e148f24d99ae45b3c6930a33d49173fd31b2c236593d98375956077b3feb4d1b
assert_hash "$repo/.lane/q1273-phase/tools/generate_phase_schedule.py" \
  83bfa142f2cf546ea5673de424597bf26ed3a57db0173d2b177a009ad9f8e966
assert_hash "$ops" \
  ee6448dbb23aa877123733724b109266e584f1ba14abf5c38b43b9ab6aa26cd1
[[ $(od -An -tu8 -j8 -N8 "$ops" | tr -d '[:space:]') == 12933805 ]] || \
  die 'ops count drift'
assert_hash "$packet/h64/fixtures.tsv" \
  7918937a30d562a2dd26cf59374cdb702c11ce0f08d42789f9ef42da8264b5f4
assert_hash "$packet/original-d16/MANIFEST.sha256" \
  bf8f73cd6570bcf1c6dc2eddcf227ba40f4f0fe5bc3b4877bc119e01a5bf9e41
assert_hash "$d32/fixtures.tsv" \
  9cbd9a0e41459f43963bb6bf619b9a3561adfd16f99c9025c6e4769964405cac
assert_hash "$d32/MANIFEST.sha256" \
  4e094b128e8bf32408d1bc28376ee6e71291130d62eaa72b63bde5d7fc354f01
assert_hash "$repo/.lane/q1273-wrap-exact/D32.nonces" \
  62bca2420f684c718e52b516dc850f05d72c33f64798002fe2afd215642a0f90

g++ -O3 -std=c++17 -pthread -Wall -Wextra -Werror -Wno-unused-parameter \
  -o "$bin" "$repo/.lane/q1273-predictor/src/ppcpu.cpp"
assert_hash "$bin" \
  2234a6cfc61dfb996fdfe757b506dcc5a4917662477cbcdc7894659ce6c098c7

tmp=$(mktemp -d /private/tmp/q1273-combined-qualify.XXXXXX)
trap 'rm -rf "$tmp"' EXIT
python3 "$repo/.lane/q1273-phase/tools/generate_phase_schedule.py" \
  "$repo/.lane/q1273-phase/Q1273_PHASE_SCHEDULE.tsv" \
  "$tmp/pp_phase_schedule.h" "$tmp/Q1273_PHASE_SCHEDULE.tsv" \
  >"$tmp/generator.stdout"
cmp -s "$repo/.lane/q1273-phase/src/pp_phase_schedule.h" \
  "$tmp/pp_phase_schedule.h" || die 'phase header regeneration drift'
cmp -s "$repo/.lane/q1273-phase/Q1273_PHASE_SCHEDULE.tsv" \
  "$tmp/Q1273_PHASE_SCHEDULE.tsv" || die 'phase schedule regeneration drift'

mkdir -p "$out"/{classical,phase,negatives}
classical_summary="$out/classical.tsv.tmp"
phase_summary="$out/phase.tsv.tmp"
printf 'corpus\tnonce\texpected\tpredicted\tshot_sha256\traw_sha256\tstatus\n' \
  >"$classical_summary"
printf 'nonce\texpected\tpredicted\tshot_sha256\tstatus\n' >"$phase_summary"

run_classical() {
  local corpus=$1 nonce=$2 expected=$3 dir expected_count predicted_count
  local expected_hash predicted_hash
  dir="$out/classical/$corpus-$nonce"
  mkdir -p "$dir"
  PPF_OPS="$ops" "$bin" faultshots "$nonce" >"$dir/raw" 2>"$dir/stderr"
  awk 'NF != 2 || $1 !~ /^[0-9]+$/ || $2 !~ /^(1|2|4|8|16)$/ {exit 2}
       $1 < 0 || $1 >= 9024 || (NR > 1 && $1 <= prev) {exit 2}
       {print $1; prev=$1}' "$dir/raw" >"$dir/shots" || \
    die "malformed classical output: $corpus/$nonce"
  expected_count=$(wc -l <"$expected" | tr -d '[:space:]')
  predicted_count=$(wc -l <"$dir/shots" | tr -d '[:space:]')
  expected_hash=$(hash "$expected")
  predicted_hash=$(hash "$dir/shots")
  [[ "$expected_count" == "$predicted_count" && "$expected_hash" == "$predicted_hash" ]] || \
    die "classical complete-set mismatch: $corpus/$nonce"
  printf '%s\t%s\t%s\t%s\t%s\t%s\tPASS\n' "$corpus" "$nonce" \
    "$expected_count" "$predicted_count" "$predicted_hash" "$(hash "$dir/raw")" \
    >>"$classical_summary"
}

set_to_lines() {
  local encoded=$1 output=$2 body
  : >"$output"
  [[ $encoded == '{}' ]] && return 0
  [[ $encoded == \{*\} ]] || die "malformed fixture set: $encoded"
  body=${encoded#\{}
  body=${body%\}}
  [[ -n $body ]] || die 'non-canonical empty fixture set'
  tr ',' '\n' <<<"$body" >"$output"
}

run_phase() {
  local nonce=$1 encoded=$2 expected_count=$3 dir predicted_count
  dir="$out/phase/$nonce"
  mkdir -p "$dir"
  set_to_lines "$encoded" "$dir/expected"
  PPF_OPS="$ops" "$bin" phasefaultshots "$nonce" >"$dir/actual" 2>"$dir/stderr"
  awk 'NF != 1 || $1 !~ /^[0-9]+$/ || $1 < 0 || $1 >= 9024 ||
       (NR > 1 && $1 <= prev) {exit 2} {prev=$1}' "$dir/actual" || \
    die "malformed phase output: $nonce"
  cmp -s "$dir/expected" "$dir/actual" || die "phase complete-set mismatch: $nonce"
  predicted_count=$(wc -l <"$dir/actual" | tr -d '[:space:]')
  [[ "$expected_count" == "$predicted_count" ]] || die "phase count mismatch: $nonce"
  printf '%s\t%s\t%s\t%s\tPASS\n' "$nonce" "$expected_count" \
    "$predicted_count" "$(hash "$dir/actual")" >>"$phase_summary"
}

run_classical inherited 100000045835813 "$packet/inherited.evaluator.shots"
for i in $(seq 0 63); do
  nonce=$((444000000000 + i))
  run_classical h64 "$nonce" "$packet/h64/$nonce/evaluator.shots"
done
while IFS=$'\t' read -r nonce _ _ _ _ _ _ _; do
  [[ $nonce == \#* || $nonce == 100000045835813 ]] && continue
  run_classical d16 "$nonce" "$packet/original-d16/$nonce/evaluator.shots"
done <"$phase_fixture"
while read -r nonce; do
  run_classical d32 "$nonce" "$d32/$nonce/evaluator.shots"
done <"$repo/.lane/q1273-wrap-exact/D32.nonces"

while IFS=$'\t' read -r nonce _ _ phase_count _ phase_sha _ phase_set; do
  [[ $nonce == \#* ]] && continue
  run_phase "$nonce" "$phase_set" "$phase_count"
  [[ $(tail -1 "$phase_summary" | cut -f4) == "$phase_sha" ]] || \
    die "phase fixture SHA mismatch: $nonce"
done <"$phase_fixture"

[[ $(($(wc -l <"$classical_summary") - 1)) == 113 ]] || die 'classical rows != 113'
[[ $(($(wc -l <"$phase_summary") - 1)) == 17 ]] || die 'phase rows != 17'

# Both sealed overflow witnesses must retain their repaired classifications.
PPF_OPS="$ops" "$bin" shot 730140001442 6329 >"$tmp/witness-clean" 2>"$tmp/witness-clean.stderr"
PPF_OPS="$ops" "$bin" shot 730070000721 2493 >"$tmp/witness-fault" 2>"$tmp/witness-fault.stderr"
[[ $(head -1 "$tmp/witness-clean") == 'shot 6329 mask=0' ]] || die 'clean witness drift'
[[ $(head -1 "$tmp/witness-fault") == 'shot 2493 mask=4' ]] || die 'fault witness drift'

# Deterministic combined outputs on the inherited stream.
PPF_OPS="$ops" "$bin" faultshots 100000045835813 >"$tmp/classical-repeat" \
  2>"$tmp/classical-repeat.stderr"
cmp -s "$out/classical/inherited-100000045835813/raw" "$tmp/classical-repeat" || \
  die 'classical repeat drift'
PPF_OPS="$ops" "$bin" phasefaultshots 100000045835813 >"$tmp/phase-repeat" \
  2>"$tmp/phase-repeat.stderr"
cmp -s "$out/phase/100000045835813/actual" "$tmp/phase-repeat" || \
  die 'phase repeat drift'

expected_identity='source_commit=093d85d64de87aa5006a94868172f642daacf136 ops_count=12933805 ops_sha256=ee6448dbb23aa877123733724b109266e584f1ba14abf5c38b43b9ab6aa26cd1 predictor_digest=2148e09f4c4293b2 classical_model_sha256=14fc9230b55d2b2a84721e50d860933764a18d1357ad30331e5999280f764261 phase_meta_sha256=a4043530337b91e97d7a42dde2aff7e5a967a0b820ad1a9a120b3c366d7a5294 phase_sites=3983 phase_rhmr=1942962 shots=9024 contract=phase&~classical final=classical_mask==0&&clean_phase_mask==0 raw_phase=not-claimed cuda_phase=not-claimed'
PPF_OPS="$ops" "$bin" identity >"$tmp/identity" 2>"$tmp/identity.stderr"
[[ $(cat "$tmp/identity") == "$expected_identity" ]] || die 'identity drift'
PPF_OPS="$ops" "$bin" shaketest >"$tmp/shake.stdout" 2>"$tmp/shake.stderr"
[[ ! -s "$tmp/shake.stdout" ]] || die 'SHAKE emitted stdout'
rg -q '^empty: 46b9dd2b0ba88d13233b3feb743eeb243fcd52ea62b81b82b50c27646ed5762f$' \
  "$tmp/shake.stderr" || die 'SHAKE empty KAT mismatch'
rg -q '^abc  : 483366601360a8771c6863080cc4114d8db44530f8f1e1ee4f94ea37e78b5739$' \
  "$tmp/shake.stderr" || die 'SHAKE abc KAT mismatch'

expect_reject() {
  local label=$1 stream=$2; shift 2
  set +e
  PPF_OPS="$stream" "$@" >"$out/negatives/$label.stdout" \
    2>"$out/negatives/$label.stderr"
  local rc=$?
  set -e
  [[ $rc -ne 0 ]] || die "negative accepted: $label"
  [[ ! -s "$out/negatives/$label.stdout" ]] || die "negative emitted stdout: $label"
  printf '%s\t%s\tPASS\n' "$label" "$rc" >>"$out/negatives.tsv.tmp"
}

: >"$out/negatives.tsv.tmp"
python3 - "$ops" "$tmp" <<'PY'
import pathlib, struct, sys
raw = pathlib.Path(sys.argv[1]).read_bytes()
out = pathlib.Path(sys.argv[2])
for name, offset, value in (("bad-magic.bin", 0, None),
                            ("bad-count.bin", 8, 12_933_806),
                            ("bad-sha.bin", 16, None)):
    data = bytearray(raw)
    if value is None:
        data[offset] ^= 1
    else:
        struct.pack_into("<Q", data, offset, value)
    (out / name).write_bytes(data)
PY
g++ -O3 -std=c++17 -pthread -Wall -Wextra -Werror -Wno-unused-parameter \
  -DPP_EXPECTED_STATE_DIGEST_VALUE=0x2148e09f4c4293b3ULL \
  -o "$tmp/bad-state" "$repo/.lane/q1273-predictor/src/ppcpu.cpp"
g++ -O3 -std=c++17 -pthread -Wall -Wextra -Werror -Wno-unused-parameter \
  -DPP_PHASE_FORCE_BAD_SCHEDULE \
  -o "$tmp/bad-schedule" "$repo/.lane/q1273-predictor/src/ppcpu.cpp"
expect_reject bad-magic "$tmp/bad-magic.bin" "$bin" identity
expect_reject bad-count "$tmp/bad-count.bin" "$bin" identity
expect_reject bad-sha "$tmp/bad-sha.bin" "$bin" identity
expect_reject bad-state "$ops" "$tmp/bad-state" identity
expect_reject bad-schedule "$ops" "$tmp/bad-schedule" phasefaultshots 100000045835813
expect_reject missing-ops "$tmp/missing.bin" "$bin" identity
expect_reject scan-disabled "$ops" "$bin" scan
expect_reject unknown-selector "$ops" "$bin" census
for bad_nonce in '' 00 +1 -1 281474976710656 18446744073709551616 abc; do
  label=$(printf '%s' "$bad_nonce" | sha256sum | cut -c1-12)
  expect_reject "nonce-$label" "$ops" "$bin" phasefaultshots "$bad_nonce"
done
expect_reject bad-index "$ops" "$bin" shot 1 9024
expect_reject noncanonical-index "$ops" "$bin" shot 1 00

mv "$classical_summary" "$out/classical.tsv"
mv "$phase_summary" "$out/phase.tsv"
mv "$out/negatives.tsv.tmp" "$out/negatives.tsv"
(
  cd "$out"
  find classical phase negatives -type f -print0 | sort -z | xargs -0 sha256sum
  sha256sum classical.tsv phase.tsv negatives.tsv
) >"$out/MANIFEST.sha256.tmp"
mv "$out/MANIFEST.sha256.tmp" "$out/MANIFEST.sha256"
sha256sum "$out/classical.tsv" "$out/phase.tsv" "$out/negatives.tsv" \
  "$out/MANIFEST.sha256"
