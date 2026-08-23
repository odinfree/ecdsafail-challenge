#!/bin/bash
set -euo pipefail

phase_stage_dir="$(cd "$(dirname "$0")" && pwd)"
phase_ops="${1:?usage: verify_phase_cpu.sh OPS_BIN PPCPU}"
phase_cpu="${2:?usage: verify_phase_cpu.sh OPS_BIN PPCPU}"
phase_tmp_dir="$(mktemp -d)"
trap 'rm -rf "$phase_tmp_dir"' EXIT

phase_pass=0
while IFS=$'\t' read -r phase_nonce phase_cls phase_count phase_sha; do
    [[ -z "$phase_nonce" || "$phase_nonce" == \#* ]] && continue
    phase_out="$phase_tmp_dir/$phase_nonce.tsv"
    phase_log="$phase_tmp_dir/$phase_nonce.log"
    env PPF_OPS="$phase_ops" "$phase_cpu" phasefaultshots "$phase_nonce" \
        >"$phase_out" 2>"$phase_log"
    phase_got_count="$(wc -l <"$phase_out" | tr -d ' ')"
    phase_got_sha="$(shasum -a 256 "$phase_out" | awk '{print $1}')"
    if [[ "$phase_got_count" != "$phase_count" || "$phase_got_sha" != "$phase_sha" ]]; then
        echo "FAIL nonce=$phase_nonce clean_phase=$phase_got_count/$phase_count sha=$phase_got_sha/$phase_sha" >&2
        exit 1
    fi
    if ! grep -q "classical=$phase_cls clean_phase=$phase_count .*contract=phase&~classical" "$phase_log"; then
        echo "FAIL nonce=$phase_nonce classical/contract receipt" >&2
        exit 1
    fi
    phase_pass=$((phase_pass + 1))
    echo "PASS nonce=$phase_nonce classical=$phase_cls clean_phase=$phase_count sha256=$phase_sha"
done <"$phase_stage_dir/PHASE_FIXTURES.tsv"

[[ "$phase_pass" == 23 ]] || { echo "FAIL fixture count $phase_pass/23" >&2; exit 1; }
echo "PASS frozen23 complete masked phase sets 23/23"
