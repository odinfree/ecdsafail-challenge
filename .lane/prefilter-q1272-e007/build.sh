#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

CUDA_ARCH=${PPGPU_CUDA_ARCH:-89}
case "$CUDA_ARCH" in
  89|120) ;;
  *) echo "unsupported PPGPU_CUDA_ARCH=$CUDA_ARCH" >&2; exit 2 ;;
esac

# This packet is for fixture parity only. Range entry points stay compiled out
# until a later reviewed source commit closes the exactness gates.
${CXX:-g++} -O3 -std=c++17 -pthread -DPP_DISABLE_SCAN=1 \
  -o ppcpu.tmp src/ppcpu.cpp
mv ppcpu.tmp ppcpu

nvcc -O3 --std=c++17 -lineinfo -Xptxas=-v -DPP_DISABLE_SCAN=1 \
  -gencode "arch=compute_$CUDA_ARCH,code=sm_$CUDA_ARCH" \
  src/ppgpu.cu -o ppgpu.tmp
mv ppgpu.tmp ppgpu

sha256sum ppcpu ppgpu
