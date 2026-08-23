//! Diagnostic-only exact operation-site trace builder.
//!
//! This uses the same contestant build path as `build_circuit`, then writes
//! one source-site row per post-constprop operation.  The operation stream is
//! never changed and the generated trace stays outside Git.

use quantum_ecc::circuit::OperationType;
use std::fs::File;
use std::io::{BufWriter, Write};

#[allow(dead_code)]
#[path = "../point_add/mod.rs"]
mod point_add;

#[allow(unused_imports)]
use quantum_ecc::{circuit, sim, weierstrass_elliptic_curve};

fn main() {
    let output = std::env::args()
        .nth(1)
        .expect("usage: build_phase_trace OUTPUT.tsv");
    let ops = point_add::build();
    let sites = point_add::take_last_op_sites();
    assert_eq!(
        ops.len(),
        sites.len() + 96,
        "operation/site trace must omit exactly the cancelling nonce tail",
    );

    let file = File::create(&output).expect("create output trace");
    let mut writer = BufWriter::new(file);
    let mut rhmr_ordinal = 0u64;
    for (index, (op, (source, line, context))) in ops.iter().zip(sites).enumerate() {
        let ordinal = match op.kind {
            OperationType::R | OperationType::Hmr => {
                let value = rhmr_ordinal;
                rhmr_ordinal += 1;
                value.to_string()
            }
            _ => "-".to_owned(),
        };
        writeln!(
            writer,
            "{index}\t{source}\t{line}\t{context}\t{}\t{ordinal}",
            op.kind as u32
        )
        .expect("write output trace");
    }
    writer.flush().expect("flush output trace");
    eprintln!(
        "build-phase-trace: PASS ops={} rhmr={} output={}",
        ops.len(),
        rhmr_ordinal,
        output
    );
}
