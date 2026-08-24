#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "$0")/.." && pwd)"
out_dir="${1:-$repo_dir/artifacts/smallwidth-pareto}"
mkdir -p "$out_dir"

(cd "$repo_dir" && cargo build --offline --release --bin smallwidth_pareto)

SMALLWIDTH_WIDTHS="${SMALLWIDTH_WIDTHS:-32,64,96,128,256}" \
SMALLWIDTH_MAX_BLOCKS="${SMALLWIDTH_MAX_BLOCKS:-32}" \
SMALLWIDTH_MAX_WINDOW="${SMALLWIDTH_MAX_WINDOW:-32}" \
SMALLWIDTH_VALIDATE="${SMALLWIDTH_VALIDATE:-1}" \
    "$repo_dir/target/release/smallwidth_pareto" > "$out_dir/results.jsonl"

python3 "$repo_dir/tools/analyze_smallwidth_pareto.py" \
    "$out_dir/results.jsonl" \
    --events "$out_dir/discontinuities.jsonl" \
    --lifts "$out_dir/lift-assessments.jsonl" \
    --summary "$out_dir/SUMMARY.md"

shasum -a 256 \
    "$out_dir/results.jsonl" \
    "$out_dir/discontinuities.jsonl" \
    "$out_dir/lift-assessments.jsonl" \
    "$out_dir/SUMMARY.md" > "$out_dir/SHA256SUMS"

printf '%s\n' "$out_dir"
