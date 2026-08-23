//! Source-bound Fiat-Shamir prefix checkpoint for the exact Q1270 stream.
//!
//! This contains no circuit predictor. It builds the contestant stream,
//! checkpoints the nonce-independent SHAKE256 prefix, verifies the checkpoint
//! against the trusted full-stream SHAKE implementation, and writes PPFSCKP1.

#[allow(dead_code)]
#[path = "../point_add/mod.rs"]
mod point_add;

#[allow(unused_imports)]
use quantum_ecc::{circuit, sim, weierstrass_elliptic_curve};

use quantum_ecc::circuit::{Op, OperationType};
use sha3::{
    digest::{ExtendableOutput, Update, XofReader},
    Shake256,
};
use std::io::Write;

const EXPECTED_OPS: usize = 12_953_636;
const INHERITED_NONCE: u64 = 65_700_024_945_645;
const TAIL_OPS: usize = 96;
const ABSORB_BYTES_PER_OP: usize = 49;
const RATE: usize = 136;

const RC: [u64; 24] = [
    0x0000000000000001,
    0x0000000000008082,
    0x800000000000808a,
    0x8000000080008000,
    0x000000000000808b,
    0x0000000080000001,
    0x8000000080008081,
    0x8000000000008009,
    0x000000000000008a,
    0x0000000000000088,
    0x0000000080008009,
    0x000000008000000a,
    0x000000008000808b,
    0x800000000000008b,
    0x8000000000008089,
    0x8000000000008003,
    0x8000000000008002,
    0x8000000000000080,
    0x000000000000800a,
    0x800000008000000a,
    0x8000000080008081,
    0x8000000000008080,
    0x0000000080000001,
    0x8000000080008008,
];
const RHO: [u32; 24] = [
    1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 2, 14, 27, 41, 56, 8, 25, 43, 62, 18,
    39, 61, 20, 44,
];
const PIJ: [usize; 24] = [
    10, 7, 11, 17, 18, 3, 5, 16, 8, 21, 24, 4, 15, 23, 19, 13, 12, 2, 20, 14,
    22, 9, 6, 1,
];

fn keccakf(a: &mut [u64; 25]) {
    for &round_constant in &RC {
        let mut columns = [0u64; 5];
        for i in 0..5 {
            columns[i] = a[i] ^ a[i + 5] ^ a[i + 10] ^ a[i + 15] ^ a[i + 20];
        }
        for i in 0..5 {
            let delta = columns[(i + 4) % 5] ^ columns[(i + 1) % 5].rotate_left(1);
            let mut j = 0;
            while j < 25 {
                a[j + i] ^= delta;
                j += 5;
            }
        }
        let mut rotated = a[1];
        for i in 0..24 {
            let j = PIJ[i];
            let previous = a[j];
            a[j] = rotated.rotate_left(RHO[i]);
            rotated = previous;
        }
        let mut j = 0;
        while j < 25 {
            let row = [a[j], a[j + 1], a[j + 2], a[j + 3], a[j + 4]];
            for i in 0..5 {
                a[j + i] = row[i] ^ ((!row[(i + 1) % 5]) & row[(i + 2) % 5]);
            }
            j += 5;
        }
        a[0] ^= round_constant;
    }
}

#[derive(Clone)]
struct Sponge {
    state: [u64; 25],
    buffer: [u8; RATE],
    len: usize,
}

impl Sponge {
    fn new() -> Self {
        Self {
            state: [0u64; 25],
            buffer: [0u8; RATE],
            len: 0,
        }
    }

    fn permute_block(&mut self) {
        for i in 0..RATE / 8 {
            self.state[i] ^=
                u64::from_le_bytes(self.buffer[i * 8..i * 8 + 8].try_into().unwrap());
        }
        keccakf(&mut self.state);
    }

    fn absorb(&mut self, data: &[u8]) {
        let mut offset = 0;
        while offset < data.len() {
            let take = (RATE - self.len).min(data.len() - offset);
            self.buffer[self.len..self.len + take]
                .copy_from_slice(&data[offset..offset + take]);
            self.len += take;
            offset += take;
            if self.len == RATE {
                self.permute_block();
                self.len = 0;
            }
        }
    }

    fn finalize_into(mut self, out: &mut [u8]) {
        self.buffer[self.len..].fill(0);
        self.buffer[self.len] ^= 0x1f;
        self.buffer[RATE - 1] ^= 0x80;
        self.permute_block();
        let mut offset = 0;
        loop {
            let take = (out.len() - offset).min(RATE);
            for i in 0..take.div_ceil(8) {
                let lane = self.state[i].to_le_bytes();
                let n = take.min(i * 8 + 8) - i * 8;
                out[offset + i * 8..offset + i * 8 + n].copy_from_slice(&lane[..n]);
            }
            offset += take;
            if offset >= out.len() {
                break;
            }
            keccakf(&mut self.state);
        }
    }
}

fn op_bytes(op: &Op, out: &mut [u8; ABSORB_BYTES_PER_OP]) {
    out[0] = op.kind as u8;
    out[1..9].copy_from_slice(&op.q_control2.0.to_le_bytes());
    out[9..17].copy_from_slice(&op.q_control1.0.to_le_bytes());
    out[17..25].copy_from_slice(&op.q_target.0.to_le_bytes());
    out[25..33].copy_from_slice(&op.c_target.0.to_le_bytes());
    out[33..41].copy_from_slice(&op.c_condition.0.to_le_bytes());
    out[41..49].copy_from_slice(&op.r_target.0.to_le_bytes());
}

struct Checkpoint {
    sponge: Sponge,
    tail_template: [[u8; ABSORB_BYTES_PER_OP]; TAIL_OPS],
    n_ops: usize,
}

impl Checkpoint {
    fn build(ops: &[Op]) -> Self {
        assert_eq!(ops.len(), EXPECTED_OPS, "unexpected operation count");
        let mut sponge = Sponge::new();
        sponge.absorb(b"quantum_ecc-fiat-shamir-v2");
        sponge.absorb(&(ops.len() as u64).to_le_bytes());
        let cut = ops.len() - TAIL_OPS;
        const BATCH: usize = 4096;
        let mut chunk = vec![0u8; BATCH * ABSORB_BYTES_PER_OP];
        let mut record = [0u8; ABSORB_BYTES_PER_OP];
        let mut index = 0;
        while index < cut {
            let n = BATCH.min(cut - index);
            for j in 0..n {
                op_bytes(&ops[index + j], &mut record);
                chunk[j * ABSORB_BYTES_PER_OP..(j + 1) * ABSORB_BYTES_PER_OP]
                    .copy_from_slice(&record);
            }
            sponge.absorb(&chunk[..n * ABSORB_BYTES_PER_OP]);
            index += n;
        }

        let mut tail_template = [[0u8; ABSORB_BYTES_PER_OP]; TAIL_OPS];
        for k in 0..TAIL_OPS {
            assert_eq!(ops[cut + k].kind, OperationType::X, "tail op is not X");
            op_bytes(&ops[cut + k], &mut tail_template[k]);
        }
        Self {
            sponge,
            tail_template,
            n_ops: ops.len(),
        }
    }

    fn xof_for(&self, nonce: u64, out: &mut [u8]) {
        let mut sponge = self.sponge.clone();
        for k in 0..TAIL_OPS {
            let mut record = self.tail_template[k];
            let q = (nonce >> (k / 2)) & 1;
            record[17..25].copy_from_slice(&q.to_le_bytes());
            sponge.absorb(&record);
        }
        sponge.finalize_into(out);
    }

    fn dump(&self, path: &str) -> std::io::Result<()> {
        let mut file = std::io::BufWriter::new(std::fs::File::create(path)?);
        file.write_all(b"PPFSCKP1")?;
        file.write_all(&(self.n_ops as u64).to_le_bytes())?;
        file.write_all(&(self.sponge.len as u64).to_le_bytes())?;
        for lane in &self.sponge.state {
            file.write_all(&lane.to_le_bytes())?;
        }
        file.write_all(&self.sponge.buffer)?;
        for record in &self.tail_template {
            file.write_all(record)?;
        }
        file.flush()
    }
}

fn trusted_full_xof(ops: &[Op], out: &mut [u8]) {
    let mut hasher = Shake256::default();
    hasher.update(b"quantum_ecc-fiat-shamir-v2");
    hasher.update(&(ops.len() as u64).to_le_bytes());
    let mut record = [0u8; ABSORB_BYTES_PER_OP];
    for op in ops {
        op_bytes(op, &mut record);
        hasher.update(&record);
    }
    hasher.finalize_xof().read(out);
}

fn main() {
    let output = std::env::args()
        .nth(1)
        .expect("usage: dump_fs_checkpoint OUTPUT.bin");
    let ops = point_add::build();
    let checkpoint = Checkpoint::build(&ops);

    let mut checkpoint_probe = [0u8; 4096];
    let mut trusted_probe = [0u8; 4096];
    checkpoint.xof_for(INHERITED_NONCE, &mut checkpoint_probe);
    trusted_full_xof(&ops, &mut trusted_probe);
    assert_eq!(
        checkpoint_probe, trusted_probe,
        "checkpoint XOF diverges from trusted full-stream SHAKE256"
    );

    checkpoint.dump(&output).expect("write checkpoint");
    eprintln!(
        "dump-fs-checkpoint: PASS ops={} residual={} tail={} probe_bytes={} output={}",
        checkpoint.n_ops,
        checkpoint.sponge.len,
        TAIL_OPS,
        checkpoint_probe.len(),
        output
    );
}
