#!/usr/bin/env python3
"""Generate the frozen 4,096-denominator Teddy round-3 corpus."""

from __future__ import annotations

import hashlib
import pathlib
import sys


EXPECTED_COUNT = 4096
EXPECTED_SHA256 = "9cbe05c8d2a2865318da958ce825163b9ac3052c142abd08c4026fff43076dbe"
EXPECTED_BASES_SHA256 = "307bdf64649d16c32e1c0ba89f4ed1806fa7a473f78b29507b551616eeaf3eab"
MASK256 = (1 << 256) - 1
SECP256K1_P = (1 << 256) - (1 << 32) - 977


def fail(message: str) -> None:
    raise SystemExit(f"generate-teddy-round3-corpus: {message}")


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: generate_teddy_round3_corpus.py OUTPUT")
    output = pathlib.Path(sys.argv[1])
    stride = SECP256K1_P >> 4
    bases: list[int] = []
    denominators: list[int] = []
    for state in range(8):
        anchor = (stride * (state + 1)) & MASK256
        base = ((anchor >> 12) << 12) + (state << 9)
        bases.append(base)
        denominators.extend(base + residue for residue in range(512))
    if len(denominators) != EXPECTED_COUNT or len(set(denominators)) != EXPECTED_COUNT:
        fail("corpus is not 4,096 unique denominators")
    if [((base >> 9) & 7) for base in bases] != list(range(8)):
        fail("high-prefix dirty-bridge states are not exhaustive")
    bases_blob = "".join(f"{base:064x}\n" for base in bases).encode("ascii")
    if hashlib.sha256(bases_blob).hexdigest() != EXPECTED_BASES_SHA256:
        fail("high-prefix identity changed")
    blob = "".join(f"{denominator:064x}\n" for denominator in denominators).encode("ascii")
    digest = hashlib.sha256(blob).hexdigest()
    if digest != EXPECTED_SHA256:
        fail(f"corpus SHA-256 {digest} != {EXPECTED_SHA256}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(blob)
    print(
        "generate-teddy-round3-corpus: PASS "
        f"count={len(denominators)} unique={len(set(denominators))} sha256={digest}"
    )


if __name__ == "__main__":
    main()
