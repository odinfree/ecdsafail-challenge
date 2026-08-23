#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

CUDA_ARCH=${PPGPU_CUDA_ARCH:-89}
case "$CUDA_ARCH" in
  89|120) ;;
  *) echo "unsupported PPGPU_CUDA_ARCH=$CUDA_ARCH" >&2; exit 2 ;;
esac

${CXX:-g++} -O3 -std=c++17 -pthread -o ppcpu.tmp src/ppcpu.cpp
mv ppcpu.tmp ppcpu

nvcc -O3 --std=c++17 -lineinfo -Xptxas=-v \
  -gencode "arch=compute_$CUDA_ARCH,code=sm_$CUDA_ARCH" \
  src/ppgpu.cu -o ppgpu.tmp
mv ppgpu.tmp ppgpu

sha256sum ppcpu ppgpu
