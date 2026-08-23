#!/usr/bin/env bash
set -euo pipefail

PK=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
OPS_ROOT=${ECDSA_OPS_ROOT:-/Users/olifreuler/ecdsa-ops}
# shellcheck disable=SC1091
. "$PK/WAVE.meta"
PARENT="$OPS_ROOT/$PARENT_PACKET_DIR"
PILOT="$OPS_ROOT/$PILOT_PACKET_DIR"

sha256_file() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$1" | awk '{print $1}'
    else
        shasum -a 256 "$1" | awk '{print $1}'
    fi
}

test -f "$PK/MANIFEST.sha256" || { echo 'packet is not sealed' >&2; exit 66; }
if command -v sha256sum >/dev/null 2>&1; then
    (cd "$PK" && sha256sum -c MANIFEST.sha256 >/dev/null)
else
    (cd "$PK" && shasum -a 256 -c MANIFEST.sha256 >/dev/null)
fi

test "$PACKET_ID" = q1272-selector-extension-1b-72b8a97-v1
test "$STATUS" = SUPERSEDED_UNACTIVATED
test "$CIRCUIT_SOURCE_COMMIT" = 14608572e84daf89397768c43ac0d812c714c3bd
test "$OPS_COUNT" = 12908488
test "$QUBITS" = 1272
test "$OPS_SHA256" = 678c149f65ce00cd44caada6a534817e8b69f993913c509a8b396b6f526c22f0
test "$CHECKPOINT_SHA256" = 0dbd37238642df839b7672e25a85d2d5183c202102f80388de749feaecf1c361
test "$(sha256_file "$PARENT/MANIFEST.sha256")" = "$PARENT_MANIFEST_SHA256"
"$PARENT/verify_packet.sh" >/dev/null
"$PILOT/verify_pilot.sh" >/dev/null
"$PK/audit_pilot.sh" >/dev/null

test "$((WAVE_TO_EXCLUSIVE - WAVE_FROM))" = "$WAVE_COUNT"
test "$WAVE_FROM" = "$PILOT_TO_EXCLUSIVE"
test "$WAVE_COUNT" = 1000000000
test "$RECOMMENDED_HOSTS" = 20
test "$SHARD_COUNT" = 20
test "$SHARD_SIZE" = 50000000
test "$CHUNK_SIZE" = 1000000
test "$CHUNKS_PER_SHARD" = 50
test "$FULL_EVAL_SHOTS" = 9024
test "$SCAN_MODE" = EXACT_COMPLETE_9024_CLASSICAL
test "$WAVE_TO_EXCLUSIVE" -lt 281474976710656
test "$RANGE_DECLARED" = NO
test "$PROVIDER_AUTHORIZED" = NO
test "$AUTO_EXTENSION" = NO
test "$SUBMISSION_AUTHORIZED" = NO

computed_t_max=$(( (FROZEN_LEADER_SCORE - 1) / QUBITS ))
test "$computed_t_max" = "$STRICT_ROUNDED_T_MAX"
test "$STRICT_ROUNDED_T_MAX" = 914961
test "$CANDIDATE_SCORE" = "$((QUBITS * CANDIDATE_ROUNDED_T))"
test "$FROZEN_SCORE_MARGIN" = "$((FROZEN_LEADER_SCORE - CANDIDATE_SCORE))"
test "$((QUBITS * STRICT_ROUNDED_T_MAX))" -lt "$FROZEN_LEADER_SCORE"
test "$((QUBITS * (STRICT_ROUNDED_T_MAX + 1)))" -ge "$FROZEN_LEADER_SCORE"

perl "$PK/tools/validate_shards.pl" "$PK/SHARDS.tsv" \
    "$PILOT/OCCUPIED-Q1272-RANGES.tsv" \
    "$PARENT/fixtures/h64.nonces" "$PARENT/fixtures/d32.nonces" \
    "$WAVE_FROM" "$WAVE_TO_EXCLUSIVE" "$PILOT_FROM" "$PILOT_TO_EXCLUSIVE" >/dev/null

test ! -e "$PK/WAVE.authorization"
test ! -e "$PK/HOSTS.assigned.tsv"
if rg -n '([v]astai|[r]unpod|[s]sh |[s]cp |ecdsafail [s]ubmit|[c]url |[w]get )' \
    "$PK"/*.sh "$PK"/tools/*.pl >/dev/null; then
    echo 'provider, network, or submission primitive in local packet' >&2
    exit 65
fi

printf 'Q1272_SELECTOR_EXTENSION_SUPERSEDED_OK source=%s wave=[%s,%s) shards=%s count=%s strict_t_max=%s provider=unused range=undeclared auto_extension=no\n' \
    "$CIRCUIT_SOURCE_COMMIT" "$WAVE_FROM" "$WAVE_TO_EXCLUSIVE" \
    "$SHARD_COUNT" "$WAVE_COUNT" "$STRICT_ROUNDED_T_MAX"
