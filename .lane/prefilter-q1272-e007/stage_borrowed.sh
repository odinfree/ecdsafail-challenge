#!/bin/bash
# Incumbent-preserving fixture parity. Deliberately unarmed: the exact
# incumbent assignment, executable, ops stream, and coverage log must be
# frozen in a later reviewed commit before this script can run.
set -euo pipefail

readonly BORROW_GUARD_ARMED=0
readonly INC_ROOT=/workspace/COMMIT_EXACT_INCUMBENT_ROOT
readonly INC_BIN=/workspace/COMMIT_EXACT_INCUMBENT_BINARY
readonly INC_OPS=/workspace/COMMIT_EXACT_INCUMBENT_OPS
readonly INC_LOG=/workspace/COMMIT_EXACT_INCUMBENT_LOG
readonly INC_BIN_SHA=COMMIT_EXACT_INCUMBENT_BINARY_SHA256
readonly INC_OPS_SHA=COMMIT_EXACT_INCUMBENT_OPS_SHA256
readonly ASSIGN_FROM=0
readonly ASSIGN_TO=0
readonly CHUNK_SIZE=0

if [ "$BORROW_GUARD_ARMED" -ne 1 ]; then
  echo 'borrowed parity is unarmed; freeze exact incumbent guards in a reviewed commit' >&2
  exit 78
fi

W=$(cd "$(dirname "$0")" && pwd)
readonly COMMON_SHA=94950be99c0bcafc20373c9d29ebc142679cb026151d1d5558a3fea3a2b43bd9
test "$(sha256sum "$W/stage_common.sh" | awk '{print $1}')" = "$COMMON_SHA"
# shellcheck source=stage_common.sh
source "$W/stage_common.sh"

test "$W" = "$EXPECTED_STAGE_ROOT"
test "$INC_ROOT" != "$W"
test "$ASSIGN_FROM" -lt "$ASSIGN_TO"
test "$CHUNK_SIZE" -gt 0
test "$INC_BIN" = "$INC_ROOT/${INC_BIN##*/}"
test "$INC_OPS" = "$INC_ROOT/${INC_OPS##*/}"
test "$INC_LOG" = "$INC_ROOT/${INC_LOG##*/}"
exec 9>"$W/stage-borrowed.lock"
flock -n 9

audit_incumbent() {
  local incumbent_pid='' proc exe cmd active_from active_to gpu_pids
  test "$(stage_sha "$INC_BIN")" = "$INC_BIN_SHA"
  test "$(stage_sha "$INC_OPS")" = "$INC_OPS_SHA"
  for proc in /proc/[0-9]*; do
    exe=$(readlink "$proc/exe" 2>/dev/null || true)
    case "$exe" in
      "$INC_BIN")
        test -z "$incumbent_pid"
        incumbent_pid=${proc##*/}
        ;;
      "$W/ppgpu"|"$W/ppcpu")
        echo 'candidate process already active' >&2
        return 75
        ;;
    esac
  done
  test -n "$incumbent_pid"
  cmd=$(tr '\000' ' ' < "/proc/$incumbent_pid/cmdline")
  case "$cmd" in
    "$INC_BIN "*) ;;
    *) return 75 ;;
  esac
  printf '%s\n' "$cmd" | grep -Fq -- "--ops $INC_OPS"
  active_from=$(printf '%s\n' "$cmd" | \
    sed -n 's/.*--from \([0-9][0-9]*\).*/\1/p')
  active_to=$(printf '%s\n' "$cmd" | \
    sed -n 's/.*--to \([0-9][0-9]*\).*/\1/p')
  test "$active_from" -ge "$ASSIGN_FROM"
  test "$active_to" -le "$ASSIGN_TO"
  test $((active_to - active_from)) -eq "$CHUNK_SIZE"
  gpu_pids=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader | \
    sed '/^$/d' | tr -d ' ')
  test "$gpu_pids" = "$incumbent_pid"
  printf '%s %s %s\n' "$active_from" "$active_to" "$incumbent_pid"
}

freeze_coverage() {
  local out=$1
  sed -n 's/^TELEMETRY {"from":\([0-9][0-9]*\),"to":\([0-9][0-9]*\),.*/\1 \2/p' \
    "$INC_LOG" | awk -v lo="$ASSIGN_FROM" -v hi="$ASSIGN_TO" \
    '$1 >= lo && $2 <= hi' | sort -n -k1,1 -k2,2 -u > "$out"
  awk -v start="$ASSIGN_FROM" -v chunk="$CHUNK_SIZE" '
    BEGIN { cur=start }
    $1 != cur || $2-$1 != chunk { exit 1 }
    { cur=$2; rows++ }
    END { if (rows < 1) exit 1; printf "%s %s\n", cur, rows }
  ' "$out"
}

COVERAGE_BEFORE=$(mktemp)
COVERAGE_AFTER=$(mktemp)
trap 'rm -f "$COVERAGE_BEFORE" "$COVERAGE_AFTER"' EXIT
read -r ACTIVE_FROM_BEFORE ACTIVE_TO_BEFORE ACTIVE_PID_BEFORE < <(audit_incumbent)
read -r COVERAGE_END_BEFORE COVERAGE_ROWS_BEFORE < <(freeze_coverage "$COVERAGE_BEFORE")
test "$COVERAGE_END_BEFORE" = "$ACTIVE_FROM_BEFORE"
COVERAGE_SHA_BEFORE=$(stage_sha "$COVERAGE_BEFORE")

case "$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader | tr -d '\r')" in
  8.9) CUDA_ARCH=89 ;;
  12.0) CUDA_ARCH=120 ;;
  *) echo 'unsupported borrowed GPU compute capability' >&2; exit 2 ;;
esac
stage_execute_parity_only "$W" "$CUDA_ARCH"

test "$(stage_sha "$INC_BIN")" = "$INC_BIN_SHA"
test "$(stage_sha "$INC_OPS")" = "$INC_OPS_SHA"
read -r ACTIVE_FROM_AFTER ACTIVE_TO_AFTER ACTIVE_PID_AFTER < <(audit_incumbent)
read -r COVERAGE_END_AFTER COVERAGE_ROWS_AFTER < <(freeze_coverage "$COVERAGE_AFTER")
test "$COVERAGE_END_AFTER" = "$ACTIVE_FROM_AFTER"
test "$COVERAGE_END_AFTER" -ge "$COVERAGE_END_BEFORE"
COVERAGE_SHA_AFTER=$(stage_sha "$COVERAGE_AFTER")

{
  printf 'mode=borrowed incumbent_signals=0 scanner_launches=0\n'
  printf 'inc_bin_sha256=%s inc_ops_sha256=%s\n' "$INC_BIN_SHA" "$INC_OPS_SHA"
  printf 'assignment=%s-%s chunk=%s\n' "$ASSIGN_FROM" "$ASSIGN_TO" "$CHUNK_SIZE"
  printf 'before=%s-%s rows=%s pid=%s coverage_sha256=%s\n' \
    "$ACTIVE_FROM_BEFORE" "$ACTIVE_TO_BEFORE" "$COVERAGE_ROWS_BEFORE" \
    "$ACTIVE_PID_BEFORE" "$COVERAGE_SHA_BEFORE"
  printf 'after=%s-%s rows=%s pid=%s coverage_sha256=%s\n' \
    "$ACTIVE_FROM_AFTER" "$ACTIVE_TO_AFTER" "$COVERAGE_ROWS_AFTER" \
    "$ACTIVE_PID_AFTER" "$COVERAGE_SHA_AFTER"
} > "$W/BORROW.complete.tmp"
mv "$W/BORROW.complete.tmp" "$W/BORROW.complete"
printf 'BORROWED_PARITY_COMPLETE state_digest=%s scanner_launches=0 signals=0\n' \
  "$STATE_DIGEST"
