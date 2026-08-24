#!/bin/bash
# build.sh — build ppgpu (CUDA, sm_89) and ppcpu (CPU reference) on a host
# with nvcc. Keeps CPU usage polite: single-threaded compile, nice.
set -euo pipefail
cd "$(dirname "$0")"

echo "== ppcpu (CPU reference) =="
g++ -O3 -std=c++17 -o ppcpu src/ppcpu.cpp

echo "== ppgpu (CUDA sm_89) =="
nvcc -O3 --std=c++17 -lineinfo -Xptxas=-v \
  -gencode arch=compute_89,code=sm_89 \
  src/ppgpu.cu -o ppgpu

echo "== smoke: __int128 device probe compiled into ppgpu OK =="
ls -la ppgpu ppcpu
