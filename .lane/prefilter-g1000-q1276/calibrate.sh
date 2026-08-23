#!/bin/bash
# Run one predeclared qualification interval. This is deliberately not a
# general range runner: expanding either interval requires a new reviewed edit.
set -euo pipefail

if [ "$#" -ne 3 ]; then
  echo "usage: $0 START END MAX_FAULTS" >&2
  exit 2
fi

S=$1
E=$2
M=$3
case "$S:$E:$M" in
  270000000000:270128000000:0) ;;
  270128000000:270130000000:3) ;;
  *) echo "refusing an undeclared calibration interval" >&2; exit 2 ;;
esac

W=$(cd "$(dirname "$0")" && pwd)
RUN=$W/runs/$S-$E-m$M
OPS_SHA=d1461959eac52b19b644f1f97a3b44a3ea249a109f14a406d19e872cd17c5422

test "$(sha256sum "$W/ops.bin" | awk '{print $1}')" = "$OPS_SHA"
test -f "$W/FINGERPRINTS"
test -f "$W/PARITY.complete"
test ! -e "$RUN"

HOST_PROOFS=0
test -f "$W/BORROW.complete" && HOST_PROOFS=$((HOST_PROOFS+1))
test -f "$W/DEDICATED.complete" && HOST_PROOFS=$((HOST_PROOFS+1))
test "$HOST_PROOFS" -eq 1

DIGEST=$(sed -n 's/^state_digest=\([0-9a-f]\{16\}\)$/\1/p' "$W/FINGERPRINTS")
test "${#DIGEST}" -eq 16

# No other scanner may share this GPU. Inspect exact executables so this guard
# does not match its own command line.
for proc in /proc/[0-9]*; do
  exe=$(readlink "$proc/exe" 2>/dev/null || true)
  case "$exe" in
    "$W/ppgpu"|/workspace/ev-g1000/ppgpu-g1000|/workspace/ev-cc20/ppgpu-cc20)
      echo "another GPU scanner is active" >&2
      exit 75
      ;;
  esac
done
GPU_APPS=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader | sed '/^$/d')
test -z "$GPU_APPS"

mkdir -p "$W/runs"
mkdir "$RUN"
exec 9>"$W/calibration.lock"
flock -n 9

set +e
timeout --signal=TERM --kill-after=15s 14400 \
  "$W/ppgpu" --ops "$W/ops.bin" --from "$S" --to "$E" \
    --max-faults "$M" --threads-block 128 --blocks 512 --comb-bits 16 \
  > "$RUN/counts.tsv.tmp" 2> "$RUN/scan.stderr.tmp"
rc=$?
set -e
test "$rc" -eq 0

grep -Fq "total_ops=12929346" "$RUN/scan.stderr.tmp"
grep -Fq "state_digest=$DIGEST" "$RUN/scan.stderr.tmp"
grep -Fq "\"from\":$S,\"to\":$E,\"count\":$((E-S))" "$RUN/scan.stderr.tmp"
grep -Fq "\"max_faults\":$M" "$RUN/scan.stderr.tmp"
grep -Fq "\"state_digest\":\"$DIGEST\"" "$RUN/scan.stderr.tmp"
test "$(grep -c '^TELEMETRY ' "$RUN/scan.stderr.tmp")" -eq 1

awk -v s="$S" -v e="$E" -v m="$M" '
  NF != 2 || $1 !~ /^[0-9]+$/ || $2 !~ /^pred_cls=[0-9]+$/ ||
  $1+0 < s || $1+0 >= e || seen[$1]++ { bad=1; next }
  { split($2, a, "="); if (a[2]+0 > m) bad=1 }
  END { exit bad }
' "$RUN/counts.tsv.tmp"

actual=$(wc -l < "$RUN/counts.tsv.tmp" | tr -d ' ')
reported=$(sed -n 's/.*"survivors":\([0-9][0-9]*\).*/\1/p' "$RUN/scan.stderr.tmp")
test "$actual" = "$reported"

GPU_APPS_AFTER=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader | sed '/^$/d')
test -z "$GPU_APPS_AFTER"

mv "$RUN/counts.tsv.tmp" "$RUN/counts.tsv"
mv "$RUN/scan.stderr.tmp" "$RUN/scan.stderr"
printf '%s\t%s\t%s\t%s\n' "$S" "$E" "$M" "$actual" \
  > "$RUN/calibration.complete.tmp"
mv "$RUN/calibration.complete.tmp" "$RUN/calibration.complete"
printf 'CALIBRATION_COMPLETE range=%s-%s max_faults=%s retained=%s\n' \
  "$S" "$E" "$M" "$actual"
