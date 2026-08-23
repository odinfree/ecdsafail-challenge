#!/usr/bin/env bash
set -euo pipefail

PK=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
# shellcheck disable=SC1091
. "$PK/PACKET.meta"

sha256_file() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$1" | awk '{print $1}'
    else
        shasum -a 256 "$1" | awk '{print $1}'
    fi
}

require_sha() {
    local path=$1 want=$2 got
    test -f "$path" || { echo "missing packet file: $path" >&2; exit 66; }
    got=$(sha256_file "$path")
    test "$got" = "$want" || {
        echo "packet hash mismatch: $path ($got != $want)" >&2
        exit 65
    }
}

test "$PACKET_ID" = q1272-selector-parity-v1
test "$CPU_EVIDENCE_COMMIT" = 72b8a97a459344300828eb63c3a0d61fa0b6cc2b
test "$CUDA_SOURCE_COMMIT" = 2246f4c52f35443f84e3bbaeb9a3f40dbb241161
test "$CIRCUIT_SOURCE_COMMIT" = 14608572e84daf89397768c43ac0d812c714c3bd
test "$OPS_COUNT" = 12908488
test "$QUBITS" = 1272
test "$OPS_SHA256" = 678c149f65ce00cd44caada6a534817e8b69f993913c509a8b396b6f526c22f0
test "$CHECKPOINT_SHA256" = 0dbd37238642df839b7672e25a85d2d5183c202102f80388de749feaecf1c361

test -f "$PK/MANIFEST.sha256"
if command -v sha256sum >/dev/null 2>&1; then
    (cd "$PK" && sha256sum -c MANIFEST.sha256 >/dev/null)
else
    (cd "$PK" && shasum -a 256 -c MANIFEST.sha256 >/dev/null)
fi

require_sha "$PK/source/cpu-72b8a97.tar" "$CPU_SOURCE_ARCHIVE_SHA256"
require_sha "$PK/source/cuda-2246f4c.tar" "$CUDA_SOURCE_ARCHIVE_SHA256"
require_sha "$PK/artifacts/ops.bin" "$OPS_SHA256"
require_sha "$PK/artifacts/checkpoint.bin" "$CHECKPOINT_SHA256"
require_sha "$PK/tools/compare_fault_masks.pl" "$COMPARATOR_SHA256"
require_sha "$PK/fixtures/h64.nonces" "$H64_NONCES_SHA256"
require_sha "$PK/fixtures/h64.expected.tsv" "$H64_EXPECTED_MASKS_SHA256"
require_sha "$PK/fixtures/h64.evaluator.tsv" "$H64_EVALUATOR_MASKS_SHA256"
require_sha "$PK/fixtures/d32.nonces" "$D32_NONCES_SHA256"
require_sha "$PK/fixtures/d32.expected.tsv" "$D32_EXPECTED_MASKS_SHA256"
require_sha "$PK/fixtures/d32.evaluator.tsv" "$D32_EVALUATOR_MASKS_SHA256"

test "$(tar -xOf "$PK/source/cpu-72b8a97.tar" cpu-source/src/bin/pingpong_filter.rs | sha256_file /dev/stdin)" = \
    "$CPU_PREDICTOR_SOURCE_SHA256"
test "$(tar -xOf "$PK/source/cuda-2246f4c.tar" cuda-source/.lane/q1272-cuda/pingpong_filter.cu | sha256_file /dev/stdin)" = \
    "$CUDA_SOURCE_SHA256"

perl - "$PK/artifacts/ops.bin" "$OPS_COUNT" "$PK/artifacts/checkpoint.bin" \
    "$CHECKPOINT_SIZE" "$CHECKPOINT_RESIDUAL_LEN" <<'PERL'
use strict;
use warnings;
my ($ops_path, $want_ops, $ckp_path, $want_size, $want_residual) = @ARGV;
open my $ops, '<:raw', $ops_path or die $!;
read($ops, my $oh, 16) == 16 or die "short ops header\n";
my ($omagic, $ocount) = unpack('a8Q<', $oh);
die "bad ops header\n" unless $omagic eq 'QECCOPSZ' && $ocount == $want_ops;
close $ops or die $!;
open my $ckp, '<:raw', $ckp_path or die $!;
my $size = -s $ckp_path;
read($ckp, my $ch, 24) == 24 or die "short checkpoint header\n";
my ($cmagic, $ccount, $residual) = unpack('a8Q<Q<', $ch);
die "bad checkpoint header\n" unless $size == $want_size &&
    $cmagic eq 'PPFSCKP1' && $ccount == $want_ops && $residual == $want_residual;
close $ckp or die $!;
PERL

test "$(wc -l < "$PK/fixtures/h64.nonces" | tr -d ' ')" = "$H64_ROWS"
test "$(wc -l < "$PK/fixtures/d32.nonces" | tr -d ' ')" = "$D32_ROWS"
test "$(sort -u "$PK/fixtures/h64.nonces" | wc -l | tr -d ' ')" = "$H64_ROWS"
test "$(sort -u "$PK/fixtures/d32.nonces" | wc -l | tr -d ' ')" = "$D32_ROWS"
test -z "$(comm -12 <(sort -n "$PK/fixtures/h64.nonces") <(sort -n "$PK/fixtures/d32.nonces"))"

h64_cmp=$(perl "$PK/tools/compare_fault_masks.pl" \
    "$PK/fixtures/h64.evaluator.tsv" "$PK/fixtures/h64.expected.tsv")
d32_cmp=$(perl "$PK/tools/compare_fault_masks.pl" \
    "$PK/fixtures/d32.evaluator.tsv" "$PK/fixtures/d32.expected.tsv")
test "$h64_cmp" = "rows=$H64_ROWS evaluator_faults=$H64_CLASSICAL_FAULTS predictor_faults=$H64_CLASSICAL_FAULTS exact=$H64_ROWS mismatches=0"
test "$d32_cmp" = "rows=$D32_ROWS evaluator_faults=$D32_CLASSICAL_FAULTS predictor_faults=$D32_CLASSICAL_FAULTS exact=$D32_ROWS mismatches=0"

perl - "$PK/artifacts/checkpoint.bin" "$PK/negative/wrong-state.checkpoint" \
    "$PK/negative/wrong-count.checkpoint" "$PK/negative/bad-magic.checkpoint" \
    "$PK/negative/short.checkpoint" "$OPS_COUNT" "$CHECKPOINT_SIZE" <<'PERL'
use strict;
use warnings;
my ($good, $state, $count, $magic, $short, $want_ops, $want_size) = @ARGV;
sub read_all { my ($p)=@_; open my $f,'<:raw',$p or die $!; local $/; my $x=<$f>; close $f; return $x; }
my $g=read_all($good); my $s=read_all($state); my $c=read_all($count);
my $m=read_all($magic); my $h=read_all($short);
die unless length($g)==$want_size && length($s)==$want_size && length($c)==$want_size && length($m)==$want_size;
die unless length($h)==$want_size-1;
die unless substr($s,0,24) eq substr($g,0,24) && $s ne $g;
die unless substr($c,0,8) eq 'PPFSCKP1' && unpack('Q<',substr($c,8,8))==$want_ops-1;
die unless substr($m,0,8) ne 'PPFSCKP1';
PERL

printf 'Q1272_SELECTOR_PARITY_PACKET_OK rows=%s cpu_faults=%s checkpoint=%s\n' \
    "$((H64_ROWS + D32_ROWS))" "$((H64_CLASSICAL_FAULTS + D32_CLASSICAL_FAULTS))" \
    "$CHECKPOINT_SHA256"
