#!/usr/bin/env bash
set -euo pipefail

if test "$#" -lt 2; then
    echo "usage: $0 /path/to/ppgpu /path/to/checkpoint [exact-mode arguments]" >&2
    exit 64
fi

PK=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
# shellcheck disable=SC1091
. "$PK/PACKET.meta"
PPGPU=$1
CHECKPOINT=$2
shift 2

for arg in "$@"; do
    case "$arg" in
        --checkpoint|--ops|--allow-op-mismatch|--screen)
            echo "forbidden exact-wrapper argument: $arg" >&2
            exit 64
            ;;
    esac
done

test -x "$PPGPU" || { echo "missing GPU binary: $PPGPU" >&2; exit 66; }
test -f "$CHECKPOINT" || { echo "missing checkpoint: $CHECKPOINT" >&2; exit 66; }
got=$(sha256sum "$CHECKPOINT" | awk '{print $1}')
test "$got" = "$CHECKPOINT_SHA256" || {
    echo "wrong checkpoint: $got" >&2
    exit 65
}
test "$(stat -c '%s' "$CHECKPOINT")" = "$CHECKPOINT_SIZE"

exec "$PPGPU" --checkpoint "$CHECKPOINT" --ops "$OPS_COUNT" "$@"
