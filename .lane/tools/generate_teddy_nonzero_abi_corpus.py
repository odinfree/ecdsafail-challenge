#!/usr/bin/env python3
"""Generate the frozen X008 denominator x replay-seed corpus."""

from __future__ import annotations

import hashlib
import pathlib
import sys


P = (1 << 256) - (1 << 32) - 977
EXPECTED_DENOMINATORS = 64
EXPECTED_SEEDS = 64
EXPECTED_ROWS = EXPECTED_DENOMINATORS * EXPECTED_SEEDS
EXPECTED_DENOMINATORS_SHA256 = "bd1c937e2aa188106bc156929b19f536f6b5933510221371e42d1cbaeedeea2d"
EXPECTED_SEEDS_SHA256 = "4a48e4569fd7ad7df277e9624f06a58b2b453cf8629c76eb07db24052d305d39"
EXPECTED_CORPUS_SHA256 = "53b06714ffdf079be23b2d3e1d25706c0d2853ab08d13345588f9a505c9409b0"


def fail(message: str) -> None:
    raise SystemExit(f"generate-teddy-nonzero-abi-corpus: {message}")


def field_xof(label: bytes, index: int) -> int:
    digest = hashlib.shake_256(label + index.to_bytes(8, "little")).digest(64)
    return int.from_bytes(digest, "little") % (P - 1) + 1


def unique_field_values(label: bytes, prefix: list[int], count: int) -> list[int]:
    values: list[int] = []
    seen: set[int] = set()
    for value in prefix:
        value %= P
        if value == 0 or value in seen:
            fail(f"invalid or duplicate frozen prefix value {value:#x}")
        values.append(value)
        seen.add(value)
    index = 0
    while len(values) < count:
        value = field_xof(label, index)
        index += 1
        if value not in seen:
            values.append(value)
            seen.add(value)
    return values


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: generate_teddy_nonzero_abi_corpus.py OUTPUT")
    output = pathlib.Path(sys.argv[1])

    f = (1 << 32) + 977
    denominators = unique_field_values(
        b"Teddy X008 independent denominator v1",
        [
            1,
            2,
            3,
            4,
            P - 1,
            P - 2,
            P - 3,
            P - 4,
            f,
            f - 1,
            f + 1,
            (1 << 128) - 1,
            1 << 128,
            (1 << 128) + 1,
            (1 << 255) - 19,
            (1 << 255) + 19,
        ],
        EXPECTED_DENOMINATORS,
    )

    production_numerators = unique_field_values(
        b"Teddy X008 production numerator v1",
        [1, 2, 3, f - 1, f, f + 1, (1 << 128) + 1, P - 1],
        32,
    )
    seeds: list[tuple[int, int]] = [(0, numerator) for numerator in production_numerators]

    strict_prefix = [
        (1, 1),
        (1, P - 1),
        (P - 1, 1),
        (P - 1, P - 1),
        (f, f + 1),
        ((1 << 128) - 1, (1 << 128) + 1),
        ((1 << 255) - 19, f),
        (f + 1, (1 << 255) + 19),
    ]
    strict_seen: set[tuple[int, int]] = set()
    strict_seeds: list[tuple[int, int]] = []
    for coefficient, numerator in strict_prefix:
        pair = (coefficient % P, numerator % P)
        if pair[0] == 0 or pair[1] == 0 or pair in strict_seen:
            fail("invalid strict seed prefix")
        strict_seeds.append(pair)
        strict_seen.add(pair)
    index = 0
    while len(strict_seeds) < 32:
        coefficient = field_xof(b"Teddy X008 strict coefficient v1", index)
        numerator = field_xof(b"Teddy X008 strict numerator v1", index)
        index += 1
        pair = (coefficient, numerator)
        if pair not in strict_seen:
            strict_seeds.append(pair)
            strict_seen.add(pair)
    seeds.extend(strict_seeds)

    if len(denominators) != EXPECTED_DENOMINATORS or len(set(denominators)) != len(denominators):
        fail("denominator count or uniqueness changed")
    if len(seeds) != EXPECTED_SEEDS or len(set(seeds)) != len(seeds):
        fail("seed count or uniqueness changed")
    if any(numerator == 0 for _, numerator in seeds):
        fail("every numerator seed must be nonzero")
    if any(coefficient != 0 for coefficient, _ in seeds[:32]):
        fail("production-ABI coefficient seeds must be zero")
    if any(coefficient == 0 for coefficient, _ in seeds[32:]):
        fail("strict transducer coefficient seeds must be nonzero")

    denominator_blob = "".join(f"{value:064x}\n" for value in denominators).encode("ascii")
    seed_blob = "".join(
        f"{coefficient:064x}\t{numerator:064x}\n" for coefficient, numerator in seeds
    ).encode("ascii")
    corpus_blob = "".join(
        f"{denominator:064x}\t{coefficient:064x}\t{numerator:064x}\n"
        for denominator in denominators
        for coefficient, numerator in seeds
    ).encode("ascii")

    denominator_digest = hashlib.sha256(denominator_blob).hexdigest()
    seed_digest = hashlib.sha256(seed_blob).hexdigest()
    corpus_digest = hashlib.sha256(corpus_blob).hexdigest()
    expected = [
        ("denominators", denominator_digest, EXPECTED_DENOMINATORS_SHA256),
        ("seeds", seed_digest, EXPECTED_SEEDS_SHA256),
        ("corpus", corpus_digest, EXPECTED_CORPUS_SHA256),
    ]
    for name, actual, frozen in expected:
        if frozen and actual != frozen:
            fail(f"{name} SHA-256 {actual} != {frozen}")

    if corpus_blob.count(b"\n") != EXPECTED_ROWS:
        fail("corpus row count changed")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(corpus_blob)
    print(
        "generate-teddy-nonzero-abi-corpus: PASS "
        f"denominators={len(denominators)} seeds={len(seeds)} rows={EXPECTED_ROWS} "
        f"production_seeds=32 strict_seeds=32 denominator_sha256={denominator_digest} "
        f"seed_sha256={seed_digest} corpus_sha256={corpus_digest}"
    )


if __name__ == "__main__":
    main()
