//! Dedicated reduced-width resource probe for the promoted 6752417 source.
//!
//! This binary deliberately does not enter the challenge evaluator.  It
//! exercises width-parametric adder primitives from the submitted source and
//! writes machine-readable JSONL for the companion discontinuity detector.

#[allow(dead_code)]
#[path = "../point_add/mod.rs"]
mod point_add;

#[allow(unused_imports)]
use quantum_ecc::{circuit, sim, weierstrass_elliptic_curve};

fn main() {
    if let Err(error) = point_add::smallwidth_pareto::main_entry() {
        eprintln!("smallwidth_pareto: {error}");
        std::process::exit(2);
    }
}
