#!/usr/bin/env bash
set -euo pipefail

repo_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd -P)
binary="$repo_dir/target/release/build_circuit"
scratch=$(mktemp -d "${TMPDIR:-/tmp}/product-square-b-k2.XXXXXX")
trap 'rm -rf -- "$scratch"' EXIT

cargo build \
  --manifest-path "$repo_dir/Cargo.toml" \
  --release \
  --locked \
  --bin build_circuit

run_selfcheck() {
  local enabled=$1
  local output=$2
  (
    cd -- "$scratch"
    env -i \
      SUB4_PRODUCT_SQUARE_SELFTEST=1 \
      SUB4_SQUARE_B_LOCAL_K2="$enabled" \
      "$binary"
  ) >"$output" 2>&1
}

extract_metrics() {
  local output=$1
  local line
  line=$(grep -E '^product-register square: [0-9]+ emitted / [0-9.]+ executed Toffoli, [0-9]+ peak qubits$' "$output")
  sed -E \
    's/^product-register square: ([0-9]+) emitted \/ ([0-9.]+) executed Toffoli, ([0-9]+) peak qubits$/\1 \2 \3/' \
    <<<"$line"
}

run_selfcheck 0 "$scratch/baseline.log"
run_selfcheck invalid "$scratch/invalid-flag.log"
run_selfcheck 1 "$scratch/candidate.log"

read -r baseline_emitted baseline_executed baseline_peak < <(extract_metrics "$scratch/baseline.log")
read -r invalid_emitted invalid_executed invalid_peak < <(extract_metrics "$scratch/invalid-flag.log")
read -r candidate_emitted candidate_executed candidate_peak < <(extract_metrics "$scratch/candidate.log")

[[ "$baseline_emitted" == 55111 ]]
[[ "$baseline_executed" == 54882.297 ]]
[[ "$baseline_peak" == 1153 ]]
[[ "$invalid_emitted $invalid_executed $invalid_peak" == \
   "$baseline_emitted $baseline_executed $baseline_peak" ]]

(( baseline_emitted - candidate_emitted >= 2000 ))
awk -v baseline="$baseline_executed" -v candidate="$candidate_executed" \
  'BEGIN { exit !((baseline - candidate) >= 2000.0) }'
(( candidate_peak <= 1266 ))

printf 'PASS baseline=%s/%s/%s candidate=%s/%s/%s\n' \
  "$baseline_emitted" "$baseline_executed" "$baseline_peak" \
  "$candidate_emitted" "$candidate_executed" "$candidate_peak"
