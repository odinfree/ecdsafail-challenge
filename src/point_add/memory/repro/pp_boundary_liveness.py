#!/usr/bin/env python3
"""Exact information/liveness certificate for replay chunk boundaries.

The model is intentionally Boolean and source-bound.  It certifies whether a
chunk input carry or a MAJ-hosted internal carry can disappear from the live
state without the predecessor information needed by the exact inverse.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from typing import Sequence

SOURCE_COMMIT = "67524171baaf568dc3dc606f38515745f70804ff"
SOURCE_TREE = "8202910d176fa1f3332ff961e6f3f789ca6a7ac2"
OPS_SHA256 = "87371140be9e81a7b4a79b87b92cd0a8b0f13362bee5ecb23229807a8af6d05e"
SEMANTIC_OPS_SHA256 = "bd3612b1494a257234e8def20fb55a397f14246c1647e6c8c240080ef7e0ad37"
EMITTED_OPS = 12_593_858
LIVE_SCORE = 1_154_731_130
LIVE_QUBITS = 1_267
LIVE_TOFFOLI = 911_390


@dataclass(frozen=True, slots=True)
class PeakOwner:
    tape: int = 335
    replay_words: int = 512
    walk_limbs: int = 292
    owned_carries: int = 126
    boundaries: int = 2
    compare_window: int = 21

    @property
    def total(self) -> int:
        return self.tape + self.replay_words + self.walk_limbs + self.owned_carries + self.boundaries

    @property
    def chunk_width(self) -> int:
        return self.owned_carries + 1

    @property
    def entry_carry_index(self) -> int:
        return self.chunk_width - self.compare_window

    @property
    def q1268_strict_t_ceiling(self) -> int:
        return (LIVE_SCORE - 1) // 1268


@dataclass(frozen=True, slots=True)
class ChunkCase:
    width: int
    addend: int
    accumulator: int
    carry_in: int
    result: int
    carry_out: int

    @property
    def output_key(self) -> tuple[int, int, int]:
        return self.addend, self.result, self.carry_out


@dataclass(frozen=True, slots=True)
class Collision:
    left: ChunkCase
    right: ChunkCase


@dataclass(frozen=True, slots=True)
class WindowCase:
    width: int
    window: int
    addend: int
    accumulator: int
    carry_in: int
    result: int
    carry_out: int
    entry_carry: int

    @property
    def visible_key(self) -> tuple[int, int, int]:
        shift = self.width - self.window
        return self.addend >> shift, self.result >> shift, self.carry_in


@dataclass(frozen=True, slots=True)
class WindowAmbiguity:
    left: WindowCase
    right: WindowCase


def chunk_add(addend: int, accumulator: int, carry_in: int, width: int) -> tuple[int, int]:
    if width < 1:
        raise ValueError("width must be positive")
    if carry_in not in (0, 1):
        raise ValueError("carry_in must be a bit")
    limit = 1 << width
    if not 0 <= addend < limit or not 0 <= accumulator < limit:
        raise ValueError("operands must fit the configured width")
    total = addend + accumulator + carry_in
    return total & (limit - 1), int(total >= limit)


def _case(addend: int, accumulator: int, carry_in: int, width: int) -> ChunkCase:
    result, carry_out = chunk_add(addend, accumulator, carry_in, width)
    return ChunkCase(width, addend, accumulator, carry_in, result, carry_out)


def chunk_input_collisions(width: int) -> tuple[Collision, ...]:
    """Find equal semantic outputs produced by both values of input carry."""

    limit = 1 << width
    first: dict[tuple[int, int, int], ChunkCase] = {}
    collisions: list[Collision] = []
    for addend in range(limit):
        for accumulator in range(limit):
            for carry_in in (0, 1):
                case = _case(addend, accumulator, carry_in, width)
                previous = first.setdefault(case.output_key, case)
                if previous.carry_in != carry_in:
                    collisions.append(Collision(previous, case))
    return tuple(collisions)


def carry_into(addend: int, accumulator: int, carry_in: int, index: int) -> int:
    """Carry entering bit ``index`` of an ordinary fixed-width add."""

    carry = carry_in
    for bit_index in range(index):
        a = (addend >> bit_index) & 1
        b = (accumulator >> bit_index) & 1
        carry = (a & b) ^ (a & carry) ^ (b & carry)
    return carry


def top_window_ambiguities(width: int, window: int) -> tuple[WindowAmbiguity, ...]:
    """Witness that top slices plus chunk carry-in do not fix carry-out."""

    if not 1 <= window < width:
        raise ValueError("window must be a strict nonempty suffix")
    limit = 1 << width
    shift = width - window
    first: dict[tuple[int, int, int], WindowCase] = {}
    ambiguities: list[WindowAmbiguity] = []
    for addend in range(limit):
        for accumulator in range(limit):
            for carry_in in (0, 1):
                result, carry_out = chunk_add(addend, accumulator, carry_in, width)
                case = WindowCase(
                    width,
                    window,
                    addend,
                    accumulator,
                    carry_in,
                    result,
                    carry_out,
                    carry_into(addend, accumulator, carry_in, shift),
                )
                previous = first.setdefault(case.visible_key, case)
                if previous.carry_out != carry_out:
                    ambiguities.append(WindowAmbiguity(previous, case))
    return tuple(ambiguities)


def maj_host_forward(source: int, accumulator: int, predecessor: int) -> tuple[int, int, int]:
    """The exact source-host MAJ cell used by the earlier Q1274 lane."""

    if any(value not in (0, 1) for value in (source, accumulator, predecessor)):
        raise ValueError("MAJ host inputs must be bits")
    accumulator ^= source
    predecessor ^= source
    source ^= accumulator & predecessor
    return source, accumulator, predecessor


def maj_host_inverse(hosted_source: int, twisted_accumulator: int, twisted_predecessor: int) -> tuple[int, int, int]:
    """Finish the UMA cell, restoring source/predecessor and emitting sum."""

    if any(
        value not in (0, 1)
        for value in (hosted_source, twisted_accumulator, twisted_predecessor)
    ):
        raise ValueError("UMA host inputs must be bits")
    hosted_source ^= twisted_accumulator & twisted_predecessor
    twisted_predecessor ^= hosted_source
    twisted_accumulator ^= twisted_predecessor
    return hosted_source, twisted_accumulator, twisted_predecessor


def dependency_chain(entry_carry_index: int) -> tuple[int, ...]:
    """Predecessor carries required to restore a source-hosted entry carry."""

    if entry_carry_index < 1:
        raise ValueError("entry carry must lie above bit zero")
    return tuple(range(entry_carry_index - 1, -1, -1))


def _case_dict(case: ChunkCase | WindowCase) -> dict[str, int]:
    return asdict(case)


def build_receipt() -> dict[str, object]:
    owner = PeakOwner()
    collision_rows = []
    for width in range(1, 9):
        collisions = chunk_input_collisions(width)
        collision_rows.append(
            {
                "width": width,
                "ambiguous_output_keys": len(collisions),
                "first_witness": {
                    "left": _case_dict(collisions[0].left),
                    "right": _case_dict(collisions[0].right),
                },
            }
        )
    window_rows = []
    for width in range(2, 9):
        for window in range(1, width):
            ambiguities = top_window_ambiguities(width, window)
            window_rows.append(
                {
                    "width": width,
                    "window": window,
                    "ambiguous_visible_keys": len(ambiguities),
                    "first_witness": {
                        "left": _case_dict(ambiguities[0].left),
                        "right": _case_dict(ambiguities[0].right),
                    },
                }
            )
    host_rows = []
    for source in (0, 1):
        for accumulator in (0, 1):
            for predecessor in (0, 1):
                hosted = maj_host_forward(source, accumulator, predecessor)
                host_rows.append(
                    {
                        "input": [source, accumulator, predecessor],
                        "hosted": list(hosted),
                        "finished": list(maj_host_inverse(*hosted)),
                    }
                )
    peak_owner = {
        **asdict(owner),
        "total": owner.total,
        "chunk_width": owner.chunk_width,
        "entry_carry_index": owner.entry_carry_index,
        "entry_restore_dependency_count": len(dependency_chain(owner.entry_carry_index)),
        "q1268_strict_t_ceiling": owner.q1268_strict_t_ceiling,
        "minimum_rounded_t_saving_if_q1268": LIVE_TOFFOLI - owner.q1268_strict_t_ceiling,
    }
    return {
        "artifact": "pp-boundary-carry-liveness-v1",
        "source_binding": {
            "commit": SOURCE_COMMIT,
            "tree": SOURCE_TREE,
            "ops_sha256": OPS_SHA256,
            "canonical_semantic_ops_sha256": SEMANTIC_OPS_SHA256,
            "emitted_ops": EMITTED_OPS,
        },
        "live_binding": {
            "score": LIVE_SCORE,
            "qubits": LIVE_QUBITS,
            "rounded_toffoli": LIVE_TOFFOLI,
        },
        "peak_owner": peak_owner,
        "chunk_input_noninjectivity": collision_rows,
        "top_window_ambiguity": window_rows,
        "maj_host_truth_table": host_rows,
        "dependency_theorem": {
            "entry": "c106",
            "restore_requires": "c105 through c0, or exact recomputation of the omitted 106-bit prefix",
            "co_resident_prefix_wires": 106,
            "consequence": "one source/output host moves the bit but does not close its lifetime",
        },
        "verdict": "HARD_NACK_ONE_ENTRY_CARRY_HOST",
        "non_authority": "no production edit, trusted replay, provider, nonce, fleet, queue, push, public note, protected instance, or submission",
    }


def render_receipt(argv: Sequence[str] | None = None) -> str:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    return json.dumps(build_receipt(), indent=2, sort_keys=True) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    print(render_receipt(argv), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
