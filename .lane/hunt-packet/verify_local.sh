#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 4 ]]; then
  echo "usage: $0 OPS.bin PPCPU EVAL_CIRCUIT TAIL_PATCH" >&2
  exit 2
fi

packet=$(cd "$(dirname "$0")" && pwd -P)
repo=$(git -C "$packet" rev-parse --show-toplevel)
source "$packet/TARGET.env"
ops=$1
predictor=$2
evaluator=$3
patcher=$4

sha256() {
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  else
    sha256sum "$1" | awk '{print $1}'
  fi
}

md5_digest() {
  if command -v md5 >/dev/null 2>&1; then
    md5 -q "$1"
  else
    md5sum "$1" | awk '{print $1}'
  fi
}

git -C "$repo" cat-file -e "$SOURCE_COMMIT^{commit}"
test "$(git -C "$repo" show -s --format=%P "$SOURCE_COMMIT")" = "$LIVE_BASE_COMMIT"
git -C "$repo" diff --quiet "$SOURCE_COMMIT" -- src/point_add
test "$(git -C "$repo" show "$SOURCE_COMMIT:src/point_add/pingpong_div.rs" | grep -Fc 'tuned_window("SUB4_PP_REPLAY_CHUNK_COMPARE", &SLOT, 19)')" -eq 1

test "$(sha256 "$ops")" = "$OPS_SHA256"
test "$(md5_digest "$ops")" = "$OPS_MD5"
test "$(xxd -p -l 16 "$ops")" = "$OPS_HEADER_HEX"
test "$(sha256 "$predictor")" = "$PREDICTOR_SHA256"
test "$(sha256 "$evaluator")" = "$EVALUATOR_LOCAL_SHA256"
test "$(sha256 "$patcher")" = "$TAIL_PATCH_LOCAL_SHA256"

prediction=$(PPF_OPS="$ops" "$predictor" breakdown "$INHERITED_NONCE" 2>&1)
grep -Fq "12926071 ops state_digest=$STATE_DIGEST" <<<"$prediction"
grep -Fq "nonce $INHERITED_NONCE pred_cls=$INHERITED_PRED_CLS " <<<"$prediction"

tmp=$(mktemp -d /tmp/compare19-preflight.XXXXXX)
trap 'rm -rf "$tmp"' EXIT
(
  cd "$repo"
  "$patcher" "$INHERITED_NONCE" "$tmp"
)
cmp "$ops" "$tmp/ops.bin"

awk -F '\t' '
  NR == 1 { next }
  $1 ~ /^fresh-/ { fresh++ }
  $3 != $4 { exit 1 }
  END { if (NR != 7 || fresh != 5) exit 1 }
' "$packet/FIXTURE_RESULTS.tsv"

test "$(wc -l < "$packet/RANGE_LEDGER_TEMPLATE.tsv" | tr -d ' ')" = 1
echo "LOCAL_PACKET_OK SCAN_BLOCKED"
