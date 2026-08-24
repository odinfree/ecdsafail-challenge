#!/usr/bin/env python3
"""Exact reduced-width model for the promoted ping-pong history recurrence.

This is a structural falsifier, not a benchmark candidate.  It mirrors the
integer walk and modular coefficient replay in ``pingpong_div.rs`` at commit
67524171baaf568dc3dc606f38515745f70804ff, while replacing the secp256k1
constants with explicitly configured small odd moduli for exhaustive search.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True, slots=True)
class Config:
    width: int
    modulus: int
    rounds: int

    def __post_init__(self) -> None:
        if self.width < 3:
            raise ValueError("width must be at least 3")
        if self.modulus <= 2 or self.modulus >= 1 << self.width:
            raise ValueError("modulus must fit the configured width")
        if self.modulus % 2 == 0:
            raise ValueError("modulus must be odd")
        if self.rounds < 1:
            raise ValueError("rounds must be positive")


@dataclass(frozen=True, slots=True, order=True)
class State:
    """Post-round semantic state.

    ``u`` and ``v`` are signed walk integers. ``x`` and ``y`` are canonical
    residues modulo the configured modulus.
    """

    u: int
    v: int
    x: int
    y: int


@dataclass(frozen=True, slots=True)
class Trace:
    states: tuple[State, ...]
    signs: tuple[int, ...]
    history: int


@dataclass(frozen=True, slots=True)
class FiberRound:
    round_index: int
    raw_history_bits: int
    endpoint_count: int
    endpoint_history_count: int
    maximum_fiber_size: int
    minimum_code_bits: int
    singleton_endpoints: int
    members_sha256: str


@dataclass(frozen=True, slots=True)
class FiberReport:
    config: Config
    input_count: int
    rounds: tuple[FiberRound, ...]
    round_trip_ok: bool


def bit1(value: int, width: int) -> int:
    """Return bit one of ``value`` in fixed-width two's-complement form."""

    if width < 2:
        raise ValueError("width must expose bit one")
    return ((value & ((1 << width) - 1)) >> 1) & 1


def half_mod(value: int, modulus: int) -> int:
    """Divide a residue by two modulo an odd modulus."""

    if modulus <= 2 or modulus % 2 == 0:
        raise ValueError("modulus must be odd and greater than two")
    value %= modulus
    if value & 1:
        value += modulus
    return value // 2


def step(config: Config, state: State, round_index: int) -> tuple[State, int]:
    """Apply one walk round and its matching forward coefficient replay."""

    if not 0 <= round_index < config.rounds:
        raise ValueError("round index lies outside the configured traversal")

    if round_index % 2 == 0:
        walk_source, walk_target = state.u, state.v
        replay_source, replay_target = state.x, state.y
    else:
        walk_source, walk_target = state.v, state.u
        replay_source, replay_target = state.y, state.x

    sign = bit1(walk_source, config.width) ^ bit1(walk_target, config.width)
    walk_numerator = walk_target + (-walk_source if sign else walk_source)
    if walk_numerator & 1:
        raise AssertionError(
            f"round {round_index}: sign rule produced an odd walk numerator"
        )
    walk_target = walk_numerator // 2

    if round_index == 0:
        replay_target = half_mod(replay_target, config.modulus)
    elif round_index == 1:
        replay_target = half_mod(
            -replay_source if sign else replay_source, config.modulus
        )
    else:
        replay_target = half_mod(
            replay_target + (-replay_source if sign else replay_source),
            config.modulus,
        )

    if round_index % 2 == 0:
        return State(state.u, walk_target, state.x, replay_target), sign
    return State(walk_target, state.v, replay_target, state.y), sign


def run_case(config: Config, denominator: int, numerator: int) -> Trace:
    """Run one legal input through every configured round."""

    if not 1 <= denominator < config.modulus:
        raise ValueError("denominator must lie in [1, modulus)")
    if not 0 <= numerator < config.modulus:
        raise ValueError("numerator must lie in [0, modulus)")

    lifted_denominator = (
        denominator if denominator & 1 else denominator - config.modulus
    )
    state = State(config.modulus, lifted_denominator, 0, numerator)
    states: list[State] = []
    signs: list[int] = []
    history = 0
    for round_index in range(config.rounds):
        state, sign = step(config, state, round_index)
        states.append(state)
        signs.append(sign)
        history |= sign << round_index
    return Trace(tuple(states), tuple(signs), history)


def local_predecessor_signs(source: int, post_target: int, width: int) -> tuple[int, ...]:
    """Return the sign choices consistent with one odd post-walk state."""

    if source & 1 == 0 or post_target & 1 == 0:
        raise ValueError("source and post-target must both be odd")
    valid: list[int] = []
    for sign in (0, 1):
        predecessor = 2 * post_target + (source if sign else -source)
        observed = bit1(source, width) ^ bit1(predecessor, width)
        if observed == sign:
            valid.append(sign)
    return tuple(valid)


def encode(
    endpoint: State,
    history: int,
    members: Mapping[State, tuple[int, ...]],
) -> int:
    """Return the canonical index of ``history`` in an endpoint fiber."""

    fiber = members[endpoint]
    try:
        return fiber.index(history)
    except ValueError as error:
        raise KeyError("history is not a member of the endpoint fiber") from error


def decode(
    endpoint: State,
    code: int,
    members: Mapping[State, tuple[int, ...]],
) -> int:
    """Decode one canonical endpoint-fiber index."""

    fiber = members[endpoint]
    if not 0 <= code < len(fiber):
        raise KeyError("code lies outside the endpoint fiber")
    return fiber[code]


def _fiber_digest(members: Mapping[State, tuple[int, ...]]) -> str:
    digest = hashlib.sha256()
    for endpoint in sorted(members):
        histories = members[endpoint]
        digest.update(
            (
                f"{endpoint.u},{endpoint.v},{endpoint.x},{endpoint.y}:"
                + ",".join(str(history) for history in histories)
                + "\n"
            ).encode("ascii")
        )
    return digest.hexdigest()


def enumerate_fibers(config: Config) -> FiberReport:
    """Exhaustively enumerate exact reachable endpoint/history fibers."""

    traces = [
        run_case(config, denominator, numerator)
        for denominator in range(1, config.modulus)
        for numerator in range(config.modulus)
    ]
    rows: list[FiberRound] = []
    round_trip_ok = True
    for round_index in range(1, config.rounds + 1):
        history_mask = (1 << round_index) - 1
        grouped: dict[State, set[int]] = {}
        for trace in traces:
            endpoint = trace.states[round_index - 1]
            history = trace.history & history_mask
            grouped.setdefault(endpoint, set()).add(history)

        members = {
            endpoint: tuple(sorted(histories))
            for endpoint, histories in grouped.items()
        }
        for endpoint, histories in members.items():
            for history in histories:
                code = encode(endpoint, history, members)
                if decode(endpoint, code, members) != history:
                    round_trip_ok = False
                    raise AssertionError(
                        f"round {round_index}: endpoint fiber failed to round trip"
                    )

        maximum_fiber_size = max(map(len, members.values()), default=0)
        rows.append(
            FiberRound(
                round_index=round_index,
                raw_history_bits=round_index,
                endpoint_count=len(members),
                endpoint_history_count=sum(map(len, members.values())),
                maximum_fiber_size=maximum_fiber_size,
                minimum_code_bits=(maximum_fiber_size - 1).bit_length(),
                singleton_endpoints=sum(len(fiber) == 1 for fiber in members.values()),
                members_sha256=_fiber_digest(members),
            )
        )

    return FiberReport(
        config=config,
        input_count=len(traces),
        rounds=tuple(rows),
        round_trip_ok=round_trip_ok,
    )
