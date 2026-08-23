#!/usr/bin/env bash
set -euo pipefail

PK=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
OPS_ROOT=${ECDSA_OPS_ROOT:-/Users/olifreuler/ecdsa-ops}
# shellcheck disable=SC1091
. "$PK/WAVE.meta"
PILOT="$OPS_ROOT/$PILOT_PACKET_DIR"
RECEIPT="$OPS_ROOT/$PILOT_RECEIPT_DIR"
RR="$RECEIPT/remote-receipts"

sha256_file() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$1" | awk '{print $1}'
    else
        shasum -a 256 "$1" | awk '{print $1}'
    fi
}
field() {
    local key=$1 path=$2
    awk -F= -v k="$key" '$1 == k {print substr($0, length(k)+2); n++} END {if(n != 1) exit 1}' "$path"
}
require_sha() {
    local path=$1 want=$2 got
    test -f "$path" || { echo "missing: $path" >&2; exit 66; }
    got=$(sha256_file "$path")
    test "$got" = "$want" || { echo "hash drift: $path" >&2; exit 65; }
}

"$PILOT/verify_pilot.sh" >/dev/null
require_sha "$PILOT/MANIFEST.sha256" "$PILOT_PACKET_MANIFEST_SHA256"
require_sha "$OPS_ROOT/$PILOT_PACKET_DIR.tar.gz" "$PILOT_PACKET_ARCHIVE_SHA256"
require_sha "$RECEIPT/q1272-selector-pilot-receipts.tgz" "$PILOT_RECEIPT_ARCHIVE_SHA256"
require_sha "$RECEIPT/PILOT.intent" "$PILOT_INTENT_SHA256"
require_sha "$RECEIPT/PILOT.authorization" "$PILOT_AUTHORIZATION_SHA256"
require_sha "$RR/pilot/PILOT.complete" "$PILOT_COMPLETE_SHA256"
cmp "$RECEIPT/PILOT.intent" "$RR/receipts/PILOT.intent"
cmp "$RECEIPT/PILOT.authorization" "$RR/PILOT.authorization"

files=$(find "$RR" -type f | wc -l | tr -d ' ')
test "$files" = "$PILOT_RECEIPT_FILE_COUNT"
dirs=$(find "$RR/pilot/chunks" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
test "$dirs" = "$PILOT_CHUNKS"
test "$(field status "$RR/pilot/PILOT.complete")" = TERMINAL_NO_EXTENSION_NO_SUBMISSION
test "$(field pilot_from "$RR/pilot/PILOT.complete")" = "$PILOT_FROM"
test "$(field pilot_to_exclusive "$RR/pilot/PILOT.complete")" = "$PILOT_TO_EXCLUSIVE"
test "$(field screened "$RR/pilot/PILOT.complete")" = "$PILOT_COUNT"
test "$(field chunks "$RR/pilot/PILOT.complete")" = "$PILOT_CHUNKS"
test "$(field survivors "$RR/pilot/PILOT.complete")" = "$PILOT_SURVIVORS"
test "$(field terminal_full_9024 "$RR/pilot/PILOT.complete")" = 0
test "$(field clean_strict_beat "$RR/pilot/PILOT.complete")" = 0
test "$(field dirty "$RR/pilot/PILOT.complete")" = 0
test "$(field all_survivors_full_9024 "$RR/pilot/PILOT.complete")" = yes
test "$(field extension_authorized "$RR/pilot/PILOT.complete")" = no
test "$(field submission_authorized "$RR/pilot/PILOT.complete")" = no
test "$(field next_nonce "$RR/pilot/PILOT.checkpoint")" = "$PILOT_TO_EXCLUSIVE"
test "$(field completed_chunks "$RR/pilot/PILOT.checkpoint")" = "$PILOT_CHUNKS"
cmp "$RR/pilot/receipts/GPU.pre" "$RR/pilot/receipts/GPU.post"
test ! -s "$RR/pilot/receipts/ALL-SURVIVORS.nonces"
test ! -s "$RR/pilot/receipts/ALL-TERMINALS.sha256"

if command -v sha256sum >/dev/null 2>&1; then
    (cd "$RR/pilot" && sha256sum -c receipts/SCANS.sha256 >/dev/null)
    (cd "$RR/pilot" && sha256sum -c receipts/CONFIRMS.sha256 >/dev/null)
else
    (cd "$RR/pilot" && shasum -a 256 -c receipts/SCANS.sha256 >/dev/null)
    (cd "$RR/pilot" && shasum -a 256 -c receipts/CONFIRMS.sha256 >/dev/null)
fi

next=$PILOT_FROM
chunks=0
rows=0
while test "$next" -lt "$PILOT_TO_EXCLUSIVE"; do
    end=$((next + 50000))
    C="$RR/pilot/chunks/$next-$end"
    test -d "$C"
    test "$(find "$C" -type f | wc -l | tr -d ' ')" = 7
    test "$(field from "$C/SCAN.complete")" = "$next"
    test "$(field to_exclusive "$C/SCAN.complete")" = "$end"
    test "$(field count "$C/SCAN.complete")" = 50000
    test "$(field survivors "$C/SCAN.complete")" = 0
    test "$(field ops_sha256 "$C/SCAN.complete")" = "$OPS_SHA256"
    test "$(field checkpoint_sha256 "$C/SCAN.complete")" = "$CHECKPOINT_SHA256"
    test "$(field ppgpu_sha256 "$C/SCAN.complete")" = "$LINUX_PPGPU_SHA256"
    test "$(field parity_receipt_sha256 "$C/SCAN.complete")" = "$PARITY_TERMINAL_RECEIPT_SHA256"
    test "$(field mode "$C/SCAN.complete")" = exact_complete_9024_classical
    require_sha "$C/raw.tsv" "$(field raw_sha256 "$C/SCAN.complete")"
    require_sha "$C/scan.stderr" "$(field scan_stderr_sha256 "$C/SCAN.complete")"
    require_sha "$C/survivors.nonces" "$(field survivors_sha256 "$C/SCAN.complete")"
    require_sha "$C/validator.stderr" "$(field validator_stderr_sha256 "$C/SCAN.complete")"
    test ! -s "$C/survivors.nonces"
    test ! -s "$C/TERMINALS.sha256"
    perl "$PILOT/tools/validate_scan_output.pl" "$C/raw.tsv" "$next" "$end" >/dev/null 2>&1
    test "$(field terminal "$C/CONFIRM.complete")" = 0
    test "$(field clean_strict_beat "$C/CONFIRM.complete")" = 0
    test "$(field dirty "$C/CONFIRM.complete")" = 0
    test "$(field all_survivors_full_9024 "$C/CONFIRM.complete")" = yes
    next=$end
    chunks=$((chunks + 1))
    rows=$((rows + 50000))
done
test "$next" = "$PILOT_TO_EXCLUSIVE"
test "$chunks" = "$PILOT_CHUNKS"
test "$rows" = "$PILOT_COUNT"

printf 'Q1272_SELECTOR_PILOT_AUDIT_OK files=%s chunks=%s rows=%s survivors=0 full9024=0 terminal=%s\n' \
    "$files" "$chunks" "$rows" "$PILOT_COMPLETE_SHA256"
