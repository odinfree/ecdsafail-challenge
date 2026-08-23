#!/usr/bin/env bash
set -euo pipefail

PK=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
OPS_ROOT=${ECDSA_OPS_ROOT:-/Users/olifreuler/ecdsa-ops}
# shellcheck disable=SC1091
. "$PK/WAVE.meta"
PARENT="$OPS_ROOT/$PARENT_PACKET_DIR"
PILOT="$OPS_ROOT/$PILOT_PACKET_DIR"
"$PK/verify_packet.sh" >/dev/null

tmp=$(mktemp -d /tmp/q1272-selector-extension-selftest.XXXXXX)
cleanup() {
    find "$tmp" -type f -delete 2>/dev/null || true
    find "$tmp" -depth -type d -exec rmdir {} \; 2>/dev/null || true
}
trap cleanup EXIT

expect_fail() {
    local label=$1
    shift
    set +e
    "$@" >"$tmp/$label.stdout" 2>"$tmp/$label.stderr"
    local rc=$?
    set -e
    test "$rc" -ne 0 || { echo "$label unexpectedly passed" >&2; exit 1; }
}
validate() {
    perl "$PK/tools/validate_shards.pl" "$1" \
        "$PILOT/OCCUPIED-Q1272-RANGES.tsv" \
        "$PARENT/fixtures/h64.nonces" "$PARENT/fixtures/d32.nonces" \
        "$WAVE_FROM" "$WAVE_TO_EXCLUSIVE" "$PILOT_FROM" "$PILOT_TO_EXCLUSIVE"
}

sed 's/^slot01\t100000036457280\t100000086457280/slot01\t100000036457279\t100000086457279/' \
    "$PK/SHARDS.tsv" >"$tmp/overlap.tsv"
expect_fail overlap validate "$tmp/overlap.tsv"
sed 's/^slot02\t100000086457280\t100000136457280/slot02\t100000086457281\t100000136457281/' \
    "$PK/SHARDS.tsv" >"$tmp/gap.tsv"
expect_fail gap validate "$tmp/gap.tsv"
sed '0,/planned_not_declared/s//declared/' "$PK/SHARDS.tsv" >"$tmp/declared.tsv"
expect_fail premature-declaration validate "$tmp/declared.tsv"
test ! -e "$PK/WAVE.authorization"
test ! -e "$PK/HOSTS.assigned.tsv"

for script in "$PK"/*.sh; do bash -n "$script"; done
for script in "$PK"/tools/*.pl; do perl -c "$script" >/dev/null; done

printf 'Q1272_SELECTOR_EXTENSION_FAILCLOSED_OK range_negatives=3 authorization=absent host_assignment=absent provider_paths=0\n'
