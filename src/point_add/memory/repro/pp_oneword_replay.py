#!/usr/bin/env python3
"""Exact falsifier for a sign-local one-word ping-pong replay coordinate."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass

from pp_history_fiber import Config, run_case

SOURCE_COMMIT = "67524171baaf568dc3dc606f38515745f70804ff"
SOURCE_TREE = "8202910d176fa1f3332ff961e6f3f789ca6a7ac2"


@dataclass(frozen=True, slots=True)
class ReachableReplayReport:
    width: int
    modulus: int
    rounds: int
    reachable_denominators: int
    prefix_pair_classes: tuple[int, ...]
    terminal_pair_classes: int
    minimum_terminal_code_bits: int
    terminal_inverse_ok: bool


def _projective_lines(modulus: int) -> tuple[tuple[int, int], ...]:
    """Canonical projective lines over a prime field."""

    return tuple((1, slope) for slope in range(modulus)) + ((0, 1),)


def _canonical_line(vector: tuple[int, int], modulus: int) -> tuple[int, int]:
    a, b = (part % modulus for part in vector)
    if a:
        inverse = pow(a, -1, modulus)
        return 1, (b * inverse) % modulus
    if b:
        return 0, 1
    raise ValueError("the zero vector has no projective line")


def _row_times_branch_matrix(
    row: tuple[int, int], parity: int, sign: int, modulus: int
) -> tuple[int, int]:
    """Multiply a row coordinate by one replay branch matrix."""

    inverse_two = pow(2, -1, modulus)
    a, b = row
    if parity == 0:
        # (x, y) -> (x, (y + sign*x)/2)
        return (
            (a + b * sign * inverse_two) % modulus,
            (b * inverse_two) % modulus,
        )
    # (x, y) -> ((x + sign*y)/2, y)
    return (
        (a * inverse_two) % modulus,
        (b + a * sign * inverse_two) % modulus,
    )


def local_coordinate_transitions(
    modulus: int, parity: int
) -> tuple[tuple[tuple[int, int], tuple[int, int]], ...]:
    """Return (pre, post) projective coordinates closed for both signs.

    A post-round row ``l_post`` is a valid one-word coordinate only when
    ``l_post M_-`` and ``l_post M_+`` are the same nonzero projective line.
    That shared line is the required pre-round coordinate.
    """

    transitions: list[tuple[tuple[int, int], tuple[int, int]]] = []
    for post in _projective_lines(modulus):
        before_minus = _row_times_branch_matrix(post, parity, -1, modulus)
        before_plus = _row_times_branch_matrix(post, parity, 1, modulus)
        if before_minus == (0, 0) or before_plus == (0, 0):
            continue
        line_minus = _canonical_line(before_minus, modulus)
        line_plus = _canonical_line(before_plus, modulus)
        if line_minus == line_plus:
            transitions.append((line_minus, post))
    return tuple(transitions)


def two_round_local_coordinate_exists(modulus: int) -> bool:
    """Whether an even replay cell can compose with the following odd cell."""

    even = local_coordinate_transitions(modulus, 0)
    odd = local_coordinate_transitions(modulus, 1)
    even_post = {post for _before, post in even}
    odd_before = {before for before, _post in odd}
    return bool(even_post & odd_before)


def reachable_replay_report(
    width: int, modulus: int, rounds: int
) -> ReachableReplayReport:
    """Count coefficient-pair classes on reachable denominator tapes only."""

    config = Config(width, modulus, rounds)
    traces = {
        denominator: run_case(config, denominator, 1)
        for denominator in range(1, modulus)
    }
    prefix_pair_classes = tuple(
        len(
            {
                (trace.states[round_index].x, trace.states[round_index].y)
                for trace in traces.values()
            }
        )
        for round_index in range(rounds)
    )

    terminal_inverse_ok = True
    for denominator, trace in traces.items():
        terminal = trace.states[-1]
        x = terminal.x if terminal.u > 0 else (-terminal.x) % modulus
        y = terminal.y if terminal.v > 0 else (-terminal.y) % modulus
        expected = pow(denominator, -1, modulus)
        terminal_inverse_ok &= x == expected and y == expected

    terminal_pair_classes = prefix_pair_classes[-1]
    return ReachableReplayReport(
        width=width,
        modulus=modulus,
        rounds=rounds,
        reachable_denominators=modulus - 1,
        prefix_pair_classes=prefix_pair_classes,
        terminal_pair_classes=terminal_pair_classes,
        minimum_terminal_code_bits=(terminal_pair_classes - 1).bit_length(),
        terminal_inverse_ok=terminal_inverse_ok,
    )


def receipt() -> dict[str, object]:
    configs = ((5, 29, 12), (6, 61, 17), (7, 127, 20))
    reports = [reachable_replay_report(*config) for config in configs]
    local = {
        str(modulus): {
            "even_transitions": local_coordinate_transitions(modulus, 0),
            "odd_transitions": local_coordinate_transitions(modulus, 1),
            "two_round_coordinate_exists": two_round_local_coordinate_exists(modulus),
        }
        for modulus in (29, 61, 127)
    }
    hard_nack = all(
        not row["two_round_coordinate_exists"] for row in local.values()
    ) and all(
        report.terminal_pair_classes == report.modulus - 1
        and report.minimum_terminal_code_bits == report.width
        and report.terminal_inverse_ok
        for report in reports
    )
    return {
        "binding": {"source_commit": SOURCE_COMMIT, "source_tree": SOURCE_TREE},
        "local_linear_closure": local,
        "reachable_replay_classes": [asdict(report) for report in reports],
        "production_implication": {
            "replay_pair_qubits": 512,
            "one_data_word_qubits": 256,
            "minimum_discriminator_projection_qubits": 256,
            "projected_total_qubits_before_scratch": 512,
        },
        "reopen_condition": (
            "an explicit nonlinear in-place division transform with independent "
            "correctness and end-to-end Q/T pricing"
        ),
        "verdict": "HARD_NACK" if hard_nack else "HOLD",
        "verdict_scope": (
            "sign-local linear one-word replay plus a sub-field-word discriminator"
        ),
    }


def render_receipt() -> str:
    return json.dumps(receipt(), indent=2, sort_keys=True) + "\n"


if __name__ == "__main__":
    print(render_receipt(), end="")
