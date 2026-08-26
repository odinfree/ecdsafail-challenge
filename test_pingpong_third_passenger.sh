#!/usr/bin/env bash
set -euo pipefail

repo_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd -P)
binary="$repo_dir/target/release/build_circuit"
scratch=$(mktemp -d "${TMPDIR:-/tmp}/pingpong-third-passenger.XXXXXX")
trap 'rm -rf -- "$scratch"' EXIT

cargo build \
  --manifest-path "$repo_dir/Cargo.toml" \
  --release \
  --locked \
  --bin build_circuit

run_arm() {
  local label=$1
  local flag=$2
  local walk_peak=$3
  local arm="$scratch/$label"
  mkdir -p "$arm"
  (
    cd -- "$arm"
    if [[ "$flag" == absent ]]; then
      env -i \
        PATH="$PATH" \
        PP_PROFILE=1 \
        PP_PROFILE_SEED=third-passenger-gate \
        SUB4_SQUARE_B_LOCAL_K2=1 \
        SUB4_PP_PEAK=1267 \
        SUB4_PP_WALK_PEAK="$walk_peak" \
        SUB4_PINGPONG_INPUT_AWARE_CONSTPROP=1 \
        TLM_CASCADE_DISABLE=1 \
        "$binary"
    else
      env -i \
        PATH="$PATH" \
        PP_PROFILE=1 \
        PP_PROFILE_SEED=third-passenger-gate \
        SUB4_SQUARE_B_LOCAL_K2=1 \
        SUB4_PP_PEAK=1267 \
        SUB4_PP_WALK_PEAK="$walk_peak" \
        SUB4_PINGPONG_INPUT_AWARE_CONSTPROP=1 \
        SUB4_PP_THIRD_PASSENGER="$flag" \
        TLM_CASCADE_DISABLE=1 \
        "$binary"
    fi
  ) >"$arm/build.log" 2>&1
}

read_metrics() {
  local label=$1
  local arm="$scratch/$label"
  local emitted peak num_qubits raw_ops toffoli removed profile_digest digest
  emitted=$(sed -nE 's/^  emitted ops : ([0-9]+)$/\1/p' "$arm/build.log")
  peak=$(sed -nE 's/^PP_PROFILE peak_qubits=([0-9]+).*$/\1/p' "$arm/build.log")
  num_qubits=$(sed -nE 's/^PP_PROFILE .*num_qubits=([0-9]+).*$/\1/p' "$arm/build.log")
  raw_ops=$(sed -nE 's/^PP_PROFILE .* ops=([0-9]+)$/\1/p' "$arm/build.log")
  toffoli=$(awk '$1 == "TOTAL" { print $5 }' "$arm/build.log")
  removed=$(sed -nE 's/^CONSTPROP TOTAL .*\(toffoli removed = ([0-9]+)\)$/\1/p' "$arm/build.log")
  profile_digest=$(sed -nE 's/^PP_PROFILE lanes=64 (.*)$/\1/p' "$arm/build.log" | shasum -a 256 | awk '{print $1}')
  digest=$(shasum -a 256 "$arm/ops.bin" | awk '{print $1}')
  [[ -n "$emitted" && -n "$peak" && -n "$num_qubits" && -n "$raw_ops" && -n "$toffoli" && -n "$removed" && -n "$profile_digest" && -n "$digest" ]]
  printf '%s %s %s %s %s %s %s %s\n' "$emitted" "$peak" "$num_qubits" "$raw_ops" "$toffoli" "$removed" "$profile_digest" "$digest"
}

run_arm baseline absent 1266
run_arm zero 0 1266
run_arm invalid invalid 1266
run_arm hybrid-control 0 1265
run_arm candidate 1 1265

read -r baseline_emitted baseline_peak baseline_numq baseline_raw baseline_toffoli baseline_removed baseline_profile baseline_digest < <(read_metrics baseline)
read -r zero_emitted zero_peak zero_numq zero_raw zero_toffoli zero_removed zero_profile zero_digest < <(read_metrics zero)
read -r invalid_emitted invalid_peak invalid_numq invalid_raw invalid_toffoli invalid_removed invalid_profile invalid_digest < <(read_metrics invalid)
read -r control_emitted control_peak control_numq control_raw control_toffoli control_removed control_profile control_digest < <(read_metrics hybrid-control)
read -r candidate_emitted candidate_peak candidate_numq candidate_raw candidate_toffoli candidate_removed candidate_profile candidate_digest < <(read_metrics candidate)

printf 'OBSERVED baseline=%s/Q%s/%s/T%s zero=%s/Q%s/%s invalid=%s/Q%s/%s control=%s/Q%s/%s/T%s candidate=%s/Q%s/%s/T%s\n' \
  "$baseline_emitted" "$baseline_peak" "$baseline_numq" "$baseline_toffoli" \
  "$zero_emitted" "$zero_peak" "$zero_numq" \
  "$invalid_emitted" "$invalid_peak" "$invalid_numq" \
  "$control_emitted" "$control_peak" "$control_numq" "$control_toffoli" \
  "$candidate_emitted" "$candidate_peak" "$candidate_numq" "$candidate_toffoli"

[[ "$baseline_emitted" == 12520960 ]]
[[ "$baseline_peak" == 1265 ]]
[[ "$baseline_numq" == 1265 ]]
[[ "$zero_emitted $zero_peak $zero_numq $zero_raw $zero_toffoli $zero_removed $zero_profile $zero_digest" == \
   "$baseline_emitted $baseline_peak $baseline_numq $baseline_raw $baseline_toffoli $baseline_removed $baseline_profile $baseline_digest" ]]
[[ "$invalid_emitted $invalid_peak $invalid_numq $invalid_raw $invalid_toffoli $invalid_removed $invalid_profile $invalid_digest" == \
   "$baseline_emitted $baseline_peak $baseline_numq $baseline_raw $baseline_toffoli $baseline_removed $baseline_profile $baseline_digest" ]]

[[ "$control_peak" == 1265 ]]
[[ "$control_numq" == 1265 ]]
[[ "$candidate_peak" == 1264 ]]
[[ "$candidate_numq" == 1264 ]]
[[ "$candidate_profile" == "$control_profile" ]]
awk -v baseline="$baseline_toffoli" -v candidate="$candidate_toffoli" \
  'BEGIN { exit !((candidate - baseline) <= 300.0) }'
awk -v control="$control_toffoli" -v candidate="$candidate_toffoli" \
  'BEGIN { exit !((candidate - control) <= 50.0) }'
(( candidate_raw - control_raw >= 2500 ))
(( candidate_raw - control_raw <= 2650 ))
(( candidate_removed >= control_removed ))
(( candidate_emitted - control_emitted >= 2500 ))
(( candidate_emitted - control_emitted <= 2650 ))
[[ "$candidate_digest" != "$baseline_digest" ]]

baseline_score=$(awk -v t="$baseline_toffoli" -v removed="$baseline_removed" \
  'BEGIN { printf "%.0f", 1265 * int(t - removed + 0.5) }')
candidate_score=$(awk -v t="$candidate_toffoli" -v removed="$candidate_removed" \
  'BEGIN { printf "%.0f", 1264 * int(t - removed + 0.5) }')
(( baseline_score - candidate_score >= 500000 ))

printf 'PASS baseline=%s/Q%s/T%s candidate=%s/Q%s/T%s delta_ops=%s profile_score_gain=%s\n' \
  "$baseline_emitted" "$baseline_peak" "$baseline_toffoli" \
  "$candidate_emitted" "$candidate_peak" "$candidate_toffoli" \
  "$((candidate_emitted - baseline_emitted))" \
  "$((baseline_score - candidate_score))"
