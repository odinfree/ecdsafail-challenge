#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 || -z $1 ]]; then
    echo "usage: verify_phase_cpu.sh OPS_BIN" >&2
    exit 2
fi

script_dir=$(cd -- "$(dirname -- "$0")" && pwd -P)
repo_root=$(cd -- "$script_dir/../.." && pwd -P)
ops=$(cd -- "$(dirname -- "$1")" && pwd -P)/$(basename -- "$1")
fixture="$script_dir/Q1273_PHASE_FIXTURES.tsv"
schedule="$script_dir/Q1273_PHASE_SCHEDULE.tsv"
header="$script_dir/src/pp_phase_schedule.h"
generator="$script_dir/tools/generate_phase_schedule.py"
source_cpp="$repo_root/.lane/q1273-predictor/src/ppcpu.cpp"

expected_ops_sha=ee6448dbb23aa877123733724b109266e584f1ba14abf5c38b43b9ab6aa26cd1
expected_fixture_sha=e148f24d99ae45b3c6930a33d49173fd31b2c236593d98375956077b3feb4d1b
expected_schedule_sha=a4043530337b91e97d7a42dde2aff7e5a967a0b820ad1a9a120b3c366d7a5294
expected_header_sha=4249864aca9e2928a33865ea086b99ef8ecccc9eb596ba4c3e57468ba88d25e5
expected_generator_sha=83bfa142f2cf546ea5673de424597bf26ed3a57db0173d2b177a009ad9f8e966
expected_identity='source_commit=093d85d64de87aa5006a94868172f642daacf136 ops_count=12933805 ops_sha256=ee6448dbb23aa877123733724b109266e584f1ba14abf5c38b43b9ab6aa26cd1 predictor_digest=2148e09f4c4293b2 phase_meta_sha256=a4043530337b91e97d7a42dde2aff7e5a967a0b820ad1a9a120b3c366d7a5294 phase_sites=3983 phase_rhmr=1942962 shots=9024 contract=phase&~classical final=classical_mask==0&&clean_phase_mask==0 raw_phase=not-claimed cuda_phase=not-claimed'

die() {
    echo "verify-q1273-phase: FAIL: $*" >&2
    exit 1
}

sha256() {
    shasum -a 256 -- "$1" | awk '{print $1}'
}

assert_sha() {
    local path=$1 expected=$2 actual
    actual=$(sha256 "$path")
    [[ $actual == "$expected" ]] || die "$path sha256 $actual != $expected"
}

set_to_lines() {
    local encoded=$1 output=$2 body
    : >"$output"
    [[ $encoded == '{}' ]] && return 0
    [[ $encoded == \{*\} ]] || die "malformed fixture set: $encoded"
    body=${encoded#\{}
    body=${body%\}}
    [[ -n $body ]] || die "non-canonical empty fixture set"
    tr ',' '\n' <<<"$body" >"$output"
}

expect_reject() {
    local label=$1 expected_rc=$2 stream=$3
    shift 3
    set +e
    PPF_OPS="$stream" "$@" >"$tmp/$label.stdout" 2>"$tmp/$label.stderr"
    local rc=$?
    set -e
    [[ $rc -eq $expected_rc ]] || die "$label returned $rc, expected $expected_rc"
    [[ ! -s "$tmp/$label.stdout" ]] || die "$label emitted stdout"
}

for command in g++ python3 shasum awk cmp rg; do
    command -v "$command" >/dev/null || die "missing command: $command"
done
[[ -f $ops ]] || die "ops stream not found: $ops"

tmp=$(mktemp -d "${TMPDIR:-/tmp}/q1273-phase-verify.XXXXXX")
trap 'rm -rf -- "$tmp"' EXIT

assert_sha "$ops" "$expected_ops_sha"
assert_sha "$fixture" "$expected_fixture_sha"
assert_sha "$schedule" "$expected_schedule_sha"
assert_sha "$header" "$expected_header_sha"
assert_sha "$generator" "$expected_generator_sha"

python3 "$generator" "$schedule" "$tmp/pp_phase_schedule.h" "$tmp/schedule.tsv" \
    >"$tmp/generator.stdout"
cmp -s "$header" "$tmp/pp_phase_schedule.h" || die "generated header is not reproducible"
cmp -s "$schedule" "$tmp/schedule.tsv" || die "generated schedule is not reproducible"

"$script_dir/build_phase_cpu.sh" "$tmp/ppcpu"
g++ -O3 -std=c++17 -pthread -Wall -Wextra -Werror -Wno-unused-parameter \
    -DPP_EXPECTED_STATE_DIGEST_OVERRIDE=0x2148e09f4c4293b3ULL \
    -o "$tmp/ppcpu-bad-digest" "$source_cpp"
g++ -O3 -std=c++17 -pthread -Wall -Wextra -Werror -Wno-unused-parameter \
    -DPP_PHASE_FORCE_BAD_SCHEDULE \
    -o "$tmp/ppcpu-bad-schedule" "$source_cpp"

PPF_OPS="$ops" "$tmp/ppcpu" shaketest >"$tmp/shake.stdout" 2>"$tmp/shake.stderr"
[[ ! -s "$tmp/shake.stdout" ]] || die "SHAKE KAT emitted stdout"
cat >"$tmp/shake.expected" <<'EOF'
empty: 46b9dd2b0ba88d13233b3feb743eeb243fcd52ea62b81b82b50c27646ed5762f
ref  : 46b9dd2b0ba88d13233b3feb743eeb243fcd52ea62b81b82b50c27646ed5762f
abc  : 483366601360a8771c6863080cc4114d8db44530f8f1e1ee4f94ea37e78b5739
ref  : 483366601360a8771c6863080cc4114d8db44530f8f1e1ee4f94ea37e78b5739
EOF
cmp -s "$tmp/shake.expected" "$tmp/shake.stderr" || die "SHAKE KAT mismatch"

PPF_OPS="$ops" "$tmp/ppcpu" identity >"$tmp/identity.stdout" 2>"$tmp/identity.stderr"
[[ $(cat "$tmp/identity.stdout") == "$expected_identity" ]] || die "identity mismatch"
PPF_OPS="$ops" "$tmp/ppcpu" identity >"$tmp/identity-repeat.stdout" \
    2>"$tmp/identity-repeat.stderr"
cmp -s "$tmp/identity.stdout" "$tmp/identity-repeat.stdout" || die "identity stdout is not deterministic"
cmp -s "$tmp/identity.stderr" "$tmp/identity-repeat.stderr" || die "identity stderr is not deterministic"

python3 - "$ops" "$tmp" <<'PY'
import pathlib
import struct
import sys

source = pathlib.Path(sys.argv[1]).read_bytes()
out = pathlib.Path(sys.argv[2])
variants = {}
bad_magic = bytearray(source)
bad_magic[0] ^= 1
variants["bad-magic.bin"] = bad_magic
bad_count = bytearray(source)
struct.pack_into("<Q", bad_count, 8, 12_933_806)
variants["bad-count.bin"] = bad_count
bad_sha = bytearray(source)
bad_sha[16] ^= 1
variants["bad-sha.bin"] = bad_sha
for name, data in variants.items():
    (out / name).write_bytes(data)
PY
assert_sha "$tmp/bad-magic.bin" 23f6177d26d482b76ff0c76231fab86e40fde6563660fb34de3d314555fbddb6
assert_sha "$tmp/bad-count.bin" 2a710e4069c79488a027cfd42cfec09b5d263af57fdfe725bbd6a55440ffe1f9
assert_sha "$tmp/bad-sha.bin" 58a0de67b0d595b11a4a0e5f8a50098748dc4edf47e917744742d4a01bbd6458
expect_reject bad-magic 1 "$tmp/bad-magic.bin" "$tmp/ppcpu" identity
expect_reject bad-count 2 "$tmp/bad-count.bin" "$tmp/ppcpu" identity
expect_reject bad-sha 2 "$tmp/bad-sha.bin" "$tmp/ppcpu" identity
expect_reject bad-digest 2 "$ops" "$tmp/ppcpu-bad-digest" identity
expect_reject bad-schedule 2 "$ops" "$tmp/ppcpu-bad-schedule" \
    phasefaultshots 100000045835813
rg -q 'phase schedule mismatch' "$tmp/bad-schedule.stderr" || \
    die "wrong-schedule negative did not reach the schedule gate"
expect_reject scan-disabled 2 "$ops" "$tmp/ppcpu" scan

for bad_nonce in '' 00 +1 -1 281474976710656 18446744073709551616 abc; do
    label=$(printf '%s' "$bad_nonce" | shasum -a 256 | awk '{print "nonce-" substr($1,1,12)}')
    expect_reject "$label" 2 "$ops" "$tmp/ppcpu" phasefaultshots "$bad_nonce"
done

phase_rows=0
while IFS=$'\t' read -r nonce classical_count raw_phase_count phase_count \
    classical_sha phase_sha classical_set phase_set; do
    [[ $nonce == \#* ]] && continue
    [[ -n $phase_set ]] || die "short phase fixture row"
    phase_rows=$((phase_rows + 1))
    set_to_lines "$phase_set" "$tmp/phase-$nonce.expected"
    PPF_OPS="$ops" "$tmp/ppcpu" phasefaultshots "$nonce" \
        >"$tmp/phase-$nonce.actual" 2>"$tmp/phase-$nonce.stderr"
    awk 'NF != 1 || $1 !~ /^[0-9]+$/ { exit 1 }' "$tmp/phase-$nonce.actual" || \
        die "malformed phase output for nonce $nonce"
    cmp -s "$tmp/phase-$nonce.expected" "$tmp/phase-$nonce.actual" || \
        die "complete conditional-phase set mismatch for nonce $nonce"
    [[ $(wc -l <"$tmp/phase-$nonce.actual" | tr -d ' ') == "$phase_count" ]] || \
        die "conditional-phase count mismatch for nonce $nonce"
    [[ $(sha256 "$tmp/phase-$nonce.actual") == "$phase_sha" ]] || \
        die "conditional-phase hash mismatch for nonce $nonce"
    rg -q 'source=093d85d64de87aa5006a94868172f642daacf136' \
        "$tmp/phase-$nonce.stderr" || die "missing source binding for nonce $nonce"
    rg -q 'contract=phase&~classical raw_phase=not-claimed cuda_phase=not-claimed' \
        "$tmp/phase-$nonce.stderr" || die "missing conditional contract for nonce $nonce"
done <"$fixture"
[[ $phase_rows -eq 17 ]] || die "phase corpus contains $phase_rows rows, expected 17"

inherited=100000045835813
PPF_OPS="$ops" "$tmp/ppcpu" phasefaultshots "$inherited" \
    >"$tmp/phase-repeat.stdout" 2>"$tmp/phase-repeat.stderr"
cmp -s "$tmp/phase-$inherited.actual" "$tmp/phase-repeat.stdout" || \
    die "phase stdout is not deterministic"
cmp -s "$tmp/phase-$inherited.stderr" "$tmp/phase-repeat.stderr" || \
    die "phase stderr is not deterministic"

classical_rows=0
classical_exact_rows=0
known_classical_fp_rows=0
while IFS=$'\t' read -r nonce classical_count raw_phase_count phase_count \
    classical_sha phase_sha classical_set phase_set; do
    [[ $nonce == \#* ]] && continue
    [[ -n $phase_set ]] || die "short classical fixture row"
    classical_rows=$((classical_rows + 1))
    set_to_lines "$classical_set" "$tmp/classical-$nonce.expected"
    PPF_OPS="$ops" "$tmp/ppcpu" faultshots "$nonce" \
        >"$tmp/classical-$nonce.full" 2>"$tmp/classical-$nonce.stderr"
    awk 'NF != 2 || $1 !~ /^[0-9]+$/ || $2 !~ /^[0-9]+$/ { exit 1 } { print $1 }' \
        "$tmp/classical-$nonce.full" >"$tmp/classical-$nonce.actual" || \
        die "malformed classical output for nonce $nonce"
    if cmp -s "$tmp/classical-$nonce.expected" "$tmp/classical-$nonce.actual"; then
        [[ $(wc -l <"$tmp/classical-$nonce.actual" | tr -d ' ') == "$classical_count" ]] || \
            die "classical count mismatch for nonce $nonce"
        [[ $(sha256 "$tmp/classical-$nonce.actual") == "$classical_sha" ]] || \
            die "classical hash mismatch for nonce $nonce"
        classical_exact_rows=$((classical_exact_rows + 1))
    elif [[ $nonce == 730140001442 ]]; then
        # The balanced classical model has one sealed false positive on the
        # disjoint phase corpus.  This must remain exactly one extra shot and
        # therefore keeps combined hunt use on HOLD.  Accepting arbitrary
        # classical drift here would invalidate the conditional-phase mask.
        [[ $(wc -l <"$tmp/classical-$nonce.actual" | tr -d ' ') == 20 ]] || \
            die "known classical FP row does not contain exactly 20 predictions"
        [[ $(sha256 "$tmp/classical-$nonce.actual") == \
            acfa410b8f687b0a3da4a2d3d1c56eeb247d8300f7a49e4457b058fddf58cacf ]] || \
            die "known classical FP set drifted"
        [[ $(sha256 "$tmp/classical-$nonce.full") == \
            b4ab770cc46b111edab12e4c60083354b2449c0720b0498f5c2e5253fdbecb85 ]] || \
            die "known classical FP masks drifted"
        [[ $(rg -c '^6329 1$' "$tmp/classical-$nonce.full") == 1 ]] || \
            die "known classical FP is not exactly shot 6329 mask 1"
        awk '$1 != 6329 { print $1 }' "$tmp/classical-$nonce.full" \
            >"$tmp/classical-$nonce.without-known-fp"
        cmp -s "$tmp/classical-$nonce.expected" \
            "$tmp/classical-$nonce.without-known-fp" || \
            die "classical mismatch exceeds known shot 6329 FP"
        known_classical_fp_rows=$((known_classical_fp_rows + 1))
    else
        die "complete classical set mismatch for nonce $nonce"
    fi
done <"$fixture"
[[ $classical_rows -eq 17 ]] || die "classical corpus contains $classical_rows rows, expected 17"
[[ $classical_exact_rows -eq 16 && $known_classical_fp_rows -eq 1 ]] || \
    die "classical HOLD boundary changed: exact=$classical_exact_rows known_fp=$known_classical_fp_rows"

binary_sha=$(sha256 "$tmp/ppcpu")
identity_sha=$(sha256 "$tmp/identity.stdout")
phase_determinism_sha=$(sha256 "$tmp/phase-repeat.stdout")
echo "verify-q1273-phase: PASS_PHASE source=093d85d64de87aa5006a94868172f642daacf136 ops=12933805 ops_sha256=$expected_ops_sha predictor_digest=2148e09f4c4293b2 phase_exact=$phase_rows/$phase_rows classical_oracle_exact=$classical_exact_rows/$classical_rows known_classical_fp=nonce730140001442:shot6329:mask1 combined_hunt=HOLD binary_sha256=$binary_sha identity_sha256=$identity_sha inherited_phase_sha256=$phase_determinism_sha contract=phase&~classical raw_phase=not-claimed cuda_phase=not-claimed"
