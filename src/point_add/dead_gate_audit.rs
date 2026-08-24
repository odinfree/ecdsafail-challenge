use std::collections::BTreeSet;

use crate::circuit::{BitId, Op, OperationType, QubitId, NO_BIT, NO_QUBIT, NO_REG};

use super::{OriginRef, TracedOps};

#[derive(Clone, Copy, Debug, Eq, PartialEq, Ord, PartialOrd)]
pub(crate) enum AbstractValue {
    Known0,
    Known1,
    Unknown,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Ord, PartialOrd)]
pub(crate) enum AuditAction {
    Keep,
    NoCostIdentity,
    Drop,
    LowerToX,
    LowerToCX,
    LowerToNeg,
    LowerToZ,
    LowerToCZ,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Ord, PartialOrd)]
pub(crate) enum ProofRule {
    None,
    EffectiveConditionKnown0,
    CcxControlKnown0,
    CcxBothControlsKnown1,
    CcxOneControlKnown1,
    CczOperandKnown0,
    CczThreeOperandsKnown1,
    CczTwoOperandsKnown1,
    CczOneOperandKnown1,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub(crate) struct GateDecision {
    pub(crate) op_index: u64,
    pub(crate) kind: OperationType,
    pub(crate) facts: [AbstractValue; 3],
    pub(crate) effective_condition: AbstractValue,
    pub(crate) action: AuditAction,
    pub(crate) rule: ProofRule,
    pub(crate) origin: OriginRef,
    pub(crate) score_eligible: bool,
}

fn abstract_and(a: AbstractValue, b: AbstractValue) -> AbstractValue {
    match (a, b) {
        (AbstractValue::Known0, _) | (_, AbstractValue::Known0) => AbstractValue::Known0,
        (AbstractValue::Known1, AbstractValue::Known1) => AbstractValue::Known1,
        _ => AbstractValue::Unknown,
    }
}

fn abstract_not(value: AbstractValue) -> AbstractValue {
    match value {
        AbstractValue::Known0 => AbstractValue::Known1,
        AbstractValue::Known1 => AbstractValue::Known0,
        AbstractValue::Unknown => AbstractValue::Unknown,
    }
}

fn abstract_xor(a: AbstractValue, b: AbstractValue) -> AbstractValue {
    match (a, b) {
        (AbstractValue::Known0, value) | (value, AbstractValue::Known0) => value,
        (AbstractValue::Known1, value) | (value, AbstractValue::Known1) => abstract_not(value),
        (AbstractValue::Unknown, AbstractValue::Unknown) => AbstractValue::Unknown,
    }
}

fn join(a: AbstractValue, b: AbstractValue) -> AbstractValue {
    if a == b {
        a
    } else {
        AbstractValue::Unknown
    }
}

fn conditional_write(
    condition: AbstractValue,
    old: AbstractValue,
    executed: AbstractValue,
) -> AbstractValue {
    match condition {
        AbstractValue::Known0 => old,
        AbstractValue::Known1 => executed,
        AbstractValue::Unknown => join(old, executed),
    }
}

#[derive(Debug)]
struct AbstractMachine {
    qubits: Vec<AbstractValue>,
    bits: Vec<AbstractValue>,
    base_condition: AbstractValue,
    condition_stack: Vec<AbstractValue>,
    xof_words_consumed: u64,
}

impl AbstractMachine {
    fn new(qubits: Vec<AbstractValue>, bits: Vec<AbstractValue>) -> Self {
        Self {
            qubits,
            bits,
            base_condition: AbstractValue::Known1,
            condition_stack: Vec::new(),
            xof_words_consumed: 0,
        }
    }

    #[cfg(test)]
    fn for_test(qubits: Vec<AbstractValue>, bits: Vec<AbstractValue>) -> Self {
        Self::new(qubits, bits)
    }

    fn qubit(&self, id: QubitId) -> AbstractValue {
        self.qubits[id.0 as usize]
    }

    fn bit(&self, id: BitId) -> AbstractValue {
        self.bits[id.0 as usize]
    }

    fn effective_condition(&self, op: &Op) -> AbstractValue {
        if op.c_condition == NO_BIT {
            self.base_condition
        } else {
            abstract_and(self.base_condition, self.bit(op.c_condition))
        }
    }

    fn finish(&self) -> Result<(), String> {
        if self.condition_stack.is_empty() {
            Ok(())
        } else {
            Err(format!(
                "condition stack is nonempty at end of stream (depth {})",
                self.condition_stack.len()
            ))
        }
    }

    fn apply(
        &mut self,
        op_index: u64,
        op: &Op,
        origin: OriginRef,
    ) -> Result<Option<GateDecision>, String> {
        let effective_condition = self.effective_condition(op);
        match op.kind {
            OperationType::Neg
            | OperationType::Register
            | OperationType::AppendToRegister
            | OperationType::Z
            | OperationType::CZ
            | OperationType::DebugPrint => Ok(None),
            OperationType::BitInvert => {
                let old = self.bit(op.c_target);
                self.bits[op.c_target.0 as usize] =
                    conditional_write(effective_condition, old, abstract_not(old));
                Ok(None)
            }
            OperationType::BitStore0 => {
                let old = self.bit(op.c_target);
                self.bits[op.c_target.0 as usize] =
                    conditional_write(effective_condition, old, AbstractValue::Known0);
                Ok(None)
            }
            OperationType::BitStore1 => {
                let old = self.bit(op.c_target);
                self.bits[op.c_target.0 as usize] =
                    conditional_write(effective_condition, old, AbstractValue::Known1);
                Ok(None)
            }
            OperationType::X => {
                let old = self.qubit(op.q_target);
                self.qubits[op.q_target.0 as usize] =
                    conditional_write(effective_condition, old, abstract_not(old));
                Ok(None)
            }
            OperationType::CX => {
                let control = self.qubit(op.q_control1);
                let old_target = self.qubit(op.q_target);
                let executed_target = abstract_xor(old_target, control);
                self.qubits[op.q_target.0 as usize] =
                    conditional_write(effective_condition, old_target, executed_target);
                Ok(None)
            }
            OperationType::Swap => {
                let old_control = self.qubit(op.q_control1);
                let old_target = self.qubit(op.q_target);
                self.qubits[op.q_control1.0 as usize] =
                    conditional_write(effective_condition, old_control, old_target);
                self.qubits[op.q_target.0 as usize] =
                    conditional_write(effective_condition, old_target, old_control);
                Ok(None)
            }
            OperationType::R => {
                self.xof_words_consumed = self
                    .xof_words_consumed
                    .checked_add(1)
                    .ok_or_else(|| "XOF word count overflow".to_owned())?;
                let old_target = self.qubit(op.q_target);
                self.qubits[op.q_target.0 as usize] =
                    conditional_write(effective_condition, old_target, AbstractValue::Known0);
                Ok(None)
            }
            OperationType::Hmr => {
                self.xof_words_consumed = self
                    .xof_words_consumed
                    .checked_add(1)
                    .ok_or_else(|| "XOF word count overflow".to_owned())?;
                let old_target = self.qubit(op.q_target);
                let old_result = self.bit(op.c_target);
                self.qubits[op.q_target.0 as usize] =
                    conditional_write(effective_condition, old_target, AbstractValue::Known0);
                self.bits[op.c_target.0 as usize] =
                    conditional_write(effective_condition, old_result, AbstractValue::Unknown);
                Ok(None)
            }
            OperationType::CCX => {
                let facts = [
                    self.qubit(op.q_control2),
                    self.qubit(op.q_control1),
                    self.qubit(op.q_target),
                ];
                let (action, rule) = if effective_condition == AbstractValue::Known0 {
                    (
                        AuditAction::NoCostIdentity,
                        ProofRule::EffectiveConditionKnown0,
                    )
                } else if facts[0] == AbstractValue::Known0 || facts[1] == AbstractValue::Known0 {
                    (AuditAction::Drop, ProofRule::CcxControlKnown0)
                } else if facts[0] == AbstractValue::Known1 && facts[1] == AbstractValue::Known1 {
                    (AuditAction::LowerToX, ProofRule::CcxBothControlsKnown1)
                } else if facts[0] == AbstractValue::Known1 || facts[1] == AbstractValue::Known1 {
                    (AuditAction::LowerToCX, ProofRule::CcxOneControlKnown1)
                } else {
                    (AuditAction::Keep, ProofRule::None)
                };
                let controls = abstract_and(facts[0], facts[1]);
                let executed = abstract_xor(facts[2], controls);
                self.qubits[op.q_target.0 as usize] =
                    conditional_write(effective_condition, facts[2], executed);
                Ok(Some(GateDecision {
                    op_index,
                    kind: op.kind,
                    facts,
                    effective_condition,
                    action,
                    rule,
                    origin,
                    score_eligible: action != AuditAction::Keep
                        && action != AuditAction::NoCostIdentity,
                }))
            }
            OperationType::CCZ => {
                let facts = [
                    self.qubit(op.q_control2),
                    self.qubit(op.q_control1),
                    self.qubit(op.q_target),
                ];
                let known_ones = facts
                    .iter()
                    .filter(|&&fact| fact == AbstractValue::Known1)
                    .count();
                let (action, rule) = if effective_condition == AbstractValue::Known0 {
                    (
                        AuditAction::NoCostIdentity,
                        ProofRule::EffectiveConditionKnown0,
                    )
                } else if facts.contains(&AbstractValue::Known0) {
                    (AuditAction::Drop, ProofRule::CczOperandKnown0)
                } else {
                    match known_ones {
                        3 => (AuditAction::LowerToNeg, ProofRule::CczThreeOperandsKnown1),
                        2 => (AuditAction::LowerToZ, ProofRule::CczTwoOperandsKnown1),
                        1 => (AuditAction::LowerToCZ, ProofRule::CczOneOperandKnown1),
                        _ => (AuditAction::Keep, ProofRule::None),
                    }
                };
                Ok(Some(GateDecision {
                    op_index,
                    kind: op.kind,
                    facts,
                    effective_condition,
                    action,
                    rule,
                    origin,
                    score_eligible: action != AuditAction::Keep
                        && action != AuditAction::NoCostIdentity,
                }))
            }
            OperationType::PushCondition => {
                let old_base = self.base_condition;
                let pushed_bit = self.bit(op.c_condition);
                self.condition_stack.push(old_base);
                self.base_condition = abstract_and(old_base, pushed_bit);
                Ok(None)
            }
            OperationType::PopCondition => {
                self.base_condition = self
                    .condition_stack
                    .pop()
                    .ok_or_else(|| format!("condition stack underflow at operation {op_index}"))?;
                Ok(None)
            }
        }
    }
}

#[derive(Clone, Copy)]
enum OperandRequirement {
    Banned,
    Allowed,
    Required,
}

fn validate_operand(
    op_index: u64,
    kind: OperationType,
    field: &'static str,
    present: bool,
    requirement: OperandRequirement,
) -> Result<(), String> {
    match (requirement, present) {
        (OperandRequirement::Required, false) => Err(format!(
            "operation {op_index} kind {kind:?} requires {field}"
        )),
        (OperandRequirement::Banned, true) => Err(format!(
            "operation {op_index} kind {kind:?} forbids {field}"
        )),
        _ => Ok(()),
    }
}

fn validate_op_schema(op_index: u64, op: &Op) -> Result<(), String> {
    let qubit_operands = [
        ("q_target", op.q_target),
        ("q_control1", op.q_control1),
        ("q_control2", op.q_control2),
    ];
    for first in 0..qubit_operands.len() {
        for second in first + 1..qubit_operands.len() {
            if qubit_operands[first].1 != NO_QUBIT
                && qubit_operands[first].1 == qubit_operands[second].1
            {
                let aliased_qubit = qubit_operands[first].1;
                return Err(format!(
                    "operation {op_index} kind {:?} has illegal qubit alias {}=={}==q{}",
                    op.kind, qubit_operands[first].0, qubit_operands[second].0, aliased_qubit.0
                ));
            }
        }
    }

    if op.kind == OperationType::DebugPrint {
        return Ok(());
    }

    use OperandRequirement::{Allowed, Banned, Required};
    let mut q_target = Banned;
    let mut q_control1 = Banned;
    let mut q_control2 = Banned;
    let mut c_target = Banned;
    let mut c_condition = Banned;
    let mut r_target = Banned;

    match op.kind {
        OperationType::DebugPrint => unreachable!(),
        OperationType::Register => r_target = Required,
        OperationType::AppendToRegister => {
            if (op.q_target == NO_QUBIT) == (op.c_target == NO_BIT) {
                return Err(format!(
                    "operation {op_index} kind {:?} needs exactly one qubit target or bit target",
                    op.kind
                ));
            }
            q_target = Allowed;
            c_target = Allowed;
            r_target = Required;
        }
        OperationType::CCX | OperationType::CCZ => {
            q_target = Required;
            q_control1 = Required;
            q_control2 = Required;
            c_condition = Allowed;
        }
        OperationType::CX | OperationType::CZ | OperationType::Swap => {
            q_target = Required;
            q_control1 = Required;
            c_condition = Allowed;
        }
        OperationType::X | OperationType::Z | OperationType::R => {
            q_target = Required;
            c_condition = Allowed;
        }
        OperationType::Neg => c_condition = Allowed,
        OperationType::Hmr => {
            q_target = Required;
            c_target = Required;
            c_condition = Allowed;
        }
        OperationType::BitInvert | OperationType::BitStore0 | OperationType::BitStore1 => {
            c_target = Required;
            c_condition = Allowed;
        }
        OperationType::PushCondition => c_condition = Required,
        OperationType::PopCondition => {}
    }

    validate_operand(
        op_index,
        op.kind,
        "q_target",
        op.q_target != NO_QUBIT,
        q_target,
    )?;
    validate_operand(
        op_index,
        op.kind,
        "q_control1",
        op.q_control1 != NO_QUBIT,
        q_control1,
    )?;
    validate_operand(
        op_index,
        op.kind,
        "q_control2",
        op.q_control2 != NO_QUBIT,
        q_control2,
    )?;
    validate_operand(
        op_index,
        op.kind,
        "c_target",
        op.c_target != NO_BIT,
        c_target,
    )?;
    validate_operand(
        op_index,
        op.kind,
        "c_condition",
        op.c_condition != NO_BIT,
        c_condition,
    )?;
    validate_operand(
        op_index,
        op.kind,
        "r_target",
        op.r_target != NO_REG,
        r_target,
    )
}

#[derive(Clone, Copy, Debug)]
enum RegisterMember {
    Qubit(QubitId),
    Bit(BitId),
}

fn checked_vector_len(maximum: Option<u64>, namespace: &'static str) -> Result<usize, String> {
    let Some(maximum) = maximum else {
        return Ok(0);
    };
    let maximum =
        usize::try_from(maximum).map_err(|_| format!("{namespace} physical ID is out of range"))?;
    maximum
        .checked_add(1)
        .ok_or_else(|| format!("{namespace} physical ID range overflow"))
}

fn known_zero_state(length: usize, namespace: &'static str) -> Result<Vec<AbstractValue>, String> {
    let mut state = Vec::new();
    state
        .try_reserve_exact(length)
        .map_err(|_| format!("cannot allocate {namespace} physical ID range of length {length}"))?;
    state.resize(length, AbstractValue::Known0);
    Ok(state)
}

fn parse_exact_675_machine(ops: &[Op]) -> Result<AbstractMachine, String> {
    let mut max_qubit = None;
    let mut max_bit = None;
    let mut registers: [Vec<RegisterMember>; 4] = std::array::from_fn(|_| Vec::new());
    let mut declarations = [false; 4];
    let mut next_declaration = 0usize;
    let mut seen_qubits = BTreeSet::new();
    let mut seen_bits = BTreeSet::new();

    for (index, op) in ops.iter().enumerate() {
        let op_index = u64::try_from(index)
            .map_err(|_| "operation index cannot be represented as u64".to_owned())?;
        validate_op_schema(op_index, op)?;

        for id in [op.q_control2, op.q_control1, op.q_target] {
            if id != NO_QUBIT {
                max_qubit = Some(max_qubit.map_or(id.0, |old: u64| old.max(id.0)));
            }
        }
        for id in [op.c_target, op.c_condition] {
            if id != NO_BIT {
                max_bit = Some(max_bit.map_or(id.0, |old: u64| old.max(id.0)));
            }
        }

        match op.kind {
            OperationType::Register => {
                let register = usize::try_from(op.r_target.0)
                    .map_err(|_| format!("operation {op_index} register ID is out of range"))?;
                if register >= registers.len() {
                    return Err(format!(
                        "operation {op_index} declares unexpected register r{}",
                        op.r_target.0
                    ));
                }
                if declarations[register] {
                    return Err(format!("duplicate declaration for register r{register}"));
                }
                if register != next_declaration {
                    return Err(format!(
                        "wrong register declaration order: expected r{next_declaration}, found r{register}"
                    ));
                }
                declarations[register] = true;
                next_declaration += 1;
            }
            OperationType::AppendToRegister => {
                let register = usize::try_from(op.r_target.0)
                    .map_err(|_| format!("operation {op_index} register ID is out of range"))?;
                if register >= registers.len() {
                    return Err(format!(
                        "operation {op_index} appends to unexpected register r{}",
                        op.r_target.0
                    ));
                }
                let member = if op.q_target != NO_QUBIT {
                    if !seen_qubits.insert(op.q_target.0) {
                        return Err(format!(
                            "duplicate qubit register member q{}",
                            op.q_target.0
                        ));
                    }
                    RegisterMember::Qubit(op.q_target)
                } else {
                    if !seen_bits.insert(op.c_target.0) {
                        return Err(format!("duplicate bit register member b{}", op.c_target.0));
                    }
                    RegisterMember::Bit(op.c_target)
                };
                registers[register].push(member);
            }
            _ => {}
        }
    }

    for register in 0..registers.len() {
        if !declarations[register] {
            return Err(format!("missing declaration for register r{register}"));
        }
        if registers[register].len() != 256 {
            return Err(format!(
                "register r{register} has width {}, expected 256",
                registers[register].len()
            ));
        }
        for member in &registers[register] {
            match (register < 2, member) {
                (true, RegisterMember::Qubit(_)) | (false, RegisterMember::Bit(_)) => {}
                (true, RegisterMember::Bit(_)) => {
                    return Err(format!(
                        "register r{register} must contain only qubit members"
                    ));
                }
                (false, RegisterMember::Qubit(_)) => {
                    return Err(format!(
                        "register r{register} must contain only bit members"
                    ));
                }
            }
        }
    }

    let qubit_len = checked_vector_len(max_qubit, "qubit")?;
    let bit_len = checked_vector_len(max_bit, "bit")?;
    let mut machine = AbstractMachine::new(
        known_zero_state(qubit_len, "qubit")?,
        known_zero_state(bit_len, "bit")?,
    );
    for register in registers {
        for member in register {
            match member {
                RegisterMember::Qubit(id) => {
                    let index = usize::try_from(id.0)
                        .map_err(|_| format!("qubit q{} is out of range", id.0))?;
                    machine.qubits[index] = AbstractValue::Unknown;
                }
                RegisterMember::Bit(id) => {
                    let index = usize::try_from(id.0)
                        .map_err(|_| format!("bit b{} is out of range", id.0))?;
                    machine.bits[index] = AbstractValue::Unknown;
                }
            }
        }
    }
    Ok(machine)
}

#[derive(Debug)]
pub(crate) struct AuditCoreResult {
    pub(crate) decisions: Vec<GateDecision>,
    pub(crate) final_qubits: Vec<AbstractValue>,
    pub(crate) final_bits: Vec<AbstractValue>,
    pub(crate) xof_words_consumed: u64,
}

fn audit_parts(ops: &[Op], origins: &[OriginRef]) -> Result<AuditCoreResult, String> {
    if !ops.is_empty() && origins.is_empty() {
        return Err(format!(
            "missing origin records for {} operations",
            ops.len()
        ));
    }
    if ops.len() != origins.len() {
        return Err(format!(
            "operation/origin length drift: {} operations, {} origins",
            ops.len(),
            origins.len()
        ));
    }

    let mut machine = parse_exact_675_machine(ops)?;
    let mut decisions = Vec::new();
    for (index, (op, origin)) in ops.iter().zip(origins.iter()).enumerate() {
        let op_index = u64::try_from(index)
            .map_err(|_| "operation index cannot be represented as u64".to_owned())?;
        if let Some(decision) = machine.apply(op_index, op, *origin)? {
            decisions.push(decision);
        }
    }
    machine.finish()?;
    Ok(AuditCoreResult {
        decisions,
        final_qubits: machine.qubits,
        final_bits: machine.bits,
        xof_words_consumed: machine.xof_words_consumed,
    })
}

pub(crate) fn audit_traced(stream: &TracedOps) -> Result<AuditCoreResult, String> {
    if !stream.enabled() {
        return Err("missing origin sidecar: traced audit stream is disabled".to_owned());
    }
    audit_parts(stream, stream.origins())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::circuit::{BitId, Op, OperationType, QubitId, RegisterId};

    fn origin(op_index: u32) -> OriginRef {
        OriginRef {
            site_id: 0,
            emission_ordinal: op_index,
            inverse_depth: 0,
            flags: 0,
        }
    }

    fn op3(kind: OperationType) -> Op {
        let mut op = Op::empty();
        op.kind = kind;
        op.q_control2 = QubitId(0);
        op.q_control1 = QubitId(1);
        op.q_target = QubitId(2);
        op
    }

    fn apply_gate(
        kind: OperationType,
        facts: [AbstractValue; 3],
    ) -> (AbstractMachine, GateDecision) {
        let mut machine = AbstractMachine::for_test(facts.to_vec(), Vec::new());
        let decision = machine
            .apply(0, &op3(kind), origin(0))
            .expect("valid gate")
            .expect("CCX/CCZ decision");
        (machine, decision)
    }

    #[test]
    fn zero_controlled_ccx_drops() {
        let (_, decision) = apply_gate(
            OperationType::CCX,
            [
                AbstractValue::Known0,
                AbstractValue::Unknown,
                AbstractValue::Known1,
            ],
        );
        assert_eq!(decision.action, AuditAction::Drop);
        assert_eq!(decision.rule, ProofRule::CcxControlKnown0);
        assert!(decision.score_eligible);
    }

    #[test]
    fn one_known_one_ccx_lowers_to_cx() {
        let (_, decision) = apply_gate(
            OperationType::CCX,
            [
                AbstractValue::Known1,
                AbstractValue::Unknown,
                AbstractValue::Known0,
            ],
        );
        assert_eq!(decision.action, AuditAction::LowerToCX);
        assert_eq!(decision.rule, ProofRule::CcxOneControlKnown1);
    }

    #[test]
    fn two_known_one_ccx_lowers_to_x() {
        let (machine, decision) = apply_gate(
            OperationType::CCX,
            [
                AbstractValue::Known1,
                AbstractValue::Known1,
                AbstractValue::Known0,
            ],
        );
        assert_eq!(decision.action, AuditAction::LowerToX);
        assert_eq!(decision.rule, ProofRule::CcxBothControlsKnown1);
        assert_eq!(machine.qubit(QubitId(2)), AbstractValue::Known1);
    }

    #[test]
    fn unknown_control_keeps_ccx() {
        let (_, decision) = apply_gate(
            OperationType::CCX,
            [
                AbstractValue::Unknown,
                AbstractValue::Unknown,
                AbstractValue::Known0,
            ],
        );
        assert_eq!(decision.action, AuditAction::Keep);
        assert_eq!(decision.rule, ProofRule::None);
        assert!(!decision.score_eligible);
    }

    #[test]
    fn ccz_known_zero_drops() {
        let (_, decision) = apply_gate(
            OperationType::CCZ,
            [
                AbstractValue::Unknown,
                AbstractValue::Known0,
                AbstractValue::Known1,
            ],
        );
        assert_eq!(decision.action, AuditAction::Drop);
        assert_eq!(decision.rule, ProofRule::CczOperandKnown0);
    }

    fn concrete_phase(kind: OperationType, values: [bool; 3]) -> bool {
        match kind {
            OperationType::CCZ => values.into_iter().all(|value| value),
            _ => unreachable!(),
        }
    }

    fn lowered_phase(action: AuditAction, facts: [AbstractValue; 3], values: [bool; 3]) -> bool {
        match action {
            AuditAction::Keep => values.into_iter().all(|value| value),
            AuditAction::NoCostIdentity | AuditAction::Drop => false,
            AuditAction::LowerToNeg => true,
            AuditAction::LowerToZ => {
                let mut surviving = facts
                    .iter()
                    .enumerate()
                    .filter_map(|(index, &fact)| (fact != AbstractValue::Known1).then_some(index));
                let wire = surviving.next().expect("one surviving Z wire");
                assert!(surviving.next().is_none(), "exactly one surviving Z wire");
                values[wire]
            }
            AuditAction::LowerToCZ => {
                let mut surviving = facts
                    .iter()
                    .enumerate()
                    .filter_map(|(index, &fact)| (fact != AbstractValue::Known1).then_some(index));
                let first = surviving.next().expect("first surviving CZ wire");
                let second = surviving.next().expect("second surviving CZ wire");
                assert!(surviving.next().is_none(), "exactly two surviving CZ wires");
                values[first] && values[second]
            }
            AuditAction::LowerToX | AuditAction::LowerToCX => {
                panic!("non-phase lowering in CCZ test")
            }
        }
    }

    #[test]
    fn ccz_one_two_three_known_ones_lower_exactly() {
        for known_one_mask in 1u8..8 {
            let known_ones = known_one_mask.count_ones();
            let facts = std::array::from_fn(|index| {
                if known_one_mask & (1 << index) == 0 {
                    AbstractValue::Unknown
                } else {
                    AbstractValue::Known1
                }
            });
            let expected_action = match known_ones {
                1 => AuditAction::LowerToCZ,
                2 => AuditAction::LowerToZ,
                3 => AuditAction::LowerToNeg,
                _ => unreachable!(),
            };
            let (_, decision) = apply_gate(OperationType::CCZ, facts);
            assert_eq!(decision.action, expected_action);
            for assignment in 0u8..8 {
                let values = [
                    assignment & 1 != 0,
                    assignment & 2 != 0,
                    assignment & 4 != 0,
                ];
                let consistent = facts
                    .into_iter()
                    .zip(values)
                    .all(|(fact, value)| match fact {
                        AbstractValue::Known0 => !value,
                        AbstractValue::Known1 => value,
                        AbstractValue::Unknown => true,
                    });
                if consistent {
                    assert_eq!(
                        concrete_phase(OperationType::CCZ, values),
                        lowered_phase(decision.action, facts, values),
                        "known_one_mask={known_one_mask:03b} facts={facts:?} assignment={assignment:03b}"
                    );
                }
            }
        }

        for assignment in 0u8..8 {
            let facts = [
                if assignment & 1 == 0 {
                    AbstractValue::Known0
                } else {
                    AbstractValue::Known1
                },
                if assignment & 2 == 0 {
                    AbstractValue::Known0
                } else {
                    AbstractValue::Known1
                },
                if assignment & 4 == 0 {
                    AbstractValue::Known0
                } else {
                    AbstractValue::Known1
                },
            ];
            let (_, decision) = apply_gate(OperationType::CCZ, facts);
            let values = [
                assignment & 1 != 0,
                assignment & 2 != 0,
                assignment & 4 != 0,
            ];
            assert_eq!(
                concrete_phase(OperationType::CCZ, values),
                lowered_phase(decision.action, facts, values),
                "concrete assignment={assignment:03b} action={:?}",
                decision.action
            );
        }
    }

    #[test]
    fn unknown_conditional_write_does_not_create_constant() {
        let mut machine = AbstractMachine::for_test(
            Vec::new(),
            vec![AbstractValue::Known0, AbstractValue::Unknown],
        );
        let mut op = Op::empty();
        op.kind = OperationType::BitStore1;
        op.c_target = BitId(0);
        op.c_condition = BitId(1);

        assert!(machine.apply(0, &op, origin(0)).unwrap().is_none());
        assert_eq!(machine.bit(BitId(0)), AbstractValue::Unknown);
    }

    fn apply_plain(machine: &mut AbstractMachine, op_index: u64, op: &Op) {
        machine
            .apply(op_index, op, origin(op_index as u32))
            .expect("valid operation");
    }

    fn push_condition(bit: u64) -> Op {
        let mut op = Op::empty();
        op.kind = OperationType::PushCondition;
        op.c_condition = BitId(bit);
        op
    }

    fn pop_condition() -> Op {
        let mut op = Op::empty();
        op.kind = OperationType::PopCondition;
        op
    }

    fn x(target: u64) -> Op {
        let mut op = Op::empty();
        op.kind = OperationType::X;
        op.q_target = QubitId(target);
        op
    }

    #[test]
    fn known_false_true_and_unknown_condition_stacks_are_exact() {
        for (condition, expected) in [
            (AbstractValue::Known0, AbstractValue::Known0),
            (AbstractValue::Known1, AbstractValue::Known1),
            (AbstractValue::Unknown, AbstractValue::Unknown),
        ] {
            let mut machine =
                AbstractMachine::for_test(vec![AbstractValue::Known0], vec![condition]);
            apply_plain(&mut machine, 0, &push_condition(0));
            apply_plain(&mut machine, 1, &x(0));
            apply_plain(&mut machine, 2, &pop_condition());
            machine.finish().expect("balanced stack");
            assert_eq!(machine.qubit(QubitId(0)), expected);
        }
    }

    #[test]
    fn nested_condition_stack_ands_values() {
        let mut machine = AbstractMachine::for_test(
            vec![AbstractValue::Known0],
            vec![AbstractValue::Known1, AbstractValue::Known0],
        );
        apply_plain(&mut machine, 0, &push_condition(0));
        apply_plain(&mut machine, 1, &push_condition(1));
        apply_plain(&mut machine, 2, &x(0));
        apply_plain(&mut machine, 3, &pop_condition());
        apply_plain(&mut machine, 4, &x(0));
        apply_plain(&mut machine, 5, &pop_condition());
        machine.finish().expect("balanced stack");
        assert_eq!(machine.qubit(QubitId(0)), AbstractValue::Known1);
    }

    #[test]
    fn pushed_condition_is_a_value_snapshot_when_its_bit_mutates() {
        let mut machine =
            AbstractMachine::for_test(vec![AbstractValue::Known0], vec![AbstractValue::Known1]);
        apply_plain(&mut machine, 0, &push_condition(0));
        let mut clear = Op::empty();
        clear.kind = OperationType::BitStore0;
        clear.c_target = BitId(0);
        apply_plain(&mut machine, 1, &clear);
        apply_plain(&mut machine, 2, &x(0));
        apply_plain(&mut machine, 3, &pop_condition());
        assert_eq!(machine.bit(BitId(0)), AbstractValue::Known0);
        assert_eq!(machine.qubit(QubitId(0)), AbstractValue::Known1);
    }

    #[test]
    fn condition_stack_underflow_and_nonempty_finish_fail() {
        let mut machine = AbstractMachine::for_test(Vec::new(), Vec::new());
        assert!(machine
            .apply(0, &pop_condition(), origin(0))
            .unwrap_err()
            .contains("underflow"));

        let mut machine = AbstractMachine::for_test(Vec::new(), vec![AbstractValue::Known1]);
        apply_plain(&mut machine, 0, &push_condition(0));
        assert!(machine.finish().unwrap_err().contains("nonempty"));
    }

    #[test]
    fn hmr_result_is_unknown_when_executed() {
        let mut machine =
            AbstractMachine::for_test(vec![AbstractValue::Known1], vec![AbstractValue::Known0]);
        let mut hmr = Op::empty();
        hmr.kind = OperationType::Hmr;
        hmr.q_target = QubitId(0);
        hmr.c_target = BitId(0);
        assert!(machine.apply(0, &hmr, origin(0)).unwrap().is_none());
        assert_eq!(machine.qubit(QubitId(0)), AbstractValue::Known0);
        assert_eq!(machine.bit(BitId(0)), AbstractValue::Unknown);
        assert_eq!(machine.xof_words_consumed, 1);
    }

    #[test]
    fn reset_and_hmr_consume_xof_words_under_known_false_condition() {
        let mut machine = AbstractMachine::for_test(
            vec![AbstractValue::Known1, AbstractValue::Known1],
            vec![AbstractValue::Known0, AbstractValue::Known1],
        );
        apply_plain(&mut machine, 0, &push_condition(0));

        let mut reset = Op::empty();
        reset.kind = OperationType::R;
        reset.q_target = QubitId(0);
        assert!(machine.apply(1, &reset, origin(1)).unwrap().is_none());

        let mut hmr = Op::empty();
        hmr.kind = OperationType::Hmr;
        hmr.q_target = QubitId(1);
        hmr.c_target = BitId(1);
        assert!(machine.apply(2, &hmr, origin(2)).unwrap().is_none());
        assert_eq!(machine.xof_words_consumed, 2);
        assert_eq!(machine.qubit(QubitId(0)), AbstractValue::Known1);
        assert_eq!(machine.qubit(QubitId(1)), AbstractValue::Known1);
        assert_eq!(machine.bit(BitId(1)), AbstractValue::Known1);
    }

    #[test]
    fn known_false_ccx_is_no_cost_and_not_score_eligible() {
        let mut machine = AbstractMachine::for_test(
            vec![
                AbstractValue::Known1,
                AbstractValue::Known1,
                AbstractValue::Known0,
            ],
            vec![AbstractValue::Known0],
        );
        let mut ccx = op3(OperationType::CCX);
        ccx.c_condition = BitId(0);
        let decision = machine.apply(0, &ccx, origin(0)).unwrap().unwrap();
        assert_eq!(decision.action, AuditAction::NoCostIdentity);
        assert_eq!(decision.rule, ProofRule::EffectiveConditionKnown0);
        assert!(!decision.score_eligible);
        assert_eq!(machine.qubit(QubitId(2)), AbstractValue::Known0);
    }

    #[test]
    fn all_eighteen_operation_kinds_have_total_transfers() {
        let mut machine = AbstractMachine::for_test(
            vec![
                AbstractValue::Known0,
                AbstractValue::Known1,
                AbstractValue::Unknown,
            ],
            vec![
                AbstractValue::Known0,
                AbstractValue::Known1,
                AbstractValue::Unknown,
            ],
        );
        let mut ops = Vec::new();

        ops.push(Op::empty());
        let mut register = Op::empty();
        register.kind = OperationType::Register;
        register.r_target = RegisterId(0);
        ops.push(register);
        let mut append = Op::empty();
        append.kind = OperationType::AppendToRegister;
        append.q_target = QubitId(0);
        append.r_target = RegisterId(0);
        ops.push(append);
        for kind in [
            OperationType::BitInvert,
            OperationType::BitStore0,
            OperationType::BitStore1,
        ] {
            let mut op = Op::empty();
            op.kind = kind;
            op.c_target = BitId(0);
            ops.push(op);
        }
        ops.push(x(0));
        let mut z = x(0);
        z.kind = OperationType::Z;
        ops.push(z);
        for kind in [OperationType::CX, OperationType::CZ, OperationType::Swap] {
            let mut op = Op::empty();
            op.kind = kind;
            op.q_control1 = QubitId(0);
            op.q_target = QubitId(1);
            ops.push(op);
        }
        let mut reset = Op::empty();
        reset.kind = OperationType::R;
        reset.q_target = QubitId(0);
        ops.push(reset);
        let mut hmr = Op::empty();
        hmr.kind = OperationType::Hmr;
        hmr.q_target = QubitId(1);
        hmr.c_target = BitId(1);
        ops.push(hmr);
        ops.push(op3(OperationType::CCX));
        ops.push(op3(OperationType::CCZ));
        ops.push(push_condition(1));
        ops.push(pop_condition());
        let mut debug = Op::empty();
        debug.kind = OperationType::DebugPrint;
        ops.push(debug);

        let mut decisions = 0;
        for (index, op) in ops.iter().enumerate() {
            validate_op_schema(index as u64, op).expect("valid operation schema");
            decisions += usize::from(
                machine
                    .apply(index as u64, op, origin(index as u32))
                    .unwrap()
                    .is_some(),
            );
        }
        machine.finish().expect("balanced stack");
        assert_eq!(ops.len(), 18);
        assert_eq!(decisions, 2);
        assert_eq!(machine.xof_words_consumed, 2);
    }

    fn exact_abi_ops() -> Vec<Op> {
        let mut ops = Vec::new();
        for register in 0u64..4 {
            for offset in 0u64..256 {
                let mut append = Op::empty();
                append.kind = OperationType::AppendToRegister;
                append.r_target = RegisterId(register);
                if register < 2 {
                    append.q_target = QubitId(register * 256 + offset);
                } else {
                    append.c_target = BitId((register - 2) * 256 + offset);
                }
                ops.push(append);
            }
            let mut declaration = Op::empty();
            declaration.kind = OperationType::Register;
            declaration.r_target = RegisterId(register);
            ops.push(declaration);
        }
        ops
    }

    fn origins(count: usize) -> Vec<OriginRef> {
        (0..count)
            .map(|index| origin(u32::try_from(index).unwrap()))
            .collect()
    }

    #[test]
    fn four_256_entry_registers_seed_unknown_at_operation_zero() {
        let mut ops = exact_abi_ops();
        let mut debug = Op::empty();
        debug.kind = OperationType::DebugPrint;
        debug.q_target = QubitId(700);
        debug.c_target = BitId(700);
        ops.push(debug);

        let machine = parse_exact_675_machine(&ops).expect("exact ABI");
        for id in 0..512 {
            assert_eq!(machine.qubit(QubitId(id)), AbstractValue::Unknown);
            assert_eq!(machine.bit(BitId(id)), AbstractValue::Unknown);
        }
        assert_eq!(machine.qubit(QubitId(700)), AbstractValue::Known0);
        assert_eq!(machine.bit(BitId(700)), AbstractValue::Known0);

        let audited = audit_parts(&ops, &origins(ops.len())).expect("complete strict audit");
        assert!(audited.decisions.is_empty());
        assert_eq!(audited.xof_words_consumed, 0);
        assert_eq!(audited.final_qubits[0], AbstractValue::Unknown);
        assert_eq!(audited.final_bits[0], AbstractValue::Unknown);
        assert_eq!(audited.final_qubits[700], AbstractValue::Known0);
        assert_eq!(audited.final_bits[700], AbstractValue::Known0);
    }

    #[test]
    fn duplicate_register_member_fails() {
        let mut ops = exact_abi_ops();
        ops[1].q_target = QubitId(0);
        let error = parse_exact_675_machine(&ops).unwrap_err();
        assert!(error.contains("duplicate"), "{error}");
    }

    #[test]
    fn wrong_register_order_or_width_fails() {
        let mut wrong_order = exact_abi_ops();
        wrong_order[256].r_target = RegisterId(1);
        wrong_order[513].r_target = RegisterId(0);
        let error = parse_exact_675_machine(&wrong_order).unwrap_err();
        assert!(error.contains("order"), "{error}");

        let mut wrong_kind = exact_abi_ops();
        wrong_kind[0].q_target = crate::circuit::NO_QUBIT;
        wrong_kind[0].c_target = BitId(600);
        let error = parse_exact_675_machine(&wrong_kind).unwrap_err();
        assert!(error.contains("r0") && error.contains("qubit"), "{error}");

        let mut wrong_width = exact_abi_ops();
        wrong_width.remove(0);
        let error = parse_exact_675_machine(&wrong_width).unwrap_err();
        assert!(error.contains("width") && error.contains("255"), "{error}");
    }

    #[test]
    fn missing_register_or_out_of_range_id_fails() {
        let mut missing_register = exact_abi_ops();
        missing_register.pop();
        let error = parse_exact_675_machine(&missing_register).unwrap_err();
        assert!(
            error.contains("r3") && error.contains("declaration"),
            "{error}"
        );

        let mut out_of_range = exact_abi_ops();
        let mut huge = Op::empty();
        huge.kind = OperationType::X;
        huge.q_target = QubitId(u64::MAX - 1);
        out_of_range.push(huge);
        let error = parse_exact_675_machine(&out_of_range).unwrap_err();
        assert!(
            error.contains("cannot allocate") || error.contains("range"),
            "{error}"
        );
    }

    #[test]
    fn illegal_qubit_alias_fails_without_panicking() {
        let mut op = Op::empty();
        op.kind = OperationType::CX;
        op.q_control1 = QubitId(4);
        op.q_target = QubitId(4);
        let error = validate_op_schema(17, &op).unwrap_err();
        assert!(error.contains("alias"), "{error}");
    }

    #[test]
    fn missing_origin_and_length_drift_fail() {
        let ops = exact_abi_ops();
        let error = audit_parts(&ops, &[]).unwrap_err();
        assert!(error.contains("missing origin"), "{error}");

        let error = audit_parts(&ops, &origins(ops.len() - 1)).unwrap_err();
        assert!(error.contains("length drift"), "{error}");
    }

    #[test]
    fn physical_id_reuse_metadata_never_seeds_zero() {
        let mut machine = AbstractMachine::for_test(vec![AbstractValue::Known1], Vec::new());
        let mut append = Op::empty();
        append.kind = OperationType::AppendToRegister;
        append.q_target = QubitId(0);
        append.r_target = RegisterId(0);
        apply_plain(&mut machine, 0, &append);
        let mut register = Op::empty();
        register.kind = OperationType::Register;
        register.r_target = RegisterId(0);
        apply_plain(&mut machine, 1, &register);
        assert_eq!(machine.qubit(QubitId(0)), AbstractValue::Known1);
    }

    struct FiniteXof {
        bytes: Vec<u8>,
        cursor: usize,
    }

    impl FiniteXof {
        fn from_words(words: &[u64]) -> Self {
            let mut bytes = Vec::with_capacity(words.len() * 8);
            for word in words {
                bytes.extend_from_slice(&word.to_le_bytes());
            }
            Self { bytes, cursor: 0 }
        }
    }

    impl sha3::digest::XofReader for FiniteXof {
        fn read(&mut self, buffer: &mut [u8]) {
            let end = self.cursor + buffer.len();
            assert!(end <= self.bytes.len(), "finite XOF exhausted");
            buffer.copy_from_slice(&self.bytes[self.cursor..end]);
            self.cursor = end;
        }
    }

    struct SoundnessFixture {
        name: String,
        machine: AbstractMachine,
        ops: Vec<Op>,
        xof_words: usize,
        require_known_after_every_prefix: bool,
    }

    fn conditioned_swap(control: u64, target: u64, condition: u64) -> Op {
        let mut op = Op::empty();
        op.kind = OperationType::Swap;
        op.q_control1 = QubitId(control);
        op.q_target = QubitId(target);
        op.c_condition = BitId(condition);
        op
    }

    fn conditioned_bit(kind: OperationType, target: u64, condition: u64) -> Op {
        let mut op = Op::empty();
        op.kind = kind;
        op.c_target = BitId(target);
        op.c_condition = BitId(condition);
        op
    }

    fn declared_input_fixture(width: usize) -> SoundnessFixture {
        let input_qubits = 2 * width;
        let input_bits = 2 * width;
        let auxiliary = input_qubits as u64;
        let mut machine = AbstractMachine::for_test(
            [
                vec![AbstractValue::Unknown; input_qubits],
                vec![AbstractValue::Known0],
            ]
            .concat(),
            vec![AbstractValue::Unknown; input_bits],
        );
        machine.base_condition = AbstractValue::Known1;

        let mut ops = Vec::new();
        ops.push(x(auxiliary));

        let mut hmr = Op::empty();
        hmr.kind = OperationType::Hmr;
        hmr.q_target = QubitId(auxiliary);
        hmr.c_target = BitId(0);
        hmr.c_condition = BitId(0);
        ops.push(hmr);

        ops.push(push_condition(1));
        let mut clear_pushed = Op::empty();
        clear_pushed.kind = OperationType::BitStore0;
        clear_pushed.c_target = BitId(1);
        ops.push(clear_pushed);
        ops.push(x(auxiliary));
        ops.push(push_condition(0));

        let mut cx = Op::empty();
        cx.kind = OperationType::CX;
        cx.q_control1 = QubitId(0);
        cx.q_target = QubitId(auxiliary);
        ops.push(cx);
        ops.push(pop_condition());

        let mut reset = Op::empty();
        reset.kind = OperationType::R;
        reset.q_target = QubitId(1);
        ops.push(reset);
        ops.push(pop_condition());

        for kind in [
            OperationType::BitInvert,
            OperationType::BitStore0,
            OperationType::BitStore1,
        ] {
            let mut op = Op::empty();
            op.kind = kind;
            op.c_target = if kind == OperationType::BitStore0 {
                BitId(1)
            } else {
                BitId(0)
            };
            op.c_condition = op.c_target;
            ops.push(op);
        }

        let mut swap = Op::empty();
        swap.kind = OperationType::Swap;
        swap.q_control1 = QubitId(0);
        swap.q_target = QubitId(1);
        swap.c_condition = BitId(0);
        ops.push(swap);

        for kind in [OperationType::CCX, OperationType::CCZ] {
            let mut op = op3(kind);
            op.q_target = QubitId(auxiliary);
            op.c_condition = BitId(1);
            ops.push(op);
        }

        let mut neg = Op::empty();
        neg.c_condition = BitId(0);
        ops.push(neg);
        let mut z = x(0);
        z.kind = OperationType::Z;
        ops.push(z);
        let mut cz = Op::empty();
        cz.kind = OperationType::CZ;
        cz.q_control1 = QubitId(0);
        cz.q_target = QubitId(1);
        ops.push(cz);

        for lane in 0..width as u64 {
            let mut cx = Op::empty();
            cx.kind = OperationType::CX;
            cx.q_control1 = QubitId(lane);
            cx.q_target = QubitId(width as u64 + lane);
            cx.c_condition = BitId(lane);
            ops.push(cx);

            ops.push(conditioned_swap(
                lane,
                width as u64 + lane,
                width as u64 + lane,
            ));
            ops.push(conditioned_bit(
                OperationType::BitInvert,
                lane,
                width as u64 + lane,
            ));
            ops.push(conditioned_bit(
                OperationType::BitStore0,
                width as u64 + lane,
                lane,
            ));
        }

        let mut touched_qubits = vec![false; input_qubits];
        let mut touched_bits = vec![false; input_bits];
        for op in &ops {
            for id in [op.q_control2, op.q_control1, op.q_target] {
                if let Ok(index) = usize::try_from(id.0) {
                    if index < input_qubits {
                        touched_qubits[index] = true;
                    }
                }
            }
            for id in [op.c_target, op.c_condition] {
                if let Ok(index) = usize::try_from(id.0) {
                    if index < input_bits {
                        touched_bits[index] = true;
                    }
                }
            }
        }
        assert!(
            touched_qubits.into_iter().all(|touched| touched),
            "width {width} must use every declared qubit lane"
        );
        assert!(
            touched_bits.into_iter().all(|touched| touched),
            "width {width} must use every declared bit lane"
        );

        SoundnessFixture {
            name: format!("declared-input-width-{width}"),
            machine,
            ops,
            xof_words: 2,
            require_known_after_every_prefix: false,
        }
    }

    fn swap_and_classical_fixture() -> SoundnessFixture {
        let machine = AbstractMachine::for_test(
            vec![
                AbstractValue::Known0,
                AbstractValue::Known1,
                AbstractValue::Known1,
                AbstractValue::Known0,
                AbstractValue::Known1,
                AbstractValue::Known1,
            ],
            vec![
                AbstractValue::Known0,
                AbstractValue::Known1,
                AbstractValue::Unknown,
                AbstractValue::Known1,
                AbstractValue::Known0,
                AbstractValue::Known1,
                AbstractValue::Unknown,
            ],
        );
        let ops = vec![
            conditioned_swap(0, 1, 0),
            conditioned_swap(0, 1, 1),
            conditioned_swap(2, 3, 2),
            conditioned_swap(4, 5, 2),
            conditioned_bit(OperationType::BitInvert, 0, 0),
            conditioned_bit(OperationType::BitInvert, 1, 1),
            conditioned_bit(OperationType::BitStore0, 3, 3),
            conditioned_bit(OperationType::BitStore1, 4, 4),
            conditioned_bit(OperationType::BitStore1, 5, 5),
            conditioned_bit(OperationType::BitStore0, 6, 6),
        ];
        SoundnessFixture {
            name: "conditional-swap-and-classical-aliases".to_owned(),
            machine,
            ops,
            xof_words: 0,
            require_known_after_every_prefix: true,
        }
    }

    fn ccx_fixture() -> SoundnessFixture {
        let cases = [
            (
                [
                    AbstractValue::Known0,
                    AbstractValue::Unknown,
                    AbstractValue::Known1,
                ],
                None,
            ),
            (
                [
                    AbstractValue::Unknown,
                    AbstractValue::Known0,
                    AbstractValue::Known0,
                ],
                Some(1),
            ),
            (
                [
                    AbstractValue::Known1,
                    AbstractValue::Known1,
                    AbstractValue::Known0,
                ],
                Some(1),
            ),
            (
                [
                    AbstractValue::Known1,
                    AbstractValue::Unknown,
                    AbstractValue::Known0,
                ],
                None,
            ),
            (
                [
                    AbstractValue::Unknown,
                    AbstractValue::Known1,
                    AbstractValue::Known1,
                ],
                None,
            ),
            (
                [
                    AbstractValue::Unknown,
                    AbstractValue::Unknown,
                    AbstractValue::Known0,
                ],
                None,
            ),
            (
                [
                    AbstractValue::Known1,
                    AbstractValue::Known1,
                    AbstractValue::Known0,
                ],
                Some(0),
            ),
            (
                [
                    AbstractValue::Known1,
                    AbstractValue::Known1,
                    AbstractValue::Known0,
                ],
                Some(2),
            ),
        ];
        let mut qubits = Vec::with_capacity(cases.len() * 3);
        let mut ops = Vec::with_capacity(cases.len());
        for (case_index, (facts, condition)) in cases.into_iter().enumerate() {
            let first = qubits.len() as u64;
            qubits.extend(facts);
            let mut op = Op::empty();
            op.kind = OperationType::CCX;
            op.q_control2 = QubitId(first);
            op.q_control1 = QubitId(first + 1);
            op.q_target = QubitId(first + 2);
            if let Some(condition) = condition {
                op.c_condition = BitId(condition);
            }
            assert_eq!(first as usize, case_index * 3);
            ops.push(op);
        }
        SoundnessFixture {
            name: "ccx-drop-lower-and-keep-cases".to_owned(),
            machine: AbstractMachine::for_test(
                qubits,
                vec![
                    AbstractValue::Known0,
                    AbstractValue::Known1,
                    AbstractValue::Unknown,
                ],
            ),
            ops,
            xof_words: 0,
            require_known_after_every_prefix: true,
        }
    }

    fn ccz_fixture() -> SoundnessFixture {
        let mut cases = Vec::new();
        for zero_position in 0..3 {
            let mut facts = [AbstractValue::Known1; 3];
            facts[zero_position] = AbstractValue::Known0;
            facts[(zero_position + 1) % 3] = AbstractValue::Unknown;
            cases.push(facts);
        }
        for known_one_mask in 1u8..8 {
            cases.push(std::array::from_fn(|index| {
                if known_one_mask & (1 << index) == 0 {
                    AbstractValue::Unknown
                } else {
                    AbstractValue::Known1
                }
            }));
        }

        let mut qubits = Vec::with_capacity(cases.len() * 3);
        let mut ops = Vec::with_capacity(cases.len());
        for facts in cases {
            let first = qubits.len() as u64;
            qubits.extend(facts);
            let mut op = Op::empty();
            op.kind = OperationType::CCZ;
            op.q_control2 = QubitId(first);
            op.q_control1 = QubitId(first + 1);
            op.q_target = QubitId(first + 2);
            ops.push(op);
        }
        SoundnessFixture {
            name: "ccz-fact-position-cases".to_owned(),
            machine: AbstractMachine::for_test(qubits, Vec::new()),
            ops,
            xof_words: 0,
            require_known_after_every_prefix: true,
        }
    }

    fn stochastic_fixture() -> SoundnessFixture {
        let machine = AbstractMachine::for_test(
            vec![
                AbstractValue::Known1,
                AbstractValue::Known0,
                AbstractValue::Known1,
                AbstractValue::Known0,
                AbstractValue::Known1,
                AbstractValue::Known0,
            ],
            vec![
                AbstractValue::Known1,
                AbstractValue::Known0,
                AbstractValue::Unknown,
                AbstractValue::Known0,
                AbstractValue::Known1,
            ],
        );
        let mut ops = Vec::new();
        for (target, condition) in [(0, 1), (1, 2), (2, 0)] {
            let mut reset = Op::empty();
            reset.kind = OperationType::R;
            reset.q_target = QubitId(target);
            reset.c_condition = BitId(condition);
            ops.push(reset);
        }
        for (target, result_and_condition) in [(3, 4), (4, 1), (5, 2)] {
            let mut hmr = Op::empty();
            hmr.kind = OperationType::Hmr;
            hmr.q_target = QubitId(target);
            hmr.c_target = BitId(result_and_condition);
            hmr.c_condition = BitId(result_and_condition);
            ops.push(hmr);
        }
        SoundnessFixture {
            name: "reset-hmr-and-result-condition-aliases".to_owned(),
            machine,
            ops,
            xof_words: 6,
            require_known_after_every_prefix: true,
        }
    }

    fn assert_abstract_snapshot_sound(
        fixture: &str,
        prefix: usize,
        assignment: usize,
        xof_pattern: usize,
        abstract_qubits: &[AbstractValue],
        abstract_bits: &[AbstractValue],
        concrete_qubits: &[u64],
        concrete_bits: &[u64],
    ) {
        assert_eq!(abstract_qubits.len(), concrete_qubits.len());
        assert_eq!(abstract_bits.len(), concrete_bits.len());
        for (id, (&abstract_value, &concrete)) in
            abstract_qubits.iter().zip(concrete_qubits).enumerate()
        {
            let concrete = concrete & 1;
            match abstract_value {
                AbstractValue::Known0 => assert_eq!(
                    concrete, 0,
                    "fixture={fixture} prefix={prefix} assignment={assignment} xof={xof_pattern} q{id}"
                ),
                AbstractValue::Known1 => assert_eq!(
                    concrete, 1,
                    "fixture={fixture} prefix={prefix} assignment={assignment} xof={xof_pattern} q{id}"
                ),
                AbstractValue::Unknown => {}
            }
        }
        for (id, (&abstract_value, &concrete)) in
            abstract_bits.iter().zip(concrete_bits).enumerate()
        {
            let concrete = concrete & 1;
            match abstract_value {
                AbstractValue::Known0 => assert_eq!(
                    concrete, 0,
                    "fixture={fixture} prefix={prefix} assignment={assignment} xof={xof_pattern} b{id}"
                ),
                AbstractValue::Known1 => assert_eq!(
                    concrete, 1,
                    "fixture={fixture} prefix={prefix} assignment={assignment} xof={xof_pattern} b{id}"
                ),
                AbstractValue::Unknown => {}
            }
        }
    }

    fn initialize_concrete_state(
        facts: &[AbstractValue],
        concrete: &mut [u64],
        assignment: usize,
        unknown_index: &mut usize,
    ) {
        for (&fact, concrete) in facts.iter().zip(concrete) {
            *concrete = match fact {
                AbstractValue::Known0 => 0,
                AbstractValue::Known1 => 1,
                AbstractValue::Unknown => {
                    let value = ((assignment >> *unknown_index) & 1) as u64;
                    *unknown_index += 1;
                    value
                }
            };
        }
    }

    fn run_soundness_fixture(mut fixture: SoundnessFixture) {
        let initial_qubits = fixture.machine.qubits.clone();
        let initial_bits = fixture.machine.bits.clone();
        let unknown_count = initial_qubits
            .iter()
            .chain(&initial_bits)
            .filter(|&&fact| fact == AbstractValue::Unknown)
            .count();
        assert!(unknown_count < usize::BITS as usize);
        assert!(fixture.xof_words < usize::BITS as usize);

        let mut snapshots = Vec::with_capacity(fixture.ops.len());
        for (index, op) in fixture.ops.iter().enumerate() {
            validate_op_schema(index as u64, op).expect("valid reduced operation");
            fixture
                .machine
                .apply(index as u64, op, origin(index as u32))
                .expect("abstract transfer");
            if fixture.require_known_after_every_prefix {
                let known_count = fixture
                    .machine
                    .qubits
                    .iter()
                    .chain(&fixture.machine.bits)
                    .filter(|&&fact| fact != AbstractValue::Unknown)
                    .count();
                assert!(
                    known_count > 0,
                    "fixture {} became vacuous after prefix {}",
                    fixture.name,
                    index + 1
                );
            }
            snapshots.push((fixture.machine.qubits.clone(), fixture.machine.bits.clone()));
        }
        fixture.machine.finish().expect("balanced reduced sequence");
        assert_eq!(
            fixture.machine.xof_words_consumed, fixture.xof_words as u64,
            "fixture {} XOF count",
            fixture.name
        );

        for assignment in 0..(1usize << unknown_count) {
            // The concrete domain is deliberately finite: every Unknown input and
            // every XOF word is independently enumerated as the Boolean values 0/1.
            for xof_pattern in 0..(1usize << fixture.xof_words) {
                let words: Vec<u64> = (0..fixture.xof_words)
                    .map(|word| ((xof_pattern >> word) & 1) as u64)
                    .collect();
                for prefix in 1..=fixture.ops.len() {
                    let mut xof = FiniteXof::from_words(&words);
                    let mut simulator = crate::sim::Simulator::new(
                        initial_qubits.len(),
                        initial_bits.len(),
                        &mut xof,
                    );
                    let mut unknown_index = 0;
                    initialize_concrete_state(
                        &initial_qubits,
                        &mut simulator.qubits,
                        assignment,
                        &mut unknown_index,
                    );
                    initialize_concrete_state(
                        &initial_bits,
                        &mut simulator.bits,
                        assignment,
                        &mut unknown_index,
                    );
                    assert_eq!(unknown_index, unknown_count);

                    simulator.apply_iter(fixture.ops[..prefix].iter());
                    let (abstract_qubits, abstract_bits) = &snapshots[prefix - 1];
                    assert_abstract_snapshot_sound(
                        &fixture.name,
                        prefix,
                        assignment,
                        xof_pattern,
                        abstract_qubits,
                        abstract_bits,
                        &simulator.qubits,
                        &simulator.bits,
                    );
                }
            }
        }
    }

    #[test]
    fn exhaustive_reduced_sequence_soundness() {
        for width in 1usize..=3 {
            let fixture = declared_input_fixture(width);
            let declared_unknowns = fixture
                .machine
                .qubits
                .iter()
                .chain(&fixture.machine.bits)
                .filter(|&&fact| fact == AbstractValue::Unknown)
                .count();
            assert_eq!(declared_unknowns, 4 * width);
            run_soundness_fixture(fixture);
        }
        for fixture in [
            swap_and_classical_fixture(),
            ccx_fixture(),
            ccz_fixture(),
            stochastic_fixture(),
        ] {
            run_soundness_fixture(fixture);
        }
    }
}
