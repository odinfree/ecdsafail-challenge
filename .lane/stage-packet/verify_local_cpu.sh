#!/usr/bin/env bash
# verify_local_cpu.sh — local, fail-closed CPU re-validation of the sealed
# Q1274 repair-r100 predictor payload. Reproduces the sealed evidence on THIS
# host without any provider, remote, range-scan, hunt, or submission action.
#
# It proves, from this worktree's committed sources alone:
#   1. the repaired circuit at HEAD emits ops.bin with the bound op count and
#      full SHA-256 (byte-exact artifact reproduction);
#   2. every current packet source and fixture is byte-identical to its
#      MANIFEST.sha256 entry (the manifest separately records which sources
#      retain upstream identity and which carry the CPU-only phase extension);
#   3. a locally-built CPU predictor reproduces the frozen 323-row classical
#      failing-shot ledger EXACTLY over the 22 regression cases (behavioural
#      binding — the local binary hash is NOT expected to match the frozen
#      arm64/Linux binaries, only its per-shot mask output);
#   4. the loader fails before evaluation on wrong framing (exit 1), wrong op
#      count (exit 2), and a same-count / wrong-SHA stream (exit 2).
#
# Everything generated (ops.bin, patched negatives, the CPU binary) is written
# under a throwaway scratch dir and removed on exit. Nothing is committed.
set -euo pipefail

pkt_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
repo_root="$(cd "$pkt_dir/../.." && pwd -P)"
src_dir="$pkt_dir/src"
ledger="$pkt_dir/fixtures.local.tsv"
manifest="$pkt_dir/MANIFEST.sha256"

# Bound identities (must match the sealed target).
EXP_OPS_SHA="4c68597468ed1dbb4f2e33042842227bf57c011c51f41e9cdaf13c73194b1f8c"
EXP_OPS_COUNT="12920073"
NEG_COUNT="12921096"          # PREDICTOR.md wrong-count negative
NEG_MAGIC_SHA="f0a120ef246eac3c76123dc478522977cbc543a773ba540ae23c9d6adf30ecf1"
NEG_SHA="4daf97cffbdfd19fdd6df22d0d8861af49d6b11e0d87f43cb50aafbc85a04e38"  # byte-16 XOR 0x01

sha() { shasum -a 256 "$1" | awk '{print $1}'; }
fail() { echo "FAIL: $*" >&2; exit 1; }

for tool in shasum zstd python3 cargo; do
  command -v "$tool" >/dev/null 2>&1 || fail "missing required tool: $tool"
done
cxx="${CXX:-}"
if [[ -z "$cxx" ]]; then
  if   [[ -x /usr/bin/clang++ ]]; then cxx=/usr/bin/clang++
  elif command -v g++      >/dev/null 2>&1; then cxx="$(command -v g++)"
  elif command -v clang++  >/dev/null 2>&1; then cxx="$(command -v clang++)"
  else fail "no C++ compiler found (set CXX)"; fi
fi

scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT
echo "== scratch: $scratch"
echo "== compiler: $cxx"

# ---- gate 2: current packet matches the sealed manifest -----------------------
echo "== [gate 2] verifying current packet hashes against MANIFEST.sha256"
# MANIFEST rows are "<sha>  <relpath>" for sealed packet payload files.
while read -r want rel; do
  [[ "$want" == \#* || -z "$want" ]] && continue
  got="$(sha "$pkt_dir/$rel")"
  [[ "$got" == "$want" ]] || fail "manifest mismatch for $rel: $got != $want"
done < <(grep -E '^[0-9a-f]{64}  ' "$manifest")
echo "   OK: all manifest entries match"

# ---- gate 1: byte-exact artifact reproduction from HEAD -----------------------
echo "== [gate 1] rebuilding build_circuit and reproducing ops.bin"
( cd "$repo_root" && CARGO_NET_OFFLINE=true cargo build --release --locked --offline --bin build_circuit )
bc="$repo_root/target/release/build_circuit"
( cd "$scratch" && "$bc" >/dev/null )
ops="$scratch/ops.bin"
got_sha="$(sha "$ops")"
hdr_count="$(python3 - "$ops" <<'PY'
import struct,sys
with open(sys.argv[1],'rb') as f:
    f.read(8); print(struct.unpack("<Q", f.read(8))[0])
PY
)"
[[ "$hdr_count" == "$EXP_OPS_COUNT" ]] || fail "op count $hdr_count != $EXP_OPS_COUNT"
[[ "$got_sha"  == "$EXP_OPS_SHA"  ]] || fail "ops sha $got_sha != $EXP_OPS_SHA"
echo "   OK: ops.bin count=$hdr_count sha=$got_sha"

# ---- build the CPU predictor from sealed sources ------------------------------
echo "== building CPU predictor (behavioural reference)"
pp="$scratch/ppcpu"
"$cxx" -O3 -std=c++17 -pthread -o "$pp" "$src_dir/ppcpu.cpp"
echo "   OK: ppcpu built (local sha $(sha "$pp"))"

# ---- gate 3 (local regression): 323-row ledger set-equality -------------------
echo "== [regression] reproducing the frozen 323-row classical ledger (22 cases)"
PPF_OPS="$ops" python3 - "$pp" "$ops" "$ledger" <<'PY'
import subprocess, sys, os, collections
pp, ops, ledger = sys.argv[1], sys.argv[2], sys.argv[3]
case_nonce={}; expected=[]
for line in open(ledger):
    if line.startswith('#') or line.startswith('case\t'): continue
    c,n,s,m=line.rstrip('\n').split('\t')
    case_nonce.setdefault(c,n); expected.append((c,int(s),int(m)))
got=[]
env={**os.environ,'PPF_OPS':ops}
for c,n in case_nonce.items():
    out=subprocess.run([pp,'faultshots',n],capture_output=True,text=True,env=env)
    if out.returncode!=0:
        sys.exit(f"FAIL: predictor exit {out.returncode} on case {c}")
    for ln in out.stdout.split('\n'):
        ln=ln.strip()
        if not ln: continue
        s,m=ln.split(); got.append((c,int(s),int(m)))
if sorted(expected)!=sorted(got):
    es,gs=set(expected),set(got)
    sys.exit(f"FAIL: ledger mismatch missing={sorted(es-gs)[:5]} extra={sorted(gs-es)[:5]}")
hist=collections.Counter(m for _,_,m in got)
m16=sum(1 for _,_,m in got if m & 16)
print(f"   OK: {len(case_nonce)} cases, {len(got)}/{len(expected)} rows set-equal")
print(f"   mask histogram {dict(sorted(hist.items()))}  mask16_observed={m16}")
PY

# ---- gate 0: fail-closed negatives -------------------------------------------
echo "== [fail-closed] wrong magic stream must exit 1 (pre-header)"
python3 - "$ops" "$scratch/neg_magic.bin" <<'PY'
import sys
b=bytearray(open(sys.argv[1],'rb').read()); b[0]^=0x01
open(sys.argv[2],'wb').write(b)
PY
neg_magic_got="$(sha "$scratch/neg_magic.bin")"
[[ "$neg_magic_got" == "$NEG_MAGIC_SHA" ]] || fail "wrong-magic SHA $neg_magic_got != $NEG_MAGIC_SHA"
set +e; PPF_OPS="$scratch/neg_magic.bin" "$pp" breakdown 251000962439 >/dev/null 2>&1; rc=$?; set -e
[[ "$rc" == 1 ]] || fail "wrong-magic negative returned $rc, expected 1"
echo "   OK: exit 1 (wrong-magic $neg_magic_got)"

echo "== [fail-closed] wrong op-count stream must exit 2 (pre-hash)"
python3 - "$ops" "$scratch/neg_count.bin" "$NEG_COUNT" <<'PY'
import struct,sys
b=bytearray(open(sys.argv[1],'rb').read())
struct.pack_into("<Q", b, 8, int(sys.argv[3]))
open(sys.argv[2],'wb').write(b)
PY
set +e; PPF_OPS="$scratch/neg_count.bin" "$pp" breakdown 251000962439 >/dev/null 2>&1; rc=$?; set -e
[[ "$rc" == 2 ]] || fail "wrong-count negative returned $rc, expected 2"
echo "   OK: exit 2"

echo "== [fail-closed] same-count / wrong-SHA stream must exit 2 (pre-decompress)"
python3 - "$ops" "$scratch/neg_sha.bin" <<'PY'
import sys
b=bytearray(open(sys.argv[1],'rb').read()); b[16]^=0x01
open(sys.argv[2],'wb').write(b)
PY
neg_sha_got="$(sha "$scratch/neg_sha.bin")"
[[ "$neg_sha_got" == "$NEG_SHA" ]] || echo "   note: local wrong-SHA=$neg_sha_got (frozen negative was $NEG_SHA)"
set +e; PPF_OPS="$scratch/neg_sha.bin" "$pp" breakdown 251000962439 >/dev/null 2>&1; rc=$?; set -e
[[ "$rc" == 2 ]] || fail "wrong-sha negative returned $rc, expected 2"
echo "   OK: exit 2 (wrong-SHA $neg_sha_got)"

echo
echo "LOCAL CPU CANARY: PASS"
echo "  artifact reproduced, manifest sealed, 323/323 ledger, all three negatives fail-closed."
echo "  Result-channel (mask 16) is NOT exercised by these fixtures — see STAGE.md."
