use std::collections::{BTreeMap, BTreeSet};
use std::path::{Component, Path};

use crate::circuit::{BitId, Op, OperationType, QubitId, NO_BIT, NO_QUBIT, NO_REG};
use sha2::{Digest, Sha256};
use sha3::{
    digest::{ExtendableOutput, Update, XofReader},
    Shake256,
};

use super::{OriginRef, SourceSite, TracedOps};

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
    pub(crate) q_control2: QubitId,
    pub(crate) q_control1: QubitId,
    pub(crate) q_target: QubitId,
    pub(crate) c_condition: BitId,
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
                    q_control2: op.q_control2,
                    q_control1: op.q_control1,
                    q_target: op.q_target,
                    c_condition: op.c_condition,
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
                    q_control2: op.q_control2,
                    q_control1: op.q_control1,
                    q_target: op.q_target,
                    c_condition: op.c_condition,
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

fn parse_machine_with_width(ops: &[Op], expected_width: usize) -> Result<AbstractMachine, String> {
    if expected_width == 0 {
        return Err("register width must be nonzero".to_owned());
    }
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
        if registers[register].len() != expected_width {
            return Err(format!(
                "register r{register} has width {}, expected {expected_width}",
                registers[register].len(),
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

fn parse_exact_675_machine(ops: &[Op]) -> Result<AbstractMachine, String> {
    parse_machine_with_width(ops, 256)
}

#[derive(Debug)]
pub(crate) struct AuditCoreResult {
    pub(crate) decisions: Vec<GateDecision>,
    pub(crate) final_qubits: Vec<AbstractValue>,
    pub(crate) final_bits: Vec<AbstractValue>,
    pub(crate) xof_words_consumed: u64,
}

fn audit_parts_with_width(
    ops: &[Op],
    origins: &[OriginRef],
    expected_width: usize,
) -> Result<AuditCoreResult, String> {
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

    let mut machine = parse_machine_with_width(ops, expected_width)?;
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

fn audit_parts(ops: &[Op], origins: &[OriginRef]) -> Result<AuditCoreResult, String> {
    audit_parts_with_width(ops, origins, 256)
}

pub(crate) fn audit_traced(stream: &TracedOps) -> Result<AuditCoreResult, String> {
    if !stream.enabled() {
        return Err("missing origin sidecar: traced audit stream is disabled".to_owned());
    }
    audit_parts(stream, stream.origins())
}

const AUDIT_ACTION_COUNT: usize = 8;
const PROOF_RULE_COUNT: usize = 9;
const RAW_FORMAT: &str = "j3-dead-gate-raw-v1";
const PRODUCTION_EXACT_PREDICATES: &[ExactSourcePredicate] = &[];

#[derive(Clone, Copy, Debug, Eq, PartialEq, Ord, PartialOrd)]
enum GateKind {
    Ccx,
    Ccz,
}

impl GateKind {
    fn from_operation(kind: OperationType) -> Result<Self, String> {
        match kind {
            OperationType::CCX => Ok(Self::Ccx),
            OperationType::CCZ => Ok(Self::Ccz),
            _ => Err(format!("non-audited family operation kind {kind:?}")),
        }
    }

    fn as_str(self) -> &'static str {
        match self {
            Self::Ccx => "ccx",
            Self::Ccz => "ccz",
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq, Ord, PartialOrd)]
struct FamilyKey {
    audit_path: String,
    audit_line: u32,
    trace_context: u32,
    kind: GateKind,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum FamilyDisposition {
    UniformProvisional,
    ExactPredicateProvisional,
    DiagnosticMixed,
}

impl FamilyDisposition {
    fn as_str(self) -> &'static str {
        match self {
            Self::UniformProvisional => "uniform_provisional",
            Self::ExactPredicateProvisional => "exact_predicate_provisional",
            Self::DiagnosticMixed => "diagnostic_mixed",
        }
    }
}

/// A deliberately narrow predicate over stable source-literal metadata.
/// It cannot observe operation indices, nonces, shots, or evaluator state.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct ExactSourcePredicate {
    trace_context: u32,
    inverse_depth: u16,
    flags: u16,
}

impl ExactSourcePredicate {
    fn validate(self) -> Result<(), String> {
        OriginRef {
            site_id: 0,
            emission_ordinal: 0,
            inverse_depth: self.inverse_depth,
            flags: self.flags,
        }
        .try_validate_transform_chain()
        .map_err(str::to_owned)
    }

    fn matches(self, trace_context: u32, origin: OriginRef) -> bool {
        self.trace_context == trace_context
            && self.inverse_depth == origin.inverse_depth
            && self.flags == origin.flags
    }
}

#[derive(Debug)]
struct FamilyAccumulator {
    decision_count: u64,
    action_counts: [u64; AUDIT_ACTION_COUNT],
    rule_counts: [u64; PROOF_RULE_COUNT],
    predicate_exact: Vec<bool>,
}

impl FamilyAccumulator {
    fn new(predicate_count: usize) -> Self {
        Self {
            decision_count: 0,
            action_counts: [0; AUDIT_ACTION_COUNT],
            rule_counts: [0; PROOF_RULE_COUNT],
            predicate_exact: vec![true; predicate_count],
        }
    }

    fn record(
        &mut self,
        decision: GateDecision,
        trace_context: u32,
        predicates: &[ExactSourcePredicate],
    ) -> Result<(), String> {
        self.decision_count = self
            .decision_count
            .checked_add(1)
            .ok_or_else(|| "family decision count overflow".to_owned())?;
        let action_count = self
            .action_counts
            .get_mut(decision.action as usize)
            .ok_or_else(|| "audit action index out of range".to_owned())?;
        *action_count = action_count
            .checked_add(1)
            .ok_or_else(|| "family action count overflow".to_owned())?;
        let rule_count = self
            .rule_counts
            .get_mut(decision.rule as usize)
            .ok_or_else(|| "proof rule index out of range".to_owned())?;
        *rule_count = rule_count
            .checked_add(1)
            .ok_or_else(|| "family rule count overflow".to_owned())?;
        let is_non_keep = decision.action != AuditAction::Keep;
        for (is_exact, predicate) in self.predicate_exact.iter_mut().zip(predicates) {
            let selected = predicate.matches(trace_context, decision.origin);
            *is_exact &= selected == is_non_keep;
        }
        Ok(())
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct FamilyRow {
    key: FamilyKey,
    decision_count: u64,
    action_counts: [u64; AUDIT_ACTION_COUNT],
    rule_counts: [u64; PROOF_RULE_COUNT],
    disposition: FamilyDisposition,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Ord, PartialOrd)]
struct SiteClassKey {
    site_id: u32,
    inverse_depth: u16,
    flags: u16,
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct SiteRow {
    class: SiteClassKey,
    audit_path: String,
    audit_line: u32,
    trace_context: u32,
    occurrence_count: u64,
    transform_chain: String,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct WitnessRow {
    decision: GateDecision,
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct ValidatedSite {
    audit_path: String,
    audit_line: u32,
    trace_context: u32,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct StreamHashes {
    canonical_records_sha256: [u8; 32],
    provenance_sha256: [u8; 32],
    trusted_xof32: [u8; 32],
}

#[derive(Debug)]
pub(crate) struct AuditReport {
    core: AuditCoreResult,
    hashes: StreamHashes,
    operation_count: u64,
    provenance_count: u64,
    ccx_count: u64,
    ccz_count: u64,
    sites: Vec<SiteRow>,
    families: Vec<FamilyRow>,
    witnesses: Vec<WitnessRow>,
    validated_sites: Vec<ValidatedSite>,
}

impl AuditReport {
    fn diagnostic_family_count(&self) -> u64 {
        self.families
            .iter()
            .filter(|family| family.disposition == FamilyDisposition::DiagnosticMixed)
            .count() as u64
    }
}

fn normalize_audit_path(path: &str) -> Result<String, String> {
    if path.is_empty() {
        return Err("audit source path is empty".to_owned());
    }
    if path
        .bytes()
        .any(|byte| matches!(byte, b'\t' | b'\n' | b'\r'))
    {
        return Err("audit source path contains a forbidden control character".to_owned());
    }
    let path = Path::new(path);
    if path.is_absolute() {
        return Err("audit source path must be repository-relative".to_owned());
    }

    let mut components = Vec::new();
    for component in path.components() {
        match component {
            Component::CurDir => {}
            Component::Normal(component) => {
                let component = component
                    .to_str()
                    .ok_or_else(|| "audit source path is not UTF-8".to_owned())?;
                components.push(component);
            }
            Component::ParentDir => {
                if components.pop().is_none() {
                    return Err("audit source path traverses above repository root".to_owned());
                }
            }
            Component::RootDir | Component::Prefix(_) => {
                return Err("audit source path must be repository-relative".to_owned());
            }
        }
    }
    if components.len() < 3 || components[0] != "src" || components[1] != "point_add" {
        return Err("audit source path is outside src/point_add".to_owned());
    }
    Ok(components.join("/"))
}

fn validate_origin_metadata(origin: OriginRef, sites: &[SourceSite]) -> Result<(), String> {
    origin
        .try_validate_transform_chain()
        .map_err(str::to_owned)?;
    let site = sites.get(origin.site_id as usize).ok_or_else(|| {
        format!(
            "origin site_id {} is outside site table length {}",
            origin.site_id,
            sites.len()
        )
    })?;
    if site.line == 0 {
        return Err(format!(
            "origin site_id {} has zero source line",
            origin.site_id
        ));
    }
    normalize_audit_path(site.file)?;
    Ok(())
}

fn validate_sites(sites: &[SourceSite]) -> Result<Vec<ValidatedSite>, String> {
    sites
        .iter()
        .enumerate()
        .map(|(site_id, site)| {
            if site.line == 0 {
                return Err(format!("origin site_id {site_id} has zero source line"));
            }
            Ok(ValidatedSite {
                audit_path: normalize_audit_path(site.file)?,
                audit_line: site.line,
                trace_context: site.trace_context,
            })
        })
        .collect()
}

fn update_canonical_record<H: sha2::Digest>(hasher: &mut H, op: &Op) {
    Digest::update(hasher, [op.kind as u8]);
    for value in [
        op.q_control2.0,
        op.q_control1.0,
        op.q_target.0,
        op.c_target.0,
        op.c_condition.0,
        op.r_target.0,
    ] {
        Digest::update(hasher, value.to_le_bytes());
    }
}

fn update_xof_record(hasher: &mut Shake256, op: &Op) {
    Update::update(hasher, &[op.kind as u8]);
    for value in [
        op.q_control2.0,
        op.q_control1.0,
        op.q_target.0,
        op.c_target.0,
        op.c_condition.0,
        op.r_target.0,
    ] {
        Update::update(hasher, &value.to_le_bytes());
    }
}

fn canonical_stream_hashes(ops: &[Op]) -> ([u8; 32], [u8; 32]) {
    let operation_count = u64::try_from(ops.len()).expect("operation count exceeds u64");
    let mut canonical = Sha256::new();
    let mut trusted_xof = Shake256::default();
    Update::update(&mut trusted_xof, b"quantum_ecc-fiat-shamir-v2");
    Update::update(&mut trusted_xof, &operation_count.to_le_bytes());
    for op in ops {
        update_canonical_record(&mut canonical, op);
        update_xof_record(&mut trusted_xof, op);
    }
    let canonical_records_sha256 = canonical.finalize().into();
    let mut trusted_xof32 = [0u8; 32];
    trusted_xof.finalize_xof().read(&mut trusted_xof32);
    (canonical_records_sha256, trusted_xof32)
}

fn hash_stream(
    ops: &[Op],
    origins: &[OriginRef],
    sites: &[SourceSite],
) -> Result<(StreamHashes, Vec<ValidatedSite>), String> {
    if ops.len() != origins.len() {
        return Err(format!(
            "operation/origin length drift: {} operations, {} origins",
            ops.len(),
            origins.len()
        ));
    }
    let operation_count =
        u64::try_from(ops.len()).map_err(|_| "operation count exceeds u64".to_owned())?;
    let validated_sites = validate_sites(sites)?;

    let (canonical_records_sha256, trusted_xof32) = canonical_stream_hashes(ops);

    let mut provenance = Sha256::new();
    Digest::update(&mut provenance, operation_count.to_le_bytes());
    for (index, origin) in origins.iter().copied().enumerate() {
        validate_origin_metadata(origin, sites)?;
        let site = &validated_sites[origin.site_id as usize];
        let final_index =
            u64::try_from(index).map_err(|_| "operation index exceeds u64".to_owned())?;
        let path_len = u32::try_from(site.audit_path.len())
            .map_err(|_| "normalized audit path length exceeds u32".to_owned())?;
        Digest::update(&mut provenance, final_index.to_le_bytes());
        Digest::update(&mut provenance, path_len.to_le_bytes());
        Digest::update(&mut provenance, site.audit_path.as_bytes());
        Digest::update(&mut provenance, site.audit_line.to_le_bytes());
        Digest::update(&mut provenance, site.trace_context.to_le_bytes());
        Digest::update(&mut provenance, origin.emission_ordinal.to_le_bytes());
        Digest::update(&mut provenance, origin.inverse_depth.to_le_bytes());
        Digest::update(&mut provenance, origin.flags.to_le_bytes());
        origin
            .stream_transform_chain_digest_preimage(|bytes| Digest::update(&mut provenance, bytes));
    }

    let provenance_sha256 = provenance.finalize().into();
    Ok((
        StreamHashes {
            canonical_records_sha256,
            provenance_sha256,
            trusted_xof32,
        },
        validated_sites,
    ))
}

fn audit_report_with_width(
    stream: &TracedOps,
    expected_width: usize,
    predicates: &[ExactSourcePredicate],
) -> Result<AuditReport, String> {
    if !stream.enabled() {
        return Err("missing origin sidecar: traced audit stream is disabled".to_owned());
    }
    for predicate in predicates {
        predicate.validate()?;
    }
    let (hashes, validated_sites) = hash_stream(stream, stream.origins(), stream.sites())?;
    let core = audit_parts_with_width(stream, stream.origins(), expected_width)?;

    let mut site_counts = BTreeMap::<SiteClassKey, u64>::new();
    for origin in stream.origins().iter().copied() {
        let key = SiteClassKey {
            site_id: origin.site_id,
            inverse_depth: origin.inverse_depth,
            flags: origin.flags,
        };
        let count = site_counts.entry(key).or_default();
        *count = count
            .checked_add(1)
            .ok_or_else(|| "site occurrence count overflow".to_owned())?;
    }
    let sites = site_counts
        .into_iter()
        .map(|(class, occurrence_count)| {
            let site = &validated_sites[class.site_id as usize];
            let origin = OriginRef {
                site_id: class.site_id,
                emission_ordinal: 0,
                inverse_depth: class.inverse_depth,
                flags: class.flags,
            };
            SiteRow {
                class,
                audit_path: site.audit_path.clone(),
                audit_line: site.audit_line,
                trace_context: site.trace_context,
                occurrence_count,
                transform_chain: origin.transform_chain(),
            }
        })
        .collect::<Vec<_>>();

    let mut family_accumulators = BTreeMap::<(&str, u32, u32, GateKind), FamilyAccumulator>::new();
    for decision in &core.decisions {
        let site = &validated_sites[decision.origin.site_id as usize];
        let key = (
            site.audit_path.as_str(),
            site.audit_line,
            site.trace_context,
            GateKind::from_operation(decision.kind)?,
        );
        family_accumulators
            .entry(key)
            .or_insert_with(|| FamilyAccumulator::new(predicates.len()))
            .record(*decision, site.trace_context, predicates)?;
    }
    let families = family_accumulators
        .into_iter()
        .map(
            |((audit_path, audit_line, trace_context, kind), accumulator)| {
                let distinct_actions = accumulator
                    .action_counts
                    .iter()
                    .filter(|&&count| count != 0)
                    .count();
                let disposition = if distinct_actions == 1 {
                    FamilyDisposition::UniformProvisional
                } else if accumulator.predicate_exact.into_iter().any(|exact| exact) {
                    FamilyDisposition::ExactPredicateProvisional
                } else {
                    FamilyDisposition::DiagnosticMixed
                };
                FamilyRow {
                    key: FamilyKey {
                        audit_path: audit_path.to_owned(),
                        audit_line,
                        trace_context,
                        kind,
                    },
                    decision_count: accumulator.decision_count,
                    action_counts: accumulator.action_counts,
                    rule_counts: accumulator.rule_counts,
                    disposition,
                }
            },
        )
        .collect::<Vec<_>>();

    let mut witnesses = core
        .decisions
        .iter()
        .copied()
        .filter(|decision| decision.action != AuditAction::Keep)
        .map(|decision| WitnessRow { decision })
        .collect::<Vec<_>>();
    witnesses.sort_by_key(|witness| witness.decision.op_index);

    let operation_count =
        u64::try_from(stream.len()).map_err(|_| "operation count exceeds u64".to_owned())?;
    let provenance_count = u64::try_from(stream.origins().len())
        .map_err(|_| "provenance count exceeds u64".to_owned())?;
    let ccx_count = core
        .decisions
        .iter()
        .filter(|decision| decision.kind == OperationType::CCX)
        .count() as u64;
    let ccz_count = core
        .decisions
        .iter()
        .filter(|decision| decision.kind == OperationType::CCZ)
        .count() as u64;
    Ok(AuditReport {
        core,
        hashes,
        operation_count,
        provenance_count,
        ccx_count,
        ccz_count,
        sites,
        families,
        witnesses,
        validated_sites,
    })
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct RawManifest {
    canonical_records_sha256: [u8; 32],
    ccx_count: u64,
    ccz_count: u64,
    decision_count: u64,
    family_count: u64,
    format: String,
    operation_count: u64,
    provenance_count: u64,
    provenance_sha256: [u8; 32],
    trusted_xof32: [u8; 32],
    witness_count: u64,
    xof_words_consumed: u64,
}

fn lowercase_hex(bytes: &[u8]) -> String {
    const HEX: &[u8; 16] = b"0123456789abcdef";
    let mut result = String::with_capacity(bytes.len() * 2);
    for &byte in bytes {
        result.push(HEX[(byte >> 4) as usize] as char);
        result.push(HEX[(byte & 0xf) as usize] as char);
    }
    result
}

fn parse_lowercase_hex32(value: &str, field: &str) -> Result<[u8; 32], String> {
    if value.len() != 64
        || !value
            .bytes()
            .all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte))
    {
        return Err(format!(
            "manifest field {field} is not 64-byte lowercase hex"
        ));
    }
    let mut output = [0u8; 32];
    for (index, pair) in value.as_bytes().chunks_exact(2).enumerate() {
        let nibble = |byte: u8| match byte {
            b'0'..=b'9' => byte - b'0',
            b'a'..=b'f' => byte - b'a' + 10,
            _ => unreachable!(),
        };
        output[index] = (nibble(pair[0]) << 4) | nibble(pair[1]);
    }
    Ok(output)
}

fn manifest_rows(input: &str) -> Result<Vec<(&str, &str)>, String> {
    if !input.ends_with('\n') || input.ends_with("\n\n") {
        return Err("raw manifest must have exactly one trailing LF".to_owned());
    }
    let body = input.strip_suffix('\n').expect("trailing LF checked above");
    let mut seen = BTreeSet::new();
    let mut rows = Vec::new();
    for line in body.split('\n') {
        let (key, value) = line
            .split_once('=')
            .ok_or_else(|| format!("manifest row lacks '=': {line:?}"))?;
        if key.is_empty() || value.contains('=') {
            return Err(format!("invalid manifest row: {line:?}"));
        }
        if !seen.insert(key) {
            return Err(format!("duplicate manifest field {key}"));
        }
        rows.push((key, value));
    }
    Ok(rows)
}

fn parse_raw_manifest(input: &str) -> Result<RawManifest, String> {
    const KEYS: [&str; 12] = [
        "canonical_records_sha256",
        "ccx_count",
        "ccz_count",
        "decision_count",
        "family_count",
        "format",
        "operation_count",
        "provenance_count",
        "provenance_sha256",
        "trusted_xof32",
        "witness_count",
        "xof_words_consumed",
    ];
    let rows = manifest_rows(input)?;
    if rows.len() != KEYS.len() {
        return Err(format!(
            "raw manifest has {} fields, expected {}",
            rows.len(),
            KEYS.len()
        ));
    }
    for ((actual, _), expected) in rows.iter().zip(KEYS) {
        if *actual != expected {
            return Err(format!(
                "raw manifest field order mismatch: found {actual}, expected {expected}"
            ));
        }
    }
    let value = |index: usize| rows[index].1;
    let decimal = |index: usize| {
        value(index)
            .parse::<u64>()
            .map_err(|_| format!("manifest field {} is not decimal u64", KEYS[index]))
    };
    if value(5) != RAW_FORMAT {
        return Err(format!("unsupported raw manifest format {:?}", value(5)));
    }
    Ok(RawManifest {
        canonical_records_sha256: parse_lowercase_hex32(value(0), KEYS[0])?,
        ccx_count: decimal(1)?,
        ccz_count: decimal(2)?,
        decision_count: decimal(3)?,
        family_count: decimal(4)?,
        format: value(5).to_owned(),
        operation_count: decimal(6)?,
        provenance_count: decimal(7)?,
        provenance_sha256: parse_lowercase_hex32(value(8), KEYS[8])?,
        trusted_xof32: parse_lowercase_hex32(value(9), KEYS[9])?,
        witness_count: decimal(10)?,
        xof_words_consumed: decimal(11)?,
    })
}

fn abstract_value_name(value: AbstractValue) -> &'static str {
    match value {
        AbstractValue::Known0 => "known0",
        AbstractValue::Known1 => "known1",
        AbstractValue::Unknown => "unknown",
    }
}

fn audit_action_name(action: AuditAction) -> &'static str {
    match action {
        AuditAction::Keep => "keep",
        AuditAction::NoCostIdentity => "no_cost_identity",
        AuditAction::Drop => "drop",
        AuditAction::LowerToX => "lower_to_x",
        AuditAction::LowerToCX => "lower_to_cx",
        AuditAction::LowerToNeg => "lower_to_neg",
        AuditAction::LowerToZ => "lower_to_z",
        AuditAction::LowerToCZ => "lower_to_cz",
    }
}

fn proof_rule_name(rule: ProofRule) -> &'static str {
    match rule {
        ProofRule::None => "none",
        ProofRule::EffectiveConditionKnown0 => "effective_condition_known0",
        ProofRule::CcxControlKnown0 => "ccx_control_known0",
        ProofRule::CcxBothControlsKnown1 => "ccx_both_controls_known1",
        ProofRule::CcxOneControlKnown1 => "ccx_one_control_known1",
        ProofRule::CczOperandKnown0 => "ccz_operand_known0",
        ProofRule::CczThreeOperandsKnown1 => "ccz_three_operands_known1",
        ProofRule::CczTwoOperandsKnown1 => "ccz_two_operands_known1",
        ProofRule::CczOneOperandKnown1 => "ccz_one_operand_known1",
    }
}

fn render_raw_artifacts(report: &AuditReport) -> Result<BTreeMap<&'static str, Vec<u8>>, String> {
    let decision_count = u64::try_from(report.core.decisions.len())
        .map_err(|_| "decision count exceeds u64".to_owned())?;
    let family_count =
        u64::try_from(report.families.len()).map_err(|_| "family count exceeds u64".to_owned())?;
    let witness_count = u64::try_from(report.witnesses.len())
        .map_err(|_| "witness count exceeds u64".to_owned())?;
    let manifest = format!(
        "canonical_records_sha256={}\nccx_count={}\nccz_count={}\ndecision_count={}\nfamily_count={}\nformat={}\noperation_count={}\nprovenance_count={}\nprovenance_sha256={}\ntrusted_xof32={}\nwitness_count={}\nxof_words_consumed={}\n",
        lowercase_hex(&report.hashes.canonical_records_sha256),
        report.ccx_count,
        report.ccz_count,
        decision_count,
        family_count,
        RAW_FORMAT,
        report.operation_count,
        report.provenance_count,
        lowercase_hex(&report.hashes.provenance_sha256),
        lowercase_hex(&report.hashes.trusted_xof32),
        witness_count,
        report.core.xof_words_consumed,
    );
    parse_raw_manifest(&manifest)?;

    let mut sites = String::from(
        "site_id\taudit_path\taudit_line\ttrace_context\tinverse_depth\tflags\toccurrence_count\ttransform_chain\n",
    );
    for site in &report.sites {
        sites.push_str(&format!(
            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n",
            site.class.site_id,
            site.audit_path,
            site.audit_line,
            site.trace_context,
            site.class.inverse_depth,
            site.class.flags,
            site.occurrence_count,
            site.transform_chain,
        ));
    }

    let mut witnesses = String::from(
        "op_index\taudit_path\taudit_line\ttrace_context\tkind\tq_control2\tq_control1\tq_target\tc_condition\tfact_control2\tfact_control1\tfact_target\teffective_condition\taction\trule\tscore_eligible\tsite_id\temission_ordinal\tinverse_depth\tflags\ttransform_chain\n",
    );
    for witness in &report.witnesses {
        let decision = witness.decision;
        let site = report
            .validated_sites
            .get(decision.origin.site_id as usize)
            .ok_or_else(|| {
                format!(
                    "witness site_id {} is out of range",
                    decision.origin.site_id
                )
            })?;
        witnesses.push_str(&format!(
            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n",
            decision.op_index,
            site.audit_path,
            site.audit_line,
            site.trace_context,
            GateKind::from_operation(decision.kind)?.as_str(),
            decision.q_control2.0,
            decision.q_control1.0,
            decision.q_target.0,
            decision.c_condition.0,
            abstract_value_name(decision.facts[0]),
            abstract_value_name(decision.facts[1]),
            abstract_value_name(decision.facts[2]),
            abstract_value_name(decision.effective_condition),
            audit_action_name(decision.action),
            proof_rule_name(decision.rule),
            u8::from(decision.score_eligible),
            decision.origin.site_id,
            decision.origin.emission_ordinal,
            decision.origin.inverse_depth,
            decision.origin.flags,
            decision.origin.transform_chain(),
        ));
    }

    let action_headers = [
        "keep_count",
        "no_cost_identity_count",
        "drop_count",
        "lower_to_x_count",
        "lower_to_cx_count",
        "lower_to_neg_count",
        "lower_to_z_count",
        "lower_to_cz_count",
    ];
    let rule_headers = [
        "none_count",
        "effective_condition_known0_count",
        "ccx_control_known0_count",
        "ccx_both_controls_known1_count",
        "ccx_one_control_known1_count",
        "ccz_operand_known0_count",
        "ccz_three_operands_known1_count",
        "ccz_two_operands_known1_count",
        "ccz_one_operand_known1_count",
    ];
    let mut families = String::from("audit_path\taudit_line\ttrace_context\tkind\tdecision_count");
    for header in action_headers.into_iter().chain(rule_headers) {
        families.push('\t');
        families.push_str(header);
    }
    families.push_str("\tdisposition\n");
    for family in &report.families {
        families.push_str(&format!(
            "{}\t{}\t{}\t{}\t{}",
            family.key.audit_path,
            family.key.audit_line,
            family.key.trace_context,
            family.key.kind.as_str(),
            family.decision_count,
        ));
        for count in family.action_counts.iter().chain(&family.rule_counts) {
            families.push_str(&format!("\t{count}"));
        }
        families.push_str(&format!("\t{}\n", family.disposition.as_str()));
    }

    let uniform_count = report
        .families
        .iter()
        .filter(|family| family.disposition == FamilyDisposition::UniformProvisional)
        .count();
    let predicate_count = report
        .families
        .iter()
        .filter(|family| family.disposition == FamilyDisposition::ExactPredicateProvisional)
        .count();
    let keep_count = report
        .core
        .decisions
        .iter()
        .filter(|decision| decision.action == AuditAction::Keep)
        .count();
    let summary = format!(
        "diagnostic_family_count={}\nexact_predicate_provisional_family_count={}\nkeep_decision_count={}\nnon_keep_decision_count={}\nuniform_provisional_family_count={}\n",
        report.diagnostic_family_count(),
        predicate_count,
        keep_count,
        report.witnesses.len(),
        uniform_count,
    );

    let mut diagnostics = String::new();
    for family in report
        .families
        .iter()
        .filter(|family| family.disposition == FamilyDisposition::DiagnosticMixed)
    {
        diagnostics.push_str(&format!(
            "mixed_family\t{}\t{}\t{}\t{}\n",
            family.key.audit_path,
            family.key.audit_line,
            family.key.trace_context,
            family.key.kind.as_str(),
        ));
    }

    Ok(BTreeMap::from([
        ("manifest.raw", manifest.into_bytes()),
        ("sites.tsv", sites.into_bytes()),
        ("witnesses.tsv", witnesses.into_bytes()),
        ("families.tsv", families.into_bytes()),
        ("summary.raw", summary.into_bytes()),
        ("audit-diagnostics.log", diagnostics.into_bytes()),
    ]))
}

fn write_raw_artifacts_atomically(
    working_directory: &Path,
    artifacts: &BTreeMap<&'static str, Vec<u8>>,
) -> Result<(), String> {
    const EXPECTED_FILES: [&str; 6] = [
        "audit-diagnostics.log",
        "families.tsv",
        "manifest.raw",
        "sites.tsv",
        "summary.raw",
        "witnesses.tsv",
    ];
    let actual_files = artifacts.keys().copied().collect::<Vec<_>>();
    if actual_files != EXPECTED_FILES {
        return Err(format!(
            "raw artifact set mismatch: found {actual_files:?}, expected {EXPECTED_FILES:?}"
        ));
    }

    let final_directory = working_directory.join("j3-dead-gate-audit-raw");
    let temporary_directory = working_directory.join(".j3-dead-gate-audit-raw.tmp");
    if final_directory.exists() {
        return Err("raw artifact destination already exists".to_owned());
    }
    if temporary_directory.exists() {
        return Err("raw artifact temporary directory already exists".to_owned());
    }
    std::fs::create_dir(&temporary_directory).map_err(|error| {
        format!(
            "cannot create raw artifact temporary directory {}: {error}",
            temporary_directory.display()
        )
    })?;

    let write_result = (|| {
        for (name, contents) in artifacts {
            std::fs::write(temporary_directory.join(name), contents)
                .map_err(|error| format!("cannot write raw artifact {name}: {error}"))?;
        }
        std::fs::rename(&temporary_directory, &final_directory).map_err(|error| {
            format!(
                "cannot atomically publish raw artifact directory {}: {error}",
                final_directory.display()
            )
        })?;
        Ok(())
    })();
    if let Err(error) = write_result {
        match std::fs::remove_dir_all(&temporary_directory) {
            Ok(()) => Err(error),
            Err(cleanup_error) => Err(format!(
                "{error}; cannot remove partial raw artifact directory: {cleanup_error}"
            )),
        }
    } else {
        Ok(())
    }
}

fn audit_and_write_with_width(
    stream: &TracedOps,
    working_directory: &Path,
    expected_width: usize,
    predicates: &[ExactSourcePredicate],
) -> Result<AuditReport, String> {
    let report = audit_report_with_width(stream, expected_width, predicates)?;
    let artifacts = render_raw_artifacts(&report)?;
    write_raw_artifacts_atomically(working_directory, &artifacts)?;
    Ok(report)
}

pub(crate) fn audit_and_write(
    stream: &TracedOps,
    working_directory: &Path,
) -> Result<AuditReport, String> {
    audit_and_write_with_width(stream, working_directory, 256, PRODUCTION_EXACT_PREDICATES)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::circuit::{BitId, Op, OperationType, QubitId, RegisterId};

    fn push_at(
        stream: &mut TracedOps,
        op: Op,
        file: &'static str,
        line: u32,
        trace_context: u32,
        inverse_depth: u16,
        flags: u16,
    ) {
        stream.push_at(op, file, line, trace_context, inverse_depth, flags);
    }

    fn reduced_audit_stream(width: usize, family_path: &'static str) -> TracedOps {
        let mut stream = TracedOps::new(true);
        for register in 0u64..4 {
            for offset in 0..width as u64 {
                let mut append = Op::empty();
                append.kind = OperationType::AppendToRegister;
                append.r_target = RegisterId(register);
                if register < 2 {
                    append.q_target = QubitId(register * width as u64 + offset);
                } else {
                    append.c_target = BitId((register - 2) * width as u64 + offset);
                }
                push_at(
                    &mut stream,
                    append,
                    "src/point_add/report_fixture.rs",
                    10 + register as u32,
                    0,
                    0,
                    0,
                );
            }
            let mut declaration = Op::empty();
            declaration.kind = OperationType::Register;
            declaration.r_target = RegisterId(register);
            push_at(
                &mut stream,
                declaration,
                "src/point_add/report_fixture.rs",
                20 + register as u32,
                0,
                0,
                0,
            );
        }

        let auxiliary = (2 * width) as u64;
        let mut keep = op3(OperationType::CCX);
        keep.q_target = QubitId(auxiliary);
        push_at(&mut stream, keep, family_path, 90, 7, 0, 0);

        let mut drop = op3(OperationType::CCX);
        drop.q_control2 = QubitId(auxiliary + 1);
        drop.q_target = QubitId(auxiliary + 2);
        push_at(
            &mut stream,
            drop,
            family_path,
            90,
            7,
            0,
            crate::point_add::ORIGIN_SYNTHETIC_TAIL,
        );

        let mut ccz = op3(OperationType::CCZ);
        ccz.q_control2 = QubitId(auxiliary + 1);
        ccz.q_target = QubitId(auxiliary + 3);
        push_at(&mut stream, ccz, "src/point_add/a.rs", 4, 2, 0, 0);
        stream
    }

    #[test]
    fn report_census_is_total_sorted_normalized_and_has_exact_witness_operands() {
        let stream = reduced_audit_stream(2, "src/bin/../point_add/report_fixture.rs");
        let report = audit_report_with_width(&stream, 2, &[]).expect("reduced report");

        assert_eq!(report.core.decisions.len(), 3);
        assert_eq!(
            report
                .families
                .iter()
                .map(|family| family.decision_count)
                .sum::<u64>(),
            3
        );
        assert_eq!(report.families.len(), 2);
        assert!(report
            .families
            .windows(2)
            .all(|pair| pair[0].key < pair[1].key));
        assert_eq!(report.families[0].key.audit_path, "src/point_add/a.rs");
        assert_eq!(
            report.families[1].key.audit_path,
            "src/point_add/report_fixture.rs"
        );
        assert_eq!(report.families[1].decision_count, 2);
        assert_eq!(
            report.families[1].action_counts[AuditAction::Keep as usize],
            1
        );
        assert_eq!(
            report.families[1].action_counts[AuditAction::Drop as usize],
            1
        );

        assert_eq!(report.witnesses.len(), 2);
        assert!(report
            .witnesses
            .windows(2)
            .all(|pair| pair[0].decision.op_index < pair[1].decision.op_index));
        let ccx_witness = &report.witnesses[0].decision;
        assert_eq!(ccx_witness.q_control2, QubitId(5));
        assert_eq!(ccx_witness.q_control1, QubitId(1));
        assert_eq!(ccx_witness.q_target, QubitId(6));
        assert_eq!(ccx_witness.c_condition, crate::circuit::NO_BIT);

        assert_eq!(
            report
                .sites
                .iter()
                .map(|site| site.occurrence_count)
                .sum::<u64>(),
            stream.len() as u64
        );
    }

    #[test]
    fn report_mixed_family_is_diagnostic_without_an_exact_predicate() {
        let stream = reduced_audit_stream(2, "src/point_add/report_fixture.rs");
        let report = audit_report_with_width(&stream, 2, &[]).expect("reduced report");
        let mixed = report
            .families
            .iter()
            .find(|family| family.key.trace_context == 7)
            .expect("mixed family");
        assert_eq!(mixed.disposition, FamilyDisposition::DiagnosticMixed);
        assert_eq!(report.diagnostic_family_count(), 1);
    }

    #[test]
    fn report_exact_predicate_must_select_all_and_only_non_keep_occurrences() {
        let stream = reduced_audit_stream(2, "src/point_add/report_fixture.rs");
        let exact = ExactSourcePredicate {
            trace_context: 7,
            inverse_depth: 0,
            flags: crate::point_add::ORIGIN_SYNTHETIC_TAIL,
        };
        let report = audit_report_with_width(&stream, 2, &[exact]).expect("predicate report");
        let mixed = report
            .families
            .iter()
            .find(|family| family.key.trace_context == 7)
            .expect("mixed family");
        assert_eq!(
            mixed.disposition,
            FamilyDisposition::ExactPredicateProvisional
        );

        for wrong in [
            ExactSourcePredicate { flags: 0, ..exact },
            ExactSourcePredicate {
                inverse_depth: 1,
                flags: crate::point_add::ORIGIN_EMIT_INVERSE,
                ..exact
            },
            ExactSourcePredicate {
                trace_context: 8,
                ..exact
            },
        ] {
            let report =
                audit_report_with_width(&stream, 2, &[wrong]).expect("wrong predicate report");
            let mixed = report
                .families
                .iter()
                .find(|family| family.key.trace_context == 7)
                .expect("mixed family");
            assert_eq!(mixed.disposition, FamilyDisposition::DiagnosticMixed);
        }
    }

    #[test]
    fn report_rejects_unsafe_or_non_audit_source_metadata() {
        for bad_path in [
            "",
            "src/point_add/bad\tpath.rs",
            "src/point_add/bad\npath.rs",
            "src/point_add/bad\rpath.rs",
            "/src/point_add/absolute.rs",
            "src/elsewhere/outside.rs",
            "src/point_add/../elsewhere/outside.rs",
            "../../src/point_add/traversal.rs",
        ] {
            let stream = reduced_audit_stream(2, bad_path);
            assert!(
                audit_report_with_width(&stream, 2, &[]).is_err(),
                "accepted {bad_path:?}"
            );
        }

        let mut zero_line = TracedOps::new(true);
        push_at(
            &mut zero_line,
            Op::empty(),
            "src/point_add/zero.rs",
            0,
            0,
            0,
            0,
        );
        assert!(validate_origin_metadata(zero_line.origins()[0], zero_line.sites()).is_err());

        assert!(validate_origin_metadata(
            OriginRef {
                site_id: 1,
                emission_ordinal: 0,
                inverse_depth: 0,
                flags: 0,
            },
            zero_line.sites(),
        )
        .is_err());
        for (inverse_depth, flags) in [(1, 0), (0, crate::point_add::ORIGIN_EMIT_INVERSE)] {
            assert!(validate_origin_metadata(
                OriginRef {
                    site_id: 0,
                    emission_ordinal: 0,
                    inverse_depth,
                    flags,
                },
                &[SourceSite {
                    file: "src/point_add/valid.rs",
                    line: 1,
                    trace_context: 0,
                }],
            )
            .is_err());
        }
        assert!(validate_origin_metadata(
            OriginRef {
                site_id: 0,
                emission_ordinal: 0,
                inverse_depth: 0,
                flags: 8,
            },
            zero_line.sites(),
        )
        .is_err());
    }

    #[test]
    fn report_render_is_byte_identical_has_six_files_and_strict_manifest() {
        let stream = reduced_audit_stream(2, "src/point_add/report_fixture.rs");
        let report = audit_report_with_width(&stream, 2, &[]).expect("reduced report");
        let first = render_raw_artifacts(&report).expect("first render");
        let second = render_raw_artifacts(&report).expect("second render");
        assert_eq!(first, second);
        assert_eq!(
            first.keys().copied().collect::<Vec<_>>(),
            vec![
                "audit-diagnostics.log",
                "families.tsv",
                "manifest.raw",
                "sites.tsv",
                "summary.raw",
                "witnesses.tsv",
            ]
        );
        assert!(first["audit-diagnostics.log"].starts_with(b"mixed_family\t"));
        for (name, bytes) in &first {
            if *name != "audit-diagnostics.log" || !bytes.is_empty() {
                assert_eq!(bytes.last(), Some(&b'\n'), "{name}");
                assert!(!bytes.ends_with(b"\n\n"), "{name}");
            }
        }

        let manifest = std::str::from_utf8(&first["manifest.raw"]).unwrap();
        let parsed = parse_raw_manifest(manifest).expect("strict manifest");
        assert_eq!(parsed.format, "j3-dead-gate-raw-v1");
        assert_eq!(parsed.decision_count, 3);
        for invalid in [
            manifest.replacen("ccx_count=2\n", "ccx_count=2\nccx_count=2\n", 1),
            manifest.replacen("ccx_count=2\n", "", 1),
            format!("{manifest}unexpected=1\n"),
            manifest.replacen(
                "ccx_count=2\nccz_count=1\n",
                "ccz_count=1\nccx_count=2\n",
                1,
            ),
        ] {
            assert!(
                parse_raw_manifest(&invalid).is_err(),
                "accepted {invalid:?}"
            );
        }
    }

    #[test]
    fn hash_preimages_match_records_only_trusted_domain_and_expanded_provenance_vectors() {
        let mut ccx = Op::empty();
        ccx.kind = OperationType::CCX;
        ccx.q_control2 = QubitId(1);
        ccx.q_control1 = QubitId(2);
        ccx.q_target = QubitId(3);
        ccx.c_condition = BitId(4);
        let mut x = Op::empty();
        x.kind = OperationType::X;
        x.q_target = QubitId(9);
        let ops = [ccx, x];

        let (canonical, trusted_xof32) = canonical_stream_hashes(&ops);
        assert_eq!(
            lowercase_hex(&canonical),
            "c666d7c3113eadc13fd7ad52a41e251b5672f96b4562ff715d264ab30fcec1b9"
        );
        assert_eq!(
            lowercase_hex(&trusted_xof32),
            "233d72eda73e6f2ffb0b4521111437782d435fa8466830a547f72c7e48d4840e"
        );

        let sites = [
            SourceSite {
                file: "src/point_add/hash.rs",
                line: 11,
                trace_context: 12,
            },
            SourceSite {
                file: "src/point_add/inverse.rs",
                line: 22,
                trace_context: 23,
            },
        ];
        let origins = [
            OriginRef {
                site_id: 0,
                emission_ordinal: 2,
                inverse_depth: 0,
                flags: crate::point_add::ORIGIN_SYNTHETIC_TAIL,
            },
            OriginRef {
                site_id: 1,
                emission_ordinal: 1,
                inverse_depth: 2,
                flags: crate::point_add::ORIGIN_EMIT_INVERSE
                    | crate::point_add::ORIGIN_TAIL_NONCE_REWRITTEN,
            },
        ];
        let (hashes, _) = hash_stream(&ops, &origins, &sites).expect("fixed provenance");
        assert_eq!(hashes.canonical_records_sha256, canonical);
        assert_eq!(hashes.trusted_xof32, trusted_xof32);
        assert_eq!(
            lowercase_hex(&hashes.provenance_sha256),
            "0de60925527445b35e940ea1549b1bd21104bcd0446b4364e4690997ece1b9c1"
        );
    }

    #[test]
    fn hash_provenance_normalizes_paths_and_covers_every_valid_flag_combination() {
        let ops = vec![Op::empty(); 9];
        let sites_a = [SourceSite {
            file: "src/bin/../point_add/hash_flags.rs",
            line: 7,
            trace_context: 8,
        }];
        let sites_b = [SourceSite {
            file: "src/point_add/hash_flags.rs",
            line: 7,
            trace_context: 8,
        }];
        let origins = [
            (0, 0),
            (0, crate::point_add::ORIGIN_SYNTHETIC_TAIL),
            (0, crate::point_add::ORIGIN_TAIL_NONCE_REWRITTEN),
            (
                0,
                crate::point_add::ORIGIN_SYNTHETIC_TAIL
                    | crate::point_add::ORIGIN_TAIL_NONCE_REWRITTEN,
            ),
            (1, crate::point_add::ORIGIN_EMIT_INVERSE),
            (
                1,
                crate::point_add::ORIGIN_EMIT_INVERSE | crate::point_add::ORIGIN_SYNTHETIC_TAIL,
            ),
            (
                1,
                crate::point_add::ORIGIN_EMIT_INVERSE
                    | crate::point_add::ORIGIN_TAIL_NONCE_REWRITTEN,
            ),
            (
                1,
                crate::point_add::ORIGIN_EMIT_INVERSE
                    | crate::point_add::ORIGIN_SYNTHETIC_TAIL
                    | crate::point_add::ORIGIN_TAIL_NONCE_REWRITTEN,
            ),
            (
                3,
                crate::point_add::ORIGIN_EMIT_INVERSE
                    | crate::point_add::ORIGIN_SYNTHETIC_TAIL
                    | crate::point_add::ORIGIN_TAIL_NONCE_REWRITTEN,
            ),
        ]
        .into_iter()
        .enumerate()
        .map(|(ordinal, (inverse_depth, flags))| OriginRef {
            site_id: 0,
            emission_ordinal: ordinal as u32,
            inverse_depth,
            flags,
        })
        .collect::<Vec<_>>();

        let first = hash_stream(&ops, &origins, &sites_a).expect("all valid flags");
        let second = hash_stream(&ops, &origins, &sites_a).expect("repeat all valid flags");
        let normalized = hash_stream(&ops, &origins, &sites_b).expect("normalized path");
        assert_eq!(first.0, second.0);
        assert_eq!(first.0.provenance_sha256, normalized.0.provenance_sha256);
    }

    struct TestDirectory(std::path::PathBuf);

    impl TestDirectory {
        fn new(label: &str) -> Self {
            use std::sync::atomic::{AtomicU64, Ordering};
            static NEXT: AtomicU64 = AtomicU64::new(0);
            let nonce = NEXT.fetch_add(1, Ordering::Relaxed);
            let path = std::env::temp_dir().join(format!(
                "j3-dead-gate-task4-{label}-{}-{nonce}",
                std::process::id()
            ));
            std::fs::create_dir(&path).expect("create test directory");
            Self(path)
        }
    }

    impl Drop for TestDirectory {
        fn drop(&mut self) {
            let _ = std::fs::remove_dir_all(&self.0);
        }
    }

    #[test]
    fn raw_writer_atomically_creates_exactly_six_deterministic_files() {
        let root = TestDirectory::new("success");
        let stream = reduced_audit_stream(2, "src/point_add/report_fixture.rs");
        let predicate = ExactSourcePredicate {
            trace_context: 7,
            inverse_depth: 0,
            flags: crate::point_add::ORIGIN_SYNTHETIC_TAIL,
        };
        let report = audit_and_write_with_width(&stream, &root.0, 2, &[predicate])
            .expect("atomic raw write");
        let expected = render_raw_artifacts(&report).expect("expected artifacts");
        let output = root.0.join("j3-dead-gate-audit-raw");
        let mut actual_names = std::fs::read_dir(&output)
            .expect("raw directory")
            .map(|entry| entry.unwrap().file_name().into_string().unwrap())
            .collect::<Vec<_>>();
        actual_names.sort();
        assert_eq!(
            actual_names,
            expected
                .keys()
                .map(|name| (*name).to_owned())
                .collect::<Vec<_>>()
        );
        for (name, bytes) in expected {
            assert_eq!(std::fs::read(output.join(name)).unwrap(), bytes, "{name}");
        }
        assert_eq!(
            std::fs::read(output.join("audit-diagnostics.log")).unwrap(),
            b""
        );
        assert!(!root.0.join(".j3-dead-gate-audit-raw.tmp").exists());

        let _: fn(&TracedOps, &Path) -> Result<AuditReport, String> = audit_and_write;
    }

    #[test]
    fn raw_writer_leaves_no_partial_directory_when_a_prerequisite_fails() {
        let root = TestDirectory::new("failure");
        let stream = reduced_audit_stream(2, "src/point_add/bad\tpath.rs");
        let error = audit_and_write_with_width(&stream, &root.0, 2, &[]).unwrap_err();
        assert!(error.contains("path"), "{error}");
        assert!(!root.0.join("j3-dead-gate-audit-raw").exists());
        assert!(!root.0.join(".j3-dead-gate-audit-raw.tmp").exists());
    }

    fn reduced_full_path_stream(width: usize, enabled: bool) -> TracedOps {
        let mut stream = TracedOps::new(enabled);
        for register in 0u64..4 {
            for offset in 0..width as u64 {
                let mut append = Op::empty();
                append.kind = OperationType::AppendToRegister;
                append.r_target = RegisterId(register);
                if register < 2 {
                    append.q_target = QubitId(register * width as u64 + offset);
                } else {
                    append.c_target = BitId((register - 2) * width as u64 + offset);
                }
                push_at(
                    &mut stream,
                    append,
                    "src/point_add/full_path.rs",
                    10 + register as u32,
                    register as u32,
                    0,
                    0,
                );
            }
            let mut declaration = Op::empty();
            declaration.kind = OperationType::Register;
            declaration.r_target = RegisterId(register);
            push_at(
                &mut stream,
                declaration,
                "src/point_add/full_path.rs",
                20 + register as u32,
                register as u32,
                0,
                0,
            );
        }

        let auxiliary_q = (2 * width) as u64;
        let auxiliary_b = (2 * width) as u64;
        for (op, line) in [(push_condition(0), 30), (push_condition(1), 31)] {
            push_at(&mut stream, op, "src/point_add/full_path.rs", line, 5, 0, 0);
        }
        push_at(
            &mut stream,
            x(auxiliary_q),
            "src/point_add/inverse_block.rs",
            40,
            6,
            2,
            crate::point_add::ORIGIN_EMIT_INVERSE,
        );
        for (op, line) in [(pop_condition(), 41), (pop_condition(), 42)] {
            push_at(&mut stream, op, "src/point_add/full_path.rs", line, 5, 0, 0);
        }

        let mut reset = Op::empty();
        reset.kind = OperationType::R;
        reset.q_target = QubitId(auxiliary_q + 1);
        push_at(
            &mut stream,
            reset,
            "src/point_add/full_path.rs",
            50,
            0,
            0,
            0,
        );
        let mut hmr = Op::empty();
        hmr.kind = OperationType::Hmr;
        hmr.q_target = QubitId(auxiliary_q + 2);
        hmr.c_target = BitId(auxiliary_b);
        push_at(&mut stream, hmr, "src/point_add/full_path.rs", 51, 0, 0, 0);

        push_at(
            &mut stream,
            x(auxiliary_q + 3),
            "src/point_add/nonce_tail.rs",
            60,
            9,
            0,
            crate::point_add::ORIGIN_SYNTHETIC_TAIL | crate::point_add::ORIGIN_TAIL_NONCE_REWRITTEN,
        );
        for (offset, kind) in [OperationType::CCX, OperationType::CCZ]
            .into_iter()
            .enumerate()
        {
            let mut gate = op3(kind);
            gate.q_control2 = QubitId(auxiliary_q + 4);
            gate.q_target = QubitId(auxiliary_q + 5 + offset as u64);
            push_at(
                &mut stream,
                gate,
                "src/point_add/nonce_tail.rs",
                61 + offset as u32,
                9,
                0,
                crate::point_add::ORIGIN_SYNTHETIC_TAIL
                    | crate::point_add::ORIGIN_TAIL_NONCE_REWRITTEN,
            );
        }
        stream
    }

    #[test]
    fn reduced_full_path_widths_two_and_three_are_total_sound_repeatable_and_audit_identity() {
        for width in [2usize, 3] {
            let audited = reduced_full_path_stream(width, true);
            let plain = reduced_full_path_stream(width, false);
            assert_eq!(
                audited.to_vec(),
                plain.to_vec(),
                "width {width} op identity"
            );
            assert_eq!(audited.origins().len(), audited.len());
            assert!(plain.origins().is_empty());
            assert_eq!(
                canonical_stream_hashes(&audited),
                canonical_stream_hashes(&plain),
                "width {width} canonical digest identity"
            );

            let first = audit_report_with_width(&audited, width, &[]).expect("first full path");
            let second = audit_report_with_width(&audited, width, &[]).expect("repeat full path");
            assert_eq!(first.hashes, second.hashes, "width {width} repeat hashes");
            assert!(first
                .families
                .iter()
                .all(|family| family.disposition == FamilyDisposition::UniformProvisional));
            assert!(render_raw_artifacts(&first).unwrap()["audit-diagnostics.log"].is_empty());
            assert_eq!(first.provenance_count, audited.len() as u64);
            assert_eq!(first.core.xof_words_consumed, 2);
            assert_eq!(first.core.decisions.len(), 2);
            assert!(first
                .core
                .decisions
                .iter()
                .all(|decision| decision.action == AuditAction::Drop));

            let unknown_count = 4 * width;
            for assignment in 0..(1usize << unknown_count) {
                for measurement_pattern in 0..4usize {
                    let words = [
                        (measurement_pattern & 1) as u64,
                        ((measurement_pattern >> 1) & 1) as u64,
                    ];
                    let mut xof = FiniteXof::from_words(&words);
                    let mut simulator = crate::sim::Simulator::new(
                        first.core.final_qubits.len(),
                        first.core.final_bits.len(),
                        &mut xof,
                    );
                    for id in 0..(2 * width) {
                        simulator.qubits[id] = ((assignment >> id) & 1) as u64;
                        simulator.bits[id] = ((assignment >> (2 * width + id)) & 1) as u64;
                    }
                    simulator.apply_iter(audited.iter());
                    assert_abstract_snapshot_sound(
                        &format!("full-path-width-{width}"),
                        audited.len(),
                        assignment,
                        measurement_pattern,
                        &first.core.final_qubits,
                        &first.core.final_bits,
                        &simulator.qubits,
                        &simulator.bits,
                    );
                }
            }
        }
    }

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
