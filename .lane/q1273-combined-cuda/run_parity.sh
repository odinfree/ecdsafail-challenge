#!/usr/bin/env bash
set -euo pipefail

if test "$#" -ne 2; then
    echo "usage: $0 /exact/ops.bin /built/workspace" >&2
    exit 64
fi

lane=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ops=$1
workspace=$2
# shellcheck disable=SC1091
. "$lane/HANDOFF.meta"
ppcpu="$workspace/bin/ppcpu"
ppgpu="$workspace/bin/ppgpu"
test -x "$ppcpu" && test -x "$ppgpu"
test -f "$workspace/receipts/BUILD.complete"
test ! -e "$workspace/receipts/PARITY.complete"
"$lane/selftest_failclosed.sh" "$ops" "$workspace"
mkdir -p "$workspace/results/classical" "$workspace/results/phase"

sha256_file() {
    sha256sum "$1" | awk '{print $1}'
}

run_pair() {
    local mode=$1 corpus=$2 nonce=$3 expected_count=$4 expected_sha=$5 outdir=$6
    PPF_OPS="$ops" "$ppcpu" "$mode" "$nonce" \
        >"$outdir/$corpus-$nonce.cpu" 2>"$outdir/$corpus-$nonce.cpu.stderr"
    PPF_OPS="$ops" "$ppgpu" "$mode" "$nonce" \
        >"$outdir/$corpus-$nonce.gpu" 2>"$outdir/$corpus-$nonce.gpu.stderr"
    cmp "$outdir/$corpus-$nonce.cpu" "$outdir/$corpus-$nonce.gpu"
    test "$(wc -l <"$outdir/$corpus-$nonce.gpu" | tr -d ' ')" = "$expected_count"
    test "$(sha256_file "$outdir/$corpus-$nonce.gpu")" = "$expected_sha"
}

classical_rows=0
while IFS=$'\t' read -r corpus nonce expected_count _mask_sha raw_sha; do
    test "$corpus" != '# corpus' || continue
    run_pair faultshots "$corpus" "$nonce" "$expected_count" "$raw_sha" \
        "$workspace/results/classical"
    classical_rows=$((classical_rows + 1))
done <"$lane/fixtures/CLASSICAL_FIXTURES.tsv"
test "$classical_rows" = "$CLASSICAL_ROWS"

phase_rows=0
while IFS=$'\t' read -r nonce _classical_count _raw_phase_count phase_count \
    _classical_sha phase_sha _classical_set _phase_set; do
    case "$nonce" in \#*) continue ;; esac
    run_pair phasefaultshots phase "$nonce" "$phase_count" "$phase_sha" \
        "$workspace/results/phase"
    phase_rows=$((phase_rows + 1))
done <"$lane/fixtures/PHASE_FIXTURES.tsv"
test "$phase_rows" = "$PHASE_ROWS"

inherited=100000045835813
for mode in faultshots phasefaultshots; do
    dir=classical
    test "$mode" = faultshots || dir=phase
    PPF_OPS="$ops" "$ppcpu" "$mode" "$inherited" \
        >"$workspace/results/$dir/inherited-repeat.cpu" \
        2>"$workspace/results/$dir/inherited-repeat.cpu.stderr"
    PPF_OPS="$ops" "$ppgpu" "$mode" "$inherited" \
        >"$workspace/results/$dir/inherited-repeat.gpu" \
        2>"$workspace/results/$dir/inherited-repeat.gpu.stderr"
    cmp "$workspace/results/$dir/inherited-$inherited.cpu" \
        "$workspace/results/$dir/inherited-repeat.cpu"
    cmp "$workspace/results/$dir/inherited-$inherited.cpu.stderr" \
        "$workspace/results/$dir/inherited-repeat.cpu.stderr"
    cmp "$workspace/results/$dir/inherited-$inherited.gpu" \
        "$workspace/results/$dir/inherited-repeat.gpu"
    cmp "$workspace/results/$dir/inherited-$inherited.gpu.stderr" \
        "$workspace/results/$dir/inherited-repeat.gpu.stderr"
done

find "$workspace/results" -type f -print0 | LC_ALL=C sort -z | \
    xargs -0 sha256sum >"$workspace/receipts/PARITY.outputs.sha256"
{
    printf 'packet_id=%s\ncombined_cpu_go_commit=%s\n' \
        "$PACKET_ID" "$COMBINED_CPU_GO_COMMIT"
    printf 'classical_rows=%s\nclassical_faults=%s\nphase_rows=%s\nclean_phase_faults=87\n' \
        "$CLASSICAL_ROWS" "$CLASSICAL_FAULTS" "$PHASE_ROWS"
    printf 'cpu_cuda_complete_masks=byte-identical\ntrusted_oracle_masks=byte-identical\n'
    printf 'deterministic_inherited_classical=yes\ndeterministic_inherited_phase=yes\n'
    printf 'output_manifest_sha256=%s\n' \
        "$(sha256_file "$workspace/receipts/PARITY.outputs.sha256")"
    printf 'scan_mode=disabled\nrange_launched=no\n'
} >"$workspace/receipts/PARITY.complete.tmp"
mv "$workspace/receipts/PARITY.complete.tmp" "$workspace/receipts/PARITY.complete"
printf 'Q1273_CUDA_PARITY_OK classical=%s faults=%s phase=%s clean_phase=87 range=no\n' \
    "$CLASSICAL_ROWS" "$CLASSICAL_FAULTS" "$PHASE_ROWS"
