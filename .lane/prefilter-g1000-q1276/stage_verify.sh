#!/bin/bash
# Preserve one completed incumbent chunk, build the exact model, and prove
# bounded CPU/CUDA fixture equality without signalling or overwriting the
# incumbent. Run only in the isolated candidate workspace after source and
# ops.bin have been copied there.
set -euo pipefail

W=$(cd "$(dirname "$0")" && pwd)
INC=/workspace/ev-cc20
test "$W" = /workspace/ev-g1000-q1276-0b6ac181
test "$(md5sum "$INC/ops.bin" | awk '{print $1}')" = 091a13089a3e96dd499f296f0ef1740f
test "$(sha256sum "$INC/ppgpu-cc20" | awk '{print $1}')" = \
  f75eb8080bcf19617082f9ff02f6291d2ddf5fe9138c40e78b4a0128ad44f183

audit_incumbent() {
  local incumbent_pid="" exe cmd active_from active_to gpu_pids
  for proc in /proc/[0-9]*; do
    exe=$(readlink "$proc/exe" 2>/dev/null || true)
    case "$exe" in
      "$INC/ppgpu-cc20")
        test -z "$incumbent_pid"
        incumbent_pid=${proc##*/}
        ;;
      "$W/ppgpu"|/workspace/ev-g1000/ppgpu-g1000|/workspace/ev-peak1275-353414a/ppgpu)
        echo "unexpected GPU scanner active" >&2
        return 75
        ;;
    esac
  done
  test -n "$incumbent_pid"
  cmd=$(tr '\000' ' ' < "/proc/$incumbent_pid/cmdline")
  active_from=$(printf '%s\n' "$cmd" | sed -n 's/.*--from \([0-9][0-9]*\).*/\1/p')
  active_to=$(printf '%s\n' "$cmd" | sed -n 's/.*--to \([0-9][0-9]*\).*/\1/p')
  test "$active_from" -ge 189000000000
  test "$active_to" -le 190000000000
  test $((active_to-active_from)) -eq 50000000
  gpu_pids=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader | \
    sed '/^$/d' | tr -d ' ')
  test "$gpu_pids" = "$incumbent_pid"
  printf '%s %s %s\n' "$active_from" "$active_to" "$incumbent_pid"
}

freeze_coverage() {
  local out=$1
  sed -n 's/^TELEMETRY {"from":\([0-9][0-9]*\),"to":\([0-9][0-9]*\),.*/\1 \2/p' \
    "$INC/gscreen.log" | awk '$1 >= 189000000000 && $2 <= 190000000000' | \
    sort -n -k1,1 -k2,2 -u > "$out"
  awk '
    BEGIN { cur=189000000000; chunk=50000000 }
    $1 != cur || $2-$1 != chunk { exit 1 }
    { cur=$2; rows++ }
    END { if (rows < 1) exit 1; printf "%s %s\n", cur, rows }
  ' "$out"
}

COVERAGE_BEFORE=$(mktemp)
COVERAGE_AFTER=$(mktemp)
trap 'rm -f "$COVERAGE_BEFORE" "$COVERAGE_AFTER"' EXIT
read ACTIVE_FROM_BEFORE ACTIVE_TO_BEFORE ACTIVE_PID_BEFORE < <(audit_incumbent)
read COVERAGE_END_BEFORE COVERAGE_ROWS_BEFORE < <(freeze_coverage "$COVERAGE_BEFORE")
test "$COVERAGE_END_BEFORE" = "$ACTIVE_FROM_BEFORE"
COVERAGE_SHA_BEFORE=$(sha256sum "$COVERAGE_BEFORE" | awk '{print $1}')

test "$(sha256sum "$W/ops.bin" | awk '{print $1}')" = \
  d1461959eac52b19b644f1f97a3b44a3ea249a109f14a406d19e872cd17c5422
test "$(sha256sum "$W/src/pp_host.h" | awk '{print $1}')" = \
  257236aa61cafb8ba056271b7bd80d4144fb334bd31b11ae6b86405701c1c751
test "$(sha256sum "$W/src/pp_model.h" | awk '{print $1}')" = \
  4d3d748a3350851e263f9f3f180e6405b1240514dcff7a672b773751bbcf330e
test "$(sha256sum "$W/src/ppcpu.cpp" | awk '{print $1}')" = \
  8bbfad7fa8fa3efe0fa92805cf5ec7f41732edebceaa81ff2e8a7c9f05b9e6eb
test "$(sha256sum "$W/src/ppgpu.cu" | awk '{print $1}')" = \
  8fe6247eeb680ffad96423947909afc88321913bc039233dd85e18733b6a8fb3

"$W/build.sh"
mkdir "$W/fixtures"
for nonce in 135608492183 0 7 2500069332; do
  PPF_OPS="$W/ops.bin" "$W/ppcpu" breakdown "$nonce" \
    > "$W/fixtures/cpu.$nonce"
  "$W/ppgpu" --ops "$W/ops.bin" --breakdown "$nonce" --comb-bits 8 \
    > "$W/fixtures/gpu8.$nonce" 2> "$W/fixtures/gpu8.$nonce.stderr"
  "$W/ppgpu" --ops "$W/ops.bin" --breakdown "$nonce" --comb-bits 16 \
    > "$W/fixtures/gpu16.$nonce" 2> "$W/fixtures/gpu16.$nonce.stderr"
  cmp "$W/fixtures/cpu.$nonce" "$W/fixtures/gpu8.$nonce"
  cmp "$W/fixtures/cpu.$nonce" "$W/fixtures/gpu16.$nonce"
done

DIGEST=$(sed -n 's/.*state_digest=\([0-9a-f]\{16\}\).*/\1/p' \
  "$W/fixtures/gpu16.135608492183.stderr")
test "${#DIGEST}" -eq 16
DIGEST_ROWS=$(grep -h -F "state_digest=$DIGEST" "$W"/fixtures/gpu*.stderr | wc -l)
test "$DIGEST_ROWS" -eq 8
test "$(sed -n 's/.*state_digest=\([0-9a-f]\{16\}\).*/\1/p' \
  "$W"/fixtures/gpu*.stderr | sort -u | wc -l)" -eq 1

set +e
"$W/ppgpu" --ops "$INC/ops.bin" --from 1 --to 2 \
  > "$W/fixtures/reject.stdout" 2> "$W/fixtures/reject.stderr"
rc=$?
set -e
test "$rc" -eq 2
grep -Fq 'refusing to run on an unknown stream' "$W/fixtures/reject.stderr"

# The incumbent may cross a normal chunk boundary during fixture parity, but
# its completed coverage must remain contiguous and its immutable inputs must
# remain byte-identical.
test "$(md5sum "$INC/ops.bin" | awk '{print $1}')" = 091a13089a3e96dd499f296f0ef1740f
test "$(sha256sum "$INC/ppgpu-cc20" | awk '{print $1}')" = \
  f75eb8080bcf19617082f9ff02f6291d2ddf5fe9138c40e78b4a0128ad44f183
read ACTIVE_FROM_AFTER ACTIVE_TO_AFTER ACTIVE_PID_AFTER < <(audit_incumbent)
read COVERAGE_END_AFTER COVERAGE_ROWS_AFTER < <(freeze_coverage "$COVERAGE_AFTER")
test "$COVERAGE_END_AFTER" = "$ACTIVE_FROM_AFTER"
test "$COVERAGE_END_AFTER" -ge "$COVERAGE_END_BEFORE"
COVERAGE_SHA_AFTER=$(sha256sum "$COVERAGE_AFTER" | awk '{print $1}')

{
  sha256sum "$W/ops.bin" "$W/ppgpu" "$W/ppcpu" "$W/src/pp_host.h" \
    "$W/src/pp_model.h" "$W/src/ppcpu.cpp" "$W/src/ppgpu.cu"
  printf 'state_digest=%s\n' "$DIGEST"
} > "$W/FINGERPRINTS.tmp"
mv "$W/FINGERPRINTS.tmp" "$W/FINGERPRINTS"
printf 'assignment=189000000000-190000000000 before=%s-%s rows=%s pid=%s coverage_sha256=%s after=%s-%s rows=%s pid=%s coverage_sha256=%s\n' \
  "$ACTIVE_FROM_BEFORE" "$ACTIVE_TO_BEFORE" "$COVERAGE_ROWS_BEFORE" \
  "$ACTIVE_PID_BEFORE" "$COVERAGE_SHA_BEFORE" "$ACTIVE_FROM_AFTER" \
  "$ACTIVE_TO_AFTER" "$COVERAGE_ROWS_AFTER" "$ACTIVE_PID_AFTER" \
  "$COVERAGE_SHA_AFTER" > "$W/BORROW.complete.tmp"
mv "$W/BORROW.complete.tmp" "$W/BORROW.complete"
printf 'fixtures=135608492183,0,7,2500069332 cpu=gpu8=gpu16\n' \
  > "$W/PARITY.complete.tmp"
mv "$W/PARITY.complete.tmp" "$W/PARITY.complete"
printf 'STAGE_VERIFY_COMPLETE state_digest=%s\n' "$DIGEST"
