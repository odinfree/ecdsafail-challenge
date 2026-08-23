#!/usr/bin/env bash
# run_linux_parity.sh — Linux CPU/CUDA parity stage runner for the Q1274
# repair-r100 predictor. Self-contained from this sealed packet: it rebuilds
# both binaries from the sealed sources, binds them to the exact ops stream,
# and requires exact complete per-shot mask equality across CPU (comb8),
# GPU comb8, and GPU comb16 for all 32 frozen parity fixtures.
#
# STATUS: this gate ALREADY PASSED on a Linux+CUDA host for the original
# classical source before the default-off CPU-only phase extension (32/32
# byte-identical, 64/64 CUDA state-digest checks,
# parity-results SHA-256 924e31aee95e360eb742fb3bb3de9122552d8efce2a74828dacd7bac1ef130d1).
# This script re-runs the same classical gate against the current sealed packet
# if it is ever re-staged. It performs NO scan, provider, remote, or submission
# action. It does not implement or claim CUDA phase parity.
#
# Usage: PPF_OPS=/exact/path/ops.bin ./run_linux_parity.sh [OUTDIR]
#   ops.bin must be the canonical repaired stream (SHA-256 gate enforced). It is
#   produced by a clean `cargo build --release --locked --bin build_circuit` at
#   this branch HEAD (source fe0b7bac...) with no env overrides; its SHA-256 must
#   equal 4c68597468... (the runner re-checks). src/build.sh is vendored+sealed
#   for provenance but NOT invoked here — this runner inlines its own compiles.
#   OUTDIR (default ./parity-out) receives per-fixture mask files + receipt.
set -euo pipefail

pkt_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
src_dir="$pkt_dir/src"
fixtures="$pkt_dir/PARITY_FIXTURES.tsv"
manifest="$pkt_dir/MANIFEST.sha256"
outdir="${1:-$pkt_dir/parity-out}"

EXP_OPS_SHA="4c68597468ed1dbb4f2e33042842227bf57c011c51f41e9cdaf13c73194b1f8c"
EXP_OPS_COUNT="12920073"
EXP_STATE_DIGEST="d2c95102cb9a277d"
EXP_FIXTURES_SHA="5cdc29d0008ea68c224f5b74a292b5f2337acccb349e72c2faf57571c09e8139"

sha() { shasum -a 256 "$1" | awk '{print $1}'; }
fail() { echo "FAIL: $*" >&2; exit 1; }

: "${PPF_OPS:?set PPF_OPS to the canonical ops.bin path}"
for tool in shasum zstd python3 g++ nvcc; do
  command -v "$tool" >/dev/null 2>&1 || fail "missing required tool: $tool"
done

# ---- seal: sources + fixtures unchanged --------------------------------------
echo "== verifying sealed payload against MANIFEST.sha256"
while read -r want rel; do
  [[ "$want" == \#* || -z "$want" ]] && continue
  got="$(sha "$pkt_dir/$rel")"
  [[ "$got" == "$want" ]] || fail "manifest mismatch for $rel"
done < <(grep -E '^[0-9a-f]{64}  ' "$manifest")
[[ "$(sha "$fixtures")" == "$EXP_FIXTURES_SHA" ]] || fail "PARITY_FIXTURES.tsv hash drift"

# ---- ops stream identity ------------------------------------------------------
ops_sha="$(sha "$PPF_OPS")"
[[ "$ops_sha" == "$EXP_OPS_SHA" ]] || fail "ops sha $ops_sha != $EXP_OPS_SHA"
echo "   OK: ops.bin sha=$ops_sha"

# ---- build both binaries (gate 1). No pipeline may hide the compiler exit. ----
mkdir -p "$outdir"
echo "== [gate 1] building ppcpu (g++) and ppgpu (nvcc)"
g++  -O3 -std=c++17 -pthread -o "$outdir/ppcpu" "$src_dir/ppcpu.cpp"
echo "   ppcpu build exit 0"
nvcc -O3 --std=c++17 -lineinfo -gencode arch=compute_89,code=sm_89 \
     "$src_dir/ppgpu.cu" -o "$outdir/ppgpu"
echo "   ppgpu build exit 0"
cpu_sha="$(sha "$outdir/ppcpu")"; gpu_sha="$(sha "$outdir/ppgpu")"
echo "   Linux CPU  SHA-256: $cpu_sha"
echo "   Linux CUDA SHA-256: $gpu_sha"

# ---- self-verify the fixtures are the bound deterministic nonces --------------
echo "== verifying the 32 fixtures are self-derived and < 2^48"
python3 - "$fixtures" <<'PY'
import hashlib,sys
bad=0;n=0
for line in open(sys.argv[1]):
    if line.startswith('#') or line.startswith('index\t'): continue
    idx,nonce,seed,sha=line.rstrip('\n').split('\t'); n+=1
    d=hashlib.sha256(seed.encode()).hexdigest()
    if d!=sha or int(d[:12],16)!=int(nonce) or int(nonce)>=(1<<48): bad+=1
print(f"   OK: {n} fixtures verified" if bad==0 else f"FAIL: {bad}/{n} bad")
sys.exit(1 if bad else 0)
PY

# ---- parity: CPU comb8 == GPU comb8 == GPU comb16, complete per-shot sets ------
echo "== [gate 2+3] per-fixture CPU/GPU8/GPU16 complete mask-set parity"
fail_fixtures=0; total_faults=0; declare -A masktot=([1]=0 [2]=0 [4]=0 [8]=0 [16]=0)
digest_checks=0
while read -r idx nonce seed fsha; do
  if [[ "$idx" == \#* || "$idx" == "index" || -z "$idx" ]]; then continue; fi
  cpu="$outdir/f${idx}.cpu.txt"; g8="$outdir/f${idx}.gpu8.txt"; g16="$outdir/f${idx}.gpu16.txt"
  # CPU (comb8-only)
  PPF_OPS="$PPF_OPS" "$outdir/ppcpu" faultshots "$nonce" | sort -n > "$cpu"
  # GPU comb8 (must pass --comb-bits 8 EXPLICITLY; default is 16)
  "$outdir/ppgpu" --ops "$PPF_OPS" --faultshots "$nonce" --comb-bits 8 2> "$outdir/f${idx}.gpu8.err" \
      | sort -n > "$g8"
  # GPU comb16
  "$outdir/ppgpu" --ops "$PPF_OPS" --faultshots "$nonce" --comb-bits 16 2> "$outdir/f${idx}.gpu16.err" \
      | sort -n > "$g16"
  # state-digest gate on both GPU legs (gate 2)
  for e in "$outdir/f${idx}.gpu8.err" "$outdir/f${idx}.gpu16.err"; do
    grep -q "state_digest=$EXP_STATE_DIGEST" "$e" || fail "fixture $idx: GPU state digest missing/wrong in $e"
    digest_checks=$((digest_checks+1))
  done
  if diff -q "$cpu" "$g8" >/dev/null && diff -q "$cpu" "$g16" >/dev/null; then
    rows="$(wc -l < "$cpu" | tr -d ' ')"; total_faults=$((total_faults+rows))
    while read -r s m; do masktot[$m]=$(( ${masktot[$m]:-0} + 1 )); done < "$cpu"
    printf "   fixture %2s nonce %-16s faults %-3s  CPU==GPU8==GPU16\n" "$idx" "$nonce" "$rows"
  else
    echo "   fixture $idx MISMATCH (nonce $nonce)"; fail_fixtures=$((fail_fixtures+1))
  fi
done < "$fixtures"

m16="${masktot[16]:-0}"
{
  echo "# Q1274 repair-r100 Linux CPU/CUDA parity receipt (reproduced)"
  echo "ops_sha256=$ops_sha"
  echo "op_count=$EXP_OPS_COUNT"
  echo "state_digest=$EXP_STATE_DIGEST"
  echo "linux_cpu_sha256=$cpu_sha"
  echo "linux_cuda_sha256=$gpu_sha"
  echo "fixtures=32 mismatches=$fail_fixtures cuda_state_digest_checks=$digest_checks"
  echo "total_faults=$total_faults"
  echo "mask_1=${masktot[1]:-0} mask_2=${masktot[2]:-0} mask_4=${masktot[4]:-0} mask_8=${masktot[8]:-0} mask16_observed=$m16"
} | tee "$outdir/PARITY.receipt"

[[ "$fail_fixtures" == 0 ]] || fail "$fail_fixtures fixtures mismatched"
[[ "$digest_checks" == 64 ]] || fail "expected 64 CUDA state-digest checks, got $digest_checks"
echo
echo "LINUX PARITY: PASS (32/32 fixtures, 64/64 digest gates, mask16_observed=$m16)"
if [[ "$m16" == 0 ]]; then
  echo "  NOTE: result channel (mask 16) unexercised — parity on it is NOT proven here."
fi
exit 0
