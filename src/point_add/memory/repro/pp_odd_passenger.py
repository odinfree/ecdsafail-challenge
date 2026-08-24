#!/usr/bin/env python3
"""Independent certificate for the ping-pong odd-passenger loan.

The production circuit loans ``u[0]`` and ``v[0]`` only across replay cells.
This checker proves the low-bit recurrence exhaustively and then audits the
frozen Rust source to ensure every nonterminal loan interval is replay-only.
It does not import or execute production arithmetic code.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Sequence


IMPLEMENTATION_COMMIT = "61b974c27409d5baf3677da37f38e2f2d84078d7"
PINGPONG_SHA256 = "91cf1f711f66191b8b7d0de0a95fb8c83d84e38e5f57a27308f1e9f5443f7394"
EXPECTED_LOAN_INTERVALS = 4

REPRO_DIR = Path(__file__).resolve().parent
DEFAULT_SOURCE = REPRO_DIR.parents[1] / "pingpong_div.rs"

LOAN_INTERVAL = re.compile(
    rb"let odd_passengers = loan_interleaved_odd_passengers\(b, &u, &v\);"
    rb"(?P<body>.*?)"
    rb"restore_interleaved_odd_passengers\(b, odd_passengers\);",
    re.DOTALL,
)


def recurrence_row(source_bit1: int, target_bit1: int) -> dict[str, int]:
    """Prove the next target is odd from the complete low-two-bit support.

    Both operands have low word ``1 + 2*bit1``.  The walk chooses addition
    when their bit ones agree and subtraction when they differ.  Therefore
    the signed numerator is always 2 mod 4; its exact division by two is odd.
    """

    if source_bit1 not in (0, 1) or target_bit1 not in (0, 1):
        raise ValueError("bit-one inputs must be bits")
    source_mod4 = 1 + 2 * source_bit1
    target_mod4 = 1 + 2 * target_bit1
    sign = source_bit1 ^ target_bit1
    numerator_mod4 = (
        target_mod4 - source_mod4 if sign else target_mod4 + source_mod4
    ) % 4
    return {
        "source_bit1": source_bit1,
        "target_bit1": target_bit1,
        "sign": sign,
        "numerator_mod4": numerator_mod4,
        "next_target_bit0": numerator_mod4 // 2,
    }


def prove_recurrence() -> tuple[dict[str, int], ...]:
    rows = tuple(
        recurrence_row(source_bit1, target_bit1)
        for source_bit1 in (0, 1)
        for target_bit1 in (0, 1)
    )
    if any(row["numerator_mod4"] != 2 for row in rows):
        raise AssertionError("signed numerator is not uniformly 2 mod 4")
    if any(row["next_target_bit0"] != 1 for row in rows):
        raise AssertionError("walk recurrence does not preserve oddness")
    return rows


def prove_initial_state(modulus: int, denominator: int) -> dict[str, int]:
    """Check the exact representative lift used before the walk."""

    if modulus <= 2 or modulus % 2 == 0:
        raise ValueError("modulus must be odd")
    if not 0 < denominator < modulus:
        raise ValueError("denominator must lie in the field range")
    lifted = denominator if denominator & 1 else denominator - modulus
    if (lifted - denominator) % modulus != 0:
        raise AssertionError("lift changed the residue class")
    if modulus & 1 != 1 or lifted & 1 != 1:
        raise AssertionError("initial walk operands are not both odd")
    return {
        "modulus_bit0": modulus & 1,
        "denominator_bit0": denominator & 1,
        "lifted_bit0": lifted & 1,
    }


def audit_source(path: Path) -> dict[str, object]:
    source = path.read_bytes()
    digest = hashlib.sha256(source).hexdigest()
    if digest != PINGPONG_SHA256:
        raise AssertionError(f"pingpong source SHA drift: {digest}")

    matches = tuple(LOAN_INTERVAL.finditer(source))
    if len(matches) != EXPECTED_LOAN_INTERVALS:
        raise AssertionError(
            f"expected {EXPECTED_LOAN_INTERVALS} loan intervals, found {len(matches)}"
        )

    interval_hashes: list[str] = []
    for index, match in enumerate(matches):
        body = match.group("body")
        if re.search(rb"(?<![A-Za-z0-9_])[uv](?![A-Za-z0-9_])", body):
            raise AssertionError(f"loan interval {index} reads a walk operand")
        if b"replay_halving_round" not in body and b"replay_doubling_round" not in body:
            raise AssertionError(f"loan interval {index} is not replay-only")
        interval_hashes.append(hashlib.sha256(body).hexdigest())

    required_fragments = (
        b'b.x(q);\r\n        b.release_clean(q);',
        b'b.reacquire(q);\r\n            b.x(q);',
        b'== Some("1")',
    )
    for fragment in required_fragments:
        if fragment not in source:
            raise AssertionError(f"missing loan identity fragment: {fragment!r}")

    return {
        "path": str(path),
        "sha256": digest,
        "loan_intervals": len(matches),
        "replay_only": True,
        "interval_sha256": interval_hashes,
    }


def make_receipt(source: Path) -> dict[str, object]:
    initial_states = tuple(
        prove_initial_state(29, denominator) for denominator in range(1, 29)
    )
    if len({row["lifted_bit0"] for row in initial_states}) != 1:
        raise AssertionError("positive control failed to cover one odd lift class")
    return {
        "verdict": "PASS",
        "implementation_commit": IMPLEMENTATION_COMMIT,
        "claim": "u[0] = v[0] = 1 at every replay boundary",
        "initial_lift_denominators_checked": len(initial_states),
        "low_two_support": prove_recurrence(),
        "source_audit": audit_source(source),
    }


def render_receipt(argv: Sequence[str] | None = None) -> str:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    args = parser.parse_args(argv)
    return json.dumps(make_receipt(args.source), indent=2, sort_keys=True) + "\n"


if __name__ == "__main__":
    print(render_receipt(), end="")
