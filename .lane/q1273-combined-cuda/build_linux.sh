#!/usr/bin/env bash
set -euo pipefail

if test "$#" -ne 2; then
    echo "usage: $0 /exact/ops.bin /new/isolated/workspace" >&2
    exit 64
fi

lane=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
root=$(CDPATH= cd -- "$lane/../.." && pwd)
ops=$1
workspace=$2
# shellcheck disable=SC1091
. "$lane/HANDOFF.meta"

sha256_file() {
    sha256sum "$1" | awk '{print $1}'
}

"$lane/verify_ready.sh"
test -f "$ops" || { echo "missing ops stream: $ops" >&2; exit 66; }
test "$(sha256_file "$ops")" = "$OPS_SHA256" || {
    echo "wrong ops stream" >&2
    exit 65
}
case "$workspace" in ''|/|.|..) echo "unsafe workspace: $workspace" >&2; exit 64 ;; esac
test ! -e "$workspace" || { echo "workspace exists: $workspace" >&2; exit 73; }
mkdir -p "$workspace/bin" "$workspace/receipts" "$workspace/results"

cpu_src="$root/.lane/q1273-predictor/src/ppcpu.cpp"
cuda_src="$lane/src/ppgpu_parity.cu"
cxx=${CXX:-g++}
nvcc=${NVCC:-nvcc}

"$cxx" --version >"$workspace/receipts/cxx.txt"
"$nvcc" --version >"$workspace/receipts/nvcc.txt"
"$cxx" -O3 -std=c++17 -pthread -Wall -Wextra -Werror -Wno-unused-parameter \
    -o "$workspace/bin/ppcpu" "$cpu_src" \
    >"$workspace/receipts/cpu-build.stdout" 2>"$workspace/receipts/cpu-build.stderr"

common=(-O3 -std=c++17 -lineinfo -arch=native --expt-relaxed-constexpr)
"$nvcc" "${common[@]}" -o "$workspace/bin/ppgpu" "$cuda_src" \
    >"$workspace/receipts/cuda-build.stdout" 2>"$workspace/receipts/cuda-build.stderr"
"$nvcc" "${common[@]}" -DPP_EXPECTED_STATE_DIGEST_VALUE=0x2148e09f4c4293b3ULL \
    -o "$workspace/bin/ppgpu-bad-digest" "$cuda_src" \
    >"$workspace/receipts/bad-digest-build.stdout" \
    2>"$workspace/receipts/bad-digest-build.stderr"
"$nvcc" "${common[@]}" -DPP_PHASE_FORCE_BAD_SCHEDULE \
    -o "$workspace/bin/ppgpu-bad-schedule" "$cuda_src" \
    >"$workspace/receipts/bad-schedule-build.stdout" \
    2>"$workspace/receipts/bad-schedule-build.stderr"

for binary in ppcpu ppgpu ppgpu-bad-digest ppgpu-bad-schedule; do
    test -x "$workspace/bin/$binary"
    sha256sum "$workspace/bin/$binary"
done >"$workspace/receipts/BINARIES.sha256"
sha256sum "$cpu_src" "$cuda_src" "$ops" >"$workspace/receipts/INPUTS.sha256"

PPF_OPS="$ops" "$workspace/bin/ppcpu" identity \
    >"$workspace/receipts/cpu-identity.stdout" 2>"$workspace/receipts/cpu-identity.stderr"
PPF_OPS="$ops" "$workspace/bin/ppgpu" identity \
    >"$workspace/receipts/gpu-identity.stdout" 2>"$workspace/receipts/gpu-identity.stderr"
rg -Fq "combined_cpu_commit=$COMBINED_CPU_GO_COMMIT" \
    "$workspace/receipts/gpu-identity.stdout"
rg -Fq 'scan=disabled range=unauthorized' "$workspace/receipts/gpu-identity.stdout"

{
    printf 'packet_id=%s\n' "$PACKET_ID"
    printf 'combined_cpu_go_commit=%s\n' "$COMBINED_CPU_GO_COMMIT"
    printf 'ops_sha256=%s\n' "$OPS_SHA256"
    printf 'cuda_source_sha256=%s\n' "$CUDA_SOURCE_SHA256"
    printf 'scan_mode=disabled\nrange_authorized=no\n'
    printf 'binary_manifest_sha256=%s\n' "$(sha256_file "$workspace/receipts/BINARIES.sha256")"
    printf 'input_manifest_sha256=%s\n' "$(sha256_file "$workspace/receipts/INPUTS.sha256")"
} >"$workspace/receipts/BUILD.complete.tmp"
mv "$workspace/receipts/BUILD.complete.tmp" "$workspace/receipts/BUILD.complete"
printf 'Q1273_CUDA_BUILD_OK combined=%s cuda=%s\n' \
    "$COMBINED_CPU_GO_COMMIT" "$CUDA_SOURCE_SHA256"
