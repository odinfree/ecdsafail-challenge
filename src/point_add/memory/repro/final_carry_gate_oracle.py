"""Independent basis/measurement oracle for carry-handoff phase circuits.

This module intentionally does not import the arithmetic model in
``final_carry_handoff.py``.  Candidate behavior is emitted as primitive gates;
expected Boolean values are literal Python predicates.  HMR outcomes are
explicit independent inputs, so phase cleanliness is checked on every arm.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GateMachine:
    """Tiny gate-level basis simulator with explicit HMR phase."""

    measurement_outcomes: dict[str, int]
    qubits: dict[str, int] = field(default_factory=dict)
    live_ancillas: set[str] = field(default_factory=set)
    phase: int = 0
    toffoli_class: int = 0

    def input(self, name: str, value: int) -> None:
        if name in self.qubits:
            raise ValueError(f"duplicate qubit {name}")
        self.qubits[name] = value & 1

    def alloc(self, name: str) -> None:
        if name in self.qubits:
            raise ValueError(f"duplicate qubit {name}")
        self.qubits[name] = 0
        self.live_ancillas.add(name)

    def value(self, name: str) -> int:
        return self.qubits[name]

    def ccx(self, left: str, right: str, target: str, *, condition: int = 1) -> None:
        if condition:
            self.qubits[target] ^= self.qubits[left] & self.qubits[right]
            self.toffoli_class += 1

    def ccz(
        self,
        first: str,
        second: str,
        third: str,
        *,
        condition: int = 1,
    ) -> None:
        if condition:
            self.phase ^= (
                self.qubits[first]
                & self.qubits[second]
                & self.qubits[third]
            )
            self.toffoli_class += 1

    def hmr(self, qubit: str, measurement: str, *, condition: int = 1) -> None:
        outcome = self.measurement_outcomes[measurement]
        if condition:
            self.phase ^= self.qubits[qubit] & outcome
            self.qubits[qubit] = 0

    def cz_if(
        self,
        left: str,
        right: str,
        measurement: str,
        *,
        condition: int = 1,
    ) -> None:
        if condition:
            self.phase ^= (
                self.qubits[left]
                & self.qubits[right]
                & self.measurement_outcomes[measurement]
            )

    def release_clean(self, name: str) -> None:
        if self.qubits[name] != 0:
            raise AssertionError(f"released dirty ancilla {name}={self.qubits[name]}")
        self.live_ancillas.remove(name)


def _phase_and_gadget(
    machine: GateMachine,
    inputs: list[str],
    terminal_measurement: str,
    *,
    mutation: str | None,
) -> None:
    """Apply an HMR-conditioned AND phase with measured prefix cleanup."""

    width = len(inputs)
    if width < 3:
        raise ValueError("phase gadget requires at least three inputs")
    active = machine.measurement_outcomes[terminal_measurement]
    prefix: list[str] = []
    for index in range(width - 3):
        ancilla = f"prefix_{index}"
        machine.alloc(ancilla)
        if index == 0:
            left = inputs[0]
            right = inputs[2] if mutation == "wrong_prefix_control" else inputs[1]
        else:
            left = prefix[-1]
            right = inputs[index + 1]
        machine.ccx(left, right, ancilla, condition=active)
        prefix.append(ancilla)

    terminal_left = prefix[-1] if prefix else inputs[0]
    terminal_second = inputs[-2] if prefix else inputs[1]
    terminal_third = inputs[-1] if prefix else inputs[2]
    if mutation != "drop_terminal_ccz":
        machine.ccz(
            terminal_left,
            terminal_second,
            terminal_third,
            condition=active,
        )

    for index in range(len(prefix) - 1, -1, -1):
        ancilla = prefix[index]
        measurement = f"prefix_m_{index}"
        machine.hmr(ancilla, measurement, condition=active)
        if index == 0:
            left = inputs[0]
            right = inputs[2] if mutation == "wrong_prefix_control" else inputs[1]
        else:
            left = prefix[index - 1]
            right = inputs[index + 1]
        if not (mutation == "skip_hmr_correction" and index == 0):
            machine.cz_if(left, right, measurement, condition=active)
        machine.release_clean(ancilla)


def _run_phase_and_case(
    width: int,
    bits: int,
    outcome_bits: int,
    mutation: str | None,
) -> tuple[int, int, int]:
    labels = ["terminal"] + [f"prefix_m_{i}" for i in range(width - 3)]
    outcomes = {
        label: (outcome_bits >> index) & 1 for index, label in enumerate(labels)
    }
    machine = GateMachine(outcomes)
    inputs = [f"x_{index}" for index in range(width)]
    for index, name in enumerate(inputs):
        machine.input(name, (bits >> index) & 1)
    expected_and = int(bits == (1 << width) - 1)
    machine.alloc("carry")
    machine.qubits["carry"] = expected_and
    machine.hmr("carry", "terminal")
    machine.release_clean("carry")
    _phase_and_gadget(machine, inputs, "terminal", mutation=mutation)
    return machine.phase, len(machine.live_ancillas), machine.toffoli_class


def _exhaust_phase_and(widths: range, mutation: str | None) -> dict[str, Any]:
    widths_list = list(widths)
    phase_mismatches = 0
    ancilla_mismatches = 0
    first_witness: dict[str, int] | None = None
    active_cost: dict[str, int] = {}
    for width in widths_list:
        maximum_cost = 0
        for bits in range(1 << width):
            for outcomes in range(1 << (width - 2)):
                phase, live, cost = _run_phase_and_case(
                    width, bits, outcomes, mutation
                )
                maximum_cost = max(maximum_cost, cost)
                if phase or live:
                    phase_mismatches += int(bool(phase))
                    ancilla_mismatches += int(bool(live))
                    if first_witness is None:
                        first_witness = {
                            "width": width,
                            "inputs": bits,
                            "measurement_outcomes": outcomes,
                            "phase": phase,
                            "live_ancillas": live,
                        }
        active_cost[str(width)] = maximum_cost
    return {
        "schema": "final-carry-gate-oracle-phase-and-v1",
        "widths": widths_list,
        "basis_cases": sum(1 << width for width in widths_list),
        "phase_mismatches": phase_mismatches,
        "ancilla_mismatches": ancilla_mismatches,
        "toffoli_class_by_width": active_cost,
        "first_witness": first_witness,
    }


def exhaust_phase_and_gadget(widths: range) -> dict[str, Any]:
    return _exhaust_phase_and(widths, mutation=None)


def phase_gadget_mutation_report(widths: range) -> dict[str, Any]:
    return {
        mutation: _exhaust_phase_and(widths, mutation=mutation)
        for mutation in (
            "drop_terminal_ccz",
            "wrong_prefix_control",
            "skip_hmr_correction",
        )
    }


@dataclass
class SymbolicGateMachine:
    """Gate simulator whose HMR phase is a coefficient per outcome bit."""

    qubits: list[int] = field(default_factory=list)
    ancillas: set[int] = field(default_factory=set)
    phase_coefficients: list[int] = field(default_factory=list)
    ccx_count: int = 0

    def input(self, value: int) -> int:
        self.qubits.append(value & 1)
        return len(self.qubits) - 1

    def alloc(self) -> int:
        self.qubits.append(0)
        qubit = len(self.qubits) - 1
        self.ancillas.add(qubit)
        return qubit

    def cx(self, control: int, target: int) -> None:
        self.qubits[target] ^= self.qubits[control]

    def ccx(self, left: int, right: int, target: int) -> None:
        self.qubits[target] ^= self.qubits[left] & self.qubits[right]
        self.ccx_count += 1

    def hmr(self, qubit: int) -> int:
        measurement = len(self.phase_coefficients)
        self.phase_coefficients.append(self.qubits[qubit])
        self.qubits[qubit] = 0
        return measurement

    def cz_if(self, left: int, right: int, measurement: int) -> None:
        self.phase_coefficients[measurement] ^= (
            self.qubits[left] & self.qubits[right]
        )

    def release_clean(self, qubit: int) -> None:
        if self.qubits[qubit] != 0:
            raise AssertionError(f"released dirty ancilla q{qubit}")
        self.ancillas.remove(qubit)


def _register_value(machine: SymbolicGateMachine, register: list[int]) -> int:
    return sum(machine.qubits[qubit] << index for index, qubit in enumerate(register))


def _delayed_carry_case(
    width: int,
    addend_value: int,
    accumulator_value: int,
    carry_in_value: int,
    mutation: str | None,
) -> dict[str, Any]:
    """Execute a source-shaped carry compute, delayed use, and true inverse cleanup."""

    machine = SymbolicGateMachine()
    addend = [machine.input((addend_value >> i) & 1) for i in range(width)]
    accumulator = [
        machine.input((accumulator_value >> i) & 1) for i in range(width)
    ]
    carry_in = machine.input(carry_in_value)
    carries = [machine.alloc() for _ in range(width)]

    # Primitive-gate forward carry computation, copied from the source gate
    # schedule rather than from the integer oracle below.
    for index in range(width):
        previous = carry_in if index == 0 else carries[index - 1]
        machine.cx(previous, addend[index])
        machine.cx(previous, accumulator[index])
        machine.ccx(addend[index], accumulator[index], carries[index])
        machine.cx(previous, carries[index])

    top = width - 1
    machine.cx(carries[top - 1], addend[top])
    machine.cx(addend[top], accumulator[top])

    # Complete every lower sum bit but keep the locally transformed carry
    # qubit instead of measuring it.  This is the state that must coexist with
    # the external use of the final carry.
    for index in range(width - 2, -1, -1):
        previous = carry_in if index == 0 else carries[index - 1]
        machine.cx(previous, carries[index])
        machine.cx(previous, addend[index])
        machine.cx(addend[index], accumulator[index])

    modulus = 1 << width
    total = accumulator_value + addend_value + carry_in_value
    expected_accumulator = total & (modulus - 1)
    expected_carry = int(total >= modulus)
    boundary_accumulator = _register_value(machine, accumulator)
    boundary_addend = _register_value(machine, addend)
    boundary_carry = machine.qubits[carries[-1]]

    # Invert the delayed lower-bit completion by executing the actual inverse
    # Clifford gates, low to high.  A mutation here cannot be hidden by the
    # independent integer oracle.
    for index in range(width - 1):
        previous = carry_in if index == 0 else carries[index - 1]
        machine.cx(addend[index], accumulator[index])
        machine.cx(previous, addend[index])
        if not (mutation == "skip_delayed_inverse" and index == 0):
            machine.cx(previous, carries[index])

    if mutation != "drop_top_restore":
        machine.cx(addend[top], accumulator[top])
        machine.cx(carries[top - 1], addend[top])

    # Measurement-uncompute the whole retained chain, including the formerly
    # published final carry.  Each HMR coefficient is produced by the gate
    # state and independently cancelled by the specified controls.
    for index in range(width - 1, -1, -1):
        previous = carry_in if index == 0 else carries[index - 1]
        machine.cx(previous, carries[index])
        measurement = machine.hmr(carries[index])
        wrong = mutation == "wrong_hmr_control" and index == width - 1
        right = accumulator[0] if wrong else accumulator[index]
        machine.cz_if(addend[index], right, measurement)
        machine.cx(previous, addend[index])
        machine.cx(addend[index], accumulator[index])
        machine.release_clean(carries[index])

    final_accumulator = _register_value(machine, accumulator)
    final_addend = _register_value(machine, addend)
    phase_mismatches = sum(machine.phase_coefficients)
    ancilla_mismatches = len(machine.ancillas) + sum(
        machine.qubits[qubit] for qubit in machine.ancillas
    )
    return {
        "forward_value_mismatches": int(
            boundary_accumulator != expected_accumulator
            or boundary_carry != expected_carry
        ),
        "source_restore_mismatches": int(
            boundary_addend != addend_value or final_addend != addend_value
        ),
        "inverse_cleanup_mismatches": int(
            final_accumulator != expected_accumulator
            or machine.qubits[carry_in] != carry_in_value
        ),
        "phase_coefficient_mismatches": phase_mismatches,
        "ancilla_mismatches": ancilla_mismatches,
        "measurement_arms": len(machine.phase_coefficients),
        "ccx_count": machine.ccx_count,
    }


_DELAYED_MISMATCH_KEYS = (
    "forward_value_mismatches",
    "source_restore_mismatches",
    "inverse_cleanup_mismatches",
    "phase_coefficient_mismatches",
    "ancilla_mismatches",
)


def _exhaust_delayed_carry(
    widths: range,
    mutation: str | None,
    *,
    stop_at_first: bool,
) -> dict[str, Any]:
    widths_list = list(widths)
    totals = {key: 0 for key in _DELAYED_MISMATCH_KEYS}
    basis_cases = 0
    measurement_arms: set[tuple[int, int]] = set()
    first_witness: dict[str, int] | None = None
    ccx_by_width: dict[str, int] = {}
    for width in widths_list:
        mask = (1 << width) - 1
        for carry_in in (0, 1):
            for addend in range(mask + 1):
                for accumulator in range(mask + 1):
                    result = _delayed_carry_case(
                        width,
                        addend,
                        accumulator,
                        carry_in,
                        mutation,
                    )
                    basis_cases += 1
                    ccx_by_width[str(width)] = result["ccx_count"]
                    measurement_arms.update(
                        (width, index) for index in range(result["measurement_arms"])
                    )
                    failed = False
                    for key in _DELAYED_MISMATCH_KEYS:
                        totals[key] += result[key]
                        failed |= bool(result[key])
                    if failed and first_witness is None:
                        first_witness = {
                            "width": width,
                            "addend": addend,
                            "accumulator": accumulator,
                            "carry_in": carry_in,
                        }
                        if stop_at_first:
                            return {
                                "schema": "final-carry-gate-oracle-delayed-carry-v1",
                                "widths": widths_list,
                                "basis_cases": basis_cases,
                                **totals,
                                "uncovered_measurement_arms": [],
                                "ccx_by_width": ccx_by_width,
                                "first_witness": first_witness,
                            }

    required = {
        (width, index) for width in widths_list for index in range(width)
    }
    return {
        "schema": "final-carry-gate-oracle-delayed-carry-v1",
        "widths": widths_list,
        "basis_cases": basis_cases,
        **totals,
        "uncovered_measurement_arms": sorted(required - measurement_arms),
        "ccx_by_width": ccx_by_width,
        "first_witness": first_witness,
    }


def exhaust_delayed_carry_program(widths: range) -> dict[str, Any]:
    return _exhaust_delayed_carry(widths, mutation=None, stop_at_first=False)


def delayed_carry_mutation_report(widths: range) -> dict[str, Any]:
    return {
        mutation: _exhaust_delayed_carry(
            widths, mutation=mutation, stop_at_first=True
        )
        for mutation in (
            "drop_top_restore",
            "wrong_hmr_control",
            "skip_delayed_inverse",
        )
    }


SECP256K1_F = 0x1000003D1


def _fold_controls(
    index: int,
    width: int,
    plus_f: int,
    plus_2f: int,
    minus_f: int,
    *,
    wrong_minus_orientation: bool,
) -> list[int]:
    mask = (1 << width) - 1
    f = SECP256K1_F & mask
    negative_f = f if wrong_minus_orientation else ((-f) & mask)
    controls: list[int] = []
    if (f >> index) & 1:
        controls.append(plus_f)
    if index > 0 and ((f >> (index - 1)) & 1):
        controls.append(plus_2f)
    if (negative_f >> index) & 1:
        controls.append(minus_f)
    return controls


def _fused_fold_case(
    width: int,
    accumulator_value: int,
    digit: int,
    mutation: str | None,
) -> dict[str, Any]:
    machine = SymbolicGateMachine()
    accumulator = [
        machine.input((accumulator_value >> index) & 1)
        for index in range(width)
    ]
    plus_f = machine.input(int(digit == 1))
    plus_2f = machine.input(int(digit == 2))
    minus_f = machine.input(int(digit == -1))
    selector_ids = (plus_f, plus_2f, minus_f)
    selector_before = tuple(machine.qubits[q] for q in selector_ids)
    mask = (1 << width) - 1
    f = SECP256K1_F & mask
    operand = (digit * f) & mask
    first_carry = machine.input((accumulator_value & 1) & (operand & 1))
    first_before = machine.qubits[first_carry]

    def controls(index: int) -> list[int]:
        return _fold_controls(
            index,
            width,
            plus_f,
            plus_2f,
            minus_f,
            wrong_minus_orientation=(mutation == "wrong_minus_orientation"),
        )

    for control in controls(0):
        machine.cx(control, accumulator[0])

    carries = [machine.alloc() for _ in range(width - 3)]
    for offset, carry in enumerate(carries):
        index = 1 + offset
        previous = first_carry if offset == 0 else carries[offset - 1]
        selectors = controls(index)
        if not selectors:
            machine.cx(previous, accumulator[index])
            machine.ccx(previous, accumulator[index], carry)
            machine.cx(previous, carry)
        else:
            operand_wire = selectors[0]
            for control in selectors[1:]:
                machine.cx(control, operand_wire)
            machine.cx(previous, operand_wire)
            machine.cx(previous, accumulator[index])
            machine.ccx(operand_wire, accumulator[index], carry)
            machine.cx(previous, carry)
            machine.cx(previous, operand_wire)
            for control in reversed(selectors[1:]):
                machine.cx(control, operand_wire)

    index = width - 2
    previous = carries[-1] if carries else first_carry
    selectors = controls(index)
    if not selectors:
        machine.cx(previous, accumulator[index])
        if mutation != "drop_terminal_carry":
            machine.ccx(previous, accumulator[index], accumulator[width - 1])
            machine.cx(previous, accumulator[width - 1])
    else:
        operand_wire = selectors[0]
        for control in selectors[1:]:
            machine.cx(control, operand_wire)
        machine.cx(previous, operand_wire)
        machine.cx(previous, accumulator[index])
        if mutation != "drop_terminal_carry":
            machine.ccx(
                operand_wire,
                accumulator[index],
                accumulator[width - 1],
            )
            machine.cx(previous, accumulator[width - 1])
        machine.cx(previous, operand_wire)
        machine.cx(operand_wire, accumulator[index])
        for control in reversed(selectors[1:]):
            machine.cx(control, operand_wire)
    for control in controls(width - 1):
        machine.cx(control, accumulator[width - 1])

    for offset in range(len(carries) - 1, -1, -1):
        index = 1 + offset
        carry = carries[offset]
        previous = first_carry if offset == 0 else carries[offset - 1]
        selectors = controls(index)
        if not selectors:
            machine.cx(previous, carry)
            measurement = machine.hmr(carry)
            if not (mutation == "skip_fold_hmr_correction" and offset == 0):
                machine.cz_if(previous, accumulator[index], measurement)
        else:
            operand_wire = selectors[0]
            for control in selectors[1:]:
                machine.cx(control, operand_wire)
            machine.cx(previous, carry)
            machine.cx(previous, operand_wire)
            measurement = machine.hmr(carry)
            if not (mutation == "skip_fold_hmr_correction" and offset == 0):
                machine.cz_if(operand_wire, accumulator[index], measurement)
            machine.cx(previous, operand_wire)
            machine.cx(operand_wire, accumulator[index])
            for control in reversed(selectors[1:]):
                machine.cx(control, operand_wire)
        machine.release_clean(carry)

    expected = (accumulator_value + digit * f) & mask
    observed = _register_value(machine, accumulator)
    selectors_after = tuple(machine.qubits[q] for q in selector_ids)
    return {
        "forward_value_mismatches": int(observed != expected),
        "selector_restore_mismatches": int(
            selectors_after != selector_before
            or machine.qubits[first_carry] != first_before
        ),
        "inverse_cleanup_mismatches": int(bool(machine.ancillas)),
        "phase_coefficient_mismatches": sum(machine.phase_coefficients),
        "ancilla_mismatches": len(machine.ancillas),
        "ccx_count": machine.ccx_count,
    }


_FOLD_MISMATCH_KEYS = (
    "forward_value_mismatches",
    "selector_restore_mismatches",
    "inverse_cleanup_mismatches",
    "phase_coefficient_mismatches",
    "ancilla_mismatches",
)


def _exhaust_fused_fold(
    widths: range,
    mutation: str | None,
    *,
    stop_at_first: bool,
) -> dict[str, Any]:
    widths_list = list(widths)
    totals = {key: 0 for key in _FOLD_MISMATCH_KEYS}
    basis_cases = 0
    covered_digits: set[int] = set()
    first_witness: dict[str, int] | None = None
    ccx_by_width: dict[str, int] = {}
    for width in widths_list:
        for digit in (-1, 0, 1, 2):
            covered_digits.add(digit)
            for accumulator in range(1 << width):
                result = _fused_fold_case(width, accumulator, digit, mutation)
                basis_cases += 1
                ccx_by_width[str(width)] = result["ccx_count"]
                failed = False
                for key in _FOLD_MISMATCH_KEYS:
                    totals[key] += result[key]
                    failed |= bool(result[key])
                if failed and first_witness is None:
                    first_witness = {
                        "width": width,
                        "accumulator": accumulator,
                        "digit": digit,
                    }
                    if stop_at_first:
                        return {
                            "schema": "final-carry-gate-oracle-fused-fold-v1",
                            "widths": widths_list,
                            "basis_cases": basis_cases,
                            "covered_digits": sorted(covered_digits),
                            **totals,
                            "ccx_by_width": ccx_by_width,
                            "first_witness": first_witness,
                        }
    return {
        "schema": "final-carry-gate-oracle-fused-fold-v1",
        "widths": widths_list,
        "basis_cases": basis_cases,
        "covered_digits": sorted(covered_digits),
        **totals,
        "ccx_by_width": ccx_by_width,
        "first_witness": first_witness,
    }


def exhaust_fused_fold_program(widths: range) -> dict[str, Any]:
    return _exhaust_fused_fold(widths, mutation=None, stop_at_first=False)


def fused_fold_mutation_report(widths: range) -> dict[str, Any]:
    return {
        mutation: _exhaust_fused_fold(widths, mutation, stop_at_first=True)
        for mutation in (
            "drop_terminal_carry",
            "wrong_minus_orientation",
            "skip_fold_hmr_correction",
        )
    }


def _affine_truth_table(mask: int) -> int:
    """Return the 16-row truth table of an affine form in x,y,p,a.

    Bits zero through three of ``mask`` select variables and bit four is the
    constant.  The truth-table row index uses the same x,y,p,a ordering.  This
    representation makes the synthesis search independent of either carry
    recurrence implemented above.
    """

    table = 0
    for row in range(16):
        value = (mask >> 4) & 1
        for variable in range(4):
            value ^= ((mask >> variable) & 1) & ((row >> variable) & 1)
        table |= value << row
    return table


def exhaust_single_dirty_host_synthesis() -> dict[str, Any]:
    """Exhaust the one-product conversion of q=xy into q=pa.

    A CCX-class update with freely chosen affine Clifford pre/post-processing
    can toggle a target by one product of two affine forms.  Converting the
    local dirty carry ``xy`` to the disjoint fold carry ``pa`` in one such
    update would therefore require ``L1*L2 = xy XOR pa``.  We enumerate every
    ordered pair of four-variable affine forms instead of assuming a choice of
    controls.

    This is deliberately a *local single-host* result.  It is not a lower
    bound for arbitrary multiwire selector encodings or measurement-assisted
    circuits.
    """

    affine_tables = [_affine_truth_table(mask) for mask in range(32)]
    xy = 0
    pa = 0
    for row in range(16):
        x, y, p, a = ((row >> index) & 1 for index in range(4))
        xy |= (x & y) << row
        pa |= (p & a) << row
    required_toggle = xy ^ pa

    solutions: list[tuple[int, int]] = []
    for left, left_table in enumerate(affine_tables):
        for right, right_table in enumerate(affine_tables):
            if left_table & right_table == required_toggle:
                solutions.append((left, right))

    full_table_mask = (1 << 16) - 1
    two_gate_result = xy ^ xy ^ pa
    clean_host_result = 0 ^ pa
    return {
        "schema": "final-carry-single-dirty-host-synthesis-v1",
        "basis_cases": 16,
        "affine_forms": len(affine_tables),
        "one_gate_candidates": len(affine_tables) ** 2,
        "one_gate_solutions": len(solutions),
        "first_solution": list(solutions[0]) if solutions else None,
        "two_gate_witness_passes": (two_gate_result & full_table_mask) == pa,
        "clean_host_one_gate_control_passes": (
            clean_host_result & full_table_mask
        )
        == pa,
        "scope": (
            "one target host, one affine-product toggle, four independent "
            "local variables; excludes multiwire and HMR-assisted encodings"
        ),
    }


def exact_reuse_requirement_report(
    records: list[dict[str, Any]],
    *,
    saved_ccx_per_cell: int,
    peak_limit: int,
) -> dict[str, Any]:
    """Price the optimistic retained-boundary relaxation on exact census rows.

    The source flag comparator has 21 nonlinear steps.  After saving ``s``
    steps, its remaining ``21-s`` steps can synthesize that many predecessors
    inside the final chunk.  The unresolved live state is the remaining top
    predecessors *plus the incoming final-chunk boundary*.  If these coexist
    with the clean fold ladder, ``fold_peak + retained`` is the relevant peak;
    the excess above ``peak_limit`` is the minimum number of hosts that must be
    reused in this optimistic accounting.
    """

    if not records:
        raise ValueError("exact census records must not be empty")
    if not 0 <= saved_ccx_per_cell <= 21:
        raise ValueError("saved_ccx_per_cell must be between zero and 21")

    cleanup_budget = 21 - saved_ccx_per_cell
    reused_hosts: list[int] = []
    for record in records:
        final_chunk_width = int(record["final_chunk_width"])
        retained_top_predecessors = max(0, final_chunk_width - cleanup_budget)
        retained_with_boundary = retained_top_predecessors + 1
        no_reuse_peak = int(record["fold_peak"]) + retained_with_boundary
        reused_hosts.append(max(0, no_reuse_peak - peak_limit))

    cells = len(records)
    branch_probability = 0.5
    gross_average_t = cells * saved_ccx_per_cell * branch_probability
    depth1_added_average_t = cells * branch_probability
    unconditioned_added_average_t = float(cells)
    return {
        "schema": "final-carry-exact-reuse-requirement-v1",
        "cells": cells,
        "saved_ccx_per_cell": saved_ccx_per_cell,
        "cleanup_budget": cleanup_budget,
        "cells_requiring_reuse": sum(value > 0 for value in reused_hosts),
        "minimum_reused_hosts": min(reused_hosts),
        "maximum_reused_hosts": max(reused_hosts),
        "gross_average_t": gross_average_t,
        "added_average_t_one_depth1_gate_per_cell": depth1_added_average_t,
        "added_average_t_one_unconditioned_gate_per_cell": (
            unconditioned_added_average_t
        ),
        "net_if_one_depth1_gate_per_cell": (
            gross_average_t - depth1_added_average_t
        ),
        "net_if_one_unconditioned_gate_per_cell": (
            gross_average_t - unconditioned_added_average_t
        ),
        "scope": (
            "exact static rows under retained-boundary relaxation; host count "
            "is a lifetime requirement, not a nonlinear lower bound"
        ),
    }


def exhaust_affine_dirty_host_conjugation() -> dict[str, Any]:
    """Check a full Clifford-conjugated one-gate dirty-host swap.

    At the handoff restriction, the five physical wires span
    ``{x,y,p,a,xy}``; arbitrary X/CX conjugation can therefore put any affine
    combination of those functions on either control.  A one-Toffoli span swap
    from the dirty predicate ``xy`` to the independent fold predicate ``pa``
    would require their product to lie in ``xy XOR pa XOR Aff(x,y,p,a)``.
    Exhausting all 64-by-64 control pairs finds no such product.  This is
    stronger than checking only a CCX directly targeted at the dirty wire.

    The mixed-residual mutation records why independence matters:
    ``(x XOR p)(y XOR a)`` contains ``xy XOR pa`` but also the forbidden mixed
    terms ``xa XOR py``.  A later nonlinear gate is required to cancel those
    terms before the high and low interfaces separate again.
    """

    one = (1 << 16) - 1
    variables = []
    for variable in range(4):
        variables.append(
            sum(((row >> variable) & 1) << row for row in range(16))
        )
    x, y, p, a = variables
    dirty = x & y
    fold = p & a

    physical_basis = [one, x, y, p, a, dirty]
    physical_forms: list[int] = []
    for mask in range(1 << len(physical_basis)):
        table = 0
        for index, basis in enumerate(physical_basis):
            if (mask >> index) & 1:
                table ^= basis
        physical_forms.append(table)

    data_affine: set[int] = set()
    for mask in range(1 << 5):
        table = 0
        for index, basis in enumerate([one, x, y, p, a]):
            if (mask >> index) & 1:
                table ^= basis
        data_affine.add(table)

    desired_coset = {dirty ^ fold ^ affine for affine in data_affine}
    one_gate_solutions = 0
    drop_dirty_solutions = 0
    mixed_target = dirty ^ fold ^ (x & a) ^ (p & y)
    mixed_solutions = 0
    for left in physical_forms:
        for right in physical_forms:
            product = left & right
            one_gate_solutions += int(product in desired_coset)
            drop_dirty_solutions += int(
                any(product == fold ^ affine for affine in data_affine)
            )
            mixed_solutions += int(product == mixed_target)

    return {
        "schema": "final-carry-affine-dirty-host-conjugation-v1",
        "basis_cases": 16,
        "physical_affine_forms": len(physical_forms),
        "control_pairs": len(physical_forms) ** 2,
        "one_gate_span_swap_solutions": one_gate_solutions,
        "two_gate_span_swap_witness_passes": dirty ^ dirty ^ fold == fold,
        "mutation_drop_dirty_term_has_solutions": drop_dirty_solutions > 0,
        "mutation_allow_mixed_residual_has_solutions": mixed_solutions > 0,
        "scope": (
            "arbitrary Clifford conjugation of one independent dirty product "
            "and one independent fold product; a global nonlinear multi-stage "
            "encoding still needs the separability argument"
        ),
    }


def _gf2_rank(vectors: list[int]) -> int:
    basis: list[int] = []
    for vector in vectors:
        reduced = vector
        for pivot in basis:
            reduced = min(reduced, reduced ^ pivot)
        if reduced:
            basis.append(reduced)
            basis.sort(reverse=True)
    return len(basis)


def _divide_fold_state(sign: int, parity: int, carry: int) -> tuple[int, int, int, int]:
    first = (1 ^ sign) & parity
    sign_and_parity = sign & parity
    minus = (1 ^ carry) & first
    plus_two = carry & sign_and_parity
    plus = parity ^ sign ^ minus
    return first, minus, plus, plus_two


def _multiply_fold_state(
    sign: int,
    doubled: int,
    carry: int,
    low_bit: int,
) -> tuple[int, int, int, int]:
    routed = doubled & (sign ^ carry)
    minus = routed & sign
    plus_two = routed ^ minus
    first = low_bit & (doubled ^ carry)
    plus = carry ^ doubled ^ minus
    return first, minus, plus, plus_two


def _table(rows: list[tuple[int, ...]], function: Any) -> int:
    return sum(int(function(*row)) << index for index, row in enumerate(rows))


def _exact_local_arm_witnesses(site: str) -> dict[tuple[int, ...], tuple[int, int]]:
    """Find small deterministic canonical secp witnesses for every local arm."""

    modulus = (1 << 256) - SECP256K1_F
    mask = (1 << 256) - 1
    midpoint = 1 << 255
    candidates = set(range(16))
    candidates.update(modulus - offset for offset in range(1, 17))
    candidates.update(midpoint + offset for offset in range(-8, 9))
    values = sorted(value for value in candidates if 0 <= value < modulus)
    witnesses: dict[tuple[int, ...], tuple[int, int]] = {}
    for sign in (0, 1):
        for source in values:
            for target in values:
                if site == "divide":
                    add_target = target ^ (mask if sign else 0)
                    total = add_target + source
                    post_add = total & mask
                    carry = total >> 256
                    arm = (sign, post_add & 1, carry)
                elif site == "multiply":
                    doubled = (target >> 255) & 1
                    shifted = (target << 1) & mask
                    add_target = shifted ^ (mask if sign else 0)
                    total = add_target + source
                    post_add = total & mask
                    carry = total >> 256
                    arm = (sign, doubled, carry, post_add & 1)
                else:
                    raise ValueError(f"unknown site {site}")
                witnesses.setdefault(arm, (source, target))
    return witnesses


def selector_code_rank_report() -> dict[str, Any]:
    """Rank every fold operand function, first carry, and final add carry.

    A zero-nonlinear-cost publication can only decode controls by affine
    Clifford combinations of the live code wires.  The GF(2) truth-table rank
    is consequently a wire lower bound for that zero-cost subfamily.  Exact
    canonical secp witnesses ensure no local truth-table arm is fictitious.
    """

    report: dict[str, Any] = {
        "schema": "final-carry-selector-code-rank-v1"
    }
    for site, width in (("divide", 54), ("multiply", 53)):
        if site == "divide":
            rows = [
                (sign, parity, carry)
                for sign in (0, 1)
                for parity in (0, 1)
                for carry in (0, 1)
            ]
            state = _divide_fold_state
            final_index = 2
            baseline_live_functions = 5
        else:
            rows = [
                (sign, doubled, carry, low_bit)
                for sign in (0, 1)
                for doubled in (0, 1)
                for carry in (0, 1)
                for low_bit in (0, 1)
            ]
            state = _multiply_fold_state
            final_index = 2
            # doubled_out is already an independently live source wire, so
            # the source uses one more allocated selector carrier than the
            # affine quotient strictly needs.
            baseline_live_functions = 6

        negative = (-SECP256K1_F) & ((1 << width) - 1)
        operand_tables: list[int] = []
        for index in range(width):
            def operand(*arm: int, index: int = index) -> int:
                _first, minus, plus, plus_two = state(*arm)
                return (
                    (((SECP256K1_F >> index) & 1) & plus)
                    ^ (
                        int(index > 0)
                        & ((SECP256K1_F >> max(0, index - 1)) & 1)
                        & plus_two
                    )
                    ^ (((negative >> index) & 1) & minus)
                )

            operand_tables.append(_table(rows, operand))

        first_table = _table(rows, lambda *arm: state(*arm)[0])
        final_table = _table(rows, lambda *arm: arm[final_index])
        desired_rank = _gf2_rank(operand_tables + [first_table, final_table])
        witnesses = _exact_local_arm_witnesses(site)
        report[site] = {
            "fold_width": width,
            "local_arms": len(rows),
            "exact_source_witnessed_arms": len(witnesses),
            "missing_exact_source_arms": [
                list(row) for row in rows if row not in witnesses
            ],
            "distinct_operand_functions": len(set(operand_tables)),
            "operand_function_rank": _gf2_rank(operand_tables),
            "operand_plus_first_carry_rank": _gf2_rank(
                operand_tables + [first_table]
            ),
            "operand_first_and_final_carry_rank": desired_rank,
            "baseline_live_function_wires": baseline_live_functions,
            "zero_t_wire_reclaim_upper_bound": (
                baseline_live_functions - desired_rank
            ),
            "scope": (
                "affine/Clifford-decodable publication; fewer wires require "
                "nonlinear decoding and must be charged"
            ),
        }
    return report


def optimistic_phase_host_report(
    records: list[dict[str, Any]],
    *,
    saved_ccx_per_cell: int,
    phase_terminal_discount: int,
    free_selector_wires: int,
    peak_limit: int,
) -> dict[str, Any]:
    """Give phase gadgets and selector coding every favorable Q assumption.

    The old retained-boundary relaxation allowed one missing carry transition
    per remaining comparator CCX.  Here ``phase_terminal_discount`` grants
    extra missing transitions for free, and ``free_selector_wires`` is
    deducted at the peak for *both* sites even though the rank report grants it
    only to multiply.  The production report uses a discount of 25: eighteen
    three-local nonlinear gates are thereby credited with a 43-input carry
    phase, beyond even the generous connected-support ceiling ``2g+1 = 37``.
    Any remaining excess under that deliberately impossible advantage must
    still be released or reused.
    """

    if not records:
        raise ValueError("exact census records must not be empty")
    phase_cost = 21 - saved_ccx_per_cell
    unretained = phase_cost + phase_terminal_discount
    excesses: list[int] = []
    for record in records:
        retained_top = max(0, int(record["final_chunk_width"]) - unretained)
        retained_with_boundary = retained_top + 1
        optimistic_peak = (
            int(record["fold_peak"])
            + retained_with_boundary
            - free_selector_wires
        )
        excesses.append(max(0, optimistic_peak - peak_limit))

    cells = len(records)
    gross = cells * saved_ccx_per_cell * 0.5
    affected = sum(value > 0 for value in excesses)
    added_depth1 = affected * 0.5
    return {
        "schema": "final-carry-optimistic-phase-host-v1",
        "cells": cells,
        "remaining_phase_toffoli_class_per_cell": phase_cost,
        "phase_terminal_discount": phase_terminal_discount,
        "unretained_bits_at_same_phase_cost": unretained,
        "free_selector_wires": free_selector_wires,
        "cells_still_requiring_host_reuse": affected,
        "minimum_reused_hosts": min(excesses),
        "maximum_reused_hosts": max(excesses),
        "gross_average_t": gross,
        "added_if_one_depth1_gate_per_affected_cell": added_depth1,
        "net_upper_bound_after_one_depth1_gate": gross - added_depth1,
        "scope": (
            "optimistic relaxation, not a phase construction; it intentionally "
            "overcredits terminal phase and selector savings"
        ),
    }


def _carry_sequence(left: int, right: int, width: int, carry_in: int = 0) -> int:
    """Pack c_1 through c_width for an ordinary binary addition."""

    carry = carry_in
    packed = 0
    for index in range(width):
        a = (left >> index) & 1
        b = (right >> index) & 1
        carry = (a & b) ^ (a & carry) ^ (b & carry)
        packed |= carry << index
    return packed


def carry_bank_independence_report(
    reduced_widths: range,
    *,
    exact_rank: int,
) -> dict[str, Any]:
    """Check the retained add-carry bank is a full independent dirty bank.

    Given any requested next-carry word ``z``, choosing both add bits at
    position i equal to ``z_i`` forces the next carry to ``z_i`` regardless of
    the incoming carry.  Thus every raw carry word occurs.  The source's
    retained transformed word consists of adjacent carry differences, an
    invertible triangular Clifford change of coordinates once the boundary is
    present, so it has the same full image.

    The exact transfer places this construction in bits below 255 with top bit
    zero.  Both canonical divide operands are then below 2^255.  At multiply,
    the desired shifted add-target bits are placed one position lower in the
    original target, also below 2^255.  Low fold bits stay zero and are
    therefore independent of every tested bank pattern.
    """

    widths = list(reduced_widths)
    reduced_patterns = 0
    recurrence_mismatches = 0
    missing_patterns = 0
    for width in widths:
        observed: set[int] = set()
        for requested in range(1 << width):
            left = requested
            right = requested
            observed_word = _carry_sequence(left, right, width)
            reduced_patterns += 1
            recurrence_mismatches += int(observed_word != requested)
            observed.add(observed_word)
        missing_patterns += (1 << width) - len(observed)

    if not 1 <= exact_rank <= 254:
        raise ValueError("exact_rank must fit below the fixed zero top bit")
    exact_mask = (1 << exact_rank) - 1
    alternating_even = sum(1 << index for index in range(0, exact_rank, 2))
    alternating_odd = sum(1 << index for index in range(1, exact_rank, 2))
    patterns = {
        0,
        exact_mask,
        alternating_even,
        alternating_odd,
        *(1 << index for index in range(exact_rank)),
    }
    modulus = (1 << 256) - SECP256K1_F
    full_mask = (1 << 256) - 1
    start = 255 - exact_rank
    canonical_mismatches = 0
    exact_recurrence_mismatches = 0
    low_fold_mismatches = 0
    site_counts = {"divide": 0, "multiply": 0}
    for site in site_counts:
        for requested in sorted(patterns):
            addend = 0
            add_target = 0
            original_target = 0
            for offset in range(exact_rank):
                bit = (requested >> offset) & 1
                position = start + offset
                addend |= bit << position
                add_target |= bit << position
                if site == "multiply":
                    original_target |= bit << (position - 1)

            if site == "divide":
                source = addend
                target = add_target
                observed_add_target = target
                fold_width = 54
            else:
                source = addend
                target = original_target
                observed_add_target = (target << 1) & full_mask
                fold_width = 53

            canonical_mismatches += int(
                not (0 <= source < modulus and 0 <= target < modulus)
            )
            observed = _carry_sequence(
                source >> start,
                observed_add_target >> start,
                exact_rank,
            )
            exact_recurrence_mismatches += int(observed != requested)
            low_fold_mismatches += int(
                (source & ((1 << fold_width) - 1)) != 0
                or (observed_add_target & ((1 << fold_width) - 1)) != 0
            )
            site_counts[site] += 1

    return {
        "schema": "final-carry-bank-independence-v1",
        "reduced_widths": widths,
        "reduced_patterns": reduced_patterns,
        "reduced_recurrence_mismatches": recurrence_mismatches,
        "reduced_missing_patterns": missing_patterns,
        "exact_rank": exact_rank,
        "exact_patterns_per_site": len(patterns),
        "exact_canonical_mismatches": canonical_mismatches,
        "exact_recurrence_mismatches": exact_recurrence_mismatches,
        "exact_low_fold_state_mismatches": low_fold_mismatches,
        "sites": {
            site: {"patterns": count} for site, count in site_counts.items()
        },
        "transformed_bank": (
            "d_i = c_(i+1) XOR c_i is an invertible triangular Clifford "
            "coordinate map when the incoming boundary c_0 is retained"
        ),
        "exact_transfer": (
            "sign=0, top operand bits zero, patterns embedded below bit 255; "
            "multiply target shifted from one position lower"
        ),
    }


def _packed_add_interface_tables(
    width: int,
) -> tuple[list[int], list[int], list[int]]:
    """Return source, modular-sum, and raw-carry truth tables.

    The row index packs the source below the target.  Bytearrays avoid the
    quadratic large-integer behavior of setting one Python-int bit at a time
    when width nine reaches 262,144 rows.
    """

    rows = 1 << (2 * width)
    byte_count = (rows + 7) // 8
    source_bits = [bytearray(byte_count) for _ in range(width)]
    sum_bits = [bytearray(byte_count) for _ in range(width)]
    carry_bits = [bytearray(byte_count) for _ in range(width)]
    mask = (1 << width) - 1
    for row in range(rows):
        source = row & mask
        target = row >> width
        summed = (source + target) & mask
        carry = 0
        byte = row >> 3
        bit = 1 << (row & 7)
        for index in range(width):
            source_bit = (source >> index) & 1
            target_bit = (target >> index) & 1
            if source_bit:
                source_bits[index][byte] |= bit
            if (summed >> index) & 1:
                sum_bits[index][byte] |= bit
            carry = (
                (source_bit & target_bit)
                ^ (source_bit & carry)
                ^ (target_bit & carry)
            )
            if carry:
                carry_bits[index][byte] |= bit

    convert = lambda tables: [
        int.from_bytes(table, "little") for table in tables
    ]
    return convert(source_bits), convert(sum_bits), convert(carry_bits)


def carry_checkpoint_quotient_rank_report(
    reduced_widths: range,
) -> dict[str, Any]:
    """Rank retained carries modulo the actual live add interface.

    A raw full-image carry word is not enough: a reviewer could ask whether
    source and finished-sum wires already contain affine copies of those
    carries.  This exhaustive quotient test includes precisely those live
    wires.  Every carry adds one new Boolean-function dimension.  Adjacent
    differences have the same rank because the boundary-plus-difference map
    is triangular and invertible.

    The exact-width transfer uses source-valid witnesses rather than an
    extrapolation from the reduced ranks.  Canonical unit inputs on the two
    coordinate axes first eliminate every source and finished-sum coefficient
    in a putative affine relation.  For each exact final-chunk width, setting
    both add inputs equal on that chunk then realizes zero, all-one,
    alternating, and every unit carry word.  The unit words eliminate every
    retained-carry coefficient.  The recurrence is executed across all 256
    positions, including the actual divide target and the multiply target
    before its source-exact left shift.
    """

    widths = list(reduced_widths)
    raw_ranks: dict[str, int] = {}
    transformed_ranks: dict[str, int] = {}
    basis_cases: dict[str, int] = {}
    mismatches = 0
    for width in widths:
        source, summed, carries = _packed_add_interface_tables(width)
        rows = 1 << (2 * width)
        common = [(1 << rows) - 1, *source, *summed]
        common_rank = _gf2_rank(common)
        raw_rank = _gf2_rank([*common, *carries]) - common_rank
        transformed = [
            carry ^ (carries[index - 1] if index else 0)
            for index, carry in enumerate(carries)
        ]
        transformed_rank = (
            _gf2_rank([*common, *transformed]) - common_rank
        )
        raw_ranks[str(width)] = raw_rank
        transformed_ranks[str(width)] = transformed_rank
        basis_cases[str(width)] = rows
        mismatches += int(raw_rank != width or transformed_rank != width)

    modulus = (1 << 256) - SECP256K1_F
    full_mask = (1 << 256) - 1
    canonical_mismatches = 0
    exact_recurrence_mismatches = 0

    # These canonical coordinate-axis witnesses eliminate the constant,
    # source, and finished-sum terms of any affine relation before the carry
    # witnesses below are considered.  Every unit is strictly below p.
    axis_inputs = [(0, 0)]
    axis_inputs.extend((1 << bit, 0) for bit in range(256))
    axis_inputs.extend((0, 1 << bit) for bit in range(256))
    for source, target in axis_inputs:
        canonical_mismatches += int(
            not (0 <= source < modulus and 0 <= target < modulus)
        )
        exact_recurrence_mismatches += int(
            _carry_sequence(source, target, 256) != 0
        )

    exact_transfer: dict[str, dict[str, int]] = {}
    for site, width in (("divide", 127), ("multiply", 128)):
        start = 256 - width
        carry_mask = (1 << width) - 1
        alternating_even = sum(1 << index for index in range(0, width, 2))
        alternating_odd = sum(1 << index for index in range(1, width, 2))
        requested_patterns = {
            0,
            carry_mask,
            alternating_even,
            alternating_odd,
            *(1 << index for index in range(width)),
        }
        for requested in sorted(requested_patterns):
            source = requested << start
            add_target = requested << start
            if site == "divide":
                original_target = add_target
                observed_add_target = original_target
            else:
                # The exact multiply cell shifts the original target left by
                # one before publishing the add carry.  Our top bit is zero,
                # so this is the exact source transformation without wrap.
                original_target = add_target >> 1
                observed_add_target = (original_target << 1) & full_mask

            canonical_mismatches += int(
                not (
                    0 <= source < modulus
                    and 0 <= original_target < modulus
                )
            )
            observed = _carry_sequence(source, observed_add_target, 256)
            observed_chunk = (observed >> start) & carry_mask
            exact_recurrence_mismatches += int(
                observed_chunk != requested
                or observed & ((1 << start) - 1) != 0
            )

        exact_transfer[site] = {
            "maximum_final_chunk_width": width,
            "quotient_rank": width,
            "source_valid_patterns": len(requested_patterns),
        }

    return {
        "schema": "final-carry-checkpoint-quotient-rank-v2",
        "reduced_widths": widths,
        "basis_cases_by_width": basis_cases,
        "reduced_raw_carry_quotient_rank": raw_ranks,
        "reduced_transformed_carry_quotient_rank": transformed_ranks,
        "rank_mismatches": mismatches,
        "exact_axis_source_valid_patterns": len(axis_inputs),
        "exact_canonical_mismatches": canonical_mismatches,
        "exact_recurrence_mismatches": exact_recurrence_mismatches,
        "exact_transfer": exact_transfer,
        "scope": (
            "Boolean-function rank modulo source plus finished-sum wires; "
            "this is an information/lifetime rank, not a nonlinear gate "
            "lower bound"
        ),
    }


def _anf_coefficients(truth_table: int, variables: int) -> int:
    coefficients = [
        (truth_table >> row) & 1 for row in range(1 << variables)
    ]
    for variable in range(variables):
        for monomial in range(1 << variables):
            if (monomial >> variable) & 1:
                coefficients[monomial] ^= coefficients[
                    monomial ^ (1 << variable)
                ]
    return sum(
        coefficient << monomial
        for monomial, coefficient in enumerate(coefficients)
    )


def _strip_affine_anf(coefficients: int, variables: int) -> int:
    nonlinear = coefficients & ~1
    for variable in range(variables):
        nonlinear &= ~(1 << (1 << variable))
    return nonlinear


def fold_nonlinear_rank_report(reduced_widths: range) -> dict[str, Any]:
    """Measure the nonlinear output rank of the +f fold restriction.

    Fixing the selector to ``+f`` leaves an ordinary in-place constant add.
    Its first two output bits are affine.  Output bit i>=2 contains the unique
    leading carry monomial ``a_0 ... a_(i-1)``.  Consequently the nonlinear
    output quotient has rank ``width-2``.  An XOR/AND circuit needs at least
    that many product values because every nonlinear output is an affine
    combination of the product-gate results.  The source fold emits exactly
    ``width-3`` stored-carry CCX plus one terminal CCX.
    """

    widths = list(reduced_widths)
    reduced_rank: dict[str, int] = {}
    reduced_source: dict[str, int] = {}
    rank_mismatches = 0
    for width in widths:
        mask = (1 << width) - 1
        constant = SECP256K1_F & mask
        nonlinear_outputs: list[int] = []
        for output_bit in range(width):
            truth_table = 0
            for accumulator in range(1 << width):
                output = (accumulator + constant) & mask
                truth_table |= ((output >> output_bit) & 1) << accumulator
            anf = _anf_coefficients(truth_table, width)
            nonlinear_outputs.append(_strip_affine_anf(anf, width))
        observed_rank = _gf2_rank(nonlinear_outputs)
        source_ccx = width - 2
        reduced_rank[str(width)] = observed_rank
        reduced_source[str(width)] = source_ccx
        rank_mismatches += int(observed_rank != source_ccx)

    exact = {
        "divide": {"width": 54, "nonlinear_rank": 52, "source_ccx": 52},
        "multiply": {"width": 53, "nonlinear_rank": 51, "source_ccx": 51},
    }
    return {
        "schema": "final-carry-fold-nonlinear-rank-v1",
        "reduced_widths": widths,
        "reduced_nonlinear_rank": reduced_rank,
        "reduced_source_ccx": reduced_source,
        "rank_mismatches": rank_mismatches,
        "exact": exact,
        "exact_transfer": (
            "for +f, f_0=1 gives c_1=a_0; induction through each fixed "
            "constant bit leaves leading monomial a_0...a_i in c_(i+1)"
        ),
        "scope": "XOR/AND value circuits; phase-only gates do not create outputs",
    }


def separable_handoff_cost_report(
    records: list[dict[str, Any]],
    *,
    peak_limit: int,
) -> dict[str, Any]:
    """Combine the checked separable dirty-host dichotomy with exact pricing.

    This closes source-shaped and affine-conjugated handoffs, but intentionally
    stops short of calling a whole-family theorem: a globally mixed nonlinear
    encoding spanning several fold stages still needs an independent direct-
    sum proof or exhaustive synthesis certificate.
    """

    phase_host = optimistic_phase_host_report(
        records,
        saved_ccx_per_cell=3,
        phase_terminal_discount=25,
        free_selector_wires=1,
        peak_limit=peak_limit,
    )
    affine_swap = exhaust_affine_dirty_host_conjugation()
    cells = len(records)
    affected = phase_host["cells_still_requiring_host_reuse"]
    if affine_swap["one_gate_span_swap_solutions"] != 0:
        raise AssertionError("one-gate dirty-host span swap unexpectedly exists")
    minimum_added = affected * 0.5
    gross = phase_host["gross_average_t"]
    allowed_added = gross - 1_500.0
    return {
        "schema": "final-carry-separable-handoff-cost-v1",
        "cells": cells,
        "cells_requiring_release_or_reuse": affected,
        "optimistic_reused_hosts": {
            "minimum": phase_host["minimum_reused_hosts"],
            "maximum": phase_host["maximum_reused_hosts"],
        },
        "unitary_dirty_swap_extra_gates_per_affected_cell": 1,
        "measured_checkpoint_extra_phase_gates_per_affected_cell": 1,
        "extra_gate_condition_depth_lower_bound": 1,
        "minimum_added_average_t": minimum_added,
        "allowed_added_average_t": allowed_added,
        "gross_average_t": gross,
        "net_average_t_upper_bound": gross - minimum_added,
        "target_net_average_t": 1_500.0,
        "economics_can_reach_target": gross - minimum_added >= 1_500.0,
        "is_terminal_whole_family_proof": False,
        "covered": [
            "direct dirty-target substitution",
            "arbitrary Clifford pre/post conjugation of an independent host",
            "HMR release followed by source-shaped checkpoint reconstruction",
        ],
        "remaining_gap": (
            "exclude a globally mixed nonlinear encoding that amortizes its "
            "cross-term cancellation over multiple fold stages"
        ),
    }


def _canonical_function_basis(functions: list[int]) -> tuple[int, ...]:
    basis: list[int] = []
    for function in functions:
        reduced = function
        for pivot in basis:
            reduced = min(reduced, reduced ^ pivot)
        if reduced:
            basis.append(reduced)
            basis.sort(reverse=True)
    return tuple(basis)


def _reduce_function(function: int, basis: tuple[int, ...]) -> int:
    reduced = function
    for pivot in basis:
        reduced = min(reduced, reduced ^ pivot)
    return reduced


def _affine_span_forms(basis: list[int]) -> list[int]:
    forms: list[int] = []
    for mask in range(1 << len(basis)):
        function = 0
        for index, item in enumerate(basis):
            if (mask >> index) & 1:
                function ^= item
        forms.append(function)
    return forms


def _one_gate_subspaces_within_envelope(
    start: list[int],
    envelope: tuple[int, ...],
) -> tuple[set[tuple[int, ...]], int]:
    """Enumerate optimistic affine-conjugated one-Toffoli successor spaces."""

    start_canonical = _canonical_function_basis(start)
    forms = _affine_span_forms(start)
    products: set[int] = set()
    for left_index, left in enumerate(forms):
        for right in forms[left_index:]:
            product = left & right
            if (
                _reduce_function(product, envelope) == 0
                and _reduce_function(product, start_canonical) != 0
            ):
                products.add(product)

    # start[0] is the constant, followed by ten independent physical-wire
    # functions.  A free affine conjugation may choose any hyperplane of that
    # ten-dimensional wire quotient as the unaffected target complement.
    wire_count = len(start) - 1
    subspaces: set[tuple[int, ...]] = set()
    for product in products:
        for functional in range(1, 1 << wire_count):
            pivot = (functional & -functional).bit_length() - 1
            pivot_function = start[1 + pivot]
            generators = [start[0]]
            for index in range(wire_count):
                if index == pivot:
                    continue
                generator = start[1 + index]
                if (functional >> index) & 1:
                    generator ^= pivot_function
                generators.append(generator)
            generators.append(pivot_function ^ product)
            subspaces.add(_canonical_function_basis(generators))
    return subspaces, len(products)


def exhaust_two_bank_affine_conjugation() -> dict[str, Any]:
    """Meet in the middle on two dirty products and two fold products.

    This search permits arbitrary affine X/CX conjugation, identical controls,
    and every target hyperplane, so it is a relaxation of physical Toffoli
    synthesis.  A two-gate solution would appear as a subspace reachable in
    one gate from both the dirty start and the clean goal because Toffoli is
    self-inverse.  The envelope restriction is necessary, not heuristic: with
    only two gates, the two new quotient dimensions must be exactly the two
    desired fold products; a mixed or higher-degree third dimension cannot be
    removed.
    """

    variables_count = 8
    rows = 1 << variables_count
    one = (1 << rows) - 1
    variables = [
        sum(((row >> variable) & 1) << row for row in range(rows))
        for variable in range(variables_count)
    ]
    dirty = [variables[0] & variables[1], variables[2] & variables[3]]
    fold = [variables[4] & variables[5], variables[6] & variables[7]]
    start = [one, *variables, *dirty]
    goal = [one, *variables, *fold]
    envelope = _canonical_function_basis([*start, *fold])

    start_reachable, start_products = _one_gate_subspaces_within_envelope(
        start, envelope
    )
    goal_reachable, goal_products = _one_gate_subspaces_within_envelope(
        goal, envelope
    )
    clean_intersections = len(start_reachable & goal_reachable)

    # Mutation: accepting d_i XOR f_i instead of clean f_i makes the obvious
    # two toggles admissible.  The meet-in-the-middle intersection must then be
    # nonempty, demonstrating that the search distinguishes dirty offsets.
    dirty_goal = [
        one,
        *variables,
        dirty[0] ^ fold[0],
        dirty[1] ^ fold[1],
    ]
    dirty_goal_reachable, _ = _one_gate_subspaces_within_envelope(
        dirty_goal, envelope
    )
    dirty_intersections = len(start_reachable & dirty_goal_reachable)

    return {
        "schema": "final-carry-two-bank-affine-conjugation-v1",
        "logical_variables": variables_count,
        "physical_affine_forms_per_side": 1 << len(start),
        "admissible_first_products_start": start_products,
        "admissible_first_products_goal": goal_products,
        "one_gate_subspaces_start": len(start_reachable),
        "one_gate_subspaces_goal": len(goal_reachable),
        "two_gate_clean_intersections": clean_intersections,
        "clean_fold_product_gates": 2,
        "dirty_swap_gate_lower_bound": 3 if clean_intersections == 0 else 2,
        "mutation_keep_dirty_offsets_intersections": dirty_intersections,
        "relaxations": [
            "identical control functions allowed",
            "all affine target hyperplanes allowed",
            "gate legality ignored when doing so enlarges the search",
        ],
        "scope": (
            "two independent banks; larger-bank transfer uses the nonlinear "
            "rank/direct-sum argument and is not established by enumeration alone"
        ),
    }


def _quadratic_product(left: int, right: int, variables: int) -> int:
    """Polar/off-diagonal quadratic part of two linear forms."""

    pair_index = 0
    product = 0
    for first in range(variables):
        for second in range(first + 1, variables):
            coefficient = (
                (((left >> first) & 1) & ((right >> second) & 1))
                ^ (((left >> second) & 1) & ((right >> first) & 1))
            )
            product |= coefficient << pair_index
            pair_index += 1
    return product


def exhaust_two_bank_quadratic_catalysts() -> dict[str, Any]:
    """Exclude every three-generator mixed catalyst for two dirty hosts.

    Unlike :func:`exhaust_two_bank_affine_conjugation`, this test does not
    require intermediate functions to stay inside the dirty-plus-fold
    envelope.  It enumerates every decomposable quadratic form on all eight
    high/low variables, so arbitrary mixed cross terms are admitted.

    For each of the six isomorphisms between the two-dimensional dirty and
    fold spaces, its graph G has no nonzero decomposable member.  If three
    decomposable generators spanned G, their three-dimensional span would be
    G plus one coset; all three generators would lie in that coset.  Choosing
    the first generator p therefore reduces the complete search to checking
    p, p+g1, and p+g2 for every p and graph basis g1,g2.  None exists.  Four
    pure clear/create generators are an explicit witness.

    This closes the earlier envelope caveat for exactly two quadratic banks.
    It intentionally does not assert a larger-bank direct-sum theorem or an
    HMR-assisted whole-circuit lower bound.
    """

    variables = 8
    decomposable = {
        _quadratic_product(left, right, variables)
        for left in range(1, 1 << variables)
        for right in range(left + 1, 1 << variables)
    }
    decomposable.discard(0)

    def pair(first: int, second: int) -> int:
        index = 0
        for left in range(variables):
            for right in range(left + 1, variables):
                if (left, right) == (first, second):
                    return 1 << index
                index += 1
        raise AssertionError("quadratic pair index was not found")

    dirty = [pair(0, 1), pair(2, 3)]
    fold = [pair(4, 5), pair(6, 7)]
    graph_maps = [
        (first, second)
        for first in (1, 2, 3)
        for second in (1, 2, 3)
        if first != second
    ]
    solutions: list[dict[str, int]] = []
    for first_image, second_image in graph_maps:
        graph_first = dirty[0]
        graph_second = dirty[1]
        if first_image & 1:
            graph_first ^= fold[0]
        if first_image & 2:
            graph_first ^= fold[1]
        if second_image & 1:
            graph_second ^= fold[0]
        if second_image & 2:
            graph_second ^= fold[1]
        for catalyst in decomposable:
            if (
                (catalyst ^ graph_first) in decomposable
                and (catalyst ^ graph_second) in decomposable
            ):
                solutions.append(
                    {
                        "first_image": first_image,
                        "second_image": second_image,
                        "catalyst": catalyst,
                    }
                )
                break

    return {
        "schema": "final-carry-two-bank-quadratic-catalyst-v1",
        "logical_variables": variables,
        "decomposable_quadratic_forms": len(decomposable),
        "dirty_to_fold_graph_isomorphisms": len(graph_maps),
        "three_generator_coset_candidates": (
            len(decomposable) * len(graph_maps)
        ),
        "three_decomposable_generator_solutions": len(solutions),
        "first_solution": solutions[0] if solutions else None,
        "decomposable_generator_lower_bound": 4 if not solutions else 3,
        "four_generator_clear_create_witness": all(
            function in decomposable for function in [*dirty, *fold]
        ),
        "mutation_allow_rank_four_direct_solutions": len(graph_maps),
        "is_larger_bank_direct_sum_proof": False,
        "scope": (
            "two dirty quadratic products versus two fold quadratic products; "
            "arbitrary mixed quadratic catalysts allowed, higher-degree and "
            "larger-bank/HMR amortization not closed"
        ),
    }
