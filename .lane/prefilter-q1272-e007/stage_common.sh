#!/bin/bash
# Shared fail-closed fixture-parity stage. This file never invokes a range
# mode; build.sh compiles both binaries with PP_DISABLE_SCAN=1.
set -euo pipefail

readonly EXPECTED_STAGE_ROOT=/workspace/ev-q1272-e007-ea93a131
readonly EXPECTED_OPS=12943345
readonly OPS_SHA=4618d4af86c23c06cc72fef26f8a8e5986c7a9de5f804891541a8ce6eb189f37
readonly STATE_DIGEST=963a662d2e392804
readonly HOST_SHA=ff609173d16d2cb6d3d69f81b22a1361b42772c3d58c8b83ac836222028ccbaa
readonly MODEL_SHA=609d21cab5ad8dd40180f1a20311d1578b2b6d243133a0137951d3f2dddcc81d
readonly CPU_SRC_SHA=47061664fa5365793e01427c0834dcbee9e01daca16981ba980b9c4f22bbc460
readonly GPU_SRC_SHA=bc3acb5867a477d8d50b00a997b38fcab78d92267f9e8906bba9ddff5ab28872
readonly BUILD_SHA=349287129102bc97aec491c2e0fd6cc7470cbc9ebef64fa567770f94547b2cd7
readonly FIXTURES_SHA=ff272f7d203a2f8dc56c21b577f0bcc661ab0dde5390477b239c0bdbe52b3057
readonly INHERITED_SET_SHA=77c521cb00cbd6fcc32bd6f9accb49d26f1c435b0b79091cf09dbfbd0efc9eaf
readonly INHERITED_NONCE=251000962439

stage_sha() {
  sha256sum "$1" | awk '{print $1}'
}

stage_require_tools() {
  local tool
  for tool in awk cmp cuobjdump dd flock g++ grep head nvidia-smi nvcc od \
    sed sha256sum tail tr zstd; do
    command -v "$tool" >/dev/null
  done
}

stage_assert_root_and_sources() {
  local w=$1
  test "$w" = "$EXPECTED_STAGE_ROOT"
  test "$(stage_sha "$w/ops.bin")" = "$OPS_SHA"
  test "$(stage_sha "$w/src/pp_host.h")" = "$HOST_SHA"
  test "$(stage_sha "$w/src/pp_model.h")" = "$MODEL_SHA"
  test "$(stage_sha "$w/src/ppcpu.cpp")" = "$CPU_SRC_SHA"
  test "$(stage_sha "$w/src/ppgpu.cu")" = "$GPU_SRC_SHA"
  test "$(stage_sha "$w/build.sh")" = "$BUILD_SHA"
  test "$(stage_sha "$w/fixtures.tsv")" = "$FIXTURES_SHA"
  test "$(stage_sha "$w/inherited-faultshots.tsv")" = "$INHERITED_SET_SHA"
}

stage_assert_fresh_outputs() {
  local w=$1 path
  for path in ppcpu ppgpu FINGERPRINTS PARITY.complete DEDICATED.complete \
    BORROW.complete fixtures negative; do
    test ! -e "$w/$path"
  done
}

stage_assert_no_candidate_process() {
  local w=$1 proc exe
  for proc in /proc/[0-9]*; do
    exe=$(readlink "$proc/exe" 2>/dev/null || true)
    test "$exe" != "$w/ppgpu"
    test "$exe" != "$w/ppcpu"
  done
}

stage_build_scan_disabled() {
  local w=$1 cuda_arch=$2
  PPGPU_CUDA_ARCH="$cuda_arch" "$w/build.sh"
  test "$(cuobjdump --list-elf "$w/ppgpu" | grep -Fc "sm_$cuda_arch")" -ge 1
  grep -aFq 'ppcpu: range scanning is disabled in this parity build' "$w/ppcpu"
  grep -aFq 'ppgpu: range scanning is disabled in this parity build' "$w/ppgpu"
}

stage_run_fixtures() {
  local w=$1 nonce baked_sha model_cls walk_div replay_div walk_mul replay_mul
  local result model_first full_cls full_phase full_ancilla full_first cpu_gate
  local expected digest_rows
  mkdir "$w/fixtures"

  while IFS=$'\t' read -r nonce baked_sha model_cls walk_div replay_div \
    walk_mul replay_mul result model_first full_cls full_phase full_ancilla \
    full_first cpu_gate; do
    test "$baked_sha" != "baked_ops_sha256"
    expected="$w/fixtures/expected.breakdown.$nonce"
    printf 'nonce %s pred_cls=%s walk_div=%s replay_div=%s walk_mul=%s replay_mul=%s result=%s shots=9024 first=%s\n' \
      "$nonce" "$model_cls" "$walk_div" "$replay_div" "$walk_mul" \
      "$replay_mul" "$result" "$model_first" > "$expected"
    PPF_OPS="$w/ops.bin" "$w/ppcpu" breakdown "$nonce" \
      > "$w/fixtures/cpu.breakdown.$nonce" \
      2> "$w/fixtures/cpu.breakdown.$nonce.stderr"
    "$w/ppgpu" --ops "$w/ops.bin" --breakdown "$nonce" --comb-bits 8 \
      > "$w/fixtures/gpu8.breakdown.$nonce" \
      2> "$w/fixtures/gpu8.breakdown.$nonce.stderr"
    "$w/ppgpu" --ops "$w/ops.bin" --breakdown "$nonce" --comb-bits 16 \
      > "$w/fixtures/gpu16.breakdown.$nonce" \
      2> "$w/fixtures/gpu16.breakdown.$nonce.stderr"
    cmp "$expected" "$w/fixtures/cpu.breakdown.$nonce"
    cmp "$expected" "$w/fixtures/gpu8.breakdown.$nonce"
    cmp "$expected" "$w/fixtures/gpu16.breakdown.$nonce"
  done < <(tail -n +2 "$w/fixtures.tsv")

  PPF_OPS="$w/ops.bin" "$w/ppcpu" faultshots "$INHERITED_NONCE" \
    > "$w/fixtures/cpu.faultshots.$INHERITED_NONCE" \
    2> "$w/fixtures/cpu.faultshots.$INHERITED_NONCE.stderr"
  "$w/ppgpu" --ops "$w/ops.bin" --faultshots "$INHERITED_NONCE" --comb-bits 8 \
    > "$w/fixtures/gpu8.faultshots.$INHERITED_NONCE" \
    2> "$w/fixtures/gpu8.faultshots.$INHERITED_NONCE.stderr"
  "$w/ppgpu" --ops "$w/ops.bin" --faultshots "$INHERITED_NONCE" --comb-bits 16 \
    > "$w/fixtures/gpu16.faultshots.$INHERITED_NONCE" \
    2> "$w/fixtures/gpu16.faultshots.$INHERITED_NONCE.stderr"
  cmp "$w/inherited-faultshots.tsv" \
    "$w/fixtures/cpu.faultshots.$INHERITED_NONCE"
  cmp "$w/inherited-faultshots.tsv" \
    "$w/fixtures/gpu8.faultshots.$INHERITED_NONCE"
  cmp "$w/inherited-faultshots.tsv" \
    "$w/fixtures/gpu16.faultshots.$INHERITED_NONCE"

  test "$(PPF_OPS="$w/ops.bin" "$w/ppcpu" statedigest)" = "$STATE_DIGEST"
  digest_rows=$(grep -h -F "state_digest=$STATE_DIGEST" \
    "$w"/fixtures/gpu*.stderr | wc -l | tr -d ' ')
  test "$digest_rows" -eq 10
  test "$(sed -n 's/.*state_digest=\([0-9a-f]\{16\}\).*/\1/p' \
    "$w"/fixtures/gpu*.stderr | sort -u | wc -l | tr -d ' ')" -eq 1
}

stage_expect_reject() {
  local w=$1 artifact=$2 label=$3 expected_text=$4 rc
  set +e
  PPF_OPS="$artifact" "$w/ppcpu" statedigest \
    > "$w/negative/$label.cpu.stdout" 2> "$w/negative/$label.cpu.stderr"
  rc=$?
  set -e
  test "$rc" -eq 2
  grep -Fq "$expected_text" "$w/negative/$label.cpu.stderr"

  set +e
  "$w/ppgpu" --ops "$artifact" --breakdown "$INHERITED_NONCE" --comb-bits 8 \
    > "$w/negative/$label.gpu.stdout" 2> "$w/negative/$label.gpu.stderr"
  rc=$?
  set -e
  test "$rc" -eq 2
  grep -Fq "$expected_text" "$w/negative/$label.gpu.stderr"
}

stage_run_negative_streams() {
  local w=$1 body old_byte new_byte oct
  mkdir "$w/negative"

  cp "$w/ops.bin" "$w/negative/wrong-count.ops.bin"
  printf '\360\177\305\000\000\000\000\000' | dd \
    of="$w/negative/wrong-count.ops.bin" bs=1 seek=8 conv=notrunc status=none
  test "$(stage_sha "$w/negative/wrong-count.ops.bin")" != "$OPS_SHA"
  stage_expect_reject "$w" "$w/negative/wrong-count.ops.bin" wrong-count \
    'refusing to run on an unknown stream'

  body="$w/negative/same-count.body"
  tail -c +17 -- "$w/ops.bin" | zstd -dc > "$body"
  test "$(wc -c < "$body" | tr -d ' ')" -eq $((EXPECTED_OPS * 56))
  old_byte=$(od -An -tu1 -j 8 -N 1 "$body" | tr -d ' ')
  new_byte=$(((old_byte + 1) & 255))
  printf -v oct '%03o' "$new_byte"
  printf "\\$oct" | dd of="$body" bs=1 seek=8 conv=notrunc status=none
  {
    head -c 16 "$w/ops.bin"
    zstd -q -c "$body"
  } > "$w/negative/same-count-wrong-sha.ops.bin"
  test "$(stage_sha "$w/negative/same-count-wrong-sha.ops.bin")" != "$OPS_SHA"
  stage_expect_reject "$w" "$w/negative/same-count-wrong-sha.ops.bin" \
    same-count-wrong-sha 'refusing same-count unknown stream'
}

stage_write_common_receipts() {
  local w=$1 cuda_arch=$2
  {
    sha256sum "$w/ops.bin" "$w/ppgpu" "$w/ppcpu" "$w/build.sh" \
      "$w/fixtures.tsv" "$w/inherited-faultshots.tsv" \
      "$w/src/pp_host.h" "$w/src/pp_model.h" "$w/src/ppcpu.cpp" \
      "$w/src/ppgpu.cu"
    printf 'source_commit=ea93a131e2bc488bff6fa12010d1f3606c7771b0\n'
    printf 'operation_count=%s\n' "$EXPECTED_OPS"
    printf 'state_digest=%s\n' "$STATE_DIGEST"
    printf 'cuda_arch=%s\n' "$cuda_arch"
    printf 'scanner_launches=0 scan_entrypoints=compiled_disabled\n'
    printf 'max_faults_source_supported=0,1,2,3 scan_runtime=disabled tolerant_pilot=proof_gated_disabled\n'
  } > "$w/FINGERPRINTS.tmp"
  mv "$w/FINGERPRINTS.tmp" "$w/FINGERPRINTS"
  {
    printf 'fixtures=251000962439,0,7,2500069332 cpu=gpu8=gpu16\n'
    printf 'inherited_faultshots=11 cpu=gpu8=gpu16\n'
    printf 'wrong_count=cpu2,gpu2 same_count_wrong_sha=cpu2,gpu2\n'
    printf 'scanner_launches=0\n'
  } > "$w/PARITY.complete.tmp"
  mv "$w/PARITY.complete.tmp" "$w/PARITY.complete"
}

stage_execute_parity_only() {
  local w=$1 cuda_arch=$2
  stage_require_tools
  stage_assert_root_and_sources "$w"
  stage_assert_fresh_outputs "$w"
  stage_assert_no_candidate_process "$w"
  stage_build_scan_disabled "$w" "$cuda_arch"
  stage_run_fixtures "$w"
  stage_run_negative_streams "$w"
  stage_assert_no_candidate_process "$w"
  stage_write_common_receipts "$w" "$cuda_arch"
}
