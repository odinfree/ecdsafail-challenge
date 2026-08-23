#!/usr/bin/env bash
# Full local gate for the CPU-only Q1274 finite-list conditional-phase packet.
set -euo pipefail
export LC_ALL=C

packet_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
wrapper="$packet_dir/phase_postfilter.sh"
manifest="$packet_dir/MANIFEST.sha256"

fail() { echo "verify-phase-postfilter: FAIL: $*" >&2; exit 1; }
sha() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$1" | awk '{print $1}'
    else
        shasum -a 256 "$1" | awk '{print $1}'
    fi
}

[[ $# == 2 ]] || fail "usage: verify_phase_postfilter.sh OPS_BIN PHASEPOSTFILTER_BIN"
ops="$1"; binary="$2"
[[ -f "$ops" ]] || fail "ops stream not found"
[[ -f "$binary" && -x "$binary" ]] || fail "postfilter binary not executable"

scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT

echo "== manifest and executable identity"
while read -r want rel; do
    [[ -z "$want" || "$want" == \#* ]] && continue
    got="$(sha "$packet_dir/$rel")"
    [[ "$got" == "$want" ]] || fail "manifest mismatch for $rel"
done < <(grep -E '^[0-9a-f]{64}  ' "$manifest")
expected_identity=$'source_commit=fe0b7bac6348fb35b7680784d4295899e498d0e3\tops_count=12920073\tops_sha256=4c68597468ed1dbb4f2e33042842227bf57c011c51f41e9cdaf13c73194b1f8c\tpredictor_digest=d2c95102cb9a277d\tshots=9024\tcontract=phase&~classical\tfinal=classical_mask==0&&clean_phase_mask==0\traw_phase=not-claimed\tcuda_phase=not-claimed'
[[ "$("$binary" identity)" == "$expected_identity" ]] || fail "identity mismatch"
echo "   PASS source/count/SHA/digest/contract identity"

echo "== frozen23 + blinded disjoint32 complete masked-set audit"
python3 - "$packet_dir/PHASE_FIXTURES.tsv" \
    "$packet_dir/PHASE_D32_FIXTURES.tsv" "$scratch/all.nonces" <<'PY'
import sys
out=[]
for path in sys.argv[1:3]:
    for line in open(path,encoding='ascii'):
        if line and not line.startswith('#'):
            out.append(line.split('\t',1)[0])
assert len(out)==55 and len(set(out))==55
open(sys.argv[3],'w',encoding='ascii',newline='\n').write('\n'.join(out)+'\n')
PY
"$binary" audit --ops "$ops" --nonces "$scratch/all.nonces" \
    >"$scratch/audit.tsv" 2>"$scratch/audit.stderr"
python3 - "$packet_dir/PHASE_FIXTURES.tsv" \
    "$packet_dir/PHASE_D32_FIXTURES.tsv" "$scratch/audit.tsv" <<'PY'
import hashlib,sys
expected=[]
for path in sys.argv[1:3]:
    for line in open(path,encoding='ascii'):
        if not line or line.startswith('#'): continue
        n,c,k,h,s=line.rstrip('\n').split('\t')
        expected.append((n,int(c),int(k),h,s))
got=[]
for line in open(sys.argv[3],encoding='ascii'):
    n,c,k,s=line.rstrip('\n').split('\t')
    got.append((n,int(c),int(k),s))
assert len(got)==len(expected)==55
for e,g in zip(expected,got):
    n,c,k,h,s=e
    assert g==(n,c,k,s), (e,g)
    vals=[] if s=='{}' else [int(x) for x in s[1:-1].split(',')]
    assert vals==sorted(vals) and len(vals)==len(set(vals))==k
    raw=''.join(f'{x}\n' for x in vals).encode('ascii')
    assert hashlib.sha256(raw).hexdigest()==h
print('   PASS frozen23=23/23 D32=32/32 complete sets and per-set SHA-256')
PY
audit_sha="$(sha "$scratch/audit.tsv")"
echo "   deterministic audit sha256=$audit_sha"

echo "== deterministic production wrapper on frozen classically-clean canary"
printf '100000035106674\n' >"$scratch/canary.nonces"
for run in 1 2; do
    "$wrapper" --binary "$binary" --ops "$ops" \
        --nonces "$scratch/canary.nonces" \
        --output "$scratch/canary.$run.out" \
        --receipt "$scratch/canary.$run.receipt" \
        >"$scratch/canary.$run.stdout" 2>"$scratch/canary.$run.stderr"
done
cmp "$scratch/canary.1.out" "$scratch/canary.2.out" >/dev/null ||
    fail "repeated output differs"
cmp "$scratch/canary.1.receipt" "$scratch/canary.2.receipt" >/dev/null ||
    fail "repeated receipt differs"
cmp "$scratch/canary.1.out" "$scratch/canary.1.stdout" >/dev/null ||
    fail "stdout differs from published output"
[[ ! -s "$scratch/canary.1.out" ]] || fail "phase-dirty canary was emitted"
[[ "$(sha "$scratch/canary.1.out")" == \
   "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" ]] ||
    fail "unexpected empty-output SHA"
grep -qx 'final_predicate=classical_mask==0&&clean_phase_mask==0' \
    "$scratch/canary.1.receipt" || fail "receipt predicate missing"
echo "   PASS repeated byte-identical empty output/receipt; canary {1753,5833} omitted"

echo "== existing destination fail-closed gates"
printf 'do-not-overwrite-output\n' >"$scratch/existing-output.out"
existing_output_sha="$(sha "$scratch/existing-output.out")"
set +e
"$wrapper" --binary "$binary" --ops "$ops" --nonces "$scratch/canary.nonces" \
    --output "$scratch/existing-output.out" --receipt "$scratch/existing-output.receipt" \
    >"$scratch/existing-output.stdout" 2>"$scratch/existing-output.stderr"
rc=$?
set -e
[[ "$rc" == 2 ]] || fail "existing output exit=$rc expected=2"
[[ "$(sha "$scratch/existing-output.out")" == "$existing_output_sha" ]] ||
    fail "existing output was modified"
[[ ! -e "$scratch/existing-output.receipt" ]] ||
    fail "existing-output rejection published receipt"
[[ ! -s "$scratch/existing-output.stdout" ]] ||
    fail "existing-output rejection leaked stdout"

printf 'do-not-overwrite-receipt\n' >"$scratch/existing-receipt.receipt"
existing_receipt_sha="$(sha "$scratch/existing-receipt.receipt")"
set +e
"$wrapper" --binary "$binary" --ops "$ops" --nonces "$scratch/canary.nonces" \
    --output "$scratch/existing-receipt.out" --receipt "$scratch/existing-receipt.receipt" \
    >"$scratch/existing-receipt.stdout" 2>"$scratch/existing-receipt.stderr"
rc=$?
set -e
[[ "$rc" == 2 ]] || fail "existing receipt exit=$rc expected=2"
[[ "$(sha "$scratch/existing-receipt.receipt")" == "$existing_receipt_sha" ]] ||
    fail "existing receipt was modified"
[[ ! -e "$scratch/existing-receipt.out" ]] ||
    fail "existing-receipt rejection published output"
[[ ! -s "$scratch/existing-receipt.stdout" ]] ||
    fail "existing-receipt rejection leaked stdout"
echo "   PASS existing output/receipt preserved; no peer artifact or stdout"

echo "== exact-classical precondition rejects dirty input atomically"
printf '251000962439\n100000035106674\n' >"$scratch/dirty.nonces"
set +e
"$wrapper" --binary "$binary" --ops "$ops" --nonces "$scratch/dirty.nonces" \
    --output "$scratch/dirty.out" --receipt "$scratch/dirty.receipt" \
    >"$scratch/dirty.stdout" 2>"$scratch/dirty.stderr"
rc=$?
set -e
[[ "$rc" == 4 ]] || fail "dirty input exit=$rc expected=4"
[[ ! -e "$scratch/dirty.out" && ! -e "$scratch/dirty.receipt" ]] ||
    fail "dirty input published output or receipt"
[[ ! -s "$scratch/dirty.stdout" ]] || fail "dirty input leaked partial stdout"
echo "   PASS exit 4, no output/receipt/stdout"

expect_list_reject() {
    local name="$1" content="$2"
    local list="$scratch/list-$name.txt"
    printf '%b' "$content" >"$list"
    set +e
    "$binary" filter --ops "$ops" --nonces "$list" \
        >"$scratch/list-$name.direct.stdout" \
        2>"$scratch/list-$name.direct.stderr"
    local direct_rc=$?
    set -e
    [[ "$direct_rc" == 3 ]] || fail "$name direct-list exit=$direct_rc expected=3"
    [[ ! -s "$scratch/list-$name.direct.stdout" ]] ||
        fail "$name direct-list leaked stdout"
    set +e
    "$wrapper" --binary "$binary" --ops "$ops" --nonces "$list" \
        --output "$scratch/list-$name.out" \
        --receipt "$scratch/list-$name.receipt" \
        >"$scratch/list-$name.stdout" 2>"$scratch/list-$name.stderr"
    local rc=$?
    set -e
    [[ "$rc" == 3 ]] || fail "$name list exit=$rc expected=3"
    [[ ! -e "$scratch/list-$name.out" && ! -e "$scratch/list-$name.receipt" ]] ||
        fail "$name list published output or receipt"
    [[ ! -s "$scratch/list-$name.stdout" ]] || fail "$name list leaked stdout"
}

echo "== malformed/duplicate/range list gates"
expect_list_reject empty ''
expect_list_reject unterminated '1'
expect_list_reject whitespace '1 \n'
expect_list_reject signed '+1\n'
expect_list_reject leading_zero '01\n'
expect_list_reject non_decimal '1x\n'
expect_list_reject blank_line '1\n\n'
expect_list_reject duplicate '1\n1\n'
expect_list_reject out_of_range '281474976710656\n'
echo "   PASS 9/9 invalid finite-list forms rejected without publication"

echo "== wrong stream/count/hash negatives"
python3 - "$ops" "$scratch" <<'PY'
import struct,sys
b=bytearray(open(sys.argv[1],'rb').read()); d=sys.argv[2]
x=bytearray(b);x[0]^=1;open(d+'/bad-magic.bin','wb').write(x)
x=bytearray(b);struct.pack_into('<Q',x,8,12921096);open(d+'/bad-count.bin','wb').write(x)
x=bytearray(b);x[16]^=1;open(d+'/bad-sha.bin','wb').write(x)
PY
expect_stream_reject() {
    local name="$1" expected_rc="$2" expected_sha="$3"
    local stream="$scratch/$name.bin"
    [[ "$(sha "$stream")" == "$expected_sha" ]] || fail "$name negative SHA mismatch"
    set +e
    "$binary" audit --ops "$stream" --nonces "$scratch/canary.nonces" \
        >"$scratch/$name.stdout" 2>"$scratch/$name.stderr"
    local rc=$?
    set -e
    [[ "$rc" == "$expected_rc" ]] || fail "$name stream exit=$rc expected=$expected_rc"
    [[ ! -s "$scratch/$name.stdout" ]] || fail "$name stream leaked output"
}
expect_stream_reject bad-magic 1 f0a120ef246eac3c76123dc478522977cbc543a773ba540ae23c9d6adf30ecf1
expect_stream_reject bad-count 2 afb4eda48b819711710ae1e3f5eaf5fabdac2c1d19c2ffebe6a75d6e7d6abfeb
expect_stream_reject bad-sha 2 4daf97cffbdfd19fdd6df22d0d8861af49d6b11e0d87f43cb50aafbc85a04e38
echo "   PASS wrong magic/count/same-count-hash exits 1/2/2 before output"

echo "== unchanged classical 323-row provenance rerun"
bash "$packet_dir/verify_local_cpu.sh"

echo
echo "Q1274 CONDITIONAL-PHASE POSTFILTER: PASS"
echo "  frozen23+D32 exact; deterministic finite-list filter; classical323 and all negatives green"
echo "  contract=phase&~classical final=classical_mask==0&&clean_phase_mask==0"
echo "  raw phase and CUDA phase are not claimed"
