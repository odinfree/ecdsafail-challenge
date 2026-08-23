#!/usr/bin/env bash
set -euo pipefail

if test "$#" -ne 1; then
    echo "usage: $0 /built/workspace" >&2
    exit 64
fi

PK=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
W=$1
# shellcheck disable=SC1091
. "$PK/PACKET.meta"
PPGPU="$W/bin/ppgpu"
test -x "$PPGPU"
test -f "$W/receipts/BUILD.complete"
test ! -e "$W/receipts/NEGATIVES.complete"
mkdir -p "$W/negative-results"

expect_exit() {
    local want=$1 label=$2
    shift 2
    set +e
    "$@" > "$W/negative-results/$label.stdout" 2> "$W/negative-results/$label.stderr"
    local got=$?
    set -e
    test "$got" = "$want" || {
        echo "$label: got exit $got, expected $want" >&2
        exit 1
    }
    test ! -s "$W/negative-results/$label.stdout"
}

expect_exit 65 wrapper-wrong-state \
    "$PK/run_ppgpu_exact.sh" "$PPGPU" "$PK/negative/wrong-state.checkpoint" \
      --from 0 --to 0 --faultshots
expect_exit 65 wrapper-wrong-count \
    "$PK/run_ppgpu_exact.sh" "$PPGPU" "$PK/negative/wrong-count.checkpoint" \
      --from 0 --to 0 --faultshots
expect_exit 64 wrapper-allow-mismatch \
    "$PK/run_ppgpu_exact.sh" "$PPGPU" "$PK/artifacts/checkpoint.bin" \
      --from 0 --to 0 --allow-op-mismatch
expect_exit 64 wrapper-incomplete-screen \
    "$PK/run_ppgpu_exact.sh" "$PPGPU" "$PK/artifacts/checkpoint.bin" \
      --from 0 --to 0 --screen --faultshots

expect_exit 4 binary-wrong-source-count \
    "$PPGPU" --checkpoint "$PK/negative/wrong-count.checkpoint" --ops "$((OPS_COUNT - 1))" \
      --from 0 --to 0 --faultshots
expect_exit 4 binary-wrong-declared-count \
    "$PPGPU" --checkpoint "$PK/artifacts/checkpoint.bin" --ops "$((OPS_COUNT - 1))" \
      --from 0 --to 0 --faultshots
expect_exit 2 binary-bad-magic \
    "$PPGPU" --checkpoint "$PK/negative/bad-magic.checkpoint" --ops "$OPS_COUNT" \
      --from 0 --to 0 --faultshots
expect_exit 2 binary-short-checkpoint \
    "$PPGPU" --checkpoint "$PK/negative/short.checkpoint" --ops "$OPS_COUNT" \
      --from 0 --to 0 --faultshots
expect_exit 2 binary-screen-plus-mask \
    "$PPGPU" --checkpoint "$PK/artifacts/checkpoint.bin" --ops "$OPS_COUNT" \
      --from 0 --to 0 --screen --faultshots

(
    cd "$W/negative-results"
    find . -type f -print | LC_ALL=C sort | while IFS= read -r path; do
        sha256sum "$path"
    done
) > "$W/receipts/NEGATIVES.manifest"
negative_sha=$(sha256sum "$W/receipts/NEGATIVES.manifest" | awk '{print $1}')
{
    printf 'packet_id=%s\n' "$PACKET_ID"
    printf 'negative_cases=9\n'
    printf 'negative_manifest_sha256=%s\n' "$negative_sha"
    printf 'wrong_checkpoint_fail_closed=yes\n'
    printf 'wrong_count_fail_closed=yes\n'
    printf 'screen_plus_faultshots_fail_closed=yes\n'
} > "$W/receipts/NEGATIVES.complete.tmp"
mv "$W/receipts/NEGATIVES.complete.tmp" "$W/receipts/NEGATIVES.complete"
printf 'Q1272_SELECTOR_NEGATIVES_OK cases=9 manifest=%s\n' "$negative_sha"
