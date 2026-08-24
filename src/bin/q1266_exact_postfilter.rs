//! Exact, source-bound postfilter for the Q1266 odd-passenger candidate.
//!
//! The input is the frozen base candidate stream. The requested 48-bit nonce
//! is applied in memory to the final 96 cancelling X operations before both
//! Fiat-Shamir hashing and simulation. This is a correctness postfilter for
//! rare classical-prefilter survivors, not a score or submission receipt.

use alloy_primitives::U256;
use quantum_ecc::circuit::{
    analyze_ops, BitId, Op, OperationType, QubitId, QubitOrBit, RegisterId,
};
use quantum_ecc::sim::Simulator;
use quantum_ecc::weierstrass_elliptic_curve::WeierstrassEllipticCurve;
use sha2::{Digest, Sha256};
use sha3::{
    digest::{ExtendableOutput, Update, XofReader},
    Shake256,
};
use std::fs::File;
use std::io::{BufReader, Read};

const MAGIC: &[u8; 8] = b"QECCOPSZ";
const OP_BYTES: usize = 56;
const EXPECTED_OPS: usize = 12_596_439;
const EXPECTED_SHA256: &str =
    "5f39b385c693a3f9179d7ba6d674c13676c0bb489bf2b07e208048b0e6ed561c";
const NUM_TESTS: usize = 9_024;
const TAIL_OPS: usize = 96;

fn fail(message: impl AsRef<str>) -> ! {
    eprintln!("q1266-exact-postfilter: FATAL: {}", message.as_ref());
    std::process::exit(2);
}

fn read_u64(bytes: &[u8], offset: usize) -> u64 {
    u64::from_le_bytes(bytes[offset..offset + 8].try_into().unwrap())
}

fn op_kind(value: u32) -> Option<OperationType> {
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

fn load_bound_ops(path: &str) -> Vec<Op> {
    let compressed = std::fs::read(path).unwrap_or_else(|error| fail(error.to_string()));
    let digest = format!("{:x}", Sha256::digest(&compressed));
    if digest != EXPECTED_SHA256 {
        fail(format!(
            "ops SHA-256 {digest} != frozen candidate {EXPECTED_SHA256}"
        ));
    }

    let mut file = File::open(path).unwrap_or_else(|error| fail(error.to_string()));
    let mut header = [0u8; 16];
    file.read_exact(&mut header)
        .unwrap_or_else(|error| fail(error.to_string()));
    if &header[..8] != MAGIC {
        fail("bad ops magic");
    }
    let count = u64::from_le_bytes(header[8..16].try_into().unwrap()) as usize;
    if count != EXPECTED_OPS {
        fail(format!("op count {count} != {EXPECTED_OPS}"));
    }
    let mut decoder = zstd::stream::read::Decoder::new(BufReader::new(file))
        .unwrap_or_else(|error| fail(error.to_string()));
    let mut ops = Vec::with_capacity(count);
    let mut record = [0u8; OP_BYTES];
    for index in 0..count {
        decoder
            .read_exact(&mut record)
            .unwrap_or_else(|error| fail(format!("op {index}: {error}")));
        let kind = op_kind(u32::from_le_bytes(record[0..4].try_into().unwrap()))
            .unwrap_or_else(|| fail(format!("op {index}: bad kind")));
        let op = Op {
            kind,
            q_control2: QubitId(read_u64(&record, 8)),
            q_control1: QubitId(read_u64(&record, 16)),
            q_target: QubitId(read_u64(&record, 24)),
            c_target: BitId(read_u64(&record, 32)),
            c_condition: BitId(read_u64(&record, 40)),
            r_target: RegisterId(read_u64(&record, 48)),
        };
        op.validate();
        ops.push(op);
    }
    ops
}

fn patch_nonce_tail(ops: &mut [Op], nonce: u64) {
    if nonce >= (1u64 << 48) {
        fail("nonce must fit the source's 48-bit tail");
    }
    let start = ops.len() - TAIL_OPS;
    for bit in 0..48 {
        let target = QubitId((nonce >> bit) & 1);
        let first = &ops[start + 2 * bit];
        let second = &ops[start + 2 * bit + 1];
        if first.kind != OperationType::X
            || second.kind != OperationType::X
            || first.q_target != second.q_target
        {
            fail(format!("tail pair {bit} is not a cancelling X/X identity"));
        }
        ops[start + 2 * bit].q_target = target;
        ops[start + 2 * bit + 1].q_target = target;
    }
}

fn parse_hex(value: &str) -> U256 {
    U256::from_str_radix(value, 16).unwrap()
}

fn curve() -> WeierstrassEllipticCurve {
    WeierstrassEllipticCurve {
        modulus: parse_hex("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F"),
        a: U256::ZERO,
        b: U256::from(7),
        gx: parse_hex("79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798"),
        gy: parse_hex("483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8"),
        order: parse_hex("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141"),
    }
}

type Input = (U256, U256, U256, U256);

fn derive_corpus(ops: &[Op]) -> (Vec<Input>, sha3::Shake256Reader) {
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
    let mut reader = hasher.finalize_xof();
    let curve = curve();
    let mut accepted = Vec::with_capacity(NUM_TESTS);
    for _ in 0..NUM_TESTS {
        let mut bytes = [[0u8; 32]; 2];
        XofReader::read(&mut reader, &mut bytes[0]);
        XofReader::read(&mut reader, &mut bytes[1]);
        let target = curve.mul(curve.gx, curve.gy, U256::from_le_bytes(bytes[0]));
        let offset = curve.mul(curve.gx, curve.gy, U256::from_le_bytes(bytes[1]));
        if target.0 == offset.0
            || (target.0.is_zero() && target.1.is_zero())
            || (offset.0.is_zero() && offset.1.is_zero())
        {
            continue;
        }
        accepted.push((target.0, target.1, offset.0, offset.1));
    }
    if accepted.len() != NUM_TESTS {
        fail(format!("accepted corpus {} != {NUM_TESTS}", accepted.len()));
    }
    (accepted, reader)
}

fn format_indices(indices: &[usize]) -> String {
    indices
        .iter()
        .map(usize::to_string)
        .collect::<Vec<_>>()
        .join(",")
}

fn main() {
    let mut args = std::env::args().skip(1);
    let path = args
        .next()
        .unwrap_or_else(|| fail("usage: q1266_exact_postfilter BASE_OPS NONCE"));
    let nonce = args
        .next()
        .and_then(|value| value.parse::<u64>().ok())
        .unwrap_or_else(|| fail("usage: q1266_exact_postfilter BASE_OPS NONCE"));
    if args.next().is_some() {
        fail("usage: q1266_exact_postfilter BASE_OPS NONCE");
    }

    let mut ops = load_bound_ops(&path);
    patch_nonce_tail(&mut ops, nonce);
    let (num_qubits, num_bits, _, registers) = analyze_ops(ops.iter());
    if registers.len() != 4 || num_qubits != 1266 {
        fail(format!(
            "resource shape Q={num_qubits} registers={} != Q1266/four registers",
            registers.len()
        ));
    }
    let (inputs, mut reader) = derive_corpus(&ops);
    let curve = curve();
    let mut sim = Simulator::new(num_qubits as usize, num_bits as usize, &mut reader);
    let mut classical = Vec::new();
    let mut raw_phase = Vec::new();
    let mut dirty_batches = 0usize;

    for batch in 0..(NUM_TESTS / 64) {
        sim.clear_for_shot();
        for lane in 0..64 {
            let input = inputs[batch * 64 + lane];
            sim.set_register(&registers[0], input.0, lane);
            sim.set_register(&registers[1], input.1, lane);
            sim.set_register(&registers[2], input.2, lane);
            sim.set_register(&registers[3], input.3, lane);
        }
        sim.apply_iter(ops.iter());
        for lane in 0..64 {
            let index = batch * 64 + lane;
            let input = inputs[index];
            let expected = curve.add(input.0, input.1, input.2, input.3);
            let got = (
                sim.get_register(&registers[0], lane),
                sim.get_register(&registers[1], lane),
            );
            if got != expected {
                classical.push(index);
            }
            if sim.phase & (1u64 << lane) != 0 {
                raw_phase.push(index);
            }
        }
        for register in &registers {
            for wire in register {
                if let QubitOrBit::Qubit(qubit) = *wire {
                    *sim.qubit_mut(qubit) = 0;
                }
            }
        }
        dirty_batches += usize::from(
            (0..num_qubits).any(|index| sim.qubit(QubitId(index)) != 0),
        );
    }

    let clean = classical.is_empty() && raw_phase.is_empty() && dirty_batches == 0;
    println!("classical_indices=[{}]", format_indices(&classical));
    println!("raw_phase_indices=[{}]", format_indices(&raw_phase));
    println!(
        concat!(
            "postfilter_summary nonce={} shots={} q={} bits={} ",
            "classical={} raw_phase={} dirty_batches={} clean={}"
        ),
        nonce,
        NUM_TESTS,
        num_qubits,
        num_bits,
        classical.len(),
        raw_phase.len(),
        dirty_batches,
        clean,
    );
    if !clean {
        std::process::exit(3);
    }
}
