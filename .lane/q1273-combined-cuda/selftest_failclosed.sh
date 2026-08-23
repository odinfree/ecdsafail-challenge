#!/usr/bin/env bash
set -euo pipefail

if test "$#" -ne 2; then
    echo "usage: $0 /exact/ops.bin /built/workspace" >&2
    exit 64
fi

lane=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ops=$1
workspace=$2
# shellcheck disable=SC1091
. "$lane/HANDOFF.meta"
ppgpu="$workspace/bin/ppgpu"
test -x "$ppgpu"
test -x "$workspace/bin/ppgpu-bad-digest"
test -x "$workspace/bin/ppgpu-bad-schedule"
test -f "$workspace/receipts/BUILD.complete"
mkdir -p "$workspace/negative-results"

expect_exit() {
    local expected=$1 label=$2 stream=$3
    shift 3
    set +e
    PPF_OPS="$stream" "$@" >"$workspace/negative-results/$label.stdout" \
        2>"$workspace/negative-results/$label.stderr"
    local actual=$?
    set -e
    test "$actual" = "$expected" || {
        echo "$label: got exit $actual, expected $expected" >&2
        exit 1
    }
    test ! -s "$workspace/negative-results/$label.stdout" || {
        echo "$label emitted result stdout" >&2
        exit 1
    }
}

perl - "$ops" "$workspace/negative-results" <<'PERL'
use strict;
use warnings;
my ($source, $out) = @ARGV;
open my $fh, '<:raw', $source or die $!;
local $/;
my $blob = <$fh>;
close $fh;
my $magic = $blob; substr($magic, 0, 1) = chr(ord(substr($magic, 0, 1)) ^ 1);
my $count = $blob; substr($count, 8, 8) = pack('Q<', 12_933_806);
my $sha = $blob; substr($sha, 16, 1) = chr(ord(substr($sha, 16, 1)) ^ 1);
for my $pair (['bad-magic.bin', $magic], ['bad-count.bin', $count], ['bad-sha.bin', $sha]) {
    open my $o, '>:raw', "$out/$pair->[0]" or die $!;
    print {$o} $pair->[1];
    close $o or die $!;
}
PERL

expect_exit 1 bad-magic "$workspace/negative-results/bad-magic.bin" "$ppgpu" identity
expect_exit 2 wrong-count "$workspace/negative-results/bad-count.bin" "$ppgpu" identity
expect_exit 2 wrong-sha "$workspace/negative-results/bad-sha.bin" "$ppgpu" identity
expect_exit 2 wrong-state "$ops" "$workspace/bin/ppgpu-bad-digest" identity
expect_exit 2 wrong-schedule "$ops" "$workspace/bin/ppgpu-bad-schedule" \
    phasefaultshots 100000045835813
expect_exit 1 missing-stream "$workspace/negative-results/missing.bin" "$ppgpu" identity
expect_exit 2 scan-disabled "$ops" "$ppgpu" scan
expect_exit 2 range-from-disabled "$ops" "$ppgpu" --from 1
expect_exit 2 range-to-disabled "$ops" "$ppgpu" --to 2
expect_exit 2 screen-disabled "$ops" "$ppgpu" --screen
expect_exit 2 unknown-selector "$ops" "$ppgpu" survivors 1

for bad_nonce in '' 00 +1 -1 281474976710656 18446744073709551616 abc; do
    label=$(printf '%s' "$bad_nonce" | sha256sum | awk '{print "nonce-" substr($1,1,12)}')
    expect_exit 2 "$label" "$ops" "$ppgpu" faultshots "$bad_nonce"
done

(
    cd "$workspace/negative-results"
    find . -type f -print | LC_ALL=C sort | while IFS= read -r path; do
        sha256sum "$path"
    done
) >"$workspace/receipts/NEGATIVES.sha256"
{
    printf 'packet_id=%s\nnegative_cases=18\n' "$PACKET_ID"
    printf 'negative_manifest_sha256=%s\n' \
        "$(sha256sum "$workspace/receipts/NEGATIVES.sha256" | awk '{print $1}')"
    printf 'result_stdout_empty=yes\nscan_mode=disabled\nrange_authorized=no\n'
} >"$workspace/receipts/NEGATIVES.complete.tmp"
mv "$workspace/receipts/NEGATIVES.complete.tmp" \
    "$workspace/receipts/NEGATIVES.complete"
printf 'Q1273_CUDA_NEGATIVES_OK cases=18 scan=disabled range=no\n'
