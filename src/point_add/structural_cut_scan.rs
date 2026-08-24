//! Exact, fail-closed constant-state scan of the promoted ping-pong stream.
//!
//! The diagnostic (`STRUCTURAL_CUT_SCAN=1 TRACE_OP_SITES=1`) never changes the
//! operation stream. The separately gated materializer
//! (`STRUCTURAL_CUT_APPLY=1`) removes only the exact certified set. Both paths
//! interpret constants over all values admitted by the declared circuit
//! interface; `Unknown` is deliberately not split or fitted to a finite
//! evaluator population.

use crate::circuit::{analyze_ops, Op, OperationType, QubitOrBit, NO_BIT};
use std::collections::BTreeMap;

const EXPECTED_PRE_TAIL_OPS: usize = 12_593_762;
const EXPECTED_HITS: &[(usize, u64, u64, u64)] = &[
    (15_461, 513, 775, 776),
    (15_464, 514, 776, 777),
    (5_836_416, 513, 781, 782),
    (5_836_417, 514, 782, 1055),
    (5_913_066, 582, 710, 773),
    (5_935_732, 582, 512, 773),
    (6_003_685, 709, 731, 1060),
    (6_021_218, 709, 771, 1060),
    (6_089_324, 732, 708, 773),
    (6_121_152, 732, 512, 773),
    (6_281_357, 581, 512, 1112),
    (6_340_361, 581, 1099, 1112),
    (6_515_872, 584, 521, 771),
    (6_533_956, 584, 772, 771),
    (6_602_891, 520, 540, 781),
    (6_618_347, 520, 778, 781),
    (6_688_557, 541, 519, 776),
    (6_715_372, 541, 775, 776),
    (6_758_096, 515, 775, 776),
    (6_758_099, 513, 776, 777),
    (12_571_629, 515, 1055, 784),
    (12_571_630, 513, 784, 785),
];

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Value {
    Zero,
    One,
    Unknown,
}

impl Value {
    fn and(self, rhs: Self) -> Self {
        use Value::{One, Unknown, Zero};
        match (self, rhs) {
            (Zero, _) | (_, Zero) => Zero,
            (One, One) => One,
            _ => Unknown,
        }
    }

    fn xor(self, rhs: Self) -> Self {
        use Value::{One, Unknown, Zero};
        match (self, rhs) {
            (Unknown, _) | (_, Unknown) => Unknown,
            (Zero, value) | (value, Zero) => value,
            (One, One) => Zero,
        }
    }

    fn store_zero_if(self, condition: Self) -> Self {
        use Value::{One, Unknown, Zero};
        match condition {
            Zero => self,
            One => Zero,
            Unknown if self == Zero => Zero,
            Unknown => Unknown,
        }
    }

    fn store_one_if(self, condition: Self) -> Self {
        use Value::{One, Unknown, Zero};
        match condition {
            Zero => self,
            One => One,
            Unknown if self == One => One,
            Unknown => Unknown,
        }
    }
}

#[derive(Clone, Debug)]
struct Hit {
    op_index: usize,
    kind: OperationType,
    q2: u64,
    q1: u64,
    target: u64,
    condition_zero: bool,
    q2_zero: bool,
    q1_zero: bool,
    target_zero: bool,
}

impl Hit {
    fn quantum_zero(&self) -> bool {
        self.q2_zero || self.q1_zero || (self.kind == OperationType::CCZ && self.target_zero)
    }

    fn reason(&self) -> String {
        let mut parts = Vec::new();
        if self.condition_zero {
            parts.push("condition");
        }
        if self.q2_zero {
            parts.push("q2");
        }
        if self.q1_zero {
            parts.push("q1");
        }
        if self.target_zero {
            parts.push("target");
        }
        parts.join("+")
    }
}

fn conditional_swap(a: Value, b: Value, condition: Value) -> (Value, Value) {
    match condition {
        Value::Zero => (a, b),
        Value::One => (b, a),
        Value::Unknown if a == b && a != Value::Unknown => (a, b),
        Value::Unknown => (Value::Unknown, Value::Unknown),
    }
}

fn input_state(ops: &[Op]) -> (Vec<Value>, Vec<Value>) {
    let (num_qubits, num_bits, num_registers, registers) = analyze_ops(ops.iter());
    assert_eq!(
        num_registers, 4,
        "structural scan expects the four-register point-add ABI"
    );
    assert_eq!(registers.len(), 4, "structural scan register table drift");

    let mut qubits = vec![Value::Zero; num_qubits as usize];
    let mut bits = vec![Value::Zero; num_bits as usize];
    for register in registers {
        for wire in register {
            match wire {
                QubitOrBit::Qubit(q) => qubits[q.0 as usize] = Value::Unknown,
                QubitOrBit::Bit(b) => bits[b.0 as usize] = Value::Unknown,
            }
        }
    }
    (qubits, bits)
}

fn interpret(ops: &[Op]) -> Vec<Hit> {
    let (mut qubits, mut bits) = input_state(ops);
    let mut base_condition = Value::One;
    let mut condition_stack = Vec::new();
    let mut hits = Vec::new();

    for (op_index, op) in ops.iter().enumerate() {
        let condition = if op.c_condition == NO_BIT {
            base_condition
        } else {
            base_condition.and(bits[op.c_condition.0 as usize])
        };

        match op.kind {
            OperationType::CCX | OperationType::CCZ => {
                let q2 = qubits[op.q_control2.0 as usize];
                let q1 = qubits[op.q_control1.0 as usize];
                let target = qubits[op.q_target.0 as usize];
                let phase_factor = if op.kind == OperationType::CCZ {
                    target
                } else {
                    Value::One
                };
                if condition.and(q2).and(q1).and(phase_factor) == Value::Zero {
                    hits.push(Hit {
                        op_index,
                        kind: op.kind,
                        q2: op.q_control2.0,
                        q1: op.q_control1.0,
                        target: op.q_target.0,
                        condition_zero: condition == Value::Zero,
                        q2_zero: q2 == Value::Zero,
                        q1_zero: q1 == Value::Zero,
                        target_zero: op.kind == OperationType::CCZ && target == Value::Zero,
                    });
                }
                if op.kind == OperationType::CCX {
                    let delta = condition.and(q2).and(q1);
                    let slot = &mut qubits[op.q_target.0 as usize];
                    *slot = slot.xor(delta);
                }
            }
            OperationType::CX => {
                let delta = condition.and(qubits[op.q_control1.0 as usize]);
                let slot = &mut qubits[op.q_target.0 as usize];
                *slot = slot.xor(delta);
            }
            OperationType::Swap => {
                let a = qubits[op.q_control1.0 as usize];
                let b = qubits[op.q_target.0 as usize];
                let (next_a, next_b) = conditional_swap(a, b, condition);
                qubits[op.q_control1.0 as usize] = next_a;
                qubits[op.q_target.0 as usize] = next_b;
            }
            OperationType::X => {
                let slot = &mut qubits[op.q_target.0 as usize];
                *slot = slot.xor(condition);
            }
            OperationType::Hmr | OperationType::R => {
                let slot = &mut qubits[op.q_target.0 as usize];
                *slot = slot.store_zero_if(condition);
                if op.kind == OperationType::Hmr {
                    let bit = &mut bits[op.c_target.0 as usize];
                    *bit = if condition == Value::Zero {
                        *bit
                    } else {
                        Value::Unknown
                    };
                }
            }
            OperationType::BitInvert => {
                let slot = &mut bits[op.c_target.0 as usize];
                *slot = slot.xor(condition);
            }
            OperationType::BitStore0 => {
                let slot = &mut bits[op.c_target.0 as usize];
                *slot = slot.store_zero_if(condition);
            }
            OperationType::BitStore1 => {
                let slot = &mut bits[op.c_target.0 as usize];
                *slot = slot.store_one_if(condition);
            }
            OperationType::PushCondition => {
                condition_stack.push(base_condition);
                base_condition = base_condition.and(bits[op.c_condition.0 as usize]);
            }
            OperationType::PopCondition => {
                base_condition = condition_stack.pop().expect("unbalanced condition stack");
            }
            OperationType::Neg
            | OperationType::Register
            | OperationType::AppendToRegister
            | OperationType::Z
            | OperationType::CZ
            | OperationType::DebugPrint => {}
        }
    }
    assert!(
        condition_stack.is_empty(),
        "unbalanced condition stack at stream end"
    );
    hits
}

pub(crate) fn scan(ops: &[Op]) {
    assert!(
        super::op_site_trace_enabled(),
        "STRUCTURAL_CUT_SCAN requires TRACE_OP_SITES=1"
    );
    let sites = super::take_last_op_sites();
    assert_eq!(
        sites.len(),
        ops.len(),
        "operation/source trace length drift"
    );
    let hits = interpret(ops);

    let q775 = hits.iter().any(|hit| {
        hit.op_index == 15_461
            && hit.kind == OperationType::CCX
            && hit.q2 == 513
            && hit.q1 == 775
            && hit.target == 776
            && hit.q1_zero
    });
    assert!(
        q775,
        "exact scanner failed to reproduce the frozen q775 witness"
    );

    type Key = (u8, &'static str, u32, u32, String, bool);
    let mut groups: BTreeMap<Key, (usize, Vec<usize>)> = BTreeMap::new();
    for hit in &hits {
        let (file, line, context) = sites[hit.op_index];
        let key = (
            hit.kind as u8,
            file,
            line,
            context,
            hit.reason(),
            hit.quantum_zero(),
        );
        let group = groups.entry(key).or_insert((0, Vec::new()));
        group.0 += 1;
        if group.1.len() < 8 {
            group.1.push(hit.op_index);
        }
    }

    let quantum_hits = hits.iter().filter(|hit| hit.quantum_zero()).count();
    let condition_only = hits.len() - quantum_hits;
    eprintln!(
        "STRUCTURAL_CUT_SCAN_PASS ops={} nonlinear_identities={} quantum_zero={} condition_only={} groups={} q775=true",
        ops.len(),
        hits.len(),
        quantum_hits,
        condition_only,
        groups.len(),
    );

    for hit in &hits {
        let (file, line, context) = sites[hit.op_index];
        eprintln!(
            "STRUCTURAL_CUT_HIT op={} kind={:?} q2={} q1={} target={} quantum_zero={} reason={} site={file}:{line} context={context:#010x}",
            hit.op_index,
            hit.kind,
            hit.q2,
            hit.q1,
            hit.target,
            hit.quantum_zero(),
            hit.reason(),
        );
    }

    let show = std::env::var("STRUCTURAL_CUT_SCAN_SHOW")
        .ok()
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or(100);
    let mut rows: Vec<_> = groups.into_iter().collect();
    rows.sort_by(|a, b| b.1 .0.cmp(&a.1 .0).then_with(|| a.0.cmp(&b.0)));
    for ((kind, file, line, context, reason, quantum_zero), (count, sample_ops)) in
        rows.into_iter().take(show)
    {
        eprintln!(
            "STRUCTURAL_CUT_GROUP count={count} kind={kind} quantum_zero={quantum_zero} reason={reason} site={file}:{line} context={context:#010x} sample_ops={sample_ops:?}"
        );
    }
}

/// Materialize exactly the independently certified promoted-stream cut.
///
/// The proof is recomputed over the complete pre-tail stream. Every expected
/// hit and operand tuple must match and there may be no extra hit; any source,
/// ABI, schedule, or operation-order drift therefore fails closed.
pub(crate) fn apply(mut ops: Vec<Op>) -> Vec<Op> {
    assert_eq!(
        ops.len(),
        EXPECTED_PRE_TAIL_OPS,
        "structural-cut source stream drift"
    );
    let hits = interpret(&ops);
    let actual: Vec<_> = hits
        .iter()
        .map(|hit| {
            assert_eq!(
                hit.kind,
                OperationType::CCX,
                "unexpected nonlinear cut kind"
            );
            (hit.op_index, hit.q2, hit.q1, hit.target)
        })
        .collect();
    assert_eq!(actual, EXPECTED_HITS, "structural-cut proof set drift");

    for &(index, q2, q1, target) in EXPECTED_HITS.iter().rev() {
        let op = ops[index];
        assert_eq!(op.kind, OperationType::CCX);
        assert_eq!(
            (op.q_control2.0, op.q_control1.0, op.q_target.0),
            (q2, q1, target)
        );
        ops.remove(index);
    }
    assert_eq!(ops.len(), EXPECTED_PRE_TAIL_OPS - EXPECTED_HITS.len());
    ops
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn lattice_is_fail_closed() {
        assert_eq!(Value::Zero.and(Value::Unknown), Value::Zero);
        assert_eq!(Value::One.and(Value::Unknown), Value::Unknown);
        assert_eq!(Value::One.xor(Value::One), Value::Zero);
        assert_eq!(Value::Unknown.xor(Value::Unknown), Value::Unknown);
    }

    #[test]
    fn unknown_conditional_store_preserves_matching_constant() {
        assert_eq!(Value::Zero.store_zero_if(Value::Unknown), Value::Zero);
        assert_eq!(Value::One.store_one_if(Value::Unknown), Value::One);
        assert_eq!(Value::One.store_zero_if(Value::Unknown), Value::Unknown);
        assert_eq!(Value::Zero.store_one_if(Value::Unknown), Value::Unknown);
    }

    #[test]
    fn unknown_conditional_swap_only_preserves_proved_equal_constants() {
        assert_eq!(
            conditional_swap(Value::Zero, Value::Zero, Value::Unknown),
            (Value::Zero, Value::Zero)
        );
        assert_eq!(
            conditional_swap(Value::Unknown, Value::Unknown, Value::Unknown),
            (Value::Unknown, Value::Unknown)
        );
    }
}
