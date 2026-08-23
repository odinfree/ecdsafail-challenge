#!/bin/bash
# Build and run fixture parity on one fresh, dedicated, idle CUDA GPU. This
# script does not provision a host and cannot invoke a range scan.
set -euo pipefail

W=$(cd "$(dirname "$0")" && pwd)
readonly COMMON_SHA=94950be99c0bcafc20373c9d29ebc142679cb026151d1d5558a3fea3a2b43bd9
test "$(sha256sum "$W/stage_common.sh" | awk '{print $1}')" = "$COMMON_SHA"
# shellcheck source=stage_common.sh
source "$W/stage_common.sh"

test "$W" = "$EXPECTED_STAGE_ROOT"
exec 9>"$W/stage-dedicated.lock"
flock -n 9

assert_gpu_idle() {
  local apps
  apps=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader | \
    sed '/^$/d' | tr -d ' ')
  test -z "$apps"
}

assert_gpu_idle
test "$(nvidia-smi --query-gpu=index --format=csv,noheader | wc -l | tr -d ' ')" -eq 1
GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | tr -d '\r')
GPU_CC=$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader | tr -d '\r')
case "$GPU_CC" in
  8.9) CUDA_ARCH=89 ;;
  12.0) CUDA_ARCH=120 ;;
  *) echo "unsupported dedicated GPU compute capability: $GPU_CC" >&2; exit 2 ;;
esac
nvcc --list-gpu-code | grep -Fqx "sm_$CUDA_ARCH"

stage_execute_parity_only "$W" "$CUDA_ARCH"

assert_gpu_idle
stage_assert_no_candidate_process "$W"
UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)
{
  printf 'utc=%s\n' "$UTC"
  printf 'mode=dedicated gpu_apps_before=0 gpu_apps_after=0\n'
  printf 'gpu_name=%s compute_capability=%s cuda_arch=%s\n' \
    "$GPU_NAME" "$GPU_CC" "$CUDA_ARCH"
  printf 'ops_sha256=%s state_digest=%s\n' "$OPS_SHA" "$STATE_DIGEST"
  printf 'ppgpu_sha256=%s\n' "$(stage_sha "$W/ppgpu")"
  printf 'ppcpu_sha256=%s\n' "$(stage_sha "$W/ppcpu")"
  printf 'scanner_launches=0 incumbent_touched=0\n'
} > "$W/DEDICATED.complete.tmp"
mv "$W/DEDICATED.complete.tmp" "$W/DEDICATED.complete"
printf 'DEDICATED_PARITY_COMPLETE state_digest=%s scanner_launches=0\n' \
  "$STATE_DIGEST"
