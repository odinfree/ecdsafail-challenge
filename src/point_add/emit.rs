use super::*;

pub(crate) fn emit_inverse<F: FnOnce(&mut B)>(b: &mut B, f: F) {
    if b.count_only {
        let snap = b.count_snapshot();
        f(b);
        let delta = b.count_delta_since(snap);
        b.restore_count_snapshot(snap);
        add_inverse_count_delta(b, &delta);
        return;
    }
    let start = b.ops.len();
    f(b);
    let end = b.ops.len();

    if b.ops.enabled() {
        let fwd = b.ops.paired_range(start, end);
        b.ops.truncate(start);
        emit_inverse_pairs_allowing_clean_resets(b, &fwd, "emit_inverse");
    } else {
        let fwd: Vec<_> = b.ops[start..end].to_vec();
        b.ops.truncate(start);
        emit_inverse_ops_allowing_clean_resets(b, &fwd, "emit_inverse");
    }
}

pub(crate) fn add_inverse_count_delta(b: &mut B, delta: &[usize; 18]) {
    for kind in [
        OperationType::X,
        OperationType::Z,
        OperationType::CX,
        OperationType::CZ,
        OperationType::CCX,
        OperationType::CCZ,
        OperationType::Swap,
    ] {
        b.add_counted_kind(kind, delta[kind as usize]);
    }
}

pub(crate) fn emit_inverse_ops_allowing_clean_resets(b: &mut B, fwd: &[Op], context: &'static str) {
    for op in fwd.iter().rev().copied() {
        match op.kind {
            OperationType::X
            | OperationType::Z
            | OperationType::CX
            | OperationType::CZ
            | OperationType::CCX
            | OperationType::CCZ
            | OperationType::Swap => b.push_op(op),

            OperationType::R => {}

            OperationType::Register
            | OperationType::AppendToRegister
            | OperationType::DebugPrint => {}
            _ => panic!(
                "{context}: non-invertible op kind {:?} inside forward block",
                op.kind
            ),
        }
    }
}
fn emit_inverse_pairs_allowing_clean_resets(
    b: &mut B,
    fwd: &[(Op, OriginRef)],
    context: &'static str,
) {
    for &(op, origin) in fwd.iter().rev() {
        match op.kind {
            OperationType::X
            | OperationType::Z
            | OperationType::CX
            | OperationType::CZ
            | OperationType::CCX
            | OperationType::CCZ
            | OperationType::Swap => {
                b.add_counted_kind(op.kind, 1);
                record_op_site((file!(), line!(), current_trace_context()));
                b.ops.push_inherited(op, origin);
            }

            OperationType::R => {}

            OperationType::Register
            | OperationType::AppendToRegister
            | OperationType::DebugPrint => {}
            _ => panic!(
                "{context}: non-invertible op kind {:?} inside forward block",
                op.kind
            ),
        }
    }
}
