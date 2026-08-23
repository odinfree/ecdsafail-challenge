#!/bin/bash
# One-shot drain of the obsolete cc20 producer. The current ppgpu child and
# confirmer are protected: this script signals only the exact supervisor and
# gscreen parent snapshots declared below, then waits for the child to finish.
set -euo pipefail

W=$(cd "$(dirname "$0")" && pwd)
INC=/workspace/ev-cc20
test "$W" = /workspace/ev-g1000-q1276-0b6ac181
test ! -e "$W/DRAINED_AT"
exec 9>"$W/drain.lock"
flock -n 9

SUP_PID=589965
SUP_START=125592491
GSCREEN_PID=590319
GSCREEN_START=125595502
WRAPPER_PID=2719612
WRAPPER_START=128016524
PPGPU_PID=2719613
PPGPU_START=128016524
CONFIRM_PID=590322
CONFIRM_START=125595502
ACTIVE_FROM=189450000000
ACTIVE_TO=189500000000

test "$(md5sum "$INC/ops.bin" | awk '{print $1}')" = \
  091a13089a3e96dd499f296f0ef1740f
test "$(sha256sum "$INC/ppgpu-cc20" | awk '{print $1}')" = \
  f75eb8080bcf19617082f9ff02f6291d2ddf5fe9138c40e78b4a0128ad44f183
test "$(sha256sum "$INC/supervisor-gpu.sh" | awk '{print $1}')" = \
  26630d0618449c70560a6e17822df2c328c18bdce5c8e9398020a3d5f7ddbc22
test "$(sha256sum "$INC/gpu_screen_loop.sh" | awk '{print $1}')" = \
  b7259b46408781dc83addbf76064ed1ac2d42ce9a821c9cf204b63e763cb39e6
test "$(sha256sum "$INC/confirm_loop.sh" | awk '{print $1}')" = \
  6308ce9e96f0e78a2471b266b04d921b16977c760f936c4d51cd8fa93e66bc94

pid_start() {
  awk '{print $22}' "/proc/$1/stat" 2>/dev/null
}

pid_ppid() {
  awk '{print $4}' "/proc/$1/stat" 2>/dev/null
}

pid_cmd() {
  tr '\000' ' ' < "/proc/$1/cmdline" 2>/dev/null
}

assert_bash_role() {
  local pid=$1 start=$2 ppid=$3 token=$4
  test "$(pid_start "$pid")" = "$start"
  test "$(pid_ppid "$pid")" = "$ppid"
  test "$(readlink "/proc/$pid/cwd")" = "$INC"
  test "$(readlink "/proc/$pid/exe")" = /usr/bin/bash
  pid_cmd "$pid" | grep -Fq "$token"
}

assert_ppgpu() {
  test "$(pid_start "$PPGPU_PID")" = "$PPGPU_START"
  test "$(pid_ppid "$PPGPU_PID")" = "$WRAPPER_PID"
  test "$(readlink "/proc/$PPGPU_PID/cwd")" = "$INC"
  test "$(readlink "/proc/$PPGPU_PID/exe")" = "$INC/ppgpu-cc20"
  test "$(pid_cmd "$PPGPU_PID")" = \
    "./ppgpu-cc20 --ops $INC/ops.bin --from $ACTIVE_FROM --to $ACTIVE_TO "
}

assert_bash_role "$SUP_PID" "$SUP_START" 1 './supervisor-gpu.sh '
assert_bash_role "$GSCREEN_PID" "$GSCREEN_START" "$SUP_PID" \
  './gpu_screen_loop.sh 189000000000 190000000000 '
assert_bash_role "$WRAPPER_PID" "$WRAPPER_START" "$GSCREEN_PID" \
  './gpu_screen_loop.sh 189000000000 190000000000 '
assert_bash_role "$CONFIRM_PID" "$CONFIRM_START" "$SUP_PID" './confirm_loop.sh '
assert_ppgpu
test "$(cat "$INC/gscreen.pid")" = "$GSCREEN_PID"
test "$(cat "$INC/confirm.pid")" = "$CONFIRM_PID"

GPU_PIDS=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader | \
  sed '/^$/d' | tr -d ' ')
test "$GPU_PIDS" = "$PPGPU_PID"

pending_count() {
  awk '
    FNR == NR { if ($1 ~ /^[0-9]+$/) done[$1]=1; next }
    $1 ~ /^[0-9]+$/ && !done[$1] && !seen[$1]++ { pending++ }
    END { print pending+0 }
  ' "$INC/confirmed.txt" "$INC/survivors.tsv"
}

freeze_file() {
  local path=$1 prefix=$2
  if [ -e "$path" ]; then
    test -f "$path"
    stat -c '%i %s' "$path" > "$prefix.meta"
    sha256sum "$path" | awk '{print $1}' > "$prefix.sha"
  else
    printf 'ABSENT 0\n' > "$prefix.meta"
    printf 'ABSENT\n' > "$prefix.sha"
  fi
}

assert_append_only() {
  local path=$1 prefix=$2 inode size prior_sha current_prefix_sha
  read inode size < "$prefix.meta"
  if [ "$inode" = ABSENT ]; then
    test ! -e "$path" || test -f "$path"
    return
  fi
  test -f "$path"
  test "$(stat -c %i "$path")" = "$inode"
  test "$(stat -c %s "$path")" -ge "$size"
  prior_sha=$(cat "$prefix.sha")
  current_prefix_sha=$(head -c "$size" "$path" | sha256sum | awk '{print $1}')
  test "$current_prefix_sha" = "$prior_sha"
}

SNAP=$(mktemp -d)
trap 'rm -rf "$SNAP"' EXIT
for name in survivors.tsv confirmed.txt clean.tsv confirm-fails.tsv confirm-errors.tsv gscreen.log; do
  freeze_file "$INC/$name" "$SNAP/$name"
done
PENDING_BEFORE=$(pending_count)
LOG_SIZE_BEFORE=$(awk '{print $2}' "$SNAP/gscreen.log.meta")

# Signal exactly the two producer parents. Never signal the wrapper, ppgpu,
# confirmer, or any confirmer child.
kill -TERM "$SUP_PID"
kill -TERM "$GSCREEN_PID"
for _ in 1 2 3 4 5; do
  if ! kill -0 "$SUP_PID" 2>/dev/null && ! kill -0 "$GSCREEN_PID" 2>/dev/null; then
    break
  fi
  sleep 1
done
! kill -0 "$SUP_PID" 2>/dev/null
! kill -0 "$GSCREEN_PID" 2>/dev/null
assert_ppgpu
test "$(pid_start "$CONFIRM_PID")" = "$CONFIRM_START"
test "$(readlink "/proc/$CONFIRM_PID/cwd")" = "$INC"

# Wait for the active child to finish naturally. Its identity must not drift
# while it exists. Each poll is short so the control channel stays responsive.
while kill -0 "$PPGPU_PID" 2>/dev/null; do
  assert_ppgpu
  sleep 10
done

for _ in 1 2 3 4 5; do
  if ! kill -0 "$WRAPPER_PID" 2>/dev/null; then break; fi
  sleep 1
done
! kill -0 "$WRAPPER_PID" 2>/dev/null

test "$(pid_start "$CONFIRM_PID")" = "$CONFIRM_START"
test "$(readlink "/proc/$CONFIRM_PID/cwd")" = "$INC"
test "$(readlink "/proc/$CONFIRM_PID/exe")" = /usr/bin/bash
pid_cmd "$CONFIRM_PID" | grep -Fq './confirm_loop.sh '

for name in survivors.tsv confirmed.txt clean.tsv confirm-fails.tsv confirm-errors.tsv gscreen.log; do
  assert_append_only "$INC/$name" "$SNAP/$name"
done

NEW_LOG=$SNAP/new.log
tail -c "+$((LOG_SIZE_BEFORE+1))" "$INC/gscreen.log" > "$NEW_LOG"
test "$(grep -c '^TELEMETRY ' "$NEW_LOG")" -eq 1
grep -Fq "\"from\":$ACTIVE_FROM,\"to\":$ACTIVE_TO,\"count\":50000000" "$NEW_LOG"
grep -Fq '"state_digest":"03d9e2e37c73fd94"' "$NEW_LOG"

COVERAGE=$SNAP/coverage
sed -n 's/^TELEMETRY {"from":\([0-9][0-9]*\),"to":\([0-9][0-9]*\),.*/\1 \2/p' \
  "$INC/gscreen.log" | awk '$1 >= 189000000000 && $2 <= 189500000000' | \
  sort -n -k1,1 -k2,2 -u > "$COVERAGE"
awk '
  BEGIN { cur=189000000000; end=189500000000; chunk=50000000 }
  $1 != cur || $2-$1 != chunk { exit 1 }
  { cur=$2; rows++ }
  END { if (rows != 10 || cur != end) exit 1 }
' "$COVERAGE"
COVERAGE_SHA=$(sha256sum "$COVERAGE" | awk '{print $1}')

test -z "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader | sed '/^$/d')"
PENDING_AFTER=$(pending_count)
UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)
{
  printf 'utc=%s\n' "$UTC"
  printf 'assignment=189000000000-190000000000\n'
  printf 'drained_chunk=%s-%s\n' "$ACTIVE_FROM" "$ACTIVE_TO"
  printf 'coverage=189000000000-189500000000 chunks=10 sha256=%s\n' "$COVERAGE_SHA"
  printf 'supervisor_pid=%s start=%s signaled=TERM\n' "$SUP_PID" "$SUP_START"
  printf 'gscreen_pid=%s start=%s signaled=TERM\n' "$GSCREEN_PID" "$GSCREEN_START"
  printf 'ppgpu_pid=%s start=%s finish=natural\n' "$PPGPU_PID" "$PPGPU_START"
  printf 'confirmer_pid=%s start=%s preserved=1\n' "$CONFIRM_PID" "$CONFIRM_START"
  printf 'pending_before=%s pending_after=%s gpu_apps=0\n' \
    "$PENDING_BEFORE" "$PENDING_AFTER"
} > "$W/DRAINED_AT.tmp"
mv "$W/DRAINED_AT.tmp" "$W/DRAINED_AT"
printf 'DRAIN_COMPLETE chunk=%s-%s coverage_sha256=%s\n' \
  "$ACTIVE_FROM" "$ACTIVE_TO" "$COVERAGE_SHA"
