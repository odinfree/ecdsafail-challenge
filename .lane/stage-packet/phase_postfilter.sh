#!/usr/bin/env bash
# Atomic finite-list wrapper for the sealed Q1274 CPU phase postfilter.
set -euo pipefail
export LC_ALL=C
umask 077

fail() { local rc="$1"; shift; echo "phase-postfilter: FAIL: $*" >&2; exit "$rc"; }
sha() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$1" | awk '{print $1}'
    else
        shasum -a 256 "$1" | awk '{print $1}'
    fi
}

binary=""; ops=""; nonces=""; output=""; receipt=""
while (($#)); do
    case "$1" in
        --binary|--ops|--nonces|--output|--receipt)
            (($# >= 2)) || fail 2 "missing value for $1"
            case "$1" in
                --binary) binary="$2" ;;
                --ops) ops="$2" ;;
                --nonces) nonces="$2" ;;
                --output) output="$2" ;;
                --receipt) receipt="$2" ;;
            esac
            shift 2
            ;;
        *) fail 2 "unknown argument $1" ;;
    esac
done

[[ -n "$binary" && -n "$ops" && -n "$nonces" && -n "$output" && -n "$receipt" ]] ||
    fail 2 "usage: phase_postfilter.sh --binary BIN --ops OPS --nonces LIST --output OUT --receipt RECEIPT"
[[ -f "$binary" && -x "$binary" ]] || fail 2 "binary is not an executable file"
[[ -f "$ops" ]] || fail 2 "ops stream is not a regular file"
[[ -f "$nonces" ]] || fail 3 "nonce list is not a regular file"
[[ "$output" != "$receipt" ]] || fail 2 "output and receipt paths must differ"
[[ ! -e "$output" && ! -L "$output" ]] || fail 2 "refusing to overwrite output"
[[ ! -e "$receipt" && ! -L "$receipt" ]] || fail 2 "refusing to overwrite receipt"

output_dir="$(cd "$(dirname "$output")" && pwd -P)"
receipt_dir="$(cd "$(dirname "$receipt")" && pwd -P)"
output_abs="$output_dir/$(basename "$output")"
receipt_abs="$receipt_dir/$(basename "$receipt")"

expected_identity="source_commit=fe0b7bac6348fb35b7680784d4295899e498d0e3	ops_count=12920073	ops_sha256=4c68597468ed1dbb4f2e33042842227bf57c011c51f41e9cdaf13c73194b1f8c	predictor_digest=d2c95102cb9a277d	shots=9024	contract=phase&~classical	final=classical_mask==0&&clean_phase_mask==0	raw_phase=not-claimed	cuda_phase=not-claimed"
identity="$("$binary" identity)" || fail 2 "binary identity command failed"
[[ "$identity" == "$expected_identity" ]] || fail 2 "binary identity mismatch"

set +e
input_count="$(python3 - "$nonces" <<'PY'
import sys
p=sys.argv[1]
try:
    b=open(p,'rb').read()
except OSError as e:
    print(f"phase-postfilter: cannot read nonce list: {e}",file=sys.stderr);sys.exit(3)
if not b:
    print("phase-postfilter: nonce list must be non-empty",file=sys.stderr);sys.exit(3)
if not b.endswith(b'\n'):
    print("phase-postfilter: nonce list must end in LF",file=sys.stderr);sys.exit(3)
try:
    s=b.decode('ascii')
except UnicodeDecodeError:
    print("phase-postfilter: nonce list must be ASCII",file=sys.stderr);sys.exit(3)
seen=set(); rows=s[:-1].split('\n')
for i,row in enumerate(rows,1):
    if not row or not row.isdecimal() or (len(row)>1 and row[0]=='0'):
        print(f"phase-postfilter: malformed nonce at line {i}",file=sys.stderr);sys.exit(3)
    n=int(row)
    if n >= 1<<48:
        print(f"phase-postfilter: nonce out of range at line {i}",file=sys.stderr);sys.exit(3)
    if n in seen:
        print(f"phase-postfilter: duplicate nonce at line {i}",file=sys.stderr);sys.exit(3)
    seen.add(n)
print(len(rows))
PY
)"
rc=$?
set -e
[[ "$rc" == 0 ]] || exit "$rc"

tmp_output="$(mktemp "$output_dir/.phasepostfilter.output.XXXXXX")"
tmp_receipt="$(mktemp "$receipt_dir/.phasepostfilter.receipt.XXXXXX")"
tmp_stderr="$(mktemp "$output_dir/.phasepostfilter.stderr.XXXXXX")"
cleanup() { rm -f "$tmp_output" "$tmp_receipt" "$tmp_stderr"; }
trap cleanup EXIT

set +e
"$binary" filter --ops "$ops" --nonces "$nonces" >"$tmp_output" 2>"$tmp_stderr"
rc=$?
set -e
if [[ "$rc" != 0 ]]; then
    cat "$tmp_stderr" >&2
    exit "$rc"
fi

output_count="$(python3 - "$nonces" "$tmp_output" <<'PY'
import sys
ins=open(sys.argv[1],encoding='ascii').read().splitlines()
b=open(sys.argv[2],'rb').read()
if b and not b.endswith(b'\n'):
    print("phase-postfilter: unterminated output",file=sys.stderr);sys.exit(5)
try:
    outs=[] if not b else b[:-1].decode('ascii').split('\n')
except UnicodeDecodeError:
    print("phase-postfilter: non-ASCII output",file=sys.stderr);sys.exit(5)
positions={row:i for i,row in enumerate(ins)}
pos=-1
for row in outs:
    if not row or not row.isdecimal() or (len(row)>1 and row[0]=='0'):
        print("phase-postfilter: malformed output row",file=sys.stderr);sys.exit(5)
    nxt=positions.get(row,-1)
    if nxt <= pos:
        print("phase-postfilter: output is not an ordered input subset",file=sys.stderr);sys.exit(5)
    pos=nxt
if len(set(outs)) != len(outs):
    print("phase-postfilter: duplicate output row",file=sys.stderr);sys.exit(5)
print(len(outs))
PY
)"

grep -Fq "inputs=$input_count survivors=$output_count " "$tmp_stderr" ||
    fail 5 "binary summary count mismatch"
grep -Fq "contract=phase&~classical final=classical_mask==0&&clean_phase_mask==0 raw_phase=not-claimed cuda_phase=not-claimed" "$tmp_stderr" ||
    fail 5 "binary summary contract mismatch"

input_sha="$(sha "$nonces")"
output_sha="$(sha "$tmp_output")"
binary_sha="$(sha "$binary")"
{
    printf 'packet=q1274-conditional-phase-postfilter-v1\n'
    printf 'source_commit=fe0b7bac6348fb35b7680784d4295899e498d0e3\n'
    printf 'ops_count=12920073\n'
    printf 'ops_sha256=4c68597468ed1dbb4f2e33042842227bf57c011c51f41e9cdaf13c73194b1f8c\n'
    printf 'predictor_digest=d2c95102cb9a277d\n'
    printf 'binary_sha256=%s\n' "$binary_sha"
    printf 'input_rows=%s\n' "$input_count"
    printf 'input_sha256=%s\n' "$input_sha"
    printf 'output_rows=%s\n' "$output_count"
    printf 'output_sha256=%s\n' "$output_sha"
    printf 'output_order=input-order\n'
    printf 'output_schema=canonical-decimal-nonce-lf\n'
    printf 'contract=phase&~classical\n'
    printf 'final_predicate=classical_mask==0&&clean_phase_mask==0\n'
    printf 'raw_phase=not-claimed\n'
    printf 'cuda_phase=not-claimed\n'
} >"$tmp_receipt"

ln "$tmp_receipt" "$receipt_abs" || fail 5 "receipt appeared concurrently; refusing to overwrite"
rm -f "$tmp_receipt"
if ! ln "$tmp_output" "$output_abs"; then
    rm -f "$receipt_abs"
    fail 5 "output appeared concurrently; refusing to overwrite"
fi
rm -f "$tmp_output"
cat "$output_abs"
echo "phase-postfilter: PASS input_rows=$input_count output_rows=$output_count output_sha256=$output_sha" >&2
trap - EXIT
rm -f "$tmp_stderr"
