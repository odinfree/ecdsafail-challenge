#!/bin/bash
# Build and qualify the exact model on a fresh, dedicated, idle GPU host.
set -euo pipefail

W=$(cd "$(dirname "$0")" && pwd)
test "$W" = /workspace/ev-g1000-q1276-0b6ac181
test ! -e "$W/BORROW.complete"
test ! -e "$W/DEDICATED.complete"
test ! -e "$W/PARITY.complete"
test ! -e "$W/FINGERPRINTS"
test ! -e "$W/fixtures"
exec 9>"$W/stage-dedicated.lock"
flock -n 9

assert_gpu_idle() {
  local apps
  apps=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader | sed '/^$/d')
  test -z "$apps"
}

assert_gpu_idle
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

grep -Fqx 'nonce 135608492183 pred_cls=15 walk_div=3 replay_div=0 walk_mul=11 replay_mul=1 result=0 shots=9024 first=32' \
  "$W/fixtures/cpu.135608492183"
grep -Fqx 'nonce 0 pred_cls=18 walk_div=9 replay_div=1 walk_mul=8 replay_mul=0 result=0 shots=9024 first=521' \
  "$W/fixtures/cpu.0"
grep -Fqx 'nonce 7 pred_cls=20 walk_div=10 replay_div=0 walk_mul=10 replay_mul=0 result=0 shots=9024 first=594' \
  "$W/fixtures/cpu.7"
grep -Fqx 'nonce 2500069332 pred_cls=17 walk_div=9 replay_div=0 walk_mul=7 replay_mul=1 result=0 shots=9024 first=266' \
  "$W/fixtures/cpu.2500069332"

DIGEST=$(sed -n 's/.*state_digest=\([0-9a-f]\{16\}\).*/\1/p' \
  "$W/fixtures/gpu16.135608492183.stderr")
test "$DIGEST" = 5a0a4564563a201a
DIGEST_ROWS=$(grep -h -F "state_digest=$DIGEST" "$W"/fixtures/gpu*.stderr | wc -l)
test "$DIGEST_ROWS" -eq 8
test "$(sed -n 's/.*state_digest=\([0-9a-f]\{16\}\).*/\1/p' \
  "$W"/fixtures/gpu*.stderr | sort -u | wc -l)" -eq 1
assert_gpu_idle

PPGPU_SHA=$(sha256sum "$W/ppgpu" | awk '{print $1}')
PPCPU_SHA=$(sha256sum "$W/ppcpu" | awk '{print $1}')
{
  sha256sum "$W/ops.bin" "$W/ppgpu" "$W/ppcpu" "$W/src/pp_host.h" \
    "$W/src/pp_model.h" "$W/src/ppcpu.cpp" "$W/src/ppgpu.cu"
  printf 'state_digest=%s\n' "$DIGEST"
} > "$W/FINGERPRINTS.tmp"
mv "$W/FINGERPRINTS.tmp" "$W/FINGERPRINTS"
printf 'fixtures=135608492183,0,7,2500069332 cpu=gpu8=gpu16\n' \
  > "$W/PARITY.complete.tmp"
mv "$W/PARITY.complete.tmp" "$W/PARITY.complete"
UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)
{
  printf 'utc=%s\n' "$UTC"
  printf 'gpu_apps_before=0 gpu_apps_after=0\n'
  printf 'ops_sha256=d1461959eac52b19b644f1f97a3b44a3ea249a109f14a406d19e872cd17c5422\n'
  printf 'state_digest=%s\n' "$DIGEST"
  printf 'ppgpu_sha256=%s\n' "$PPGPU_SHA"
  printf 'ppcpu_sha256=%s\n' "$PPCPU_SHA"
} > "$W/DEDICATED.complete.tmp"
mv "$W/DEDICATED.complete.tmp" "$W/DEDICATED.complete"
printf 'DEDICATED_STAGE_COMPLETE state_digest=%s ppgpu_sha256=%s ppcpu_sha256=%s\n' \
  "$DIGEST" "$PPGPU_SHA" "$PPCPU_SHA"
