#!/usr/bin/env python3
"""Exact affine-domain scan for nonlinear gate identities and downgrades.

Unlike a sampled simulator, this treats all declared inputs and every
unconditional HMR result as independent Boolean variables. Affine forms are
canonical; a nonlinear product becomes UNKNOWN unless Boolean idempotence or
an inconsistent affine control system reduces it exactly.
"""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
from typing import TypeAlias

from exact_constant_cut import (
    APPEND,
    BIT_INVERT,
    BIT_STORE0,
    BIT_STORE1,
    CCX,
    CCZ,
    CX,
    DEBUG_PRINT,
    EXPECTED_COUNT,
    EXPECTED_SHA256,
    HMR,
    NEG,
    NO_WIRE,
    OpStream,
    POP_CONDITION,
    PUSH_CONDITION,
    R,
    REGISTER,
    SWAP,
    X,
    Z,
    CZ,
)


# 0 and 1 encode constants. Integers >=2 encode one variable with the low bit
# as its affine constant. Multi-variable forms are (constant, sorted vars).
Form: TypeAlias = int | tuple[int, tuple[int, ...]] | None
Condition: TypeAlias = tuple[Form, ...] | None
ZERO: Form = 0
ONE: Form = 1
UNKNOWN: Form = None


def atom(variable: int, constant: int = 0) -> Form:
    return 2 + 2 * variable + constant


def form_parts(value: Form) -> tuple[int, tuple[int, ...]] | None:
    if value is None:
        return None
    if isinstance(value, int):
        if value < 2:
            return value, ()
        return value & 1, ((value - 2) // 2,)
    return value


def make_form(constant: int, variables: tuple[int, ...]) -> Form:
    constant &= 1
    if not variables:
        return constant
    if len(variables) == 1:
        return atom(variables[0], constant)
    return constant, variables


def affine_not(value: Form) -> Form:
    parts = form_parts(value)
    if parts is None:
        return None
    constant, variables = parts
    return make_form(constant ^ 1, variables)


def affine_xor(left: Form, right: Form) -> Form:
    lparts = form_parts(left)
    rparts = form_parts(right)
    if lparts is None or rparts is None:
        return None
    lc, lv = lparts
    rc, rv = rparts
    out: list[int] = []
    i = j = 0
    while i < len(lv) and j < len(rv):
        if lv[i] < rv[j]:
            out.append(lv[i])
            i += 1
        elif rv[j] < lv[i]:
            out.append(rv[j])
            j += 1
        else:
            i += 1
            j += 1
    out.extend(lv[i:])
    out.extend(rv[j:])
    return make_form(lc ^ rc, tuple(out))


def product(factors: list[Form] | tuple[Form, ...]) -> Form:
    """Return an affine product when exact, ZERO when controls conflict, else UNKNOWN."""
    if any(value == ZERO for value in factors):
        return ZERO
    if any(value is None for value in factors):
        return UNKNOWN
    unique: list[Form] = []
    for value in factors:
        if value == ONE:
            continue
        if value not in unique:
            unique.append(value)

    # The conjunction f_i=1 is impossible iff a subset XOR of the affine
    # equations contradicts the parity of that subset. There are at most four
    # factors for a nonlinear gate, so exhaustive subset elimination is exact.
    for mask in range(1, 1 << len(unique)):
        combined: Form = ZERO
        parity = 0
        for index, value in enumerate(unique):
            if mask >> index & 1:
                combined = affine_xor(combined, value)
                parity ^= 1
        if combined in (ZERO, ONE) and combined != parity:
            return ZERO

    if not unique:
        return ONE
    if len(unique) == 1:
        return unique[0]
    return UNKNOWN


def condition_factors(base: Condition, direct: Form | None) -> Condition:
    if base is None or direct is None:
        return None
    factors = list(base)
    if direct != ONE:
        factors.append(direct)
    if product(factors) == ZERO:
        return (ZERO,)
    return tuple(factors)


def condition_product(condition: Condition) -> Form:
    return UNKNOWN if condition is None else product(condition)


def store_zero_if(value: Form, condition: Condition) -> Form:
    cond = condition_product(condition)
    if cond == ZERO:
        return value
    if cond == ONE or value == ZERO:
        return ZERO
    if cond is None:
        return UNKNOWN
    return product([value, affine_not(cond)])


def store_one_if(value: Form, condition: Condition) -> Form:
    cond = condition_product(condition)
    if cond == ZERO:
        return value
    if cond == ONE or value == ONE:
        return ONE
    if value == ZERO:
        return cond
    if cond is None or value is None:
        return UNKNOWN
    if value == cond:
        return value
    if value == affine_not(cond):
        return ONE
    return UNKNOWN


def ensure(values: list[Form], index: int) -> None:
    if index >= len(values):
        values.extend([ZERO] * (index + 1 - len(values)))


def scan(path: Path) -> tuple[list[tuple[int, int, int, int, int]], list[tuple[int, str, int]]]:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256:
        raise AssertionError(f"baseline SHA drift: {digest}")
    stream = OpStream(path)
    if stream.count != EXPECTED_COUNT:
        raise AssertionError(f"baseline count drift: {stream.count}")

    next_variable = 0
    qubits: list[Form] = []
    for _ in range(512):
        qubits.append(atom(next_variable))
        next_variable += 1
    qubits.extend([ZERO] * 1024)
    bits: list[Form] = []
    for _ in range(512):
        bits.append(atom(next_variable))
        next_variable += 1

    base: Condition = ()
    stack: list[Condition] = []
    identities: list[tuple[int, int, int, int, int]] = []
    reductions: list[tuple[int, str, int]] = []
    registers: dict[int, list[tuple[str, int]]] = {}
    watch = {
        int(value)
        for value in os.environ.get("AFFINE_WATCH_OPS", "").split(",")
        if value
    }

    for index, (kind, q2, q1, target, ctarget, ccondition, rtarget) in enumerate(stream):
        for q in (q2, q1, target):
            if q != NO_WIRE:
                ensure(qubits, q)
        for bit in (ctarget, ccondition):
            if bit != NO_WIRE:
                ensure(bits, bit)

        direct = ONE if ccondition == NO_WIRE else bits[ccondition]
        condition = condition_factors(base, direct)

        if kind in (CCX, CCZ):
            quantum_factors = [qubits[q2], qubits[q1]]
            if kind == CCZ:
                quantum_factors.append(qubits[target])
            if index in watch:
                print(
                    f"AFFINE_WATCH op={index} condition={condition!r} "
                    f"q2={qubits[q2]!r} q1={qubits[q1]!r} target={qubits[target]!r}"
                )
            all_factors = None if condition is None else list(condition) + quantum_factors
            predicate = UNKNOWN if all_factors is None else product(all_factors)
            if predicate == ZERO:
                identities.append((index, kind, q2, q1, target))
            else:
                quantum_product = product(quantum_factors)
                if kind == CCX:
                    if qubits[q2] == ONE and qubits[q1] == ONE:
                        reductions.append((index, "X", target))
                    elif qubits[q2] == ONE:
                        reductions.append((index, "CX_Q1", target))
                    elif qubits[q1] == ONE:
                        reductions.append((index, "CX_Q2", target))
                    elif quantum_product not in (ZERO, UNKNOWN) and quantum_product == qubits[q2]:
                        reductions.append((index, "CX_Q2", target))
                    elif quantum_product not in (ZERO, UNKNOWN) and quantum_product == qubits[q1]:
                        reductions.append((index, "CX_Q1", target))
                elif kind == CCZ and quantum_product not in (ZERO, UNKNOWN):
                    if quantum_product == ONE:
                        reductions.append((index, "NEG", target))
                    elif quantum_product == qubits[q2]:
                        reductions.append((index, "PHASE_Q2", target))
                    elif quantum_product == qubits[q1]:
                        reductions.append((index, "PHASE_Q1", target))
                    elif quantum_product == qubits[target]:
                        reductions.append((index, "PHASE_TARGET", target))

            if kind == CCX:
                delta = predicate
                qubits[target] = affine_xor(qubits[target], delta)
        elif kind == CX:
            factors = None if condition is None else list(condition) + [qubits[q1]]
            delta = UNKNOWN if factors is None else product(factors)
            qubits[target] = affine_xor(qubits[target], delta)
        elif kind == SWAP:
            delta = affine_xor(qubits[q1], qubits[target])
            factors = None if condition is None else list(condition) + [delta]
            toggled = UNKNOWN if factors is None else product(factors)
            qubits[q1] = affine_xor(qubits[q1], toggled)
            qubits[target] = affine_xor(qubits[target], toggled)
        elif kind == X:
            qubits[target] = affine_xor(qubits[target], condition_product(condition))
        elif kind in (R, HMR):
            qubits[target] = store_zero_if(qubits[target], condition)
            if kind == HMR:
                cond = condition_product(condition)
                fresh = atom(next_variable)
                next_variable += 1
                if cond == ONE:
                    bits[ctarget] = fresh
                elif cond != ZERO:
                    bits[ctarget] = UNKNOWN
        elif kind == BIT_INVERT:
            bits[ctarget] = affine_xor(bits[ctarget], condition_product(condition))
        elif kind == BIT_STORE0:
            bits[ctarget] = store_zero_if(bits[ctarget], condition)
        elif kind == BIT_STORE1:
            bits[ctarget] = store_one_if(bits[ctarget], condition)
        elif kind == PUSH_CONDITION:
            stack.append(base)
            base = condition_factors(base, bits[ccondition])
        elif kind == POP_CONDITION:
            if not stack:
                raise AssertionError(f"unbalanced condition stack at op {index}")
            base = stack.pop()
        elif kind == APPEND:
            wire = ("q", target) if target != NO_WIRE else ("b", ctarget)
            registers.setdefault(rtarget, []).append(wire)
        elif kind not in (NEG, REGISTER, Z, CZ, DEBUG_PRINT):
            raise AssertionError(f"unknown operation kind {kind} at op {index}")

    if stack:
        raise AssertionError("unbalanced condition stack")
    if [len(registers.get(index, [])) for index in range(4)] != [256] * 4:
        raise AssertionError("four-register ABI drift")
    return identities, reductions


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("ops", type=Path)
    args = parser.parse_args()
    identities, reductions = scan(args.ops)
    print(
        f"AFFINE_SCAN_PASS ops={EXPECTED_COUNT} identities={len(identities)} "
        f"reductions={len(reductions)}"
    )
    for row in identities:
        print("AFFINE_IDENTITY op={} kind={} q2={} q1={} target={}".format(*row))
    for index, replacement, target in reductions:
        print(f"AFFINE_REDUCE op={index} replacement={replacement} target={target}")


if __name__ == "__main__":
    main()
