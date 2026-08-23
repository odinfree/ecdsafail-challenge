#!/usr/bin/env bash
set -euo pipefail

if test "$#" -lt 1 || test "$#" -gt 2; then
    echo "usage: $0 /new/isolated/workspace [cuda-device]" >&2
    exit 64
fi

PK=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
W=$1
DEVICE=${2:-0}
# shellcheck disable=SC1091
. "$PK/PACKET.meta"
case "$DEVICE" in ''|*[!0-9]*) echo "invalid CUDA device" >&2; exit 64 ;; esac

"$PK/build_linux.sh" "$W"
"$PK/selftest_failclosed.sh" "$W"

gpu_compute_pids() {
    nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits 2>/dev/null |
        awk '/^[[:space:]]*[0-9]+[[:space:]]*$/ {print $1}'
}

test -z "$(gpu_compute_pids)" || {
    echo "GPU is not idle before parity" >&2
    exit 75
}
nvidia-smi -i "$DEVICE" --query-gpu=name,compute_cap,driver_version \
    --format=csv,noheader > "$W/receipts/GPU.pre"

mkdir -p "$W/results"
PPGPU="$W/bin/ppgpu"
PPCPU="$W/bin/ppcpu"
CHECKPOINT="$PK/artifacts/checkpoint.bin"

SUB4_PP_PEAK=1272 \
SUB4_SQUARE_LADDER=242 \
SUB4_PP_FOLD_SELECTOR_EVICT=1 \
    "$PPCPU" --nonces "$PK/fixtures/h64.nonces" --jobs 4 --faultshots \
      > "$W/results/cpu-h64.tsv" 2> "$W/results/cpu-h64.stderr"
SUB4_PP_PEAK=1272 \
SUB4_SQUARE_LADDER=242 \
SUB4_PP_FOLD_SELECTOR_EVICT=1 \
    "$PPCPU" --nonces "$PK/fixtures/d32.nonces" --jobs 4 --faultshots \
      > "$W/results/cpu-d32.tsv" 2> "$W/results/cpu-d32.stderr"
cmp "$PK/fixtures/h64.expected.tsv" "$W/results/cpu-h64.tsv"
cmp "$PK/fixtures/d32.expected.tsv" "$W/results/cpu-d32.tsv"

"$PK/run_ppgpu_exact.sh" "$PPGPU" "$CHECKPOINT" \
    --selftest --device "$DEVICE" \
    > "$W/results/gpu-selftest.stdout" 2> "$W/results/gpu-selftest.stderr"
grep -Fqx 'gx OK' "$W/results/gpu-selftest.stderr"
grep -Fqx 'gy OK' "$W/results/gpu-selftest.stderr"

h64_from=$(head -n 1 "$PK/fixtures/h64.nonces")
h64_to=$(tail -n 1 "$PK/fixtures/h64.nonces")
test "$((h64_to - h64_from + 1))" = "$H64_ROWS"
"$PK/run_ppgpu_exact.sh" "$PPGPU" "$CHECKPOINT" \
    --from "$h64_from" --to "$h64_to" --device "$DEVICE" \
    --batch "$H64_ROWS" --window 9024 --faultshots \
    > "$W/results/gpu-h64.tsv" 2> "$W/results/gpu-h64.stderr"

: > "$W/results/gpu-d32.tsv.tmp"
: > "$W/results/gpu-d32.stderr.tmp"
while IFS= read -r nonce; do
    "$PK/run_ppgpu_exact.sh" "$PPGPU" "$CHECKPOINT" \
        --from "$nonce" --to "$nonce" --device "$DEVICE" \
        --batch 1 --window 9024 --faultshots \
        >> "$W/results/gpu-d32.tsv.tmp" 2>> "$W/results/gpu-d32.stderr.tmp"
done < "$PK/fixtures/d32.nonces"
mv "$W/results/gpu-d32.tsv.tmp" "$W/results/gpu-d32.tsv"
mv "$W/results/gpu-d32.stderr.tmp" "$W/results/gpu-d32.stderr"

cmp "$PK/fixtures/h64.expected.tsv" "$W/results/gpu-h64.tsv"
cmp "$PK/fixtures/d32.expected.tsv" "$W/results/gpu-d32.tsv"
cmp "$W/results/cpu-h64.tsv" "$W/results/gpu-h64.tsv"
cmp "$W/results/cpu-d32.tsv" "$W/results/gpu-d32.tsv"

perl "$PK/tools/compare_fault_masks.pl" \
    "$PK/fixtures/h64.evaluator.tsv" "$W/results/gpu-h64.tsv" \
    > "$W/receipts/H64.compare"
perl "$PK/tools/compare_fault_masks.pl" \
    "$PK/fixtures/d32.evaluator.tsv" "$W/results/gpu-d32.tsv" \
    > "$W/receipts/D32.compare"
grep -Fqx "rows=$H64_ROWS evaluator_faults=$H64_CLASSICAL_FAULTS predictor_faults=$H64_CLASSICAL_FAULTS exact=$H64_ROWS mismatches=0" \
    "$W/receipts/H64.compare"
grep -Fqx "rows=$D32_ROWS evaluator_faults=$D32_CLASSICAL_FAULTS predictor_faults=$D32_CLASSICAL_FAULTS exact=$D32_ROWS mismatches=0" \
    "$W/receipts/D32.compare"

test -z "$(gpu_compute_pids)" || {
    echo "GPU is not idle after parity" >&2
    exit 75
}
nvidia-smi -i "$DEVICE" --query-gpu=name,compute_cap,driver_version \
    --format=csv,noheader > "$W/receipts/GPU.post"
cmp "$W/receipts/GPU.pre" "$W/receipts/GPU.post"

for f in cpu-h64.tsv gpu-h64.tsv cpu-d32.tsv gpu-d32.tsv; do
    sha256sum "$W/results/$f"
done > "$W/receipts/PARITY.outputs.sha256"
outputs_sha=$(sha256sum "$W/receipts/PARITY.outputs.sha256" | awk '{print $1}')
build_sha=$(sha256sum "$W/receipts/BUILD.complete" | awk '{print $1}')
negative_sha=$(sha256sum "$W/receipts/NEGATIVES.complete" | awk '{print $1}')
{
    printf 'packet_id=%s\n' "$PACKET_ID"
    printf 'rows=%s\n' "$((H64_ROWS + D32_ROWS))"
    printf 'classical_faults=%s\n' "$((H64_CLASSICAL_FAULTS + D32_CLASSICAL_FAULTS))"
    printf 'cpu_cuda_complete_masks=byte-identical\n'
    printf 'trusted_evaluator_masks=byte-identical\n'
    printf 'build_receipt_sha256=%s\n' "$build_sha"
    printf 'negative_receipt_sha256=%s\n' "$negative_sha"
    printf 'output_manifest_sha256=%s\n' "$outputs_sha"
    printf 'gpu_idle_pre_post=yes\n'
    printf 'range_launched=no\n'
} > "$W/receipts/PARITY.complete.tmp"
mv "$W/receipts/PARITY.complete.tmp" "$W/receipts/PARITY.complete"
printf 'Q1272_SELECTOR_PARITY_OK rows=%s faults=%s outputs=%s\n' \
    "$((H64_ROWS + D32_ROWS))" "$((H64_CLASSICAL_FAULTS + D32_CLASSICAL_FAULTS))" \
    "$outputs_sha"
