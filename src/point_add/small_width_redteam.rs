//! Independent red-team probe for the reduced-width chunked adder.
//!
//! This module is intentionally isolated from the submission builder. It
//! checks forward, inverse, and forward-then-inverse semantics over all pairs
//! of 8-bit inputs and exposes concrete phase witnesses for falsification.

use super::*;
use crate::circuit::{analyze_ops, OperationType, QubitOrBit};
use crate::sim::Simulator;
use sha3::{
    digest::{ExtendableOutput, Update},
    Shake256,
};
use std::collections::BTreeSet;

const WIDTH: usize = 8;
const BUDGET: usize = 4;
const CASES: usize = 1 << (2 * WIDTH);
const BATCH: usize = 64;
const ALT_SEEDS: u8 = 32;
const D2_COMPARE_WINDOW: usize = 2;

#[derive(Clone, Copy, Debug)]
enum Variant {
    Approx,
    Exact,
}

impl Variant {
    fn name(self) -> &'static str {
        match self {
            Self::Approx => "chunked-approx",
            Self::Exact => "chunked-exact-window",
        }
    }
}

#[derive(Clone, Copy, Debug)]
enum Direction {
    Forward,
    Inverse,
    RoundTrip,
}

impl Direction {
    fn name(self) -> &'static str {
        match self {
            Self::Forward => "forward",
            Self::Inverse => "inverse",
            Self::RoundTrip => "roundtrip",
        }
    }
}

struct Built {
    ops: Vec<Op>,
    registers: Vec<Vec<QubitOrBit>>,
    external: BTreeSet<u64>,
    peak_qubits: u32,
    emitted_toffoli: usize,
    hmr_count: usize,
    reset_count: usize,
}

#[derive(Default)]
struct Sweep {
    value_errors: usize,
    phase_batches: usize,
    phase_shots: usize,
    dirty_ancilla_batches: usize,
    first_value: Option<(u8, u8, u8, u8)>,
    first_phase: Option<(u8, u8, u64)>,
    first_dirty: Option<(u8, u8, u64, u64)>,
}

fn add(b: &mut B, addend: &[QubitId], acc: &[QubitId], variant: Variant) {
    match variant {
        Variant::Approx => {
            pingpong_div::add_chunked_measured_budgeted(b, addend, acc, None, BUDGET)
        }
        Variant::Exact => {
            pingpong_div::add_chunked_measured_exact_window_budgeted(b, addend, acc, BUDGET)
        }
    }
}

fn subtract(b: &mut B, addend: &[QubitId], acc: &[QubitId], variant: Variant) {
    for &q in acc {
        b.x(q);
    }
    add(b, addend, acc, variant);
    for &q in acc {
        b.x(q);
    }
}

fn build(variant: Variant, direction: Direction) -> Built {
    let mut b = B::new_for_test();
    let addend = b.alloc_qubits(WIDTH);
    let acc = b.alloc_qubits(WIDTH);
    b.set_phase("small_width_redteam");
    match direction {
        Direction::Forward => add(&mut b, &addend, &acc, variant),
        Direction::Inverse => subtract(&mut b, &addend, &acc, variant),
        Direction::RoundTrip => {
            add(&mut b, &addend, &acc, variant);
            subtract(&mut b, &addend, &acc, variant);
        }
    }
    b.declare_qubit_register(&addend);
    b.declare_qubit_register(&acc);
    let peak_qubits = b.peak_qubits;
    let ops = b.take_ops();
    let (_, _, _, registers) = analyze_ops(ops.iter());
    let external = addend.iter().chain(&acc).map(|q| q.0).collect();
    let emitted_toffoli = ops
        .iter()
        .filter(|op| matches!(op.kind, OperationType::CCX | OperationType::CCZ))
        .count();
    let hmr_count = ops
        .iter()
        .filter(|op| op.kind == OperationType::Hmr)
        .count();
    let reset_count = ops.iter().filter(|op| op.kind == OperationType::R).count();
    Built {
        ops,
        registers,
        external,
        peak_qubits,
        emitted_toffoli,
        hmr_count,
        reset_count,
    }
}

fn expected(acc: u8, addend: u8, direction: Direction) -> u8 {
    match direction {
        Direction::Forward => acc.wrapping_add(addend),
        Direction::Inverse => acc.wrapping_sub(addend),
        Direction::RoundTrip => acc,
    }
}

fn sweep(built: &Built, direction: Direction, seed_domain: &[u8]) -> Sweep {
    let (num_qubits, num_bits, _, _) = analyze_ops(built.ops.iter());
    let mut result = Sweep::default();
    for batch in 0..CASES / BATCH {
        let mut seed = Shake256::default();
        seed.update(seed_domain);
        seed.update(&(batch as u64).to_le_bytes());
        let mut reader = seed.finalize_xof();
        let mut sim = Simulator::new(num_qubits as usize, num_bits as usize, &mut reader);
        for shot in 0..BATCH {
            let case = batch * BATCH + shot;
            let addend = case as u8;
            let acc = (case >> WIDTH) as u8;
            sim.set_register(&built.registers[0], U256::from(addend), shot);
            sim.set_register(&built.registers[1], U256::from(acc), shot);
        }
        sim.apply_iter(built.ops.iter());

        if sim.phase != 0 {
            result.phase_batches += 1;
            result.phase_shots += sim.phase.count_ones() as usize;
            if result.first_phase.is_none() {
                let shot = sim.phase.trailing_zeros() as usize;
                let case = batch * BATCH + shot;
                result.first_phase = Some((case as u8, (case >> WIDTH) as u8, sim.phase));
            }
        }

        let mut dirty_mask = 0u64;
        let mut dirty_qubit = 0u64;
        for q in 0..num_qubits {
            if !built.external.contains(&u64::from(q)) {
                let value = sim.qubit(QubitId(u64::from(q)));
                if value != 0 {
                    dirty_mask = value;
                    dirty_qubit = u64::from(q);
                    break;
                }
            }
        }
        if dirty_mask != 0 {
            result.dirty_ancilla_batches += 1;
            if result.first_dirty.is_none() {
                let shot = dirty_mask.trailing_zeros() as usize;
                let case = batch * BATCH + shot;
                result.first_dirty =
                    Some((case as u8, (case >> WIDTH) as u8, dirty_qubit, dirty_mask));
            }
        }

        for shot in 0..BATCH {
            let case = batch * BATCH + shot;
            let addend = case as u8;
            let acc = (case >> WIDTH) as u8;
            let got_addend = sim.get_register(&built.registers[0], shot).to::<u8>();
            let got_acc = sim.get_register(&built.registers[1], shot).to::<u8>();
            let want_acc = expected(acc, addend, direction);
            if got_addend != addend || got_acc != want_acc {
                result.value_errors += 1;
                if result.first_value.is_none() {
                    result.first_value = Some((addend, acc, got_addend, got_acc));
                }
            }
        }
    }
    result
}

fn witness_json(witness: Option<(u8, u8, u64)>) -> String {
    match witness {
        Some((addend, acc, mask)) => format!(
            "{{\"addend\":{},\"acc\":{},\"phase_mask\":\"0x{mask:016x}\"}}",
            addend, acc
        ),
        None => "null".to_string(),
    }
}

fn print_sweep(
    variant: Variant,
    direction: Direction,
    seed_name: &str,
    built: &Built,
    sweep: &Sweep,
) {
    println!(
        concat!(
            "{{\"variant\":\"{}\",\"direction\":\"{}\",\"seed\":\"{}\",",
            "\"checked_pairs\":{},\"op_count\":{},\"emitted_toffoli\":{},",
            "\"hmr_count\":{},\"reset_count\":{},\"peak_qubits\":{},",
            "\"value_errors\":{},\"phase_batches\":{},\"phase_shots\":{},",
            "\"dirty_ancilla_batches\":{},\"first_phase\":{}}}"
        ),
        variant.name(),
        direction.name(),
        seed_name,
        CASES,
        built.ops.len(),
        built.emitted_toffoli,
        built.hmr_count,
        built.reset_count,
        built.peak_qubits,
        sweep.value_errors,
        sweep.phase_batches,
        sweep.phase_shots,
        sweep.dirty_ancilla_batches,
        witness_json(sweep.first_phase),
    );
    if let Some((addend, acc, got_addend, got_acc)) = sweep.first_value {
        eprintln!(
            "VALUE_WITNESS variant={} direction={} addend={} acc={} got_addend={} got_acc={}",
            variant.name(),
            direction.name(),
            addend,
            acc,
            got_addend,
            got_acc,
        );
    }
    if let Some((addend, acc, qubit, mask)) = sweep.first_dirty {
        eprintln!(
            "ANCILLA_WITNESS variant={} direction={} addend={} acc={} qubit={} mask=0x{:016x}",
            variant.name(),
            direction.name(),
            addend,
            acc,
            qubit,
            mask,
        );
    }
}

#[derive(Clone, Copy, Debug)]
enum D2Cleanup {
    ExactControl,
    ZeroPredecessor,
}

impl D2Cleanup {
    fn name(self) -> &'static str {
        match self {
            Self::ExactControl => "reverse-retention-control",
            Self::ZeroPredecessor => "zero-predecessor-falsifier",
        }
    }
}

/// Red-team-local copy of the value path in `pingpong_div::chunk_add`.
/// Keeping it here lets the falsifier alter only boundary phase repair without
/// making the production primitive expose another control surface.
fn d2_chunk_add(
    b: &mut B,
    addend: &[QubitId],
    acc: &[QubitId],
    carry_in: Option<QubitId>,
    carry_out: Option<QubitId>,
) {
    let width = addend.len();
    assert_eq!(width, acc.len());
    if width == 0 {
        return;
    }
    let num_carries = if carry_out.is_some() {
        width
    } else {
        width - 1
    };
    if num_carries == 0 {
        if let Some(carry) = carry_in {
            b.cx(carry, acc[0]);
        }
        b.cx(addend[0], acc[0]);
        return;
    }

    let owned = num_carries - usize::from(carry_out.is_some());
    let mut carries = b.alloc_qubits(owned);
    if let Some(carry) = carry_out {
        carries.push(carry);
    }

    for i in 0..num_carries {
        let previous = if i == 0 {
            carry_in
        } else {
            Some(carries[i - 1])
        };
        if let Some(previous) = previous {
            b.cx(previous, addend[i]);
            b.cx(previous, acc[i]);
        }
        b.ccx(addend[i], acc[i], carries[i]);
        if let Some(previous) = previous {
            b.cx(previous, carries[i]);
        }
    }

    if carry_out.is_some() {
        let i = width - 1;
        let previous = if i == 0 {
            carry_in
        } else {
            Some(carries[i - 1])
        };
        if let Some(previous) = previous {
            b.cx(previous, addend[i]);
        }
        b.cx(addend[i], acc[i]);
    } else {
        b.cx(carries[num_carries - 1], acc[width - 1]);
        b.cx(addend[width - 1], acc[width - 1]);
    }

    for i in (0..owned).rev() {
        let previous = if i == 0 {
            carry_in
        } else {
            Some(carries[i - 1])
        };
        if let Some(previous) = previous {
            b.cx(previous, carries[i]);
        }
        let measured = b.alloc_bit();
        b.hmr(carries[i], measured);
        b.cz_if(addend[i], acc[i], measured);
        if let Some(previous) = previous {
            b.cx(previous, addend[i]);
        }
        b.cx(addend[i], acc[i]);
    }
    b.free_vec(&carries[..owned]);
}

/// Retain every boundary exactly as the control does, but use a fresh zero in
/// every boundary phase repair. The lowest boundary legitimately has global
/// carry-in zero; every higher one deliberately ignores its live predecessor.
fn d2_add_zero_predecessor(
    b: &mut B,
    addend: &[QubitId],
    acc: &[QubitId],
    budget: usize,
) -> Vec<(usize, usize)> {
    let bounds = pingpong_div::research_chunk_layout(addend.len(), budget);
    let mut boundaries = Vec::new();
    let mut carry_in = None;

    for (index, &(lo, hi)) in bounds.iter().enumerate() {
        let last = index + 1 == bounds.len();
        let carry_out = (!last).then(|| b.alloc_qubit());
        d2_chunk_add(b, &addend[lo..hi], &acc[lo..hi], carry_in, carry_out);
        if let Some(carry) = carry_out {
            boundaries.push((carry, lo, hi));
        }
        carry_in = carry_out;
    }

    for &(carry, lo, hi) in boundaries.iter().rev() {
        let compare = D2_COMPARE_WINDOW.min(hi - lo);
        let split = hi - compare;
        let zero_cin = b.alloc_qubit();
        let window_cin = if split > lo {
            let q = b.alloc_qubit();
            cmp_lt_into_fast_with_cin(b, &acc[lo..split], &addend[lo..split], zero_cin, q);
            q
        } else {
            zero_cin
        };

        let phase = b.alloc_bit();
        b.hmr(carry, phase);
        let ctrl = b.alloc_qubit();
        b.x(ctrl);
        cmp_lt_phase_conditioned_with_cin(
            b,
            &acc[split..hi],
            &addend[split..hi],
            window_cin,
            ctrl,
            phase,
        );
        b.x(ctrl);
        b.free(ctrl);

        if split > lo {
            cmp_lt_into_fast_with_cin(b, &acc[lo..split], &addend[lo..split], zero_cin, window_cin);
            b.free(window_cin);
        }
        b.free(zero_cin);
        b.free(carry);
    }
    bounds
}

fn d2_build(width: usize, budget: usize, cleanup: D2Cleanup) -> (Built, Vec<(usize, usize)>) {
    let mut b = B::new_for_test();
    let addend = b.alloc_qubits(width);
    let acc = b.alloc_qubits(width);
    b.set_phase("small_width_redteam_d2");
    let bounds = match cleanup {
        D2Cleanup::ExactControl => {
            let bounds = pingpong_div::research_chunk_layout(width, budget);
            pingpong_div::add_chunked_measured_exact_window_budgeted(&mut b, &addend, &acc, budget);
            bounds
        }
        D2Cleanup::ZeroPredecessor => d2_add_zero_predecessor(&mut b, &addend, &acc, budget),
    };
    b.declare_qubit_register(&addend);
    b.declare_qubit_register(&acc);
    let peak_qubits = b.peak_qubits;
    let ops = b.take_ops();
    let (_, _, _, registers) = analyze_ops(ops.iter());
    let external = addend.iter().chain(&acc).map(|q| q.0).collect();
    let emitted_toffoli = ops
        .iter()
        .filter(|op| matches!(op.kind, OperationType::CCX | OperationType::CCZ))
        .count();
    let hmr_count = ops
        .iter()
        .filter(|op| op.kind == OperationType::Hmr)
        .count();
    let reset_count = ops.iter().filter(|op| op.kind == OperationType::R).count();
    (
        Built {
            ops,
            registers,
            external,
            peak_qubits,
            emitted_toffoli,
            hmr_count,
            reset_count,
        },
        bounds,
    )
}

fn d2_sweep(built: &Built, width: usize, budget: usize) -> Sweep {
    let cases = 1usize << (2 * width);
    let value_mask = ((1u16 << width) - 1) as u8;
    let (num_qubits, num_bits, _, _) = analyze_ops(built.ops.iter());
    let mut result = Sweep::default();

    for batch in 0..cases.div_ceil(BATCH) {
        let first_case = batch * BATCH;
        let live = (cases - first_case).min(BATCH);
        let live_mask = if live == BATCH {
            u64::MAX
        } else {
            (1u64 << live) - 1
        };
        let mut seed = Shake256::default();
        seed.update(b"small-width-redteam-d2-zero-predecessor-v1");
        seed.update(&(width as u64).to_le_bytes());
        seed.update(&(budget as u64).to_le_bytes());
        seed.update(&(batch as u64).to_le_bytes());
        let mut reader = seed.finalize_xof();
        let mut sim = Simulator::new(num_qubits as usize, num_bits as usize, &mut reader);
        for shot in 0..live {
            let case = first_case + shot;
            let addend = (case as u8) & value_mask;
            let acc = ((case >> width) as u8) & value_mask;
            sim.set_register(&built.registers[0], U256::from(addend), shot);
            sim.set_register(&built.registers[1], U256::from(acc), shot);
        }
        sim.apply_iter(built.ops.iter());

        let phase_mask = sim.phase & live_mask;
        if phase_mask != 0 {
            result.phase_batches += 1;
            result.phase_shots += phase_mask.count_ones() as usize;
            if result.first_phase.is_none() {
                let shot = phase_mask.trailing_zeros() as usize;
                let case = first_case + shot;
                result.first_phase = Some((
                    (case as u8) & value_mask,
                    ((case >> width) as u8) & value_mask,
                    phase_mask,
                ));
            }
        }

        let mut dirty_mask = 0u64;
        let mut dirty_qubit = 0u64;
        for q in 0..num_qubits {
            if !built.external.contains(&u64::from(q)) {
                let value = sim.qubit(QubitId(u64::from(q))) & live_mask;
                if value != 0 {
                    dirty_mask = value;
                    dirty_qubit = u64::from(q);
                    break;
                }
            }
        }
        if dirty_mask != 0 {
            result.dirty_ancilla_batches += 1;
            if result.first_dirty.is_none() {
                let shot = dirty_mask.trailing_zeros() as usize;
                let case = first_case + shot;
                result.first_dirty = Some((
                    (case as u8) & value_mask,
                    ((case >> width) as u8) & value_mask,
                    dirty_qubit,
                    dirty_mask,
                ));
            }
        }

        for shot in 0..live {
            let case = first_case + shot;
            let addend = (case as u8) & value_mask;
            let acc = ((case >> width) as u8) & value_mask;
            let got_addend = sim.get_register(&built.registers[0], shot).to::<u8>();
            let got_acc = sim.get_register(&built.registers[1], shot).to::<u8>();
            let want_acc = acc.wrapping_add(addend) & value_mask;
            if got_addend != addend || got_acc != want_acc {
                result.value_errors += 1;
                if result.first_value.is_none() {
                    result.first_value = Some((addend, acc, got_addend, got_acc));
                }
            }
        }
    }
    result
}

fn d2_print(
    cleanup: D2Cleanup,
    width: usize,
    budget: usize,
    bounds: &[(usize, usize)],
    built: &Built,
    sweep: &Sweep,
) {
    let sizes = bounds
        .iter()
        .map(|&(lo, hi)| (hi - lo).to_string())
        .collect::<Vec<_>>()
        .join(",");
    println!(
        concat!(
            "{{\"d2_cleanup\":\"{}\",\"width\":{},\"budget\":{},",
            "\"compare_window\":{},\"layout\":[{}],\"checked_pairs\":{},",
            "\"op_count\":{},\"emitted_toffoli\":{},\"hmr_count\":{},",
            "\"reset_count\":{},\"peak_qubits\":{},\"value_errors\":{},",
            "\"phase_batches\":{},\"phase_shots\":{},",
            "\"dirty_ancilla_batches\":{},\"first_phase\":{}}}"
        ),
        cleanup.name(),
        width,
        budget,
        D2_COMPARE_WINDOW,
        sizes,
        1usize << (2 * width),
        built.ops.len(),
        built.emitted_toffoli,
        built.hmr_count,
        built.reset_count,
        built.peak_qubits,
        sweep.value_errors,
        sweep.phase_batches,
        sweep.phase_shots,
        sweep.dirty_ancilla_batches,
        witness_json(sweep.first_phase),
    );
}

fn d2_zero_predecessor_gate() -> usize {
    for width in 1..=WIDTH {
        for budget in 1..=width {
            let bounds = pingpong_div::research_chunk_layout(width, budget);
            if bounds.len() < 3 {
                continue;
            }

            let (control, control_bounds) = d2_build(width, budget, D2Cleanup::ExactControl);
            let control_sweep = d2_sweep(&control, width, budget);
            if control_sweep.value_errors != 0
                || control_sweep.phase_batches != 0
                || control_sweep.dirty_ancilla_batches != 0
            {
                d2_print(
                    D2Cleanup::ExactControl,
                    width,
                    budget,
                    &control_bounds,
                    &control,
                    &control_sweep,
                );
                return 1;
            }

            let (falsifier, falsifier_bounds) = d2_build(width, budget, D2Cleanup::ZeroPredecessor);
            let falsifier_sweep = d2_sweep(&falsifier, width, budget);
            if falsifier_sweep.value_errors != 0 || falsifier_sweep.dirty_ancilla_batches != 0 {
                d2_print(
                    D2Cleanup::ZeroPredecessor,
                    width,
                    budget,
                    &falsifier_bounds,
                    &falsifier,
                    &falsifier_sweep,
                );
                return 1;
            }
            if falsifier_sweep.phase_batches != 0 {
                d2_print(
                    D2Cleanup::ExactControl,
                    width,
                    budget,
                    &control_bounds,
                    &control,
                    &control_sweep,
                );
                d2_print(
                    D2Cleanup::ZeroPredecessor,
                    width,
                    budget,
                    &falsifier_bounds,
                    &falsifier,
                    &falsifier_sweep,
                );
                return 0;
            }
        }
    }
    eprintln!("D2_NO_ZERO_PREDECESSOR_PHASE_WITNESS");
    1
}

pub fn main() {
    std::env::set_var("SUB4_PP_REPLAY_CHUNK_COMPARE", "2");
    let mut failures = 0usize;
    let directions = [Direction::Forward, Direction::Inverse, Direction::RoundTrip];
    for variant in [Variant::Approx, Variant::Exact] {
        for direction in directions {
            let built = build(variant, direction);
            let canonical = sweep(&built, direction, b"small-width-harness-simulator-v1");
            if canonical.value_errors != 0 || canonical.dirty_ancilla_batches != 0 {
                failures += 1;
            }
            if matches!(variant, Variant::Exact) && canonical.phase_batches != 0 {
                failures += 1;
            }
            if matches!((variant, direction), (Variant::Approx, Direction::Forward))
                && canonical.phase_batches != 192
            {
                failures += 1;
            }
            print_sweep(variant, direction, "canonical", &built, &canonical);

            if matches!(variant, Variant::Exact) {
                for seed_index in 0u8..ALT_SEEDS {
                    let mut domain = b"small-width-redteam-alt-seed-v1".to_vec();
                    domain.push(seed_index);
                    let alt = sweep(&built, direction, &domain);
                    if alt.value_errors != 0
                        || alt.phase_batches != 0
                        || alt.dirty_ancilla_batches != 0
                    {
                        failures += 1;
                    }
                    print_sweep(
                        variant,
                        direction,
                        &format!("alt-{seed_index}"),
                        &built,
                        &alt,
                    );
                }
            }
        }
    }

    let approx = build(Variant::Approx, Direction::Forward);
    let exact = build(Variant::Exact, Direction::Forward);
    let peak_delta = i64::from(exact.peak_qubits) - i64::from(approx.peak_qubits);
    let toffoli_delta = exact.emitted_toffoli as i64 - approx.emitted_toffoli as i64;
    if peak_delta != 2 || toffoli_delta != 5 {
        failures += 1;
    }
    failures += d2_zero_predecessor_gate();
    println!(
        "{{\"summary\":\"redteam\",\"alt_seeds\":{},\"peak_delta\":{},\"toffoli_delta\":{},\"failures\":{}}}",
        ALT_SEEDS, peak_delta, toffoli_delta, failures,
    );
    if failures != 0 {
        std::process::exit(1);
    }
}
