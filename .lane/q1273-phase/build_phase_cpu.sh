#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 || -z $1 ]]; then
    echo "usage: build_phase_cpu.sh OUTPUT" >&2
    exit 2
fi

script_dir=$(cd -- "$(dirname -- "$0")" && pwd -P)
repo_root=$(cd -- "$script_dir/../.." && pwd -P)

g++ -O3 -std=c++17 -pthread -Wall -Wextra -Werror -Wno-unused-parameter \
    -o "$1" "$repo_root/.lane/q1273-predictor/src/ppcpu.cpp"
