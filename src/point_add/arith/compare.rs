use super::*;

pub(crate) fn cmp_lt_into_fast(b: &mut B, u: &[QubitId], v: &[QubitId], flag: QubitId) {

    if kal_vent_modadd_enabled() {
        cmp_lt_into(b, u, v, flag);
        return;
    }
    let n = u.len();
    assert_eq!(n, v.len());
    let c_in = b.alloc_qubit();
    let carries = b.alloc_qubits(n);
    for i in 0..n {
        b.x(u[i]);
    }

    b.cx(u[0], v[0]);
    b.cx(u[0], c_in);
    b.ccx(c_in, v[0], carries[0]);
    b.cx(carries[0], u[0]);
    for i in 1..n {
        b.cx(u[i], v[i]);
        b.cx(u[i], u[i - 1]);
        b.ccx(u[i - 1], v[i], carries[i]);
        b.cx(carries[i], u[i]);
    }

    b.cx(u[n - 1], flag);

    for i in (1..n).rev() {
        b.cx(carries[i], u[i]);
        let m = b.alloc_bit();
        b.hmr(carries[i], m);
        b.cz_if(u[i - 1], v[i], m);
        b.cx(u[i], u[i - 1]);
        b.cx(u[i], v[i]);
    }
    b.cx(carries[0], u[0]);
    let m0 = b.alloc_bit();
    b.hmr(carries[0], m0);
    b.cz_if(c_in, v[0], m0);
    b.cx(u[0], c_in);
    b.cx(u[0], v[0]);

    for i in 0..n {
        b.x(u[i]);
    }
    b.free_vec(&carries);
    b.free(c_in);
}

pub(crate) fn cmp_lt_into_fast_with_cin(
    b: &mut B,
    u: &[QubitId],
    v: &[QubitId],
    c_in: QubitId,
    flag: QubitId,
) {
    let n = u.len();
    assert_eq!(n, v.len());
    assert!(!u.contains(&c_in));
    assert!(!v.contains(&c_in));
    assert_ne!(c_in, flag);
    assert!(!u.contains(&flag));
    assert!(!v.contains(&flag));
    let carries = b.alloc_qubits(n);
    for i in 0..n {
        b.x(u[i]);
    }

    b.cx(u[0], v[0]);
    b.cx(u[0], c_in);
    b.ccx(c_in, v[0], carries[0]);
    b.cx(carries[0], u[0]);
    for i in 1..n {
        b.cx(u[i], v[i]);
        b.cx(u[i], u[i - 1]);
        b.ccx(u[i - 1], v[i], carries[i]);
        b.cx(carries[i], u[i]);
    }

    b.cx(u[n - 1], flag);

    for i in (1..n).rev() {
        b.cx(carries[i], u[i]);
        let m = b.alloc_bit();
        b.hmr(carries[i], m);
        b.cz_if(u[i - 1], v[i], m);
        b.cx(u[i], u[i - 1]);
        b.cx(u[i], v[i]);
    }
    b.cx(carries[0], u[0]);
    let m0 = b.alloc_bit();
    b.hmr(carries[0], m0);
    b.cz_if(c_in, v[0], m0);
    b.cx(u[0], c_in);
    b.cx(u[0], v[0]);

    for i in 0..n {
        b.x(u[i]);
    }
    b.free_vec(&carries);
}

pub(crate) fn cmp_lt_into_fast_with_cin_borrowed_carries(
    b: &mut B,
    u: &[QubitId],
    v: &[QubitId],
    c_in: QubitId,
    flag: QubitId,
    carries: &[QubitId],
) {
    let n = u.len();
    assert_eq!(n, v.len());
    assert!(carries.len() >= n);
    for i in 0..n {
        b.x(u[i]);
    }
    b.cx(u[0], v[0]);
    b.cx(u[0], c_in);
    b.ccx(c_in, v[0], carries[0]);
    b.cx(carries[0], u[0]);
    for i in 1..n {
        b.cx(u[i], v[i]);
        b.cx(u[i], u[i - 1]);
        b.ccx(u[i - 1], v[i], carries[i]);
        b.cx(carries[i], u[i]);
    }
    b.cx(u[n - 1], flag);
    for i in (1..n).rev() {
        b.cx(carries[i], u[i]);
        let m = b.alloc_bit();
        b.hmr(carries[i], m);
        b.cz_if(u[i - 1], v[i], m);
        b.cx(u[i], u[i - 1]);
        b.cx(u[i], v[i]);
    }
    b.cx(carries[0], u[0]);
    let m0 = b.alloc_bit();
    b.hmr(carries[0], m0);
    b.cz_if(c_in, v[0], m0);
    b.cx(u[0], c_in);
    b.cx(u[0], v[0]);
    for i in 0..n {
        b.x(u[i]);
    }
}

pub(crate) fn ccx_cmp_lt_into_fast(b: &mut B, u: &[QubitId], v: &[QubitId], ctrl: QubitId, target: QubitId) {
    if kal_vent_modadd_enabled() {
        let flag = b.alloc_qubit();
        cmp_lt_into(b, u, v, flag);
        b.ccx(ctrl, flag, target);
        cmp_lt_into(b, u, v, flag);
        b.free(flag);
        return;
    }

    let n = u.len();
    assert_eq!(n, v.len());
    let c_in = b.alloc_qubit();
    let carries = b.alloc_qubits(n);
    for i in 0..n {
        b.x(u[i]);
    }

    b.cx(u[0], v[0]);
    b.cx(u[0], c_in);
    b.ccx(c_in, v[0], carries[0]);
    b.cx(carries[0], u[0]);
    for i in 1..n {
        b.cx(u[i], v[i]);
        b.cx(u[i], u[i - 1]);
        b.ccx(u[i - 1], v[i], carries[i]);
        b.cx(carries[i], u[i]);
    }

    b.ccx(ctrl, u[n - 1], target);

    for i in (1..n).rev() {
        b.cx(carries[i], u[i]);
        let m = b.alloc_bit();
        b.hmr(carries[i], m);
        b.cz_if(u[i - 1], v[i], m);
        b.cx(u[i], u[i - 1]);
        b.cx(u[i], v[i]);
    }
    b.cx(carries[0], u[0]);
    let m0 = b.alloc_bit();
    b.hmr(carries[0], m0);
    b.cz_if(c_in, v[0], m0);
    b.cx(u[0], c_in);
    b.cx(u[0], v[0]);

    for i in 0..n {
        b.x(u[i]);
    }
    b.free_vec(&carries);
    b.free(c_in);
}

pub(crate) fn ccx_cmp_lt_into_fast_prefix_targets(
    b: &mut B,
    u: &[QubitId],
    v: &[QubitId],
    ctrl: QubitId,
    targets: &[(QubitId, usize)],
) {
    if targets.is_empty() {
        return;
    }
    if kal_vent_modadd_enabled() {
        for &(target, n) in targets {
            ccx_cmp_lt_into_fast(b, &u[..n], &v[..n], ctrl, target);
        }
        return;
    }

    let n = targets.last().expect("non-empty targets").1;
    assert_eq!(u.len(), n);
    assert_eq!(v.len(), n);
    assert!(n > 0);
    assert!(targets.iter().all(|&(_, p)| (1..=n).contains(&p)));
    assert!(targets.windows(2).all(|w| w[0].1 < w[1].1));

    let c_in = b.alloc_qubit();
    let carries = b.alloc_qubits(n);
    for &q in u {
        b.x(q);
    }

    b.cx(u[0], v[0]);
    b.cx(u[0], c_in);
    b.ccx(c_in, v[0], carries[0]);
    b.cx(carries[0], u[0]);
    let mut next_target = 0;
    while next_target < targets.len() && targets[next_target].1 == 1 {
        b.ccx(ctrl, u[0], targets[next_target].0);
        next_target += 1;
    }
    for i in 1..n {
        b.cx(u[i], v[i]);
        b.cx(u[i], u[i - 1]);
        b.ccx(u[i - 1], v[i], carries[i]);
        b.cx(carries[i], u[i]);
        while next_target < targets.len() && targets[next_target].1 == i + 1 {
            b.ccx(ctrl, u[i], targets[next_target].0);
            next_target += 1;
        }
    }
    assert_eq!(next_target, targets.len());

    for i in (1..n).rev() {
        b.cx(carries[i], u[i]);
        let m = b.alloc_bit();
        b.hmr(carries[i], m);
        b.cz_if(u[i - 1], v[i], m);
        b.cx(u[i], u[i - 1]);
        b.cx(u[i], v[i]);
    }
    b.cx(carries[0], u[0]);
    let m0 = b.alloc_bit();
    b.hmr(carries[0], m0);
    b.cz_if(c_in, v[0], m0);
    b.cx(u[0], c_in);
    b.cx(u[0], v[0]);

    for &q in u {
        b.x(q);
    }
    b.free_vec(&carries);
    b.free(c_in);
}

pub(crate) fn cmp_lt_fast_prefix_window_forward(
    b: &mut B,
    u: &[QubitId],
    v: &[QubitId],
    c_in: QubitId,
    carries: &[QubitId],
    ctrl: QubitId,
    targets: &[(QubitId, usize)],
) {
    let n = u.len();
    assert_eq!(n, v.len());
    assert!(n > 0);
    assert!(carries.len() >= n);
    assert!(targets.iter().all(|&(_, p)| (1..=n).contains(&p)));
    assert!(targets.windows(2).all(|w| w[0].1 < w[1].1));

    b.cx(u[0], v[0]);
    b.cx(u[0], c_in);
    b.ccx(c_in, v[0], carries[0]);
    b.cx(carries[0], u[0]);
    let mut next_target = 0usize;
    while next_target < targets.len() && targets[next_target].1 == 1 {
        b.ccx(ctrl, u[0], targets[next_target].0);
        next_target += 1;
    }
    for i in 1..n {
        b.cx(u[i], v[i]);
        b.cx(u[i], u[i - 1]);
        b.ccx(u[i - 1], v[i], carries[i]);
        b.cx(carries[i], u[i]);
        while next_target < targets.len() && targets[next_target].1 == i + 1 {
            b.ccx(ctrl, u[i], targets[next_target].0);
            next_target += 1;
        }
    }
    assert_eq!(next_target, targets.len());
}

pub(crate) fn cmp_lt_fast_prefix_window_inverse(
    b: &mut B,
    u: &[QubitId],
    v: &[QubitId],
    c_in: QubitId,
    carries: &[QubitId],
) {
    let n = u.len();
    assert_eq!(n, v.len());
    assert!(n > 0);
    assert!(carries.len() >= n);

    for i in (1..n).rev() {
        b.cx(carries[i], u[i]);
        let m = b.alloc_bit();
        b.hmr(carries[i], m);
        b.cz_if(u[i - 1], v[i], m);
        b.cx(u[i], u[i - 1]);
        b.cx(u[i], v[i]);
    }
    b.cx(carries[0], u[0]);
    let m0 = b.alloc_bit();
    b.hmr(carries[0], m0);
    b.cz_if(c_in, v[0], m0);
    b.cx(u[0], c_in);
    b.cx(u[0], v[0]);
}

pub(crate) fn cmp_lt_phase_conditioned_with_cin(
    b: &mut B,
    u: &[QubitId],
    v: &[QubitId],
    c_in: QubitId,
    ctrl: QubitId,
    phase: BitId,
) {
    let n = u.len();
    assert_eq!(v.len(), n);
    assert!(n > 0);

    b.push_condition(phase);
    for &q in u {
        b.x(q);
    }
    let carries = b.alloc_qubits(n);
    cmp_lt_fast_prefix_window_forward(b, u, v, c_in, &carries, ctrl, &[]);
    b.cz(ctrl, u[n - 1]);
    cmp_lt_fast_prefix_window_inverse(b, u, v, c_in, &carries);
    b.free_vec(&carries);
    for &q in u {
        b.x(q);
    }
    b.pop_condition();
}

pub(crate) fn cmp_lt_phase_conditioned_borrowed_carries(
    b: &mut B,
    u: &[QubitId],
    v: &[QubitId],
    c_in: QubitId,
    carries: &[QubitId],
    ctrl: QubitId,
    phase: BitId,
) {
    let n = u.len();
    assert_eq!(v.len(), n);
    assert!(n > 0);
    assert!(carries.len() >= n);

    b.push_condition(phase);
    for &q in u {
        b.x(q);
    }
    cmp_lt_fast_prefix_window_forward(b, u, v, c_in, carries, ctrl, &[]);
    b.cz(ctrl, u[n - 1]);
    cmp_lt_fast_prefix_window_inverse(b, u, v, c_in, carries);
    for &q in u {
        b.x(q);
    }
    b.pop_condition();
}

pub(crate) fn cmp_lt_phase_conditioned_with_cin_borrowed_carries(
    b: &mut B,
    u: &[QubitId],
    v: &[QubitId],
    c_in: QubitId,
    carries: &[QubitId],
    phase: BitId,
) {
    let n = u.len();
    assert_eq!(v.len(), n);
    assert!(n > 0);
    assert!(carries.len() >= n);

    b.push_condition(phase);
    for &q in u {
        b.x(q);
    }
    cmp_lt_fast_prefix_window_forward(b, u, v, c_in, carries, c_in, &[]);
    b.cz(u[n - 1], u[n - 1]);
    cmp_lt_fast_prefix_window_inverse(b, u, v, c_in, carries);
    for &q in u {
        b.x(q);
    }
    b.pop_condition();
}

fn cmp_lt_phase_conditioned_clean_cin(
    b: &mut B,
    u: &[QubitId],
    v: &[QubitId],
    phase: BitId,
) {
    let n = u.len();
    assert_eq!(v.len(), n);
    assert!(n > 0);

    let c_in = b.alloc_qubit();
    b.push_condition(phase);
    for &q in u {
        b.x(q);
    }
    if n >= 2 {
        // The top carry is only ever consumed by a plain Z on u[n-1]. Since
        // (-1)^(a XOR b) = (-1)^a * (-1)^b, that phase factors exactly into
        // Z(u[n-1]) * CZ(u[n-2], v[n-1]) -- both Clifford, both free. So the
        // top AND is never materialised: no CCX, no carry ancilla, no erase.
        let carries = b.alloc_qubits(n - 1);
        cmp_lt_fast_prefix_window_forward(b, &u[..n - 1], &v[..n - 1], c_in, &carries, c_in, &[]);
        b.cx(u[n - 1], v[n - 1]);
        b.cx(u[n - 1], u[n - 2]);
        b.cz(u[n - 1], u[n - 1]);
        b.cz(u[n - 2], v[n - 1]);
        b.cx(u[n - 1], u[n - 2]);
        b.cx(u[n - 1], v[n - 1]);
        cmp_lt_fast_prefix_window_inverse(b, &u[..n - 1], &v[..n - 1], c_in, &carries);
        b.free_vec(&carries);
    } else {
        let carries = b.alloc_qubits(n);
        cmp_lt_fast_prefix_window_forward(b, u, v, c_in, &carries, c_in, &[]);
        b.cz(u[n - 1], u[n - 1]);
        cmp_lt_fast_prefix_window_inverse(b, u, v, c_in, &carries);
        b.free_vec(&carries);
    }
    for &q in u {
        b.x(q);
    }
    b.pop_condition();
    b.free(c_in);
}

fn cmp_lt_phase_conditioned_implicit_zero_hybrid(
    b: &mut B,
    u: &[QubitId],
    v: &[QubitId],
    phase: BitId,
) {
    let n = u.len();
    assert_eq!(v.len(), n);
    assert!(n >= 2);

    b.push_condition(phase);
    for &q in u {
        b.x(q);
    }

    let last = n - 1;
    let carries = b.alloc_qubits(last);

    // The lower prefix starts with a known-zero carry. After CX(u[0], v[0]),
    // u[0] is exactly the value the clean-c_in circuit copied into c_in, so
    // use it directly as the first nonlinear control (the 51c6 construction).
    b.cx(u[0], v[0]);
    b.ccx(u[0], v[0], carries[0]);
    b.cx(carries[0], u[0]);
    for i in 1..last {
        b.cx(u[i], v[i]);
        b.cx(u[i], u[i - 1]);
        b.ccx(u[i - 1], v[i], carries[i]);
        b.cx(carries[i], u[i]);
    }

    // Preserve d919's top-phase factorization exactly: the top AND is never
    // materialized, and its phase is emitted as Z(top) * CZ(carry, v_top).
    b.cx(u[last], v[last]);
    b.cx(u[last], u[last - 1]);
    b.cz(u[last], u[last]);
    b.cz(u[last - 1], v[last]);
    b.cx(u[last], u[last - 1]);
    b.cx(u[last], v[last]);

    for i in (1..last).rev() {
        b.cx(carries[i], u[i]);
        let m = b.alloc_bit();
        b.hmr(carries[i], m);
        b.cz_if(u[i - 1], v[i], m);
        b.cx(u[i], u[i - 1]);
        b.cx(u[i], v[i]);
    }
    b.cx(carries[0], u[0]);
    let m0 = b.alloc_bit();
    b.hmr(carries[0], m0);
    b.cz_if(u[0], v[0], m0);
    b.cx(u[0], v[0]);
    b.free_vec(&carries);

    for &q in u {
        b.x(q);
    }
    b.pop_condition();
}

pub(crate) fn cmp_lt_phase_conditioned(
    b: &mut B,
    u: &[QubitId],
    v: &[QubitId],
    phase: BitId,
) {
    if std::env::var("CMP_LT_PHASE_IMPLICIT_ZERO_HYBRID")
        .ok()
        .as_deref()
        == Some("1")
        && u.len() >= 2
    {
        cmp_lt_phase_conditioned_implicit_zero_hybrid(b, u, v, phase);
    } else {
        cmp_lt_phase_conditioned_clean_cin(b, u, v, phase);
    }
}

mod implicit_zero_hybrid_tests {
    use super::*;
    use crate::circuit::OperationType;
    use crate::sim::Simulator;
    use sha3::digest::{ExtendableOutput, Update};

    fn build_primitive(
        n: usize,
        hybrid: bool,
    ) -> (B, Vec<QubitId>, Vec<QubitId>, BitId) {
        let mut b = B::new_for_test();
        let u = b.alloc_qubits(n);
        let v = b.alloc_qubits(n);
        let phase = b.alloc_bit();
        if hybrid {
            cmp_lt_phase_conditioned_implicit_zero_hybrid(&mut b, &u, &v, phase);
        } else {
            cmp_lt_phase_conditioned_clean_cin(&mut b, &u, &v, phase);
        }
        (b, u, v, phase)
    }

    pub(super) fn run() {
        for n in 2usize..=8 {
            let (baseline, baseline_u, baseline_v, baseline_phase) = build_primitive(n, false);
            let (hybrid, hybrid_u, hybrid_v, hybrid_phase) = build_primitive(n, true);

            assert_eq!(hybrid.peak_qubits + 1, baseline.peak_qubits, "width {n}");
            assert!(hybrid.ops.len() < baseline.ops.len(), "width {n}");
            let count_toffoli = |b: &B| {
                b.ops
                    .iter()
                    .filter(|op| matches!(op.kind, OperationType::CCX | OperationType::CCZ))
                    .count()
            };
            assert_eq!(count_toffoli(&hybrid), count_toffoli(&baseline), "width {n}");

            let states = 1usize << (2 * n);
            for batch_start in (0..states).step_by(64) {
                let mut baseline_seed = sha3::Shake256::default();
                baseline_seed.update(b"cmp-lt-phase-implicit-zero-hybrid");
                baseline_seed.update(&(n as u64).to_le_bytes());
                baseline_seed.update(&(batch_start as u64).to_le_bytes());
                let hybrid_seed = baseline_seed.clone();
                let mut baseline_xof = baseline_seed.finalize_xof();
                let mut hybrid_xof = hybrid_seed.finalize_xof();
                let mut baseline_sim = Simulator::new(
                    baseline.next_qubit as usize,
                    baseline.next_bit as usize,
                    &mut baseline_xof,
                );
                let mut hybrid_sim = Simulator::new(
                    hybrid.next_qubit as usize,
                    hybrid.next_bit as usize,
                    &mut hybrid_xof,
                );
                *baseline_sim.bit_mut(baseline_phase) = u64::MAX;
                *hybrid_sim.bit_mut(hybrid_phase) = u64::MAX;

                let batch_end = (batch_start + 64).min(states);
                for state in batch_start..batch_end {
                    let shot = state - batch_start;
                    let u_value = state & ((1usize << n) - 1);
                    let v_value = state >> n;
                    for bit in 0..n {
                        if ((u_value >> bit) & 1) != 0 {
                            *baseline_sim.qubit_mut(baseline_u[bit]) |= 1u64 << shot;
                            *hybrid_sim.qubit_mut(hybrid_u[bit]) |= 1u64 << shot;
                        }
                        if ((v_value >> bit) & 1) != 0 {
                            *baseline_sim.qubit_mut(baseline_v[bit]) |= 1u64 << shot;
                            *hybrid_sim.qubit_mut(hybrid_v[bit]) |= 1u64 << shot;
                        }
                    }
                }

                baseline_sim.apply_iter(baseline.ops.iter());
                hybrid_sim.apply_iter(hybrid.ops.iter());
                assert_eq!(hybrid_sim.phase, baseline_sim.phase, "width {n}, batch {batch_start}");
                assert_eq!(hybrid_sim.bits, baseline_sim.bits, "width {n}, batch {batch_start}");
                for bit in 0..n {
                    assert_eq!(hybrid_sim.qubit(hybrid_u[bit]), baseline_sim.qubit(baseline_u[bit]));
                    assert_eq!(hybrid_sim.qubit(hybrid_v[bit]), baseline_sim.qubit(baseline_v[bit]));
                }
                for (sim, u, v) in [
                    (&baseline_sim, &baseline_u, &baseline_v),
                    (&hybrid_sim, &hybrid_u, &hybrid_v),
                ] {
                    for q in 0..sim.num_qubits {
                        let id = QubitId(q as u64);
                        if !u.contains(&id) && !v.contains(&id) {
                            assert_eq!(sim.qubit(id), 0, "width {n}, batch {batch_start}, dirty q{q}");
                        }
                    }
                }
            }
        }
    }
}

pub(crate) fn cmp_lt_phase_implicit_zero_hybrid_selftest() {
    implicit_zero_hybrid_tests::run();
    eprintln!(
        "CMP_LT_PHASE_IMPLICIT_ZERO_HYBRID: PASS widths=2..8 exhaustive deterministic-HMR value/phase/ancilla equivalence"
    );
}

pub(crate) fn ccx_cmp_lt_into_fast_prefix_targets_split(
    b: &mut B,
    u: &[QubitId],
    v: &[QubitId],
    ctrl: QubitId,
    targets: &[(QubitId, usize)],
    split: usize,
) {
    if targets.is_empty() {
        return;
    }
    let n = targets.last().expect("non-empty targets").1;
    assert_eq!(u.len(), n);
    assert_eq!(v.len(), n);
    assert!(n > 0);
    assert!(targets.iter().all(|&(_, p)| (1..=n).contains(&p)));
    assert!(targets.windows(2).all(|w| w[0].1 < w[1].1));
    if split == 0 || split >= n {
        ccx_cmp_lt_into_fast_prefix_targets(b, u, v, ctrl, targets);
        return;
    }

    if let Some(boundary_idx) = targets.iter().position(|&(_, p)| p == split) {
        let boundary = targets[boundary_idx].0;
        let targets_lo = targets[..=boundary_idx].to_vec();
        let targets_hi_rel = targets[boundary_idx + 1..]
            .iter()
            .map(|&(target, p)| (target, p - split))
            .collect::<Vec<_>>();

        for &q in u {
            b.x(q);
        }

        let hi_len = n - split;
        let carries_hi = b.alloc_qubits(hi_len);
        cmp_lt_fast_prefix_window_forward(
            b,
            &u[split..n],
            &v[split..n],
            boundary,
            &carries_hi,
            ctrl,
            &targets_hi_rel,
        );
        cmp_lt_fast_prefix_window_inverse(b, &u[split..n], &v[split..n], boundary, &carries_hi);
        b.free_vec(&carries_hi);

        let c_in_lo = b.alloc_qubit();
        let carries_lo = b.alloc_qubits(split);
        cmp_lt_fast_prefix_window_forward(
            b,
            &u[..split],
            &v[..split],
            c_in_lo,
            &carries_lo,
            ctrl,
            &targets_lo,
        );
        cmp_lt_fast_prefix_window_inverse(b, &u[..split], &v[..split], c_in_lo, &carries_lo);
        b.free_vec(&carries_lo);
        b.free(c_in_lo);

        for &q in u {
            b.x(q);
        }
        return;
    }

    let (targets_lo, targets_hi): (Vec<_>, Vec<_>) =
        targets.iter().copied().partition(|&(_, p)| p <= split);
    let targets_hi_rel = targets_hi
        .iter()
        .map(|&(target, p)| (target, p - split))
        .collect::<Vec<_>>();

    for &q in u {
        b.x(q);
    }

    let boundary = b.alloc_qubit();
    let c_in_lo = b.alloc_qubit();
    let carries_lo = b.alloc_qubits(split);
    cmp_lt_fast_prefix_window_forward(
        b,
        &u[..split],
        &v[..split],
        c_in_lo,
        &carries_lo,
        ctrl,
        &targets_lo,
    );
    b.cx(u[split - 1], boundary);
    cmp_lt_fast_prefix_window_inverse(b, &u[..split], &v[..split], c_in_lo, &carries_lo);
    b.free_vec(&carries_lo);
    b.free(c_in_lo);

    let hi_len = n - split;
    let carries_hi = b.alloc_qubits(hi_len);
    cmp_lt_fast_prefix_window_forward(
        b,
        &u[split..n],
        &v[split..n],
        boundary,
        &carries_hi,
        ctrl,
        &targets_hi_rel,
    );
    cmp_lt_fast_prefix_window_inverse(b, &u[split..n], &v[split..n], boundary, &carries_hi);
    b.free_vec(&carries_hi);

    let c_in_clear = b.alloc_qubit();
    let carries_clear = b.alloc_qubits(split);
    cmp_lt_fast_prefix_window_forward(
        b,
        &u[..split],
        &v[..split],
        c_in_clear,
        &carries_clear,
        ctrl,
        &[],
    );
    b.cx(u[split - 1], boundary);
    cmp_lt_fast_prefix_window_inverse(b, &u[..split], &v[..split], c_in_clear, &carries_clear);
    b.free_vec(&carries_clear);
    b.free(c_in_clear);
    b.free(boundary);

    for &q in u {
        b.x(q);
    }
}

pub(crate) fn cmp_lt_into_with_cin_slow(
    b: &mut B,
    u: &[QubitId],
    v: &[QubitId],
    c_in: QubitId,
    flag: QubitId,
) {
    let n = u.len();
    assert_eq!(n, v.len());
    assert!(n > 0);
    for i in 0..n {
        b.x(u[i]);
    }
    maj(b, c_in, v[0], u[0]);
    for i in 1..n {
        maj(b, u[i - 1], v[i], u[i]);
    }
    b.cx(u[n - 1], flag);
    for i in (1..n).rev() {
        inv_maj(b, u[i - 1], v[i], u[i]);
    }
    inv_maj(b, c_in, v[0], u[0]);
    for i in 0..n {
        b.x(u[i]);
    }
}

pub(crate) fn cmp_lt_into(b: &mut B, u: &[QubitId], v: &[QubitId], flag: QubitId) {
    let n = u.len();
    assert_eq!(n, v.len());

    let c_in = b.alloc_qubit();

    for i in 0..n {
        b.x(u[i]);
    }

    maj(b, c_in, v[0], u[0]);
    for i in 1..n {
        maj(b, u[i - 1], v[i], u[i]);
    }

    b.cx(u[n - 1], flag);

    for i in (1..n).rev() {
        inv_maj(b, u[i - 1], v[i], u[i]);
    }
    inv_maj(b, c_in, v[0], u[0]);

    for i in 0..n {
        b.x(u[i]);
    }

    b.free(c_in);
}

pub(crate) fn ccx_cmp_lt_into_fast_borrowed_carries(
    b: &mut B,
    u: &[QubitId],
    v: &[QubitId],
    ctrl: QubitId,
    target: QubitId,
    c_in: QubitId,
    carries: &[QubitId],
) {
    let n = u.len();
    assert_eq!(n, v.len());
    assert!(n > 0);
    assert!(carries.len() >= n);

    for i in 0..n {
        b.x(u[i]);
    }

    b.cx(u[0], v[0]);
    b.cx(u[0], c_in);
    b.ccx(c_in, v[0], carries[0]);
    b.cx(carries[0], u[0]);
    for i in 1..n {
        b.cx(u[i], v[i]);
        b.cx(u[i], u[i - 1]);
        b.ccx(u[i - 1], v[i], carries[i]);
        b.cx(carries[i], u[i]);
    }

    b.ccx(ctrl, u[n - 1], target);

    for i in (1..n).rev() {
        b.cx(carries[i], u[i]);
        let m = b.alloc_bit();
        b.hmr(carries[i], m);
        b.cz_if(u[i - 1], v[i], m);
        b.cx(u[i], u[i - 1]);
        b.cx(u[i], v[i]);
    }
    b.cx(carries[0], u[0]);
    let m0 = b.alloc_bit();
    b.hmr(carries[0], m0);
    b.cz_if(c_in, v[0], m0);
    b.cx(u[0], c_in);
    b.cx(u[0], v[0]);

    for i in 0..n {
        b.x(u[i]);
    }
}
