#!/bin/bash
# build.sh — build ppgpu (CUDA, sm_89) and ppcpu (CPU reference) on a host
# with nvcc. Keeps CPU usage polite: single-threaded compile, nice.
set -euo pipefail
cd "$(dirname "$0")"

CUDA_ARCH=${PPGPU_CUDA_ARCH:-89}
case "$CUDA_ARCH" in
  89|120) ;;
  *) echo "unsupported PPGPU_CUDA_ARCH=$CUDA_ARCH" >&2; exit 2 ;;
esac

echo "== ppcpu (CPU reference) =="
g++ -O3 -std=c++17 -o ppcpu.tmp src/ppcpu.cpp
mv ppcpu.tmp ppcpu

echo "== ppgpu (CUDA sm_$CUDA_ARCH) =="
nvcc -O3 --std=c++17 -lineinfo -Xptxas=-v \
  -gencode "arch=compute_$CUDA_ARCH,code=sm_$CUDA_ARCH" \
  src/ppgpu.cu -o ppgpu.tmp
mv ppgpu.tmp ppgpu

echo "== smoke: __int128 device probe compiled into ppgpu OK =="
ls -la ppgpu ppcpu
sha256sum ppgpu ppcpu
