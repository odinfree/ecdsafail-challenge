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
    println!(
        "{{\"summary\":\"redteam\",\"alt_seeds\":{},\"peak_delta\":{},\"toffoli_delta\":{},\"failures\":{}}}",
        ALT_SEEDS, peak_delta, toffoli_delta, failures,
    );
    if failures != 0 {
        std::process::exit(1);
    }
}
