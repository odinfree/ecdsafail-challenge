//! Output-only trusted mask oracle for the frozen Q1270 routed-control stream.
//!
//! This binary deliberately imports no point-add implementation or predictor.
//! It loads the frozen operation stream with the trusted evaluator's framing,
//! validation, Fiat-Shamir derivation, reference curve, and `Simulator`; changes
//! only the cancelling 96-X nonce image; and executes two independent complete
//! 9,024-shot passes.  It emits masks only after every field agrees exactly.

use alloy_primitives::U256;
use quantum_ecc::circuit::{
    analyze_ops, BitId, Op, OperationType, QubitId, QubitOrBit, RegisterId, NO_BIT, NO_QUBIT,
    NO_REG,
};
use quantum_ecc::sim::Simulator;
use quantum_ecc::weierstrass_elliptic_curve::WeierstrassEllipticCurve;
use sha3::{
    digest::{ExtendableOutput, Update, XofReader},
    Shake256,
};
use std::fs::File;
use std::io::{BufReader, Read};

const MAGIC: &[u8; 8] = b"QECCOPSZ";
const ZSTD_WINDOW_LOG_MAX: u32 = 27;
const OP_BYTES: usize = 56;
const MAX_OPS: u64 = 4_000_000_000;
const EXPECTED_OPS: usize = 12_953_636;
const EXPECTED_QUBITS: u64 = 1270;
const EXPECTED_BITS: u64 = 961_070;
const NUM_TESTS: usize = 9024;
const BATCH: usize = 64;
const MASK_WORDS: usize = NUM_TESTS / BATCH;
const NONCE_BITS: usize = 48;
const NONCE_TAIL_OPS: usize = NONCE_BITS * 2;

fn op_kind_from_u32(value: u32) -> Option<OperationType> {
    Some(match value {
        0 => OperationType::Neg,
        1 => OperationType::Register,
        2 => OperationType::AppendToRegister,
        3 => OperationType::BitInvert,
        4 => OperationType::BitStore0,
        5 => OperationType::BitStore1,
        6 => OperationType::X,
        7 => OperationType::Z,
        8 => OperationType::CX,
        9 => OperationType::CZ,
        10 => OperationType::Swap,
        11 => OperationType::R,
        12 => OperationType::Hmr,
        13 => OperationType::CCX,
        14 => OperationType::CCZ,
        15 => OperationType::PushCondition,
        16 => OperationType::PopCondition,
        17 => OperationType::DebugPrint,
        _ => return None,
    })
}

fn read_u64(bytes: &[u8], offset: usize) -> u64 {
    u64::from_le_bytes(bytes[offset..offset + 8].try_into().unwrap())
}

fn load_ops(path: &str) -> Result<Vec<Op>, String> {
    let mut file = File::open(path).map_err(|error| format!("open {path}: {error}"))?;
    let mut header = [0_u8; 16];
    file.read_exact(&mut header)
        .map_err(|error| format!("{path}: short header: {error}"))?;
    if &header[..8] != MAGIC {
        return Err(format!("{path}: bad magic"));
    }
    let count = u64::from_le_bytes(header[8..].try_into().unwrap());
    if count > MAX_OPS {
        return Err(format!("{path}: op count {count} exceeds cap {MAX_OPS}"));
    }

    let mut decoder = zstd::stream::read::Decoder::new(BufReader::new(file))
        .map_err(|error| format!("{path}: zstd init: {error}"))?;
    decoder
        .window_log_max(ZSTD_WINDOW_LOG_MAX)
        .map_err(|error| format!("{path}: zstd window cap: {error}"))?;

    let mut ops = Vec::with_capacity(count as usize);
    let mut record = [0_u8; OP_BYTES];
    for index in 0..count as usize {
        decoder
            .read_exact(&mut record)
            .map_err(|error| format!("op {index}: short compressed record: {error}"))?;
        let raw_kind = u32::from_le_bytes(record[0..4].try_into().unwrap());
        let kind = op_kind_from_u32(raw_kind)
            .ok_or_else(|| format!("op {index}: unknown kind {raw_kind}"))?;
        if record[4..8] != [0_u8; 4] {
            return Err(format!("op {index}: nonzero reserved padding"));
        }
        let op = Op {
            kind,
            q_control2: QubitId(read_u64(&record, 8)),
            q_control1: QubitId(read_u64(&record, 16)),
            q_target: QubitId(read_u64(&record, 24)),
            c_target: BitId(read_u64(&record, 32)),
            c_condition: BitId(read_u64(&record, 40)),
            r_target: RegisterId(read_u64(&record, 48)),
        };
        let validated = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| op.validate()));
        if let Err(payload) = validated {
            let reason = payload
                .downcast_ref::<String>()
                .cloned()
                .or_else(|| {
                    payload
                        .downcast_ref::<&'static str>()
                        .map(|text| text.to_string())
                })
                .unwrap_or_else(|| "validation panic".to_string());
            return Err(format!("op {index}: {reason}"));
        }
        ops.push(op);
    }
    let mut trailing = [0_u8; 1];
    match decoder.read(&mut trailing) {
        Ok(0) => {}
        Ok(_) => return Err(format!("{path}: trailing decompressed data")),
        Err(error) => return Err(format!("{path}: trailing-data check: {error}")),
    }
    Ok(ops)
}

fn patch_nonce_tail(ops: &mut [Op], nonce: u64) -> Result<(), String> {
    if nonce >= (1_u64 << NONCE_BITS) {
        return Err(format!("nonce {nonce} is not below 2^48"));
    }
    if ops.len() != EXPECTED_OPS || ops.len() < NONCE_TAIL_OPS {
        return Err(format!("operation count {} != {EXPECTED_OPS}", ops.len()));
    }
    let start = ops.len() - NONCE_TAIL_OPS;
    for bit in 0..NONCE_BITS {
        let left = ops[start + bit * 2];
        let right = ops[start + bit * 2 + 1];
        for (copy, op) in [(0, left), (1, right)] {
            if op.kind != OperationType::X
                || op.q_control2 != NO_QUBIT
                || op.q_control1 != NO_QUBIT
                || op.q_target == NO_QUBIT
                || op.c_target != NO_BIT
                || op.c_condition != NO_BIT
                || op.r_target != NO_REG
            {
                return Err(format!(
                    "nonce-tail shape mismatch at bit {bit} copy {copy}"
                ));
            }
        }
        if left.q_target != right.q_target || left.q_target.0 > 1 {
            return Err(format!("nonce-tail pair mismatch at bit {bit}"));
        }
        let target = QubitId((nonce >> bit) & 1);
        ops[start + bit * 2].q_target = target;
        ops[start + bit * 2 + 1].q_target = target;
    }
    Ok(())
}

fn secp256k1() -> WeierstrassEllipticCurve {
    WeierstrassEllipticCurve {
        modulus: U256::from_str_radix(
            "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F",
            16,
        )
        .unwrap(),
        a: U256::from(0),
        b: U256::from(7),
        gx: U256::from_str_radix(
            "79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798",
            16,
        )
        .unwrap(),
        gy: U256::from_str_radix(
            "483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8",
            16,
        )
        .unwrap(),
        order: U256::from_str_radix(
            "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141",
            16,
        )
        .unwrap(),
    }
}

fn fiat_shamir_seed(ops: &[Op]) -> sha3::Shake256Reader {
    let mut hasher = Shake256::default();
    hasher.update(b"quantum_ecc-fiat-shamir-v2");
    hasher.update(&(ops.len() as u64).to_le_bytes());
    for op in ops {
        hasher.update(&[op.kind as u8]);
        hasher.update(&op.q_control2.0.to_le_bytes());
        hasher.update(&op.q_control1.0.to_le_bytes());
        hasher.update(&op.q_target.0.to_le_bytes());
        hasher.update(&op.c_target.0.to_le_bytes());
        hasher.update(&op.c_condition.0.to_le_bytes());
        hasher.update(&op.r_target.0.to_le_bytes());
    }
    hasher.finalize_xof()
}

#[derive(Clone, Debug, PartialEq, Eq)]
struct MaskReport {
    classical: Vec<u64>,
    raw_phase: Vec<u64>,
    clean_phase: Vec<u64>,
    ancilla: Vec<u64>,
    total_toffoli: u64,
    total_clifford: u64,
    shots: usize,
}

fn popcount(words: &[u64]) -> u64 {
    words.iter().map(|word| word.count_ones() as u64).sum()
}

fn nonzero_words(words: &[u64]) -> usize {
    words.iter().filter(|word| **word != 0).count()
}

fn run_complete_pass(
    ops: &[Op],
    registers: &[Vec<QubitOrBit>],
    total_qubits: u64,
    num_bits: u64,
) -> Result<MaskReport, String> {
    let curve = secp256k1();
    let mut xof = fiat_shamir_seed(ops);
    let mut targets = Vec::with_capacity(NUM_TESTS);
    let mut offsets = Vec::with_capacity(NUM_TESTS);
    let mut expected = Vec::with_capacity(NUM_TESTS);
    for _ in 0..NUM_TESTS {
        let mut random = [[0_u8; 32]; 2];
        XofReader::read(&mut xof, &mut random[0]);
        XofReader::read(&mut xof, &mut random[1]);
        let k1 = U256::from_le_bytes(random[0]);
        let k2 = U256::from_le_bytes(random[1]);
        let target = curve.mul(curve.gx, curve.gy, k1);
        let offset = curve.mul(curve.gx, curve.gy, k2);
        if target.0 == offset.0
            || (target.0.is_zero() && target.1.is_zero())
            || (offset.0.is_zero() && offset.1.is_zero())
        {
            continue;
        }
        targets.push(target);
        offsets.push(offset);
        expected.push(curve.add(target.0, target.1, offset.0, offset.1));
    }
    if targets.len() != NUM_TESTS {
        return Err(format!(
            "Fiat-Shamir test set has {} shots, expected {NUM_TESTS}",
            targets.len()
        ));
    }

    let mut simulator = Simulator::new(total_qubits as usize, num_bits as usize, &mut xof);
    let mut classical = Vec::with_capacity(MASK_WORDS);
    let mut raw_phase = Vec::with_capacity(MASK_WORDS);
    let mut clean_phase = Vec::with_capacity(MASK_WORDS);
    let mut ancilla = Vec::with_capacity(MASK_WORDS);

    for batch in 0..MASK_WORDS {
        simulator.clear_for_shot();
        for lane in 0..BATCH {
            let shot = batch * BATCH + lane;
            simulator.set_register(&registers[0], targets[shot].0, lane);
            simulator.set_register(&registers[1], targets[shot].1, lane);
            simulator.set_register(&registers[2], offsets[shot].0, lane);
            simulator.set_register(&registers[3], offsets[shot].1, lane);
        }
        simulator.apply_iter(ops.iter());

        let mut classical_word = 0_u64;
        for lane in 0..BATCH {
            let shot = batch * BATCH + lane;
            let got_x = simulator.get_register(&registers[0], lane);
            let got_y = simulator.get_register(&registers[1], lane);
            if got_x != expected[shot].0 || got_y != expected[shot].1 {
                classical_word |= 1_u64 << lane;
            }
        }
        let phase_word = simulator.phase;

        for register in registers {
            for item in register {
                if let QubitOrBit::Qubit(qubit) = *item {
                    *simulator.qubit_mut(qubit) = 0;
                }
            }
        }
        let mut ancilla_word = 0_u64;
        for qubit in 0..total_qubits {
            ancilla_word |= simulator.qubit(QubitId(qubit));
        }

        classical.push(classical_word);
        raw_phase.push(phase_word);
        clean_phase.push(phase_word & !classical_word);
        ancilla.push(ancilla_word);
    }

    Ok(MaskReport {
        classical,
        raw_phase,
        clean_phase,
        ancilla,
        total_toffoli: simulator.stats.toffoli_gates,
        total_clifford: simulator.stats.clifford_gates,
        shots: NUM_TESTS,
    })
}

fn validate_layout(registers: &[Vec<QubitOrBit>], qubits: u64, bits: u64) -> Result<(), String> {
    if (qubits, bits) != (EXPECTED_QUBITS, EXPECTED_BITS) {
        return Err(format!(
            "geometry ({qubits},{bits}) != ({EXPECTED_QUBITS},{EXPECTED_BITS})"
        ));
    }
    if registers.len() != 4 || registers.iter().any(|register| register.len() != 256) {
        return Err("register geometry is not four 256-bit registers".to_string());
    }
    if registers[0..2]
        .iter()
        .flatten()
        .any(|item| !matches!(item, QubitOrBit::Qubit(_)))
        || registers[2..4]
            .iter()
            .flatten()
            .any(|item| !matches!(item, QubitOrBit::Bit(_)))
    {
        return Err("register quantum/classical ABI mismatch".to_string());
    }
    Ok(())
}

fn main() -> Result<(), String> {
    let mut arguments = std::env::args().skip(1);
    let ops_path = arguments
        .next()
        .ok_or_else(|| "usage: q1270_trusted_masks <ops.bin> <nonce>".to_string())?;
    let nonce_text = arguments
        .next()
        .ok_or_else(|| "usage: q1270_trusted_masks <ops.bin> <nonce>".to_string())?;
    if arguments.next().is_some() {
        return Err("unexpected third argument".to_string());
    }
    if nonce_text.is_empty()
        || !nonce_text.bytes().all(|byte| byte.is_ascii_digit())
        || (nonce_text.len() > 1 && nonce_text.starts_with('0'))
    {
        return Err("nonce is not canonical unsigned decimal".to_string());
    }
    let nonce: u64 = nonce_text
        .parse()
        .map_err(|error| format!("nonce parse: {error}"))?;

    let mut ops = load_ops(&ops_path)?;
    patch_nonce_tail(&mut ops, nonce)?;
    let (qubits, bits, _num_registers, registers) = analyze_ops(ops.iter());
    validate_layout(&registers, qubits, bits)?;

    let first = run_complete_pass(&ops, &registers, qubits, bits)?;
    let second = run_complete_pass(&ops, &registers, qubits, bits)?;
    if first != second {
        return Err("independent complete passes differ".to_string());
    }

    println!(
        "MASKS nonce={nonce} qubits={qubits} bits={bits} ops={} shots={} \
         total_toffoli={} total_clifford={} classical={} raw_phase={} \
         raw_phase_batches={} clean_phase={} ancilla_shots={} ancilla_batches={}",
        ops.len(),
        first.shots,
        first.total_toffoli,
        first.total_clifford,
        popcount(&first.classical),
        popcount(&first.raw_phase),
        nonzero_words(&first.raw_phase),
        popcount(&first.clean_phase),
        popcount(&first.ancilla),
        nonzero_words(&first.ancilla),
    );
    for index in 0..MASK_WORDS {
        println!(
            "WORD {index:03} {:016x} {:016x} {:016x} {:016x}",
            first.classical[index],
            first.raw_phase[index],
            first.clean_phase[index],
            first.ancilla[index],
        );
    }
    Ok(())
}
