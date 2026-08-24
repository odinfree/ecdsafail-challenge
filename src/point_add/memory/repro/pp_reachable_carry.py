#!/usr/bin/env python3
"""Exact reachable-support census for the ping-pong walk carry ladder.

This is a structural falsifier, not a benchmark candidate.  It deliberately
uses a fixed ``N+3`` envelope so an approximate production width schedule
cannot manufacture an apparent carry invariant.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from dataclasses import asdict, dataclass
from typing import Iterable, Mapping, Sequence

SOURCE_COMMIT = "67524171baaf568dc3dc606f38515745f70804ff"
SOURCE_TREE = "8202910d176fa1f3332ff961e6f3f789ca6a7ac2"
LIVE_SCORE = 1_154_731_130
LIVE_QUBITS = 1_267
LIVE_TOFFOLI = 911_390

DEFAULT_SPECS = (
    "5:29:15",
    "6:61:18",
    "7:127:21",
    "8:251:24",
    "9:509:27",
    "10:1021:30",
    "11:2039:33",
    "12:4093:36",
    "13:8191:39",
    "14:16381:42",
)


@dataclass(frozen=True, slots=True)
class Config:
    bits: int
    modulus: int
    rounds: int

    def __post_init__(self) -> None:
        if self.bits < 3:
            raise ValueError("bits must be at least three")
        if self.modulus <= 2 or self.modulus % 2 == 0:
            raise ValueError("modulus must be odd and greater than two")
        if self.modulus.bit_length() != self.bits:
            raise ValueError("modulus must have exactly the configured bit width")
        if self.rounds < 1:
            raise ValueError("rounds must be positive")

    @property
    def register_width(self) -> int:
        return self.bits + 3


@dataclass(frozen=True, slots=True)
class CarryTrace:
    internal_target: int
    carries: tuple[int, ...]
    internal_sum: int
    output: int


@dataclass(frozen=True, slots=True)
class Observation:
    denominator: int
    round_index: int
    source: int
    target: int
    sign: int
    terminal: bool
    carries: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class CellResult:
    round_index: int
    bit_index: int
    exact_required_width: int
    active_observations: int
    unique_local_states: int
    local_support_mask: str
    affine_expression: tuple[str, ...] | None
    local_affine_expression: tuple[str, ...] | None
    region: str


@dataclass(frozen=True, slots=True)
class WidthReport:
    bits: int
    modulus: int
    rounds: int
    register_width: int
    denominator_count: int
    observation_count: int
    active_observation_count: int
    terminal_observation_count: int
    known_c1_holds: bool
    known_c2_holds: bool
    active_cell_instances: int
    affine_cell_instances: int
    new_interior_affine_cell_instances: int
    new_interior_fraction: float
    candidate_cells: tuple[CellResult, ...]
    support_sha256: str


def bit(value: int, index: int, width: int) -> int:
    if not 0 <= index < width:
        raise ValueError("bit index lies outside the fixed-width word")
    return ((value & ((1 << width) - 1)) >> index) & 1


def bit1(value: int, width: int) -> int:
    return bit(value, 1, width)


def carry_ladder(source: int, target: int, sign: int, width: int) -> CarryTrace:
    """Return the exact carry trace of the complement-sandwiched add.

    The circuit computes ``target += source`` for sign zero and
    ``target -= source`` for sign one.  Carries refer to the internal add,
    after target complementation and before the matching output complement.
    """

    if sign not in (0, 1):
        raise ValueError("sign must be a bit")
    if width < 2:
        raise ValueError("width must be at least two")

    mask = (1 << width) - 1
    source_word = source & mask
    target_word = target & mask
    internal_target = target_word ^ (mask if sign else 0)
    carry = 0
    carries = [carry]
    internal_sum = 0
    for index in range(width):
        a = (source_word >> index) & 1
        b = (internal_target >> index) & 1
        internal_sum |= (a ^ b ^ carry) << index
        carry = (a & b) ^ (a & carry) ^ (b & carry)
        carries.append(carry)
    output = internal_sum ^ (mask if sign else 0)
    return CarryTrace(
        internal_target=internal_target,
        carries=tuple(carries),
        internal_sum=internal_sum,
        output=output,
    )


def enumerate_observations(config: Config) -> tuple[Observation, ...]:
    """Enumerate every legal denominator and every pre-round walk state."""

    width = config.register_width
    mask = (1 << width) - 1
    observations: list[Observation] = []
    for denominator in range(1, config.modulus):
        u = config.modulus
        v = denominator if denominator & 1 else denominator - config.modulus
        for round_index in range(config.rounds):
            source, target = (u, v) if round_index % 2 == 0 else (v, u)
            if source & 1 == 0 or target & 1 == 0:
                raise AssertionError("the signed walk operands must remain odd")
            sign = bit1(source, width) ^ bit1(target, width)
            trace = carry_ladder(source, target, sign, width)
            numerator = target + (-source if sign else source)
            if numerator & 1:
                raise AssertionError("the bit-one sign rule must produce an even numerator")
            if trace.output != (numerator & mask):
                raise AssertionError("carry model diverged from the integer walk add")
            observations.append(
                Observation(
                    denominator=denominator,
                    round_index=round_index,
                    source=source,
                    target=target,
                    sign=sign,
                    terminal=abs(u) == 1 and abs(v) == 1,
                    carries=trace.carries,
                )
            )
            next_target = numerator // 2
            if round_index % 2 == 0:
                v = next_target
            else:
                u = next_target
    return tuple(observations)


def find_sparse_affine(
    rows: Sequence[tuple[Mapping[str, int], int]],
    max_terms: int = 3,
) -> tuple[str, ...] | None:
    """Find a deterministic minimum-term XOR expression on exact support."""

    if not rows:
        return None
    names = tuple(sorted(rows[0][0], key=lambda name: (name != "one", name)))
    if any(tuple(sorted(features, key=lambda name: (name != "one", name))) != names for features, _ in rows):
        raise ValueError("all affine rows must expose the same features")
    if any(value not in (0, 1) for _, value in rows):
        raise ValueError("affine targets must be bits")
    signatures: dict[str, int] = {}
    for name in names:
        signature = 0
        for index, (features, _) in enumerate(rows):
            value = features[name]
            if value not in (0, 1):
                raise ValueError("affine features must be bits")
            signature |= value << index
        signatures[name] = signature
    target = sum(value << index for index, (_, value) in enumerate(rows))
    for term_count in range(min(max_terms, len(names)) + 1):
        for terms in itertools.combinations(names, term_count):
            signature = 0
            for name in terms:
                signature ^= signatures[name]
            if signature == target:
                return terms
    return None


def find_affine_solution(
    rows: Sequence[tuple[Mapping[str, int], int]],
) -> tuple[str, ...] | None:
    """Return one exact affine solution using every supplied live feature.

    Gaussian elimination is over GF(2).  Free coefficients are set to zero;
    the result is deterministic but is not claimed to have minimum Hamming
    weight.
    """

    if not rows:
        return None
    names = tuple(sorted(rows[0][0], key=lambda name: (name != "one", name)))
    if any(tuple(sorted(features, key=lambda name: (name != "one", name))) != names for features, _ in rows):
        raise ValueError("all affine rows must expose the same features")
    bit_rows: list[tuple[int, int]] = []
    for features, target in rows:
        if target not in (0, 1):
            raise ValueError("affine targets must be bits")
        vector = 0
        for index, name in enumerate(names):
            value = features[name]
            if value not in (0, 1):
                raise ValueError("affine features must be bits")
            vector |= value << index
        bit_rows.append((vector, target))
    return _solve_affine_bit_rows(bit_rows, names)


def _solve_affine_bit_rows(
    rows: Iterable[tuple[int, int]],
    names: Sequence[str],
) -> tuple[str, ...] | None:
    """Solve an affine system whose feature rows are already packed bits."""

    basis: dict[int, tuple[int, int]] = {}
    for vector, target in rows:
        value = target
        while vector:
            pivot = vector.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = (vector, value)
                break
            row_vector, row_value = basis[pivot]
            vector ^= row_vector
            value ^= row_value
        if not vector and value:
            return None

    solution = 0
    for pivot in sorted(basis):
        vector, value = basis[pivot]
        lower = vector & ((1 << pivot) - 1)
        coefficient = value ^ ((lower & solution).bit_count() & 1)
        solution |= coefficient << pivot
    return tuple(name for index, name in enumerate(names) if (solution >> index) & 1)


def _cell_features(
    observation: Observation,
    index: int,
    width: int,
) -> tuple[dict[str, int], int, int]:
    source_bit = bit(observation.source, index, width)
    target_bit = bit(observation.target, index, width)
    internal_target_bit = target_bit ^ observation.sign
    carry_in = observation.carries[index]
    carry_out = observation.carries[index + 1]
    local_features = {
        "one": 1,
        "sign": observation.sign,
        "carry_in": carry_in,
        "source_i": source_bit,
        "target_i": target_bit,
    }
    local_state = (
        (observation.sign << 3)
        | (carry_in << 2)
        | (source_bit << 1)
        | internal_target_bit
    )
    return local_features, carry_out ^ carry_in, local_state


def _global_feature_names(index: int, width: int) -> tuple[str, ...]:
    return (
        "one",
        "sign",
        *(f"source_{bit_index}" for bit_index in range(width)),
        *(f"target_{bit_index}" for bit_index in range(width)),
        *(f"carry_{carry_index}" for carry_index in range(1, index + 1)),
    )


def _global_feature_vector(observation: Observation, index: int, width: int) -> int:
    mask = (1 << width) - 1
    vector = 1 | (observation.sign << 1)
    vector |= (observation.source & mask) << 2
    vector |= (observation.target & mask) << (2 + width)
    carry_offset = 2 + 2 * width
    for carry_index in range(1, index + 1):
        vector |= observation.carries[carry_index] << (carry_offset + carry_index - 1)
    return vector


def _twos_complement_width(value: int) -> int:
    """Smallest positive width that represents ``value`` in two's complement."""

    if value >= 0:
        return value.bit_length() + 1
    return (~value).bit_length() + 1


def _required_width(observations: Sequence[Observation]) -> int:
    required = 1
    for observation in observations:
        result = observation.target + (
            -observation.source if observation.sign else observation.source
        )
        required = max(
            required,
            _twos_complement_width(observation.source),
            _twos_complement_width(observation.target),
            _twos_complement_width(result),
        )
    return required


def _region(round_index: int, index: int, exact_width: int) -> str:
    if round_index < 2:
        return "special-seed-round"
    if index < 2:
        return "known-low-two"
    if index < exact_width - 2:
        return "exact-interior"
    if index == exact_width - 2:
        return "exact-terminal-cell"
    return "outside-exact-envelope"


def analyze_config(config: Config) -> WidthReport:
    observations = enumerate_observations(config)
    active = tuple(observation for observation in observations if not observation.terminal)
    width = config.register_width
    by_round: dict[int, list[Observation]] = {}
    for observation in active:
        by_round.setdefault(observation.round_index, []).append(observation)

    cell_rows: list[dict[str, object]] = []
    candidate_cells: list[CellResult] = []
    affine_cell_instances = 0
    active_cell_instances = 0
    new_interior_affine = 0
    minimum_material_support = max(4, (config.modulus - 1) // 4)

    for round_index in sorted(by_round):
        round_observations = by_round[round_index]
        exact_width = _required_width(round_observations)
        for index in range(width):
            local_rows: list[tuple[Mapping[str, int], int]] = []
            global_rows: list[tuple[int, int]] = []
            local_states: set[int] = set()
            for observation in round_observations:
                local_features, delta, local_state = _cell_features(
                    observation, index, width
                )
                local_rows.append((local_features, delta))
                global_rows.append(
                    (_global_feature_vector(observation, index, width), delta)
                )
                local_states.add(local_state)
            local_expression = find_sparse_affine(local_rows, max_terms=5)
            expression = _solve_affine_bit_rows(
                global_rows, _global_feature_names(index, width)
            )
            region = _region(round_index, index, exact_width)
            active_cell_instances += 1
            if expression is not None:
                affine_cell_instances += 1
            material = (
                expression is not None
                and region == "exact-interior"
                and len(round_observations) >= minimum_material_support
            )
            if material:
                new_interior_affine += 1
            result = CellResult(
                round_index=round_index,
                bit_index=index,
                exact_required_width=exact_width,
                active_observations=len(round_observations),
                unique_local_states=len(local_states),
                local_support_mask=f"0x{sum(1 << state for state in local_states):04x}",
                affine_expression=expression,
                local_affine_expression=local_expression,
                region=region,
            )
            if material:
                candidate_cells.append(result)
            cell_rows.append(asdict(result))

    payload = json.dumps(cell_rows, sort_keys=True, separators=(",", ":")).encode("ascii")
    interior_instances = sum(
        1
        for round_index in by_round
        for index in range(width)
        if _region(round_index, index, _required_width(by_round[round_index])) == "exact-interior"
        and len(by_round[round_index]) >= minimum_material_support
    )
    known_c1_holds = all(
        observation.carries[1] == (1 ^ observation.sign)
        for observation in observations
    )
    known_c2_holds = all(
        observation.carries[2] == bit(observation.source, 1, width)
        for observation in observations
    )
    return WidthReport(
        bits=config.bits,
        modulus=config.modulus,
        rounds=config.rounds,
        register_width=width,
        denominator_count=config.modulus - 1,
        observation_count=len(observations),
        active_observation_count=len(active),
        terminal_observation_count=len(observations) - len(active),
        known_c1_holds=known_c1_holds,
        known_c2_holds=known_c2_holds,
        active_cell_instances=active_cell_instances,
        affine_cell_instances=affine_cell_instances,
        new_interior_affine_cell_instances=new_interior_affine,
        new_interior_fraction=(new_interior_affine / interior_instances if interior_instances else 0.0),
        candidate_cells=tuple(candidate_cells),
        support_sha256=hashlib.sha256(payload).hexdigest(),
    )


def parse_spec(spec: str) -> Config:
    try:
        bits_text, modulus_text, rounds_text = spec.split(":")
        return Config(int(bits_text), int(modulus_text), int(rounds_text))
    except (TypeError, ValueError) as error:
        raise argparse.ArgumentTypeError("spec must be BITS:MODULUS:ROUNDS") from error


def _expression_histogram(report: WidthReport) -> dict[str, int]:
    histogram: dict[str, int] = {}
    for cell in report.candidate_cells:
        expression = " xor ".join(cell.affine_expression or ("0",))
        histogram[expression] = histogram.get(expression, 0) + 1
    return dict(sorted(histogram.items()))


def build_receipt(configs: Iterable[Config]) -> dict[str, object]:
    reports = tuple(analyze_config(config) for config in configs)
    return {
        "artifact": "pp-reachable-carry-invariant-census-v1",
        "source_binding": {
            "commit": SOURCE_COMMIT,
            "tree": SOURCE_TREE,
        },
        "live_binding": {
            "score": LIVE_SCORE,
            "qubits": LIVE_QUBITS,
            "toffoli": LIVE_TOFFOLI,
        },
        "model_scope": {
            "denominators": "every integer in [1, modulus)",
            "envelope": "fixed modulus_bits + 3; no sampled width schedule",
            "states": "pre-round active and terminal states separated",
            "local_affine_features": ["one", "sign", "carry_in", "source_i", "target_i"],
            "global_affine_features": "one, sign, every source/target bit, and every earlier live carry",
            "maximum_local_affine_terms": 5,
            "global_affine_term_limit": "none; exact GF(2) consistency solve",
            "candidate_support_floor": "max(4, floor((modulus-1)/4)) active denominators",
            "non_authority": "diagnostic only; no source edit, replay, provider, or submission authority",
        },
        "width_reports": [
            {
                **asdict(report),
                "candidate_cells": [asdict(cell) for cell in report.candidate_cells],
                "candidate_expression_histogram": _expression_histogram(report),
            }
            for report in reports
        ],
        "gate": {
            "status": "DIAGNOSTIC",
            "admit_requires": "cross-width material interior equation plus arbitrary-width proof and production score mechanism",
        },
    }


def render_receipt(argv: Sequence[str] | None = None) -> str:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--spec",
        action="append",
        type=parse_spec,
        help="BITS:MODULUS:ROUNDS (repeatable)",
    )
    args = parser.parse_args(argv)
    configs = tuple(args.spec) if args.spec else tuple(map(parse_spec, DEFAULT_SPECS))
    return json.dumps(build_receipt(configs), indent=2, sort_keys=True) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    print(render_receipt(argv), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
