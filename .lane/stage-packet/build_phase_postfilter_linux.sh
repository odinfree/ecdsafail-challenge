#!/usr/bin/env bash
# Build the sealed CPU-only Q1274 finite-list phase postfilter on Linux.
set -euo pipefail
export LC_ALL=C

packet_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
manifest="$packet_dir/MANIFEST.sha256"

fail() { echo "build-phase-postfilter: FAIL: $*" >&2; exit 1; }
sha() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$1" | awk '{print $1}'
    else
        shasum -a 256 "$1" | awk '{print $1}'
    fi
}

[[ $# == 1 ]] || fail "usage: build_phase_postfilter_linux.sh OUTPUT_BINARY"
[[ "$(uname -s)" == "Linux" ]] || fail "Linux host required"
command -v g++ >/dev/null 2>&1 || fail "g++ is required"
command -v awk >/dev/null 2>&1 || fail "awk is required"

output="$1"
[[ ! -e "$output" && ! -L "$output" ]] || fail "refusing to overwrite $output"
output_dir="$(cd "$(dirname "$output")" && pwd -P)"
output_abs="$output_dir/$(basename "$output")"
case "$output_abs" in
    "$packet_dir"/*) fail "binary output must remain outside the tracked packet" ;;
esac

while read -r want rel; do
    [[ -z "$want" || "$want" == \#* ]] && continue
    got="$(sha "$packet_dir/$rel")"
    [[ "$got" == "$want" ]] || fail "manifest mismatch for $rel"
done < <(grep -E '^[0-9a-f]{64}  ' "$manifest")

tmp="$(mktemp "$output_dir/.phasepostfilter.build.XXXXXX")"
trap 'rm -f "$tmp"' EXIT
g++ -O3 -std=c++17 -pthread -Wall -Wextra -Werror \
    -Wno-unused-parameter \
    -o "$tmp" "$packet_dir/src/phasepostfilter.cpp"

expected_identity="source_commit=fe0b7bac6348fb35b7680784d4295899e498d0e3	ops_count=12920073	ops_sha256=4c68597468ed1dbb4f2e33042842227bf57c011c51f41e9cdaf13c73194b1f8c	predictor_digest=d2c95102cb9a277d	shots=9024	contract=phase&~classical	final=classical_mask==0&&clean_phase_mask==0	raw_phase=not-claimed	cuda_phase=not-claimed"
identity="$("$tmp" identity)"
[[ "$identity" == "$expected_identity" ]] || fail "compiled identity mismatch"

chmod 0755 "$tmp"
ln "$tmp" "$output_abs" || fail "output appeared concurrently; refusing to overwrite"
rm -f "$tmp"
trap - EXIT
echo "phasepostfilter_linux_sha256=$(sha "$output_abs")"
