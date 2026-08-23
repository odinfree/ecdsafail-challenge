#!/usr/bin/env bash
set -euo pipefail

lane=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
# shellcheck disable=SC1091
. "$lane/HANDOFF.meta"

die() {
    echo "verify-q1273-cuda-scaffold: FAIL: $*" >&2
    exit 1
}

sha256_file() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$1" | awk '{print $1}'
    else
        shasum -a 256 "$1" | awk '{print $1}'
    fi
}

test "$PACKET_ID" = q1273-combined-cuda-parity-v1 || die "packet id"
test "$STRUCTURAL_SOURCE_COMMIT" = 093d85d64de87aa5006a94868172f642daacf136 || die "source"
test "$CLASSICAL_GO_COMMIT" = 7b339f5d1fce6af6f3b3f360cb856b95326bb5ff || die "classical GO"
test "$QUBITS" = 1273 || die "qubits"
test "$OPS_COUNT" = 12933805 || die "operation count"
test "$OPS_SHA256" = ee6448dbb23aa877123733724b109266e584f1ba14abf5c38b43b9ab6aa26cd1 || die "operation hash"
test "$STATE_DIGEST" = 2148e09f4c4293b2 || die "state digest"
test "$SCAN_MODE" = DISABLED || die "scan state"
test "$RANGE_AUTHORIZED" = NO || die "range state"

classical="$lane/fixtures/CLASSICAL_FIXTURES.tsv"
phase="$lane/fixtures/PHASE_FIXTURES.tsv"
test "$(sha256_file "$classical")" = "$CLASSICAL_FIXTURES_SHA256" || die "classical fixture hash"
test "$(sha256_file "$phase")" = "$PHASE_FIXTURES_SHA256" || die "phase fixture hash"

awk -F '\t' -v rows="$CLASSICAL_ROWS" -v faults="$CLASSICAL_FAULTS" '
BEGIN { total=0; fault_total=0 }
NR == 1 {
    if ($1 != "# corpus" || $2 != "nonce" || $3 != "expected_count" ||
        $4 != "mask_sha256" || $5 != "raw_sha256") exit 10
    next
}
NF != 5 || $1 !~ /^(inherited|h64|d16|d32)$/ || $2 !~ /^[1-9][0-9]*$/ ||
$3 !~ /^[0-9]+$/ || $4 !~ /^[0-9a-f]+$/ || length($4) != 64 ||
$5 !~ /^[0-9a-f]+$/ || length($5) != 64 { exit 11 }
{ seen[$2]++; total++; fault_total += $3; corpus[$1]++ }
END {
    for (nonce in seen) if (seen[nonce] != 1) exit 12
    if (total != rows || fault_total != faults) exit 13
    if (corpus["inherited"] != 1 || corpus["h64"] != 64 ||
        corpus["d16"] != 16 || corpus["d32"] != 32) exit 14
}' "$classical" || die "classical fixture structure"

awk -F '\t' -v rows="$PHASE_ROWS" '
BEGIN { total=0; clean=0 }
/^#/ { next }
NF != 8 || $1 !~ /^[1-9][0-9]*$/ || $2 !~ /^[0-9]+$/ ||
$3 !~ /^[0-9]+$/ || $4 !~ /^[0-9]+$/ ||
$5 !~ /^[0-9a-f]+$/ || length($5) != 64 ||
$6 !~ /^[0-9a-f]+$/ || length($6) != 64 { exit 20 }
{ seen[$1]++; total++; clean += $4 }
END {
    for (nonce in seen) if (seen[nonce] != 1) exit 21
    if (total != rows || clean != 87) exit 22
}' "$phase" || die "phase fixture structure"

cuda="$lane/src/ppgpu_parity.cu"
test -f "$cuda" || die "missing CUDA source"
rg -q 'mode == "scan"' "$cuda" || die "missing explicit disabled scan guard"
rg -q 'range=disabled' "$cuda" || die "missing range-disabled receipt"
rg -q 'faultshots' "$cuda" || die "missing classical selector"
rg -q 'phasefaultshots' "$cuda" || die "missing phase selector"
if rg -n -- '--from|--to|--screen|--range|scan_kernel|survivor_kernel' "$cuda" >/dev/null; then
    die "range or incomplete-screen implementation present"
fi

for script in "$lane"/*.sh; do
    bash -n "$script" || die "shell syntax: $script"
done

printf 'Q1273_CUDA_SCAFFOLD_OK classical=%s/%s faults=%s phase=%s/17 scan=disabled\n' \
    "$CLASSICAL_ROWS" "$CLASSICAL_ROWS" "$CLASSICAL_FAULTS" "$PHASE_ROWS"
