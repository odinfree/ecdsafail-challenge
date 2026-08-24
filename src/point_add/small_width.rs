//! Reduced-width research harness for the promoted ping-pong point-add stack.
//!
//! Hypothesis credit: Justin Drake, relayed by Oli on 2026-08-24.
//!
//! This module is intentionally separate from [`super::build`].  It exercises
//! the promoted replay adder and square primitives at small widths, while the
//! challenge's 256-bit build remains on its exact, fixed secp256k1 path.
//! `PointAddProxy` preserves the four-register ABI and the dominant liveness
//! geometry, but is an identity-valued resource proxy rather than a field-
//! correct affine point addition.  It must not be submitted or used as a
//! correctness receipt for the challenge.

use super::trailmix_ludicrous::BExt;
use super::*;
use crate::circuit::{analyze_ops, OperationType, QubitOrBit};
use crate::sim::Simulator;
use sha3::{
    digest::{ExtendableOutput, Update, XofReader},
    Shake256,
};
use std::collections::BTreeSet;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Mode {
    Adder,
    PointAddProxy,
}

impl Mode {
    pub fn parse(value: &str) -> Result<Self, String> {
        match value {
            "adder" => Ok(Self::Adder),
            "point-add-proxy" | "pa-proxy" => Ok(Self::PointAddProxy),
            _ => Err(format!("unknown mode {value:?}")),
        }
    }

    pub fn name(self) -> &'static str {
        match self {
            Self::Adder => "adder",
            Self::PointAddProxy => "point-add-proxy",
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Variant {
    Ripple,
    ChunkedApprox,
    ChunkedExactWindow,
}

impl Variant {
    pub fn parse(value: &str) -> Result<Self, String> {
        match value {
            "ripple" => Ok(Self::Ripple),
            "chunked-approx" | "approx" => Ok(Self::ChunkedApprox),
            "chunked-exact-window" | "exact-window" => Ok(Self::ChunkedExactWindow),
            _ => Err(format!("unknown variant {value:?}")),
        }
    }

    pub fn name(self) -> &'static str {
        match self {
            Self::Ripple => "ripple",
            Self::ChunkedApprox => "chunked-approx",
            Self::ChunkedExactWindow => "chunked-exact-window",
        }
    }
}

#[derive(Clone, Copy, Debug)]
pub struct Config {
    pub width: usize,
    pub mode: Mode,
    pub variant: Variant,
    pub ladder_budget: usize,
    pub random_batches: usize,
    pub exhaustive: bool,
}

#[derive(Clone, Debug)]
pub struct Metrics {
    pub width: usize,
    pub mode: &'static str,
    pub variant: &'static str,
    pub ladder_budget: usize,
    pub compare_window: usize,
    pub chunk_sizes: Vec<usize>,
    pub proxy_rounds: usize,
    pub toy_prime_hex: String,
    pub op_count: usize,
    pub emitted_toffoli: usize,
    pub hmr_count: usize,
    pub peak_live_qubits: u32,
    pub allocated_qubits: u64,
    pub classical_bits: u64,
    pub peak_phase: &'static str,
    pub executed_toffoli_avg: f64,
    pub checked_shots: usize,
    pub value_mismatches: usize,
    pub phase_garbage_batches: usize,
    pub dirty_ancilla_batches: usize,
}

impl Metrics {
    pub fn score_proxy(&self) -> u128 {
        u128::from(self.peak_live_qubits) * self.emitted_toffoli as u128
    }

    pub fn json(&self) -> String {
        let chunks = self
            .chunk_sizes
            .iter()
            .map(usize::to_string)
            .collect::<Vec<_>>()
            .join(",");
        format!(
            concat!(
                "{{\"width\":{},\"mode\":\"{}\",\"variant\":\"{}\",",
                "\"ladder_budget\":{},\"compare_window\":{},\"chunk_sizes\":[{}],",
                "\"proxy_rounds\":{},\"toy_prime_hex\":\"{}\",",
                "\"op_count\":{},\"emitted_toffoli\":{},\"hmr_count\":{},",
                "\"peak_live_qubits\":{},\"allocated_qubits\":{},\"classical_bits\":{},",
                "\"peak_phase\":\"{}\",\"score_proxy\":{},",
                "\"executed_toffoli_avg\":{:.6},\"checked_shots\":{},",
                "\"value_mismatches\":{},\"phase_garbage_batches\":{},",
                "\"dirty_ancilla_batches\":{}}}"
            ),
            self.width,
            self.mode,
            self.variant,
            self.ladder_budget,
            self.compare_window,
            chunks,
            self.proxy_rounds,
            self.toy_prime_hex,
            self.op_count,
            self.emitted_toffoli,
            self.hmr_count,
            self.peak_live_qubits,
            self.allocated_qubits,
            self.classical_bits,
            self.peak_phase,
            self.score_proxy(),
            self.executed_toffoli_avg,
            self.checked_shots,
            self.value_mismatches,
            self.phase_garbage_batches,
            self.dirty_ancilla_batches,
        )
    }
}

#[derive(Clone)]
struct Built {
    ops: Vec<Op>,
    peak_live_qubits: u32,
    peak_phase: &'static str,
    external_qubits: Vec<QubitId>,
    registers: Vec<Vec<QubitOrBit>>,
}

fn validate_config(config: Config) -> Result<(), String> {
    if !(2..=256).contains(&config.width) {
        return Err("width must be in 2..=256".into());
    }
    if config.variant != Variant::Ripple && config.ladder_budget == 0 {
        return Err("chunked variants require ladder_budget > 0".into());
    }
    if config.exhaustive && config.width > 8 {
        return Err("exhaustive validation is limited to width <= 8".into());
    }
    Ok(())
}

fn toy_prime(width: usize) -> U256 {
    if width == 256 {
        return SECP256K1_P;
    }
    let k = match width {
        32 | 64 => 1u64,
        96 => 79,
        128 => 157,
        _ => 1,
    };
    (U256::from(1u64) << width) - (U256::from(1u64) << (width / 8)) - U256::from(k)
}

fn proxy_rounds(width: usize) -> usize {
    (696 * width).div_ceil(256).max(2)
}

fn add_once(b: &mut B, addend: &[QubitId], acc: &[QubitId], config: Config) {
    match config.variant {
        Variant::Ripple => add_nbit_qq_fast(b, addend, acc),
        Variant::ChunkedApprox => {
            pingpong_div::add_chunked_measured_budgeted(b, addend, acc, None, config.ladder_budget)
        }
        Variant::ChunkedExactWindow => pingpong_div::add_chunked_measured_exact_window_budgeted(
            b,
            addend,
            acc,
            config.ladder_budget,
        ),
    }
}

fn add_then_sub(b: &mut B, addend: &[QubitId], acc: &[QubitId], config: Config) {
    add_once(b, addend, acc, config);
    for &q in acc {
        b.x(q);
    }
    add_once(b, addend, acc, config);
    for &q in acc {
        b.x(q);
    }
}

fn coordinate_round_trip(b: &mut B, target: &[QubitId], coordinate: &[BitId], config: Config) {
    let loaded = b.alloc_qubits(config.width);
    for i in 0..config.width {
        b.x_if_bit(loaded[i], coordinate[i]);
    }
    add_then_sub(b, &loaded, target, config);
    for i in (0..config.width).rev() {
        b.x_if_bit(loaded[i], coordinate[i]);
    }
    b.free_vec(&loaded);
}

fn build_adder(config: Config) -> Built {
    let mut b = B::new();
    let addend = b.alloc_qubits(config.width);
    let acc = b.alloc_qubits(config.width);
    b.set_phase("small_width_adder");
    add_once(&mut b, &addend, &acc, config);
    b.declare_qubit_register(&addend);
    b.declare_qubit_register(&acc);

    let peak_live_qubits = b.peak_qubits;
    let peak_phase = b.peak_phase;
    let external_qubits = addend.iter().chain(&acc).copied().collect();
    Built {
        ops: b.take_ops(),
        peak_live_qubits,
        peak_phase,
        external_qubits,
        registers: Vec::new(),
    }
}

fn build_point_add_proxy(config: Config) -> Built {
    let mut b = B::new();
    let x = b.alloc_qubits(config.width);
    let y = b.alloc_qubits(config.width);
    let ox = b.alloc_bits(config.width);
    let oy = b.alloc_bits(config.width);

    b.set_phase("small_width_coord_front");
    coordinate_round_trip(&mut b, &x, &ox, config);
    coordinate_round_trip(&mut b, &y, &oy, config);

    b.set_phase("small_width_replay_proxy");
    let rounds = proxy_rounds(config.width);
    let tape = b.alloc_qubits(rounds);
    for (i, &q) in tape.iter().enumerate() {
        b.cx(x[i % config.width], q);
    }
    let coefficient = b.alloc_qubits(config.width);
    for i in 0..config.width {
        b.cx(y[i], coefficient[i]);
    }
    for _ in 0..rounds {
        add_then_sub(&mut b, &x, &coefficient, config);
    }
    for i in (0..config.width).rev() {
        b.cx(y[i], coefficient[i]);
    }
    b.free_vec(&coefficient);
    for (i, &q) in tape.iter().enumerate().rev() {
        b.cx(x[i % config.width], q);
    }
    b.free_vec(&tape);

    b.set_phase("small_width_square_proxy");
    let product = b.alloc_qubits(2 * config.width);
    schoolbook_square_symmetric(&mut b, &x, &product);
    schoolbook_square_symmetric_inverse(&mut b, &x, &product);
    b.free_vec(&product);

    b.set_phase("small_width_coord_back");
    coordinate_round_trip(&mut b, &y, &oy, config);
    coordinate_round_trip(&mut b, &x, &ox, config);

    b.declare_qubit_register(&x);
    b.declare_qubit_register(&y);
    b.declare_bit_register(&ox);
    b.declare_bit_register(&oy);

    let peak_live_qubits = b.peak_qubits;
    let peak_phase = b.peak_phase;
    let external_qubits = x.iter().chain(&y).copied().collect();
    Built {
        ops: b.take_ops(),
        peak_live_qubits,
        peak_phase,
        external_qubits,
        registers: Vec::new(),
    }
}

fn low_mask(width: usize) -> U256 {
    if width == 256 {
        U256::MAX
    } else {
        (U256::from(1u64) << width) - U256::from(1u64)
    }
}

fn deterministic_value(reader: &mut sha3::Shake256Reader, width: usize) -> U256 {
    let mut bytes = [0u8; 32];
    reader.read(&mut bytes);
    U256::from_le_bytes(bytes) & low_mask(width)
}

fn validate(config: Config, built: &Built) -> (f64, usize, usize, usize, usize) {
    let (num_qubits, num_bits, _, registers) = analyze_ops(built.ops.iter());
    let external: BTreeSet<u64> = built.external_qubits.iter().map(|q| q.0).collect();
    let exhaustive_cases = if config.exhaustive {
        1usize << (2 * config.width)
    } else {
        config.random_batches.max(1) * 64
    };
    let batches = exhaustive_cases.div_ceil(64);
    let mut checked = 0usize;
    let mut value_mismatches = 0usize;
    let mut phase_garbage_batches = 0usize;
    let mut dirty_ancilla_batches = 0usize;
    let mut executed_toffoli = 0u128;

    for batch in 0..batches {
        let mut seed = Shake256::default();
        seed.update(b"small-width-harness-validation-v1");
        seed.update(&(config.width as u64).to_le_bytes());
        seed.update(&(batch as u64).to_le_bytes());
        seed.update(config.mode.name().as_bytes());
        seed.update(config.variant.name().as_bytes());
        seed.update(&(config.ladder_budget as u64).to_le_bytes());
        let mut reader = seed.finalize_xof();
        let mut simulator_seed = Shake256::default();
        simulator_seed.update(b"small-width-harness-simulator-v1");
        simulator_seed.update(&(batch as u64).to_le_bytes());
        let mut simulator_reader = simulator_seed.finalize_xof();
        let mut sim = Simulator::new(
            num_qubits as usize,
            num_bits as usize,
            &mut simulator_reader,
        );

        let remaining = exhaustive_cases - checked;
        let shots = remaining.min(64);
        let mut before = Vec::with_capacity(shots);
        for shot in 0..shots {
            let case = checked + shot;
            match config.mode {
                Mode::Adder => {
                    let addend = if config.exhaustive {
                        U256::from(case & ((1usize << config.width) - 1))
                    } else {
                        deterministic_value(&mut reader, config.width)
                    };
                    let acc = if config.exhaustive {
                        U256::from(case >> config.width)
                    } else {
                        deterministic_value(&mut reader, config.width)
                    };
                    sim.set_register(&registers[0], addend, shot);
                    sim.set_register(&registers[1], acc, shot);
                    before.push(vec![addend, acc]);
                }
                Mode::PointAddProxy => {
                    let values = (0..4)
                        .map(|_| deterministic_value(&mut reader, config.width))
                        .collect::<Vec<_>>();
                    for (register, &value) in registers.iter().zip(&values) {
                        sim.set_register(register, value, shot);
                    }
                    before.push(values);
                }
            }
        }

        sim.apply_iter(built.ops.iter());
        executed_toffoli += sim.stats.toffoli_gates as u128;
        let live_mask = if shots == 64 {
            u64::MAX
        } else {
            (1u64 << shots) - 1
        };
        if sim.phase & live_mask != 0 {
            phase_garbage_batches += 1;
        }
        if (0..num_qubits)
            .any(|q| !external.contains(&q) && (sim.qubit(QubitId(q)) & live_mask) != 0)
        {
            dirty_ancilla_batches += 1;
        }

        for shot in 0..shots {
            match config.mode {
                Mode::Adder => {
                    let expected = (before[shot][0] + before[shot][1]) & low_mask(config.width);
                    if sim.get_register(&registers[0], shot) != before[shot][0]
                        || sim.get_register(&registers[1], shot) != expected
                    {
                        value_mismatches += 1;
                    }
                }
                Mode::PointAddProxy => {
                    for (index, expected) in before[shot].iter().enumerate() {
                        if sim.get_register(&registers[index], shot) != *expected {
                            value_mismatches += 1;
                            break;
                        }
                    }
                }
            }
        }
        checked += shots;
    }

    (
        executed_toffoli as f64 / checked.max(1) as f64,
        checked,
        value_mismatches,
        phase_garbage_batches,
        dirty_ancilla_batches,
    )
}

pub fn run(config: Config) -> Result<Metrics, String> {
    validate_config(config)?;
    let mut built = match config.mode {
        Mode::Adder => build_adder(config),
        Mode::PointAddProxy => build_point_add_proxy(config),
    };
    let (allocated_qubits, classical_bits, _, registers) = analyze_ops(built.ops.iter());
    built.registers = registers;
    let op_count = built.ops.len();
    let emitted_toffoli = built
        .ops
        .iter()
        .filter(|op| matches!(op.kind, OperationType::CCX | OperationType::CCZ))
        .count();
    let hmr_count = built
        .ops
        .iter()
        .filter(|op| op.kind == OperationType::Hmr)
        .count();
    let (
        executed_toffoli_avg,
        checked_shots,
        value_mismatches,
        phase_garbage_batches,
        dirty_ancilla_batches,
    ) = validate(config, &built);
    let chunk_sizes = if config.variant == Variant::Ripple {
        vec![config.width]
    } else {
        pingpong_div::research_chunk_layout(config.width, config.ladder_budget)
            .iter()
            .map(|&(lo, hi)| hi - lo)
            .collect()
    };

    Ok(Metrics {
        width: config.width,
        mode: config.mode.name(),
        variant: config.variant.name(),
        ladder_budget: config.ladder_budget,
        compare_window: std::env::var("SUB4_PP_REPLAY_CHUNK_COMPARE")
            .ok()
            .and_then(|value| value.parse().ok())
            .unwrap_or(21),
        chunk_sizes,
        proxy_rounds: if config.mode == Mode::PointAddProxy {
            proxy_rounds(config.width)
        } else {
            0
        },
        toy_prime_hex: format!("{:#x}", toy_prime(config.width)),
        op_count,
        emitted_toffoli,
        hmr_count,
        peak_live_qubits: built.peak_live_qubits,
        allocated_qubits,
        classical_bits,
        peak_phase: built.peak_phase,
        executed_toffoli_avg,
        checked_shots,
        value_mismatches,
        phase_garbage_batches,
        dirty_ancilla_batches,
    })
}
