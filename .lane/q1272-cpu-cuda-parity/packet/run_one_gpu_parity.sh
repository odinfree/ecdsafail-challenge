#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 0 ]]; then
  echo "run-one-gpu-parity: this fixed regression accepts no arguments" >&2
  exit 2
fi

packet_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [[ ${CUDA_VISIBLE_DEVICES+x} ]]; then
  visible_device=$CUDA_VISIBLE_DEVICES
else
  visible_device=0
fi
if [[ ! $visible_device =~ ^[0-9]+$ ]]; then
  echo "run-one-gpu-parity: exactly one numeric CUDA_VISIBLE_DEVICES entry is required" >&2
  exit 2
fi
export CUDA_VISIBLE_DEVICES=$visible_device

"$packet_dir/verify_packet.py"
for tool in g++ nvcc awk cmp head mktemp nvidia-smi sha256sum; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "run-one-gpu-parity: missing required tool: $tool" >&2
    exit 2
  fi
done

run_dir=$(mktemp -d /tmp/q1272-fixed8-parity.XXXXXX)
chmod 700 "$run_dir"
mkdir "$run_dir/bin" "$run_dir/cpu" "$run_dir/gpu" "$run_dir/negatives"

g++ -O3 -std=c++17 -pthread \
  -I"$packet_dir/src" -I"$packet_dir/include" \
  "$packet_dir/src/ppcpu.cpp" -o "$run_dir/bin/ppcpu"
nvcc -O3 -std=c++17 -lineinfo -arch=native \
  -I"$packet_dir/src" -I"$packet_dir/include" \
  "$packet_dir/src/ppcuda_fixed.cu" -o "$run_dir/bin/ppcuda-fixed"
nvcc -O3 -std=c++17 -lineinfo -arch=native -DPP_FIXED_FORCE_BAD_FAMILY \
  -I"$packet_dir/src" -I"$packet_dir/include" \
  "$packet_dir/src/ppcuda_fixed.cu" -o "$run_dir/bin/ppcuda-bad-family"

if nvidia-smi --query-compute-apps=pid --format=csv,noheader \
    | awk 'NF {found=1} END {exit found ? 0 : 1}'; then
  echo "run-one-gpu-parity: GPU is not idle before parity" >&2
  exit 2
fi

: >"$run_dir/cpu/classical.tsv"
: >"$run_dir/cpu/phase.tsv"
: >"$run_dir/cpu/stderr.log"
while IFS= read -r nonce; do
  PPF_OPS="$packet_dir/ops.bin" "$run_dir/bin/ppcpu" faultshots "$nonce" \
    2>>"$run_dir/cpu/stderr.log" \
    | awk -v nonce="$nonce" '{print nonce "\t" $1 "\t" $2}' \
    >>"$run_dir/cpu/classical.tsv"
  PPF_OPS="$packet_dir/ops.bin" "$run_dir/bin/ppcpu" phasefaultshots "$nonce" \
    2>>"$run_dir/cpu/stderr.log" \
    | awk -v nonce="$nonce" '{print nonce "\t" $1}' \
    >>"$run_dir/cpu/phase.tsv"
done <"$packet_dir/FIXED8.nonces"

(cd "$packet_dir" && "$run_dir/bin/ppcuda-fixed") \
  >"$run_dir/gpu/combined.tsv" 2>"$run_dir/gpu/stderr.log"
awk -F '\t' '$1 == "C" {print $2 "\t" $3 "\t" $4}' \
  "$run_dir/gpu/combined.tsv" >"$run_dir/gpu/classical.tsv"
awk -F '\t' '$1 == "P" {print $2 "\t" $3}' \
  "$run_dir/gpu/combined.tsv" >"$run_dir/gpu/phase.tsv"

cmp "$packet_dir/expected/classical.tsv" "$run_dir/cpu/classical.tsv"
cmp "$packet_dir/expected/phase.tsv" "$run_dir/cpu/phase.tsv"
cmp "$packet_dir/expected/classical.tsv" "$run_dir/gpu/classical.tsv"
cmp "$packet_dir/expected/phase.tsv" "$run_dir/gpu/phase.tsv"
cmp "$run_dir/cpu/classical.tsv" "$run_dir/gpu/classical.tsv"
cmp "$run_dir/cpu/phase.tsv" "$run_dir/gpu/phase.tsv"

if "$run_dir/bin/ppcuda-fixed" unexpected \
    >"$run_dir/negatives/argument.stdout" \
    2>"$run_dir/negatives/argument.stderr"; then
  echo "run-one-gpu-parity: argument negative did not fail closed" >&2
  exit 2
fi
if [[ -s "$run_dir/negatives/argument.stdout" ]]; then
  echo "run-one-gpu-parity: argument negative emitted stdout" >&2
  exit 2
fi

mkdir "$run_dir/negatives/missing" "$run_dir/negatives/truncated"
if (cd "$run_dir/negatives/missing" && "$run_dir/bin/ppcuda-fixed") \
    >"$run_dir/negatives/missing.stdout" \
    2>"$run_dir/negatives/missing.stderr"; then
  echo "run-one-gpu-parity: missing-ops negative did not fail closed" >&2
  exit 2
fi
head -c 64 "$packet_dir/ops.bin" >"$run_dir/negatives/truncated/ops.bin"
if (cd "$run_dir/negatives/truncated" && "$run_dir/bin/ppcuda-fixed") \
    >"$run_dir/negatives/truncated.stdout" \
    2>"$run_dir/negatives/truncated.stderr"; then
  echo "run-one-gpu-parity: truncated-ops negative did not fail closed" >&2
  exit 2
fi
if (cd "$packet_dir" && "$run_dir/bin/ppcuda-bad-family") \
    >"$run_dir/negatives/bad-family.stdout" \
    2>"$run_dir/negatives/bad-family.stderr"; then
  echo "run-one-gpu-parity: bad-family negative did not fail closed" >&2
  exit 2
fi
if [[ -s "$run_dir/negatives/bad-family.stdout" ]]; then
  echo "run-one-gpu-parity: bad-family negative emitted stdout" >&2
  exit 2
fi

if nvidia-smi --query-compute-apps=pid --format=csv,noheader \
    | awk 'NF {found=1} END {exit found ? 0 : 1}'; then
  echo "run-one-gpu-parity: GPU still has a compute process after parity" >&2
  exit 2
fi

results_sha=$(sha256sum "$run_dir/gpu/combined.tsv" | awk '{print $1}')
cat >"$run_dir/PARITY.complete" <<EOF
status=Q1272_FIXED8_CPU_CUDA_PARITY_PASS
fixtures=8
shots=72192
classical_rows=150
clean_phase_rows=32
gpu_combined_sha256=$results_sha
range_hunt_provider_submit_authority=0
EOF
echo "Q1272_FIXED8_CPU_CUDA_PARITY_PASS output=$run_dir receipt=$run_dir/PARITY.complete"
