//! Reduced-width Pareto probe for Justin Drake's small-adder hypothesis.
//!
//! The complete promoted point-addition route is fixed to secp256k1 and is
//! not width-parametric.  This probe therefore measures the exact generic
//! adder mechanisms used by that source at 32/64/96/128 bits, plus 256 as a
//! lift check.  The `co_binder_topclean` family composes two exact adders so a
//! knob sweep can expose measured peak-owner migration instead of assuming it.

use super::*;
use crate::circuit::{Op, OperationType, QubitId};
use crate::sim::Simulator;
use alloy_primitives::U256;
use sha3::{
    digest::{ExtendableOutput, Update, XofReader},
    Shake256,
};
use std::collections::BTreeMap;

const SOURCE_COMMIT: &str = "67524171baaf568dc3dc606f38515745f70804ff";
const HARNESS_VERSION: &str = "justin-drake-smallwidth-v1";
const CREDIT: &str = "Justin Drake";

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Family {
    LowQ,
    TopClean,
    Windowed,
    CoBinderTopClean,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum BoundaryRepair {
    ApproximateNoCin,
    ExactWholeChunkWithChunkCin,
    TopWindowWithEntryCarry,
}

impl BoundaryRepair {
    fn name(self) -> &'static str {
        match self {
            Self::ApproximateNoCin => "approximate_no_cin",
            Self::ExactWholeChunkWithChunkCin => "exact_whole_chunk_with_chunk_cin",
            Self::TopWindowWithEntryCarry => "topW_with_window_entry_carry",
        }
    }
}

impl Family {
    fn name(self) -> &'static str {
        match self {
            Self::LowQ => "lowq",
            Self::TopClean => "topclean",
            Self::Windowed => "windowed",
            Self::CoBinderTopClean => "co_binder_topclean",
        }
    }

    fn knob_name(self) -> &'static str {
        match self {
            Self::LowQ => "none",
            Self::TopClean | Self::CoBinderTopClean => "clean_top",
            Self::Windowed => "blocks",
        }
    }

    fn repetitions(self) -> usize {
        if self == Self::CoBinderTopClean {
            2
        } else {
            1
        }
    }
}

struct Kernel {
    ops: Vec<Op>,
    a: Vec<QubitId>,
    acc: Vec<QubitId>,
    cin: QubitId,
    num_qubits: usize,
    num_bits: usize,
    peak_qubits: u32,
    peak_owner: &'static str,
    phase_maxima: BTreeMap<&'static str, u32>,
    emitted_toffoli: usize,
}

struct BoundaryKernel {
    ops: Vec<Op>,
    u: Vec<QubitId>,
    v: Vec<QubitId>,
    retained_carry: Option<QubitId>,
    erased_boundary: QubitId,
    num_qubits: usize,
    num_bits: usize,
    peak_qubits: u32,
    peak_owner: &'static str,
    phase_maxima: BTreeMap<&'static str, u32>,
    emitted_toffoli: usize,
}

fn parse_widths() -> Result<Vec<usize>, String> {
    let raw = std::env::var("SMALLWIDTH_WIDTHS").unwrap_or_else(|_| "32,64,96,128,256".to_string());
    let mut widths = Vec::new();
    for field in raw.split(',') {
        let width = field
            .trim()
            .parse::<usize>()
            .map_err(|_| format!("invalid width {field:?}"))?;
        if !(6..=256).contains(&width) {
            return Err(format!("width {width} outside supported range 6..=256"));
        }
        widths.push(width);
    }
    widths.sort_unstable();
    widths.dedup();
    if widths.is_empty() {
        return Err("SMALLWIDTH_WIDTHS selected no widths".to_string());
    }
    Ok(widths)
}

fn parse_max_blocks(width: usize) -> usize {
    std::env::var("SMALLWIDTH_MAX_BLOCKS")
        .ok()
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or(32)
        .max(1)
        .min(width + 1)
}

fn boundary_windows(width: usize) -> Vec<usize> {
    let max_window = std::env::var("SMALLWIDTH_MAX_WINDOW")
        .ok()
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or(32)
        .max(1)
        .min(width);
    let mut windows: Vec<usize> = (1..=max_window).collect();
    windows.push(width);
    windows.sort_unstable();
    windows.dedup();
    windows
}

fn build_kernel(width: usize, family: Family, knob: usize, emit: bool) -> Kernel {
    // Phase accounting is env-gated in B. This binary owns its process and
    // turns it on before the first allocation.
    std::env::set_var("TRACE_PHASE_ACTIVE", "1");
    let mut b = if emit {
        B::new_for_test()
    } else {
        B::new_count_only()
    };
    b.set_phase("persistent_inputs");
    let a = b.alloc_qubits(width);
    let acc = b.alloc_qubits(width + 1);
    let cin = b.alloc_qubit();

    match family {
        Family::LowQ => {
            b.set_phase("lowq_inplace_add");
            cuccaro_add_low_to_ext_clean(&mut b, &a, &acc, cin);
        }
        Family::TopClean => {
            b.set_phase("topclean_hybrid_add");
            cuccaro_add_fast_low_to_ext_topclean(&mut b, &a, &acc, cin, knob);
        }
        Family::Windowed => {
            b.set_phase("windowed_add");
            cuccaro_add_fast_windowed_low_to_ext(&mut b, &a, &acc, cin, knob);
        }
        Family::CoBinderTopClean => {
            b.set_phase("candidate_topclean_add");
            cuccaro_add_fast_low_to_ext_topclean(&mut b, &a, &acc, cin, knob);
            // A second exact adder supplies an O(sqrt(n)) competing workspace.
            // This is a microcosm of the promoted route's replay/square
            // co-binder: once the candidate drops below it, global Q plateaus
            // and the peak owner migrates.
            let rival_carries = (width as f64).sqrt().ceil() as usize;
            let rival_clean_top = width.saturating_sub(rival_carries);
            b.set_phase("fixed_sqrt_rival_add");
            cuccaro_add_fast_low_to_ext_topclean(&mut b, &a, &acc, cin, rival_clean_top);
        }
    }

    let emitted_toffoli = b.counted_kind_ops[OperationType::CCX as usize]
        + b.counted_kind_ops[OperationType::CCZ as usize];
    Kernel {
        ops: b.take_ops(),
        a,
        acc,
        cin,
        num_qubits: b.next_qubit as usize,
        num_bits: b.next_bit as usize,
        peak_qubits: b.peak_qubits,
        peak_owner: b.peak_phase,
        phase_maxima: b.phase_active_max,
        emitted_toffoli,
    }
}

fn build_boundary_kernel(
    width: usize,
    repair: BoundaryRepair,
    window: usize,
    emit: bool,
) -> BoundaryKernel {
    assert!((1..=width).contains(&window));
    std::env::set_var("TRACE_PHASE_ACTIVE", "1");
    let mut b = if emit {
        B::new_for_test()
    } else {
        B::new_count_only()
    };
    b.set_phase("boundary_persistent_operands");
    let u = b.alloc_qubits(width);
    let v = b.alloc_qubits(width);
    // This is the carry bit whose measurement phase must be discharged.
    let erased_boundary = b.alloc_qubit();
    let retained_carry = match repair {
        BoundaryRepair::ApproximateNoCin => None,
        BoundaryRepair::ExactWholeChunkWithChunkCin | BoundaryRepair::TopWindowWithEntryCarry => {
            Some(b.alloc_qubit())
        }
    };
    b.set_phase(match repair {
        BoundaryRepair::ApproximateNoCin => "repair_topW_no_cin",
        BoundaryRepair::ExactWholeChunkWithChunkCin => "repair_exact_whole_chunk_cin",
        BoundaryRepair::TopWindowWithEntryCarry => "repair_topW_entry_carry",
    });
    let measured = b.alloc_bit();
    b.hmr(erased_boundary, measured);
    match repair {
        BoundaryRepair::ApproximateNoCin => {
            cmp_lt_phase_conditioned(&mut b, &u[width - window..], &v[width - window..], measured);
        }
        BoundaryRepair::ExactWholeChunkWithChunkCin => {
            let carry = retained_carry.expect("whole-chunk repair retains chunk cin");
            let carries = b.alloc_qubits(width.saturating_sub(1));
            cmp_lt_phase_conditioned_with_cin_borrowed_carries(
                &mut b, &u, &v, carry, &carries, measured,
            );
            b.free_vec(&carries);
        }
        BoundaryRepair::TopWindowWithEntryCarry => {
            let carry = retained_carry.expect("top-window repair retains entry carry");
            let carries = b.alloc_qubits(window.saturating_sub(1));
            cmp_lt_phase_conditioned_with_cin_borrowed_carries(
                &mut b,
                &u[width - window..],
                &v[width - window..],
                carry,
                &carries,
                measured,
            );
            b.free_vec(&carries);
        }
    }
    b.free(erased_boundary);

    let emitted_toffoli = b.counted_kind_ops[OperationType::CCX as usize]
        + b.counted_kind_ops[OperationType::CCZ as usize];
    BoundaryKernel {
        ops: b.take_ops(),
        u,
        v,
        retained_carry,
        erased_boundary,
        num_qubits: b.next_qubit as usize,
        num_bits: b.next_bit as usize,
        peak_qubits: b.peak_qubits,
        peak_owner: b.peak_phase,
        phase_maxima: b.phase_active_max,
        emitted_toffoli,
    }
}

fn width_mask(bits: usize) -> U256 {
    if bits >= 256 {
        U256::MAX
    } else {
        (U256::from(1u64) << bits) - U256::from(1u64)
    }
}

fn random_u256(reader: &mut impl XofReader) -> U256 {
    let mut limbs = [0u64; 4];
    for limb in &mut limbs {
        let mut bytes = [0u8; 8];
        reader.read(&mut bytes);
        *limb = u64::from_le_bytes(bytes);
    }
    U256::from_limbs(limbs)
}

fn set_qubit_register<R: XofReader>(
    sim: &mut Simulator<'_, R>,
    register: &[QubitId],
    value: U256,
    shot: usize,
) {
    for (bit, qubit) in register.iter().copied().enumerate() {
        if value.bit(bit) {
            *sim.qubit_mut(qubit) |= 1u64 << shot;
        }
    }
}

fn get_qubit_register<R: XofReader>(
    sim: &Simulator<'_, R>,
    register: &[QubitId],
    shot: usize,
) -> U256 {
    let mut value = U256::ZERO;
    for (bit, qubit) in register.iter().copied().enumerate() {
        value.set_bit(bit, ((sim.qubit(qubit) >> shot) & 1) != 0);
    }
    value
}

fn validate_kernel(width: usize, family: Family, knob: usize) -> Result<(), String> {
    if width >= 256 {
        // The adder has an n+1-bit result; U256 cannot represent the 257th bit.
        return Ok(());
    }
    let kernel = build_kernel(width, family, knob, true);
    let mut input_seed = Shake256::default();
    input_seed.update(b"justin-drake-smallwidth-inputs-v1");
    input_seed.update(&(width as u64).to_le_bytes());
    input_seed.update(family.name().as_bytes());
    input_seed.update(&(knob as u64).to_le_bytes());
    let mut input_reader = input_seed.finalize_xof();

    let mut sim_seed = Shake256::default();
    sim_seed.update(b"justin-drake-smallwidth-hmr-v1");
    sim_seed.update(&(width as u64).to_le_bytes());
    sim_seed.update(family.name().as_bytes());
    sim_seed.update(&(knob as u64).to_le_bytes());
    let mut sim_reader = sim_seed.finalize_xof();
    let mut sim = Simulator::new(kernel.num_qubits, kernel.num_bits, &mut sim_reader);
    let in_mask = width_mask(width);
    let out_mask = width_mask(width + 1);
    let mut expected = Vec::with_capacity(64);
    let mut inputs_a = Vec::with_capacity(64);
    let mut inputs_acc = Vec::with_capacity(64);
    let mut inputs_cin = Vec::with_capacity(64);

    for shot in 0..64 {
        let a = if shot == 0 {
            U256::ZERO
        } else if shot == 1 {
            in_mask
        } else {
            random_u256(&mut input_reader) & in_mask
        };
        let acc = if shot == 2 {
            out_mask
        } else {
            random_u256(&mut input_reader) & out_mask
        };
        let cin = shot % 3 == 0;
        set_qubit_register(&mut sim, &kernel.a, a, shot);
        set_qubit_register(&mut sim, &kernel.acc, acc, shot);
        if cin {
            *sim.qubit_mut(kernel.cin) |= 1u64 << shot;
        }
        let delta = a.wrapping_add(U256::from(cin as u64));
        let mut want = acc;
        for _ in 0..family.repetitions() {
            want = want.wrapping_add(delta) & out_mask;
        }
        inputs_a.push(a);
        inputs_acc.push(acc);
        inputs_cin.push(cin);
        expected.push(want);
    }
    sim.apply_iter(kernel.ops.iter());

    let live: std::collections::BTreeSet<u64> = kernel
        .a
        .iter()
        .chain(&kernel.acc)
        .copied()
        .chain(std::iter::once(kernel.cin))
        .map(|qubit| qubit.0)
        .collect();
    for shot in 0..64 {
        let got_a = get_qubit_register(&sim, &kernel.a, shot);
        let got_acc = get_qubit_register(&sim, &kernel.acc, shot);
        let got_cin = ((sim.qubit(kernel.cin) >> shot) & 1) != 0;
        if got_a != inputs_a[shot] || got_acc != expected[shot] || got_cin != inputs_cin[shot] {
            return Err(format!(
                "value mismatch width={width} family={} knob={knob} shot={shot}: a={got_a:#x}/{:#x} acc={got_acc:#x}/{:#x} cin={got_cin}/{}",
                family.name(), inputs_a[shot], expected[shot], inputs_cin[shot]
            ));
        }
    }
    if sim.phase != 0 {
        return Err(format!(
            "phase mismatch width={width} family={} knob={knob}: mask={:#018x}",
            family.name(),
            sim.phase
        ));
    }
    for (index, value) in sim.qubits.iter().copied().enumerate() {
        if !live.contains(&(index as u64)) && value != 0 {
            return Err(format!(
                "dirty ancilla width={width} family={} knob={knob}: q{index} mask={value:#018x}",
                family.name()
            ));
        }
    }
    Ok(())
}

fn lt_with_cin(u: U256, v: U256, cin: bool, bits: usize) -> bool {
    let mask = width_mask(bits);
    let u = u & mask;
    let v = v & mask;
    if cin && v == mask {
        true
    } else {
        u < v.wrapping_add(U256::from(cin as u64))
    }
}

fn validate_boundary_kernel(
    width: usize,
    repair: BoundaryRepair,
    window: usize,
) -> Result<(), String> {
    if width >= 256 {
        return Ok(());
    }
    let kernel = build_boundary_kernel(width, repair, window, true);
    let mut input_seed = Shake256::default();
    input_seed.update(b"justin-drake-boundary-inputs-v1");
    input_seed.update(&(width as u64).to_le_bytes());
    input_seed.update(repair.name().as_bytes());
    input_seed.update(&(window as u64).to_le_bytes());
    let mut input_reader = input_seed.finalize_xof();
    let mut sim_seed = Shake256::default();
    sim_seed.update(b"justin-drake-boundary-hmr-v1");
    sim_seed.update(&(width as u64).to_le_bytes());
    sim_seed.update(repair.name().as_bytes());
    sim_seed.update(&(window as u64).to_le_bytes());
    let mut sim_reader = sim_seed.finalize_xof();
    let mut sim = Simulator::new(kernel.num_qubits, kernel.num_bits, &mut sim_reader);
    let mask = width_mask(width);
    let low_bits = width - window;
    let low_mask = width_mask(low_bits);
    let top_mask = width_mask(window);
    let mut inputs = Vec::with_capacity(64);

    for shot in 0..64 {
        let u = if shot == 0 {
            U256::ZERO
        } else if shot == 1 {
            mask
        } else {
            random_u256(&mut input_reader) & mask
        };
        let v = if shot == 2 {
            mask
        } else {
            random_u256(&mut input_reader) & mask
        };
        let chunk_cin = shot % 3 == 0;
        let entry_carry = if low_bits == 0 {
            chunk_cin
        } else {
            lt_with_cin(u & low_mask, v & low_mask, chunk_cin, low_bits)
        };
        let top_u = (u >> low_bits) & top_mask;
        let top_v = (v >> low_bits) & top_mask;
        let retained_value = match repair {
            BoundaryRepair::ApproximateNoCin => false,
            BoundaryRepair::ExactWholeChunkWithChunkCin => chunk_cin,
            BoundaryRepair::TopWindowWithEntryCarry => entry_carry,
        };
        let predicate = match repair {
            BoundaryRepair::ApproximateNoCin => top_u < top_v,
            BoundaryRepair::ExactWholeChunkWithChunkCin => lt_with_cin(u, v, chunk_cin, width),
            BoundaryRepair::TopWindowWithEntryCarry => {
                lt_with_cin(top_u, top_v, entry_carry, window)
            }
        };
        set_qubit_register(&mut sim, &kernel.u, u, shot);
        set_qubit_register(&mut sim, &kernel.v, v, shot);
        if let Some(carry) = kernel.retained_carry {
            if retained_value {
                *sim.qubit_mut(carry) |= 1u64 << shot;
            }
        }
        if predicate {
            *sim.qubit_mut(kernel.erased_boundary) |= 1u64 << shot;
        }
        inputs.push((u, v, retained_value));
    }
    sim.apply_iter(kernel.ops.iter());

    let live: std::collections::BTreeSet<u64> = kernel
        .u
        .iter()
        .chain(&kernel.v)
        .copied()
        .chain(kernel.retained_carry)
        .map(|qubit| qubit.0)
        .collect();
    for (shot, &(u, v, retained)) in inputs.iter().enumerate() {
        let got_u = get_qubit_register(&sim, &kernel.u, shot);
        let got_v = get_qubit_register(&sim, &kernel.v, shot);
        let got_retained = kernel
            .retained_carry
            .is_some_and(|carry| ((sim.qubit(carry) >> shot) & 1) != 0);
        if got_u != u || got_v != v || got_retained != retained {
            return Err(format!(
                "boundary value mismatch width={width} repair={} W={window} shot={shot}",
                repair.name()
            ));
        }
    }
    if sim.phase != 0 {
        return Err(format!(
            "boundary phase mismatch width={width} repair={} W={window}: mask={:#018x}",
            repair.name(),
            sim.phase
        ));
    }
    for (index, value) in sim.qubits.iter().copied().enumerate() {
        if !live.contains(&(index as u64)) && value != 0 {
            return Err(format!(
                "boundary dirty ancilla width={width} repair={} W={window}: q{index} mask={value:#018x}",
                repair.name()
            ));
        }
    }
    Ok(())
}

fn validation_knobs(width: usize, family: Family, max_blocks: usize) -> Vec<usize> {
    let mut knobs = match family {
        Family::LowQ => vec![0],
        Family::TopClean | Family::CoBinderTopClean => vec![
            0,
            width / 4,
            width / 2,
            (3 * width) / 4,
            width.saturating_sub(1),
        ],
        Family::Windowed => vec![1, 2, 3, 4, 5, 8, max_blocks],
    };
    knobs.retain(|&knob| match family {
        Family::LowQ => true,
        Family::TopClean | Family::CoBinderTopClean => knob < width,
        Family::Windowed => knob >= 1 && knob <= max_blocks,
    });
    knobs.sort_unstable();
    knobs.dedup();
    knobs
}

fn json_phase_maxima(maxima: &BTreeMap<&'static str, u32>) -> String {
    let mut fields = Vec::with_capacity(maxima.len());
    for (phase, active) in maxima {
        fields.push(format!("\"{phase}\":{active}"));
    }
    format!("{{{}}}", fields.join(","))
}

fn emit_row(width: usize, family: Family, knob: usize, kernel: &Kernel, validation: &str) {
    let n = width as f64;
    let q = kernel.peak_qubits as f64;
    let t = kernel.emitted_toffoli as f64;
    let score = q * t;
    let knob_ratio = match family {
        Family::LowQ => 0.0,
        Family::TopClean | Family::CoBinderTopClean => knob as f64 / n,
        Family::Windowed => knob as f64 / (n + 1.0),
    };
    println!(
        concat!(
            "{{\"schema\":\"smallwidth-pareto-v1\",",
            "\"source_commit\":\"{}\",\"harness_version\":\"{}\",",
            "\"hypothesis_credit\":\"{}\",\"width_bits\":{},",
            "\"family\":\"{}\",\"knob_name\":\"{}\",",
            "\"knob_value\":{},\"knob_ratio\":{:.9},",
            "\"kernel_repetitions\":{},\"normalization_model\":\"adder-linear\",",
            "\"peak_qubits\":{},\"emitted_toffoli\":{},",
            "\"score_proxy\":{},\"q_per_n\":{:.9},",
            "\"t_per_n\":{:.9},\"t_per_n2\":{:.9},",
            "\"score_per_n2\":{:.9},\"peak_owner\":\"{}\",",
            "\"phase_maxima\":{},\"boundary_repair\":\"not_applicable\",",
            "\"theoretical_fault_probability\":0.0,\"theoretical_fault_log2\":null,",
            "\"validation\":\"{}\"}}"
        ),
        SOURCE_COMMIT,
        HARNESS_VERSION,
        CREDIT,
        width,
        family.name(),
        family.knob_name(),
        knob,
        knob_ratio,
        family.repetitions(),
        kernel.peak_qubits,
        kernel.emitted_toffoli,
        kernel.peak_qubits as u64 * kernel.emitted_toffoli as u64,
        q / n,
        t / n,
        t / (n * n),
        score / (n * n),
        kernel.peak_owner,
        json_phase_maxima(&kernel.phase_maxima),
        validation,
    );
}

fn emit_boundary_row(
    width: usize,
    repair: BoundaryRepair,
    window: usize,
    kernel: &BoundaryKernel,
    validation: &str,
) {
    let n = width as f64;
    let q = kernel.peak_qubits as f64;
    let t = kernel.emitted_toffoli as f64;
    let score = q * t;
    let (fault_probability, fault_log2) = match repair {
        BoundaryRepair::ApproximateNoCin => {
            let log2 = -(window as i64 + 1);
            (2f64.powi(log2 as i32), log2.to_string())
        }
        BoundaryRepair::ExactWholeChunkWithChunkCin | BoundaryRepair::TopWindowWithEntryCarry => {
            (0.0, "null".to_string())
        }
    };
    println!(
        concat!(
            "{{\"schema\":\"smallwidth-pareto-v1\",",
            "\"source_commit\":\"{}\",\"harness_version\":\"{}\",",
            "\"hypothesis_credit\":\"{}\",\"width_bits\":{},",
            "\"family\":\"boundary_repair\",\"knob_name\":\"window_width\",",
            "\"knob_value\":{},\"knob_ratio\":{:.9},",
            "\"kernel_repetitions\":1,\"normalization_model\":\"adder-linear\",",
            "\"peak_qubits\":{},\"emitted_toffoli\":{},",
            "\"score_proxy\":{},\"q_per_n\":{:.9},",
            "\"t_per_n\":{:.9},\"t_per_n2\":{:.9},",
            "\"score_per_n2\":{:.9},\"peak_owner\":\"{}\",",
            "\"phase_maxima\":{},\"boundary_repair\":\"{}\",",
            "\"theoretical_fault_probability\":{:.12e},",
            "\"theoretical_fault_log2\":{},\"validation\":\"{}\"}}"
        ),
        SOURCE_COMMIT,
        HARNESS_VERSION,
        CREDIT,
        width,
        window,
        window as f64 / n,
        kernel.peak_qubits,
        kernel.emitted_toffoli,
        kernel.peak_qubits as u64 * kernel.emitted_toffoli as u64,
        q / n,
        t / n,
        t / (n * n),
        score / (n * n),
        kernel.peak_owner,
        json_phase_maxima(&kernel.phase_maxima),
        repair.name(),
        fault_probability,
        fault_log2,
        validation,
    );
}

pub(crate) fn main_entry() -> Result<(), String> {
    let widths = parse_widths()?;
    let validate = std::env::var("SMALLWIDTH_VALIDATE").ok().as_deref() == Some("1");
    let families = [
        Family::LowQ,
        Family::TopClean,
        Family::Windowed,
        Family::CoBinderTopClean,
    ];

    for width in widths {
        let max_blocks = parse_max_blocks(width);
        let mut passed = std::collections::BTreeSet::new();
        if validate && width < 256 {
            for family in families {
                for knob in validation_knobs(width, family, max_blocks) {
                    validate_kernel(width, family, knob)?;
                    passed.insert((family.name(), knob));
                }
            }
        }

        for family in families {
            let knobs: Vec<usize> = match family {
                Family::LowQ => vec![0],
                Family::TopClean | Family::CoBinderTopClean => (0..width).collect(),
                Family::Windowed => (1..=max_blocks).collect(),
            };
            for knob in knobs {
                let kernel = build_kernel(width, family, knob, false);
                let validation = if width == 256 {
                    "resource-only-u256-result-limit"
                } else if passed.contains(&(family.name(), knob)) {
                    "sampled-pass-64-lane"
                } else {
                    "not-run"
                };
                emit_row(width, family, knob, &kernel, validation);
            }
        }

        let repairs = [
            BoundaryRepair::ApproximateNoCin,
            BoundaryRepair::ExactWholeChunkWithChunkCin,
            BoundaryRepair::TopWindowWithEntryCarry,
        ];
        let windows = boundary_windows(width);
        for repair in repairs {
            for &window in &windows {
                // Whole-chunk exactness has no window knob: emit only W=n so
                // every row represents a distinct circuit.
                if repair == BoundaryRepair::ExactWholeChunkWithChunkCin && window != width {
                    continue;
                }
                let sampled = validate
                    && width < 256
                    && (window == 1
                        || window == width
                        || window == width.min(8)
                        || window == width.min(16)
                        || window == width.min(24));
                if sampled {
                    validate_boundary_kernel(width, repair, window)?;
                }
                let kernel = build_boundary_kernel(width, repair, window, false);
                let validation = if width == 256 {
                    "resource-only-u256-result-limit"
                } else if sampled {
                    "sampled-pass-64-lane"
                } else {
                    "not-run"
                };
                emit_boundary_row(width, repair, window, &kernel, validation);
            }
        }
    }
    Ok(())
}
