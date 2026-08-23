#!/usr/bin/env bash
set -euo pipefail

if test "$#" -ne 1; then
    echo "usage: $0 /new/isolated/workspace" >&2
    exit 64
fi

PK=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
W=$1
# shellcheck disable=SC1091
. "$PK/PACKET.meta"
"$PK/verify_packet.sh"

case "$W" in ''|/|.|..) echo "unsafe workspace: $W" >&2; exit 64 ;; esac
test ! -e "$W" || { echo "workspace already exists: $W" >&2; exit 73; }
mkdir -p "$W/source" "$W/target" "$W/bin" "$W/generated" "$W/receipts"

tar -xf "$PK/source/cpu-72b8a97.tar" -C "$W/source"
tar -xf "$PK/source/cuda-2246f4c.tar" -C "$W/source"
CPU_ROOT="$W/source/cpu-source"
CUDA_SRC="$W/source/cuda-source/.lane/q1272-cuda/pingpong_filter.cu"

test "$(sha256sum "$CPU_ROOT/src/bin/pingpong_filter.rs" | awk '{print $1}')" = \
    "$CPU_PREDICTOR_SOURCE_SHA256"
test "$(sha256sum "$CUDA_SRC" | awk '{print $1}')" = "$CUDA_SOURCE_SHA256"

rustc -Vv > "$W/receipts/rustc.txt"
cargo -V > "$W/receipts/cargo.txt"
nvcc --version > "$W/receipts/nvcc.txt"

SUB4_PP_PEAK=1272 \
SUB4_SQUARE_LADDER=242 \
SUB4_PP_FOLD_SELECTOR_EVICT=1 \
CARGO_TARGET_DIR="$W/target" \
    cargo build --locked --release --manifest-path "$CPU_ROOT/Cargo.toml" \
      --bin build_circuit --bin pingpong_filter \
      > "$W/receipts/cargo-build.stdout" 2> "$W/receipts/cargo-build.stderr"

cp "$W/target/release/pingpong_filter" "$W/bin/ppcpu"
test -x "$W/bin/ppcpu"

(
    cd "$W/generated"
    SUB4_PP_PEAK=1272 \
    SUB4_SQUARE_LADDER=242 \
    SUB4_PP_FOLD_SELECTOR_EVICT=1 \
    SUB4_PINGPONG_TAIL_NONCE="$INHERITED_NONCE" \
        "$W/target/release/build_circuit" > build-circuit.log 2>&1
)
cmp "$PK/artifacts/ops.bin" "$W/generated/ops.bin"

SUB4_PP_PEAK=1272 \
SUB4_SQUARE_LADDER=242 \
SUB4_PP_FOLD_SELECTOR_EVICT=1 \
    "$W/bin/ppcpu" --dump-checkpoint "$W/generated/checkpoint.bin" \
      > "$W/receipts/checkpoint.stdout" 2> "$W/receipts/checkpoint.stderr"
cmp "$PK/artifacts/checkpoint.bin" "$W/generated/checkpoint.bin"

nvcc -O3 -std=c++17 -lineinfo -arch=native -Xptxas=-v \
    -o "$W/bin/ppgpu" "$CUDA_SRC" \
    > "$W/receipts/nvcc-build.stdout" 2> "$W/receipts/nvcc-build.stderr"
test -x "$W/bin/ppgpu"

cpu_sha=$(sha256sum "$W/bin/ppcpu" | awk '{print $1}')
gpu_sha=$(sha256sum "$W/bin/ppgpu" | awk '{print $1}')
ops_sha=$(sha256sum "$W/generated/ops.bin" | awk '{print $1}')
checkpoint_sha=$(sha256sum "$W/generated/checkpoint.bin" | awk '{print $1}')
test "$ops_sha" = "$OPS_SHA256"
test "$checkpoint_sha" = "$CHECKPOINT_SHA256"

{
    printf 'packet_id=%s\n' "$PACKET_ID"
    printf 'cpu_evidence_commit=%s\n' "$CPU_EVIDENCE_COMMIT"
    printf 'cuda_source_commit=%s\n' "$CUDA_SOURCE_COMMIT"
    printf 'ops_sha256=%s\n' "$ops_sha"
    printf 'checkpoint_sha256=%s\n' "$checkpoint_sha"
    printf 'linux_ppcpu_sha256=%s\n' "$cpu_sha"
    printf 'linux_ppgpu_sha256=%s\n' "$gpu_sha"
    printf 'nvcc_command=nvcc -O3 -std=c++17 -lineinfo -arch=native -Xptxas=-v\n'
} > "$W/receipts/BUILD.complete.tmp"
mv "$W/receipts/BUILD.complete.tmp" "$W/receipts/BUILD.complete"
printf 'Q1272_SELECTOR_LINUX_BUILD_OK cpu=%s gpu=%s\n' "$cpu_sha" "$gpu_sha"
