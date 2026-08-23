#!/bin/bash
set -euo pipefail

repo=$(cd "$(dirname "$0")/../.." && pwd)
packet=/Users/olifreuler/ecdsa-ops/q1273-predictor-093d85d
ops="$packet/ops.bin"
bin=${PP_WRAP_FINAL_BIN:-/private/tmp/ppcpu-q1273-wrap-exact-final}
wrong_state_bin=${PP_WRAP_WRONG_STATE_BIN:-/private/tmp/ppcpu-q1273-wrap-exact-wrong-state}
out=${PP_WRAP_NEG_OUT:-/Users/olifreuler/ecdsa-ops/q1273-wrap-exact-ea6a02f/negatives}

die() { printf 'FATAL: %s\n' "$*" >&2; exit 2; }
hash() { sha256sum "$1" | awk '{print $1}'; }

[[ $(hash "$repo/.lane/q1273-predictor/src/pp_host.h") == \
  bc2df2182beb8ebcc103a3fc498a8ca65911bf52439566dbfa1284e88407f98a ]] || \
  die 'host source drift'
[[ $(hash "$repo/.lane/q1273-predictor/src/pp_model.h") == \
  da56cb95e2c423e67e8d400b423117cc54d007505aa7281e7725bcadd2ea19ab ]] || \
  die 'model source drift'
[[ $(hash "$repo/.lane/q1273-predictor/src/ppcpu.cpp") == \
  cc93e3ea51ddcb94857452e5aa3c9cfb39327a89711f703193e494daa2585d97 ]] || \
  die 'CPU source drift'
[[ $(hash "$bin") == \
  7f9a49d25f0c487d7f35ea09beff3749d2a64050b46089fbf078dadaabb4da00 ]] || \
  die 'final CPU binary drift'
[[ $(hash "$wrong_state_bin") == \
  3f7d0452c848601c7cb02f706075f6ebb0648ab22ab939bb7477ba0cb9dcbb9b ]] || \
  die 'wrong-state binary drift'
[[ $(hash "$ops") == \
  ee6448dbb23aa877123733724b109266e584f1ba14abf5c38b43b9ab6aa26cd1 ]] || \
  die 'ops drift'
[[ $(hash "$packet/negative-wrong-count.bin") == \
  2a710e4069c79488a027cfd42cfec09b5d263af57fdfe725bbd6a55440ffe1f9 ]] || \
  die 'wrong-count fixture drift'
[[ $(hash "$packet/negative-wrong-sha.bin") == \
  58a0de67b0d595b11a4a0e5f8a50098748dc4edf47e917744742d4a01bbd6458 ]] || \
  die 'wrong-SHA fixture drift'
[[ $(hash /private/tmp/q1273-phase/bad-magic.bin) == \
  23f6177d26d482b76ff0c76231fab86e40fde6563660fb34de3d314555fbddb6 ]] || \
  die 'bad-magic fixture drift'

mkdir -p "$out"
receipt="$out/receipt.tsv.tmp"
printf 'case\trc\tstdout_sha256\tstderr_sha256\tstatus\n' >"$receipt"

run_case() {
  local name=$1 expected_rc=$2 pattern=$3
  shift 3
  set +e
  "$@" >"$out/$name.stdout" 2>"$out/$name.stderr"
  local rc=$?
  set -e
  [[ "$rc" == "$expected_rc" ]] || die "$name rc $rc != $expected_rc"
  [[ $(grep -Fxc "$pattern" "$out/$name.stderr") == 1 ]] || \
    die "$name did not emit one exact guard line"
  printf '%s\t%s\t%s\t%s\tPASS\n' "$name" "$rc" "$(hash "$out/$name.stdout")" \
    "$(hash "$out/$name.stderr")" >>"$receipt"
}

PPF_OPS="$ops" "$bin" statedigest >"$out/correct-state.stdout" \
  2>"$out/correct-state.stderr"
[[ $(grep -Fxc '2148e09f4c4293b2' "$out/correct-state.stdout") == 1 ]] || \
  die 'correct state digest failure'
printf 'correct-state\t0\t%s\t%s\tPASS\n' "$(hash "$out/correct-state.stdout")" \
  "$(hash "$out/correct-state.stderr")" >>"$receipt"

run_case wrong-count 2 \
  'ppcpu: FATAL: ops stream op count 12933806 != expected 12933805 (q1273-redescent); refusing to run on an unknown stream' \
  env PPF_OPS="$packet/negative-wrong-count.bin" "$bin" statedigest
run_case wrong-sha 2 \
  'ppgpu: FATAL: ops stream sha256 58a0de67b0d595b11a4a0e5f8a50098748dc4edf47e917744742d4a01bbd6458 != expected ee6448dbb23aa877123733724b109266e584f1ba14abf5c38b43b9ab6aa26cd1 (q1273-redescent); refusing to run on an unknown stream' \
  env PPF_OPS="$packet/negative-wrong-sha.bin" "$bin" statedigest
run_case wrong-state 2 \
  'ppcpu: FATAL: ops stream state digest 2148e09f4c4293b2 != expected 2148e09f4c4293b3 (q1273-redescent); refusing to run on an unknown stream' \
  env PPF_OPS="$ops" "$wrong_state_bin" statedigest
run_case bad-magic 1 \
  'ppgpu: bad ops magic in /private/tmp/q1273-phase/bad-magic.bin' \
  env PPF_OPS=/private/tmp/q1273-phase/bad-magic.bin "$bin" statedigest
run_case missing-ops 1 \
  'ppgpu: cannot open ops file /private/tmp/q1273-wrap-definitely-missing.bin' \
  env PPF_OPS=/private/tmp/q1273-wrap-definitely-missing.bin "$bin" statedigest
run_case malformed-nonce 2 'ppcpu: malformed nonce' \
  env PPF_OPS="$ops" "$bin" faultshots not-a-nonce
run_case malformed-index 2 'ppcpu: malformed nonce or shot index' \
  env PPF_OPS="$ops" "$bin" shot 1 9024
run_case scan-disabled 2 'ppcpu: scan mode disabled in bounded qualification build' \
  env PPF_OPS="$ops" "$bin" scan 0 1

[[ $(($(wc -l <"$receipt") - 1)) == 9 ]] || die 'negative receipt count failure'
mv "$receipt" "$out/receipt.tsv"
(
  cd "$out"
  sha256sum ./*.stdout ./*.stderr receipt.tsv
) >"$out/MANIFEST.sha256.tmp"
mv "$out/MANIFEST.sha256.tmp" "$out/MANIFEST.sha256"
sha256sum "$out/receipt.tsv" "$out/MANIFEST.sha256"
