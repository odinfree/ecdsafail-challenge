#!/usr/bin/env python3
"""Exact low-bit certificate for a third nonterminal ping-pong passenger.

The interleaved replay already releases ``u[0]`` and ``v[0]`` because both
walk values are odd.  This repro proves that one more wire is Clifford-
reconstructible at every current nonterminal loan site:

* after an even round r: ``v[1] = u[2] XOR tape[1]``;
* after an odd round r: ``u[1] = v[2] XOR tape[1]``.

The production circuit is not modified here.  The source parser, exhaustive
scaled model, full-width deterministic replay, and explicit two-CNOT
clear/restore are a standalone admission certificate for an implementation and
pricing phase.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal


MODEL_WIDTH = 259
FIELD_BITS = 256
FIELD_MODULUS = (1 << FIELD_BITS) - (1 << 32) - 977
ROUND1_H = ((1 << FIELD_BITS) - FIELD_MODULUS - 1) // 2
SAMPLE_DOMAIN = b"pingpong-third-passenger-v1"


@dataclass(frozen=True)
class BindingConfig:
    name: str
    replay_peak: int
    walk_peak: int
    measured_qubits: int


BINDING_CONFIGS = (
    BindingConfig("q1265", 1267, 1266, 1265),
    BindingConfig("q1264", 1266, 1265, 1264),
)


@dataclass(frozen=True)
class SourceContract:
    repo: Path
    rounds_div: int
    rounds_mul: int
    width_index_rounds: int
    widths: tuple[int, ...]
    r1_div: int
    r1_mul: int
    r2: int
    peak: int
    walk_peak: int
    endpoint_fold_window: int
    loaned_bits: tuple[str, ...]
    pingpong_sha256: str
    builder_sha256: str


@dataclass(frozen=True)
class LoanSite:
    direction: Literal["divide", "multiply"]
    kind: Literal["prefix-batch", "interleaved"]
    after_round: int


@dataclass(frozen=True)
class Checkpoint:
    round_index: int
    width: int
    u: int
    v: int
    tape: tuple[int, ...]


@dataclass(frozen=True)
class Violation:
    denominator: int
    round_index: int
    width: int
    passenger: str
    actual: int
    expected: int
    u: int
    v: int
    tape1: int


@dataclass(frozen=True)
class LowBitTransitionViolation:
    source_low3: int
    target_low3: int
    sign: int
    actual_post_target0: int
    actual_post_target1: int
    expected_post_target1: int


@dataclass(frozen=True)
class LowBitTransitionResult:
    rows: int
    violations: tuple[LowBitTransitionViolation, ...]


@dataclass(frozen=True)
class ExhaustiveResult:
    width: int
    f: int
    modulus: int
    denominators: int
    through_round: int
    checks: int
    violations: tuple[Violation, ...]
    state_digest: str


@dataclass(frozen=True)
class ProbeResult:
    samples: int
    first_round: int
    last_round: int
    checks: int
    violations: tuple[Violation, ...]
    input_digest: str
    checkpoint_digest: str


@dataclass(frozen=True)
class CollisionState:
    reconstructors: tuple[int, ...]
    passenger_bit: int
    sample_index: int
    denominator: int
    u: int
    v: int


@dataclass(frozen=True)
class BooleanCollision:
    round_index: int
    passenger: str
    left: CollisionState
    right: CollisionState


def _extract_u16_array(text: str, name: str) -> tuple[int, ...]:
    match = re.search(
        rf"const\s+{re.escape(name)}:\s*\[u16;\s*\d+\]\s*=\s*\[(.*?)\];",
        text,
        re.DOTALL,
    )
    if match is None:
        raise ValueError(f"missing source array {name}")
    return tuple(int(value) for value in re.findall(r"\d+", match.group(1)))


def _builder_default(text: str, name: str) -> int:
    matches = re.findall(
        rf'set_default_env\(\s*"{re.escape(name)}"\s*,\s*"(\d+)"\s*\)',
        text,
    )
    if len(matches) != 1:
        raise ValueError(f"expected one builder default for {name}, found {len(matches)}")
    return int(matches[0])


def load_source_contract(repo: Path) -> SourceContract:
    """Bind the proof to the exact Rust schedule, plan, and loan function."""

    repo = repo.resolve()
    pingpong_path = repo / "src/point_add/pingpong_div.rs"
    builder_path = repo / "src/point_add/mod.rs"
    pingpong_bytes = pingpong_path.read_bytes()
    builder_bytes = builder_path.read_bytes()
    pingpong = pingpong_bytes.decode()
    builder = builder_bytes.decode()

    schedule = _extract_u16_array(pingpong, "WIDTH_SCHEDULE")
    repair = set(_extract_u16_array(pingpong, "WIDTH_REPAIR"))
    rounds_div = _builder_default(builder, "SUB4_PP_ROUNDS")
    rounds_mul = _builder_default(builder, "SUB4_PP_ROUNDS_MUL")
    width_index_match = re.search(
        r"const\s+ROUNDS_DEFAULT:\s*usize\s*=\s*(\d+);",
        pingpong,
    )
    if width_index_match is None:
        raise ValueError("missing ROUNDS_DEFAULT")
    width_index_rounds = int(width_index_match.group(1))

    widths: list[int] = []
    for round_index in range(rounds_div):
        if round_index == 0:
            widths.append(MODEL_WIDTH)
            continue
        sampled = round_index * (width_index_rounds - 1) // (rounds_div - 1)
        scheduled = schedule[sampled] if sampled < len(schedule) else 8
        widths.append(max(8, min(MODEL_WIDTH, scheduled + (sampled in repair))))

    loan_match = re.search(
        r"fn\s+loan_interleaved_odd_passengers\(.*?let\s+passengers\s*=\s*"
        r"\[(.*?)\];",
        pingpong,
        re.DOTALL,
    )
    if loan_match is None:
        raise ValueError("missing interleaved passenger loan")
    loaned_bits = tuple(part.strip() for part in loan_match.group(1).split(","))
    if loaned_bits != ("u[0]", "v[0]"):
        raise ValueError(f"unexpected current loan family: {loaned_bits}")

    return SourceContract(
        repo=repo,
        rounds_div=rounds_div,
        rounds_mul=rounds_mul,
        width_index_rounds=width_index_rounds,
        widths=tuple(widths),
        r1_div=_builder_default(builder, "SUB4_PP_R1"),
        r1_mul=_builder_default(builder, "SUB4_PP_R1_MUL"),
        r2=_builder_default(builder, "SUB4_PP_R2"),
        peak=_builder_default(builder, "SUB4_PP_PEAK"),
        walk_peak=_builder_default(builder, "SUB4_PP_WALK_PEAK"),
        endpoint_fold_window=_builder_default(builder, "SUB4_PP_ENDPOINT_FOLD_WINDOW"),
        loaned_bits=loaned_bits,
        pingpong_sha256=hashlib.sha256(pingpong_bytes).hexdigest(),
        builder_sha256=hashlib.sha256(builder_bytes).hexdigest(),
    )


def loan_sites(contract: SourceContract, direction: str) -> tuple[LoanSite, ...]:
    """Return the exact post-walk states at which the existing loan executes."""

    if direction == "divide":
        r1 = contract.r1_div
    elif direction == "multiply":
        r1 = contract.r1_mul
    else:
        raise ValueError("direction must be divide or multiply")
    typed_direction: Literal["divide", "multiply"] = direction  # type: ignore[assignment]
    sites = [LoanSite(typed_direction, "prefix-batch", r1 - 1)]
    sites.extend(
        LoanSite(typed_direction, "interleaved", round_index)
        for round_index in range(r1, contract.r2 + 1)
    )
    return tuple(sites)


def _bit(value: int, index: int) -> int:
    return (value >> index) & 1


def _arithmetic_shift(value: int, width: int) -> int:
    mask = (1 << width) - 1
    value &= mask
    return ((value >> 1) | (_bit(value, width - 1) << (width - 1))) & mask


def _sub_low_slice(value: int, constant: int, bits: int, width: int) -> int:
    low_mask = (1 << bits) - 1
    mask = (1 << width) - 1
    return ((value & ~low_mask) | (((value & low_mask) - constant) & low_mask)) & mask


def _increment_high_slice(value: int, start: int, width: int) -> int:
    high_mask = (1 << (width - start)) - 1
    low_mask = (1 << start) - 1
    high = (((value >> start) & high_mask) + 1) & high_mask
    return (value & low_mask) | (high << start)


def _production_seed(contract: SourceContract, denominator: int) -> tuple[int, int, list[int]]:
    """Execute the source's fused round 0 and fused round 1 exactly."""

    if not 0 < denominator < FIELD_MODULUS:
        raise ValueError("denominator must be in 1..p-1")
    a0 = _bit(denominator, 0)
    a1 = _bit(denominator, 1)
    mask259 = (1 << MODEL_WIDTH) - 1
    v = (
        (denominator >> 1)
        - FIELD_MODULUS
        + a1 * FIELD_MODULUS
        + a0 * ((FIELD_MODULUS + 1) // 2)
    ) & mask259
    u = FIELD_MODULUS
    tape = [a0]

    width = contract.widths[1]
    mask = (1 << width) - 1
    u &= mask
    v &= mask
    sign1 = _bit(u, 1) ^ _bit(v, 1)
    u = _arithmetic_shift(v, width) ^ (mask if sign1 else 0)
    window = min(32 + contract.endpoint_fold_window, width)
    u = _sub_low_slice(u, ROUND1_H, window, width)
    u = _increment_high_slice(u, FIELD_BITS - 1, width) & mask
    tape.append(sign1)
    return u, v, tape


def _walk_round(u: int, v: int, round_index: int, width: int) -> tuple[int, int, int]:
    """Exact value action of walk_round for a generic round >= 2."""

    mask = (1 << width) - 1
    u &= mask
    v &= mask
    sign = _bit(u, 1) ^ _bit(v, 1)
    if round_index % 2 == 0:
        combined = (v - u if sign else v + u) & mask
        v = _arithmetic_shift(combined, width)
    else:
        combined = (u - v if sign else u + v) & mask
        u = _arithmetic_shift(combined, width)
    return u, v, sign


def _production_checkpoints(
    contract: SourceContract,
    denominator: int,
    through_round: int,
) -> tuple[Checkpoint, ...]:
    if through_round >= contract.rounds_div - 1:
        raise ValueError("checkpoint needs a following schedule width")
    u, v, tape = _production_seed(contract, denominator)
    width = contract.widths[2]
    mask = (1 << width) - 1
    u &= mask
    v &= mask
    checkpoints = [Checkpoint(1, width, u, v, tuple(tape))]
    for round_index in range(2, through_round + 1):
        u, v, sign = _walk_round(
            u,
            v,
            round_index,
            contract.widths[round_index],
        )
        tape.append(sign)
        width = contract.widths[round_index + 1]
        mask = (1 << width) - 1
        u &= mask
        v &= mask
        checkpoints.append(Checkpoint(round_index, width, u, v, tuple(tape)))
    return tuple(checkpoints)


def production_checkpoint(
    contract: SourceContract,
    denominator: int,
    round_index: int,
) -> Checkpoint:
    if round_index < 1:
        raise ValueError("the certified relation is seeded at round 1")
    return _production_checkpoints(contract, denominator, round_index)[-1]


def relation_holds(checkpoint: Checkpoint) -> bool:
    if len(checkpoint.tape) <= 1:
        return False
    if checkpoint.round_index % 2 == 0:
        passenger = _bit(checkpoint.v, 1)
        source2 = _bit(checkpoint.u, 2)
    else:
        passenger = _bit(checkpoint.u, 1)
        source2 = _bit(checkpoint.v, 2)
    return passenger == (source2 ^ checkpoint.tape[1])


def apply_third_passenger_xors(checkpoint: Checkpoint) -> Checkpoint:
    """Apply the two CNOT value actions used for both clear and restore."""

    if checkpoint.round_index % 2 == 0:
        control = _bit(checkpoint.u, 2) ^ checkpoint.tape[1]
        return Checkpoint(
            checkpoint.round_index,
            checkpoint.width,
            checkpoint.u,
            checkpoint.v ^ (control << 1),
            checkpoint.tape,
        )
    control = _bit(checkpoint.v, 2) ^ checkpoint.tape[1]
    return Checkpoint(
        checkpoint.round_index,
        checkpoint.width,
        checkpoint.u ^ (control << 1),
        checkpoint.v,
        checkpoint.tape,
    )


def exhaustive_low_bit_transition() -> LowBitTransitionResult:
    """Prove the generic-round low-bit lemma by its complete truth table.

    For odd source ``S`` and target ``T``, the source implements ``T + S``
    when ``T[1] == S[1]`` and ``T - S`` otherwise, followed by an arithmetic
    right shift.  The new target bit 1 is therefore the pre-shift result bit 2.
    All inputs to that bit fit in the three low bits exhausted here.
    """

    violations: list[LowBitTransitionViolation] = []
    rows = 0
    for source_low3 in range(1, 8, 2):
        for target_low3 in range(1, 8, 2):
            rows += 1
            sign = _bit(target_low3, 1) ^ _bit(source_low3, 1)
            combined = (
                target_low3 - source_low3
                if sign
                else target_low3 + source_low3
            ) & 0b111
            actual_post_target0 = _bit(combined, 1)
            actual = _bit(combined, 2)
            expected = (
                _bit(source_low3, 2)
                ^ _bit(target_low3, 2)
                ^ _bit(source_low3, 1)
            )
            if actual_post_target0 != 1 or actual != expected:
                violations.append(
                    LowBitTransitionViolation(
                        source_low3,
                        target_low3,
                        sign,
                        actual_post_target0,
                        actual,
                        expected,
                    )
                )
    return LowBitTransitionResult(rows, tuple(violations))


def _scaled_checkpoints(
    denominator: int,
    width: int,
    f: int,
    through_round: int,
) -> tuple[Checkpoint, ...]:
    modulus = (1 << width) - f
    envelope = width + 3
    mask = (1 << envelope) - 1
    a0 = _bit(denominator, 0)
    a1 = _bit(denominator, 1)
    v = (
        (denominator >> 1)
        - modulus
        + a1 * modulus
        + a0 * ((modulus + 1) // 2)
    ) & mask
    sign1 = _bit(modulus, 1) ^ _bit(v, 1)
    signed_v = v - (1 << envelope) if _bit(v, envelope - 1) else v
    u = (
        (modulus + signed_v) // 2
        if sign1 == 0
        else (modulus - signed_v) // 2
    ) & mask
    tape = [a0, sign1]
    checkpoints = [Checkpoint(1, envelope, u, v, tuple(tape))]
    for round_index in range(2, through_round + 1):
        u, v, sign = _walk_round(u, v, round_index, envelope)
        tape.append(sign)
        checkpoints.append(Checkpoint(round_index, envelope, u, v, tuple(tape)))
    return tuple(checkpoints)


def _violation(checkpoint: Checkpoint, denominator: int) -> Violation | None:
    if checkpoint.round_index % 2 == 0:
        passenger_name = "v[1]"
        actual = _bit(checkpoint.v, 1)
        expected = _bit(checkpoint.u, 2) ^ checkpoint.tape[1]
    else:
        passenger_name = "u[1]"
        actual = _bit(checkpoint.u, 1)
        expected = _bit(checkpoint.v, 2) ^ checkpoint.tape[1]
    if actual == expected:
        return None
    return Violation(
        denominator,
        checkpoint.round_index,
        checkpoint.width,
        passenger_name,
        actual,
        expected,
        checkpoint.u,
        checkpoint.v,
        checkpoint.tape[1],
    )


def exhaustive_scaled_support(
    *,
    width: int,
    f: int,
    through_round: int,
) -> ExhaustiveResult:
    """Exhaust every nonzero input of a scaled pseudo-Mersenne instance."""

    if width < 5 or f <= 0 or f >= (1 << width) or f % 2 == 0:
        raise ValueError("need an odd pseudo-Mersenne f inside the reduced width")
    if through_round < 1:
        raise ValueError("through_round must include the fused round-1 seed")
    modulus = (1 << width) - f
    violations: list[Violation] = []
    digest = hashlib.sha256()
    checks = 0
    for denominator in range(1, modulus):
        for checkpoint in _scaled_checkpoints(
            denominator,
            width,
            f,
            through_round,
        ):
            checks += 1
            digest.update(denominator.to_bytes(2, "big"))
            digest.update(checkpoint.round_index.to_bytes(2, "big"))
            digest.update(checkpoint.u.to_bytes(2, "big"))
            digest.update(checkpoint.v.to_bytes(2, "big"))
            found = _violation(checkpoint, denominator)
            if found is not None:
                violations.append(found)
    return ExhaustiveResult(
        width,
        f,
        modulus,
        modulus - 1,
        through_round,
        checks,
        tuple(violations),
        digest.hexdigest(),
    )


def deterministic_denominator(sample_index: int) -> int:
    if sample_index < 0:
        raise ValueError("sample index must be non-negative")
    value = int.from_bytes(
        hashlib.shake_256(SAMPLE_DOMAIN + sample_index.to_bytes(8, "big")).digest(32),
        "big",
    )
    return value % (FIELD_MODULUS - 1) + 1


def production_probe(contract: SourceContract, *, samples: int) -> ProbeResult:
    """Replay deterministic production-reachable states across every loan round."""

    if samples <= 0:
        raise ValueError("samples must be positive")
    first_round = min(contract.r1_div - 1, contract.r1_mul - 1)
    last_round = contract.r2
    violations: list[Violation] = []
    input_digest = hashlib.sha256()
    checkpoint_digest = hashlib.sha256()
    checks = 0
    for sample_index in range(samples):
        denominator = deterministic_denominator(sample_index)
        input_digest.update(denominator.to_bytes(32, "big"))
        checkpoints = _production_checkpoints(contract, denominator, last_round)
        for checkpoint in checkpoints[first_round - 1 :]:
            checks += 1
            checkpoint_digest.update(sample_index.to_bytes(4, "big"))
            checkpoint_digest.update(checkpoint.round_index.to_bytes(2, "big"))
            checkpoint_digest.update(checkpoint.width.to_bytes(2, "big"))
            checkpoint_digest.update(checkpoint.u.to_bytes(32, "big"))
            checkpoint_digest.update(checkpoint.v.to_bytes(32, "big"))
            found = _violation(checkpoint, denominator)
            if found is not None:
                violations.append(found)
    return ProbeResult(
        samples,
        first_round,
        last_round,
        checks,
        tuple(violations),
        input_digest.hexdigest(),
        checkpoint_digest.hexdigest(),
    )


def find_local_boolean_collision(
    contract: SourceContract,
    *,
    round_index: int,
    passenger: str,
    samples: int,
) -> BooleanCollision | None:
    """Apply the predeclared collision falsifier to the adjacent-sign family."""

    if passenger not in ("u", "v"):
        raise ValueError("passenger must be u or v")
    seen: dict[tuple[int, ...], CollisionState] = {}
    for sample_index in range(samples):
        denominator = deterministic_denominator(sample_index)
        checkpoint = production_checkpoint(contract, denominator, round_index)
        passenger_value = checkpoint.u if passenger == "u" else checkpoint.v
        other_value = checkpoint.v if passenger == "u" else checkpoint.u
        reconstructors = (
            _bit(other_value, 1),
            checkpoint.tape[-3],
            checkpoint.tape[-2],
            checkpoint.tape[-1],
            round_index & 1,
            _bit(checkpoint.u, 0),
            _bit(checkpoint.v, 0),
        )
        row = CollisionState(
            reconstructors,
            _bit(passenger_value, 1),
            sample_index,
            denominator,
            checkpoint.u,
            checkpoint.v,
        )
        previous = seen.get(reconstructors)
        if previous is not None and previous.passenger_bit != row.passenger_bit:
            return BooleanCollision(round_index, f"{passenger}[1]", previous, row)
        seen[reconstructors] = row
    return None


def _json_default(value: object) -> object:
    if isinstance(value, Path):
        return str(value)
    raise TypeError(type(value).__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument("--samples", type=int, default=4_096)
    args = parser.parse_args()

    contract = load_source_contract(args.repo)
    output = {
        "verdict": "ADMIT_EXACT_THIRD_PASSENGER",
        "relation": {
            "even_round": "v[1] = u[2] XOR tape[1]",
            "odd_round": "u[1] = v[2] XOR tape[1]",
        },
        "source": {
            "rounds_div": contract.rounds_div,
            "rounds_mul": contract.rounds_mul,
            "r1_div": contract.r1_div,
            "r1_mul": contract.r1_mul,
            "r2": contract.r2,
            "pingpong_sha256": contract.pingpong_sha256,
            "builder_sha256": contract.builder_sha256,
        },
        "binding_configs": [asdict(config) for config in BINDING_CONFIGS],
        "loan_sites": {
            "divide": len(loan_sites(contract, "divide")),
            "multiply": len(loan_sites(contract, "multiply")),
        },
        "low_bit_transition": asdict(exhaustive_low_bit_transition()),
        "reduced": asdict(
            exhaustive_scaled_support(width=6, f=9, through_round=39)
        ),
        "production_probe": asdict(production_probe(contract, samples=args.samples)),
    }
    print(json.dumps(output, indent=2, sort_keys=True, default=_json_default))


if __name__ == "__main__":
    main()
