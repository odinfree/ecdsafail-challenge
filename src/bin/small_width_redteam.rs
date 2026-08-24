//! Dedicated local-only falsification probe for the reduced-width harness.

#[allow(dead_code)]
#[path = "../point_add/mod.rs"]
mod point_add;

#[allow(unused_imports)]
use quantum_ecc::{circuit, sim, weierstrass_elliptic_curve};

fn main() {
    point_add::small_width_redteam::main();
}
