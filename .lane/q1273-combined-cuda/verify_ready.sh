#!/usr/bin/env bash
set -euo pipefail

lane=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
root=$(CDPATH= cd -- "$lane/../.." && pwd)
# shellcheck disable=SC1091
. "$lane/HANDOFF.meta"

die() {
    echo "verify-q1273-cuda-ready: FAIL: $*" >&2
    exit 1
}

sha256_file() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$1" | awk '{print $1}'
    else
        shasum -a 256 "$1" | awk '{print $1}'
    fi
}

"$lane/verify_scaffold.sh" >/dev/null
test "$PACKET_STATE" = READY_LOCAL_PARITY || die "packet is not ready"
for value in "$COMBINED_CPU_GO_COMMIT" "$COMBINED_HOST_SHA256" \
    "$COMBINED_MODEL_SHA256" "$COMBINED_CPU_SHA256" "$CUDA_SOURCE_SHA256"; do
    test "$value" != UNSEALED || die "unsealed identity"
done

git -C "$root" merge-base --is-ancestor "$COMBINED_CPU_GO_COMMIT" HEAD || \
    die "combined GO commit is not integrated"
test "$(sha256_file "$root/.lane/q1273-predictor/src/pp_host.h")" = \
    "$COMBINED_HOST_SHA256" || die "host source hash"
test "$(sha256_file "$root/.lane/q1273-predictor/src/pp_model.h")" = \
    "$COMBINED_MODEL_SHA256" || die "model source hash"
test "$(sha256_file "$root/.lane/q1273-predictor/src/ppcpu.cpp")" = \
    "$COMBINED_CPU_SHA256" || die "CPU source hash"
test "$(sha256_file "$root/.lane/q1273-phase/src/pp_phase_schedule.h")" = \
    "$PHASE_HEADER_SHA256" || die "phase header hash"
test "$(sha256_file "$lane/src/ppgpu_parity.cu")" = "$CUDA_SOURCE_SHA256" || \
    die "CUDA source hash"

binding="$lane/src/SEALED_BINDING.h"
rg -Fqx '#define Q1273_CUDA_HANDOFF_SEALED 1' "$binding" || die "compile barrier"
rg -Fqx "#define Q1273_COMBINED_CPU_GO_COMMIT \"$COMBINED_CPU_GO_COMMIT\"" "$binding" || \
    die "binding commit"
rg -Fqx "#define Q1273_COMBINED_HOST_SHA256 \"$COMBINED_HOST_SHA256\"" "$binding" || \
    die "binding host hash"
rg -Fqx "#define Q1273_COMBINED_MODEL_SHA256 \"$COMBINED_MODEL_SHA256\"" "$binding" || \
    die "binding model hash"
rg -Fqx "#define Q1273_COMBINED_CPU_SHA256 \"$COMBINED_CPU_SHA256\"" "$binding" || \
    die "binding CPU hash"

test ! -e "$root/ops.bin" || die "ops.bin must remain outside Git worktree"
printf 'Q1273_CUDA_LOCAL_READY combined=%s cuda=%s scan=disabled range=no\n' \
    "$COMBINED_CPU_GO_COMMIT" "$CUDA_SOURCE_SHA256"
