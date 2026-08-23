#!/bin/bash
# Predeclared shape for a future tolerant pilot. It is intentionally unarmed
# and cannot run with the parity binaries, whose range entry points are
# compiled disabled.
set -euo pipefail

readonly PILOT_GUARD_ARMED=0
readonly PILOT_FROM=0
readonly PILOT_TO=0
readonly PILOT_MAX_FAULTS=0
readonly PROVEN_GLOBAL_OVERCOUNT_BOUND=0
readonly OVERCOUNT_PROOF_SHA=COMMIT_EXACT_OVERCOUNT_PROOF_SHA256

if [ "$PILOT_GUARD_ARMED" -ne 1 ]; then
  echo 'tolerant pilot disabled: global fail-closed overcount bound is unproven' >&2
  exit 78
fi

W=$(cd "$(dirname "$0")" && pwd)
test "$W" = /workspace/ev-q1272-e007-ea93a131
test "$PROVEN_GLOBAL_OVERCOUNT_BOUND" -ge 1
test "$PROVEN_GLOBAL_OVERCOUNT_BOUND" -le 3
test "$PILOT_MAX_FAULTS" -ge "$PROVEN_GLOBAL_OVERCOUNT_BOUND"
test "$PILOT_MAX_FAULTS" -le 3
test "$PILOT_FROM" -lt "$PILOT_TO"
test "$(sha256sum "$W/OVERCOUNT_BOUND.complete" | awk '{print $1}')" = \
  "$OVERCOUNT_PROOF_SHA"
grep -Fqx 'source_commit=ea93a131e2bc488bff6fa12010d1f3606c7771b0' \
  "$W/OVERCOUNT_BOUND.complete"
grep -Fqx "global_false_positive_overcount_max=$PROVEN_GLOBAL_OVERCOUNT_BOUND" \
  "$W/OVERCOUNT_BOUND.complete"
grep -Fqx 'global_false_negative_count=0' "$W/OVERCOUNT_BOUND.complete"
test -f "$W/PARITY.complete"
test -f "$W/FINGERPRINTS"
test -f "$W/SCAN-ENABLED.complete"

HOST_PROOFS=0
test -f "$W/BORROW.complete" && HOST_PROOFS=$((HOST_PROOFS + 1))
test -f "$W/DEDICATED.complete" && HOST_PROOFS=$((HOST_PROOFS + 1))
test "$HOST_PROOFS" -eq 1

# A later reviewed commit must replace the zero placeholders, bind an exact
# proof receipt and exact interval, and produce a separately hashed
# scan-enabled binary. If those gates close, every true zero has predicted
# count <= the proven bound and is therefore retained for unchanged full
# 9,024-shot evaluation.
exec "$W/ppgpu-scan-enabled" --ops "$W/ops.bin" \
  --from "$PILOT_FROM" --to "$PILOT_TO" --max-faults "$PILOT_MAX_FAULTS" \
  --threads-block 128 --blocks 512 --comb-bits 16
