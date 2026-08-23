#!/usr/bin/env python3
"""Fail-closed truth-table check for d919's borrowed-carry adder.

This is a standalone classical model.  It deliberately does not import or run
the ECDSA circuit builder.  The gate order mirrors
`cuccaro_add_fast_borrowed_carries` at source d919bc6.  A clean carry-out sink
is inserted at the terminal carry point; its net action on addend/acc is the
same as the two original terminal-sum CNOTs.

HMR randomness is tracked symbolically.  Bit j of `phase_mask` is the
coefficient of measurement outcome m_j in the residual phase.  Therefore a
zero mask proves phase independence for every measurement branch without
enumerating 2**(width-1) random outcomes.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Iterable, List, Optional, Tuple


SOURCE_COMMIT = "d919bc64a3b6a236e17870a69993fd76a21a8092"
SOURCE_SYMBOL = "src/point_add/arith/adder.rs:cuccaro_add_fast_borrowed_carries"


@dataclass(frozen=True)
class Gate:
    kind: str
    target: str
    controls: Tuple[str, ...] = ()
    measurement: Optional[str] = None

    def text(self) -> str:
        args = [*self.controls, self.target]
        if self.measurement is not None:
            args.append(self.measurement)
        return f"{self.kind} " + " ".join(args)


def cx(control: str, target: str) -> Gate:
    return Gate("CX", target, (control,))


def ccx(control1: str, control2: str, target: str) -> Gate:
    return Gate("CCX", target, (control1, control2))


def hmr(target: str, measurement: str) -> Gate:
    return Gate("HMR", target, measurement=measurement)


def cz_if(control1: str, control2: str, measurement: str) -> Gate:
    return Gate("CZ_IF", "phase", (control1, control2), measurement)


@lru_cache(maxsize=None)
def build_gates(width: int) -> Tuple[Gate, ...]:
    """Return d919's gate order plus a minimally instrumented carry-out."""
    assert width >= 2
    a = [f"a{i}" for i in range(width)]
    acc = [f"acc{i}" for i in range(width)]
    dirty = [f"d{i}" for i in range(width - 1)]
    gates: List[Gate] = []

    # Exact d919 forward carry prefix.
    gates.extend(
        [
            cx(a[0], acc[0]),
            cx(a[0], "cin"),
            ccx("cin", acc[0], dirty[0]),
            cx(dirty[0], a[0]),
        ]
    )
    for i in range(1, width - 1):
        gates.extend(
            [
                cx(a[i], acc[i]),
                cx(a[i], a[i - 1]),
                ccx(a[i - 1], acc[i], dirty[i]),
                cx(dirty[i], a[i]),
            ]
        )

    # The original two terminal-sum gates are equivalent, on a/acc, to this
    # clean-target carry-return block.  It adds exactly one CCX and no scratch.
    prev = a[width - 2]
    top_a = a[width - 1]
    top_acc = acc[width - 1]
    gates.extend(
        [
            cx(prev, top_a),
            cx(prev, top_acc),
            ccx(top_a, top_acc, "cout"),
            cx(prev, "cout"),
            cx(prev, top_a),
            cx(top_a, top_acc),
        ]
    )

    # Exact d919 measurement-based cleanup suffix.
    for i in range(width - 2, 0, -1):
        gates.extend(
            [
                cx(dirty[i], a[i]),
                hmr(dirty[i], f"m{i}"),
                cz_if(a[i - 1], acc[i], f"m{i}"),
                cx(a[i], a[i - 1]),
                cx(a[i - 1], acc[i]),
            ]
        )
    gates.extend(
        [
            cx(dirty[0], a[0]),
            hmr(dirty[0], "m0"),
            cz_if("cin", acc[0], "m0"),
            cx(a[0], "cin"),
            cx("cin", acc[0]),
        ]
    )
    return tuple(gates)


def register_value(state: Dict[str, int], prefix: str, width: int) -> int:
    return sum(state[f"{prefix}{i}"] << i for i in range(width))


def snapshot(state: Dict[str, int], width: int, phase_mask: int) -> Dict[str, object]:
    return {
        "addend": register_value(state, "a", width),
        "acc": register_value(state, "acc", width),
        "carry_in": state["cin"],
        "borrowed": register_value(state, "d", width - 1),
        "carry_out": state["cout"],
        "phase_mask": phase_mask,
    }


def apply_gate(
    gate: Gate,
    state: Dict[str, int],
    measurement_indices: Dict[str, int],
    phase_mask: int,
) -> int:
    if gate.kind == "CX":
        state[gate.target] ^= state[gate.controls[0]]
    elif gate.kind == "CCX":
        state[gate.target] ^= state[gate.controls[0]] & state[gate.controls[1]]
    elif gate.kind == "HMR":
        assert gate.measurement is not None
        if state[gate.target]:
            phase_mask ^= 1 << measurement_indices[gate.measurement]
        state[gate.target] = 0
    elif gate.kind == "CZ_IF":
        assert gate.measurement is not None
        if state[gate.controls[0]] & state[gate.controls[1]]:
            phase_mask ^= 1 << measurement_indices[gate.measurement]
    else:
        raise AssertionError(f"unknown gate {gate.kind}")
    return phase_mask


def run_case(
    width: int, acc_in: int, addend: int, carry_in: int, borrowed: int
) -> Dict[str, object]:
    state: Dict[str, int] = {"cin": carry_in, "cout": 0}
    for i in range(width):
        state[f"a{i}"] = (addend >> i) & 1
        state[f"acc{i}"] = (acc_in >> i) & 1
    for i in range(width - 1):
        state[f"d{i}"] = (borrowed >> i) & 1

    gates = build_gates(width)
    measurement_indices = {f"m{i}": i for i in range(width - 1)}
    phase_mask = 0
    destructive_gate: Optional[Dict[str, object]] = None
    for gate_index, gate in enumerate(gates):
        before = snapshot(state, width, phase_mask)
        phase_mask = apply_gate(gate, state, measurement_indices, phase_mask)
        after = snapshot(state, width, phase_mask)
        if (
            destructive_gate is None
            and gate.kind == "HMR"
            and before["borrowed"] != after["borrowed"]
        ):
            destructive_gate = {
                "index_zero_based": gate_index,
                "gate": gate.text(),
                "before": before,
                "after": after,
            }

    modulus = 1 << width
    total = acc_in + addend + carry_in
    expected = {
        "addend": addend,
        "acc": total & (modulus - 1),
        "carry_in": carry_in,
        "borrowed": borrowed,
        "carry_out": int(total >= modulus),
        "phase_mask": 0,
    }
    actual = snapshot(state, width, phase_mask)
    failures = [key for key in expected if actual[key] != expected[key]]
    recovered_acc = (int(actual["acc"]) - addend - carry_in) & (modulus - 1)
    recovered_total = recovered_acc + addend + carry_in
    inverse_identity = (
        recovered_acc == acc_in
        and actual["addend"] == addend
        and actual["carry_in"] == carry_in
        and actual["borrowed"] == borrowed
        and actual["carry_out"] == int(recovered_total >= modulus)
        and actual["phase_mask"] == 0
    )
    return {
        "input": {
            "width": width,
            "acc": acc_in,
            "addend": addend,
            "carry_in": carry_in,
            "borrowed": borrowed,
            "carry_out_target": 0,
        },
        "expected": expected,
        "actual": actual,
        "failed_invariants": failures,
        "logical_forward_inverse_identity": {
            "passed": inverse_identity,
            "recovered_acc": recovered_acc,
        },
        "first_destructive_gate": destructive_gate,
    }


def cases() -> Iterable[Tuple[int, int, int, int, int]]:
    for width in range(2, 9):
        for acc in range(1 << width):
            for addend in range(1 << width):
                for carry_in in range(2):
                    for borrowed in range(1 << (width - 1)):
                        yield width, acc, addend, carry_in, borrowed


def cost(width: int) -> Dict[str, int]:
    gates = build_gates(width)
    return {
        "width": width,
        "candidate_toffoli_with_carry_out": sum(g.kind == "CCX" for g in gates),
        "candidate_peak_owned_ancilla": 0,
        "candidate_borrowed_wires": width - 1,
        "owned_ladder_toffoli_with_carry_out": width,
        "owned_ladder_peak_owned_ancilla": width - 1,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    checked = 0
    clean_reference_checked = 0
    failure: Optional[Dict[str, object]] = None
    for case in cases():
        checked += 1
        result = run_case(*case)
        if case[-1] == 0:
            clean_reference_checked += 1
        if result["failed_invariants"]:
            failure = result
            break

    receipt = {
        "status": "HOLD" if failure else "PASS",
        "source_commit": SOURCE_COMMIT,
        "source_symbol": SOURCE_SYMBOL,
        "domain": {
            "widths": [2, 8],
            "acc": "all width-bit values",
            "addend": "all width-bit values",
            "carry_in": [0, 1],
            "borrowed": "all (width-1)-bit values",
            "carry_out_target": 0,
            "order": "width, acc, addend, carry_in, borrowed",
        },
        "fail_closed": True,
        "clean_reference_cases_checked_before_stop": clean_reference_checked,
        "cases_checked_before_stop": checked,
        "counterexample": failure,
        "cost_model": [cost(width) for width in range(2, 9)],
        "verdict": (
            "Existing borrowed-carry sequence requires zero-initialized carry wires; "
            "arbitrary borrowed values are not preserved."
            if failure
            else "All scheduled forward/inverse, phase, and ancilla checks passed."
        ),
    }
    print(json.dumps(receipt, indent=2 if args.pretty else None, sort_keys=True))
    return 1 if failure else 0


if __name__ == "__main__":
    raise SystemExit(main())
