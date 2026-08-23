#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 0 ]]; then
  echo "selftest-failclosed: accepts no arguments" >&2
  exit 2
fi
packet_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
"$packet_dir/verify_packet.py" >/dev/null

scratch=$(mktemp -d /tmp/q1272-fixed8-packet-negative.XXXXXX)
meta_stdout="$scratch.stdout"
meta_stderr="$scratch.stderr"
trap 'find "$scratch" -type f -delete; find "$scratch" -depth -type d -exec rmdir {} \; 2>/dev/null || true; rm -f "$meta_stdout" "$meta_stderr"' EXIT
cp -R "$packet_dir/." "$scratch/"
chmod -R u+w "$scratch"
printf 'tamper=1\n' >>"$scratch/PACKET.meta"
if (cd "$scratch" && ./verify_packet.py) >"$meta_stdout" 2>"$meta_stderr"; then
  echo "selftest-failclosed: PACKET.meta tamper was accepted" >&2
  exit 2
fi
if [[ -s $meta_stdout ]]; then
  echo "selftest-failclosed: PACKET.meta tamper emitted stdout" >&2
  exit 2
fi

if "$packet_dir/run_one_gpu_parity.sh" unexpected >/dev/null 2>&1; then
  echo "selftest-failclosed: wrapper argument was accepted" >&2
  exit 2
fi
if CUDA_VISIBLE_DEVICES=0,1 "$packet_dir/run_one_gpu_parity.sh" >/dev/null 2>&1; then
  echo "selftest-failclosed: multiple-device selector was accepted" >&2
  exit 2
fi
if CUDA_VISIBLE_DEVICES= "$packet_dir/run_one_gpu_parity.sh" >/dev/null 2>&1; then
  echo "selftest-failclosed: empty-device selector was accepted" >&2
  exit 2
fi

echo "Q1272_FIXED8_PACKET_NEGATIVES_OK cases=4 cuda_execution=not-performed"
