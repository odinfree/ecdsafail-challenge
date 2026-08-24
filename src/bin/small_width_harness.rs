//! CLI for reduced-width circuit research.  This is not a challenge builder.

#[allow(dead_code)]
#[path = "../point_add/mod.rs"]
mod point_add;

#[allow(unused_imports)]
use quantum_ecc::{circuit, sim, weierstrass_elliptic_curve};

use point_add::small_width::{Config, Mode, Variant};

fn usage() -> ! {
    eprintln!(
        "usage: small_width_harness [--width N] [--mode adder|point-add-proxy] \
         [--variant ripple|chunked-approx|chunked-exact-window] [--budget N] \
         [--compare-window N] [--batches N] [--exhaustive] [--canonical]"
    );
    std::process::exit(2);
}

fn value(args: &[String], index: &mut usize) -> String {
    *index += 1;
    args.get(*index).cloned().unwrap_or_else(|| usage())
}

fn main() {
    let args = std::env::args().collect::<Vec<_>>();
    let mut width = 64usize;
    let mut mode = Mode::Adder;
    let mut variant = Variant::ChunkedApprox;
    let mut budget = None;
    let mut batches = 4usize;
    let mut exhaustive = false;
    let mut canonical = false;
    let mut compare_window = None;

    let mut i = 1usize;
    while i < args.len() {
        match args[i].as_str() {
            "--width" => width = value(&args, &mut i).parse().unwrap_or_else(|_| usage()),
            "--mode" => mode = Mode::parse(&value(&args, &mut i)).unwrap_or_else(|e| panic!("{e}")),
            "--variant" => {
                variant = Variant::parse(&value(&args, &mut i)).unwrap_or_else(|e| panic!("{e}"))
            }
            "--budget" => budget = Some(value(&args, &mut i).parse().unwrap_or_else(|_| usage())),
            "--compare-window" => {
                compare_window = Some(
                    value(&args, &mut i)
                        .parse::<usize>()
                        .unwrap_or_else(|_| usage()),
                )
            }
            "--batches" => batches = value(&args, &mut i).parse().unwrap_or_else(|_| usage()),
            "--exhaustive" => exhaustive = true,
            "--canonical" => canonical = true,
            "-h" | "--help" => usage(),
            _ => usage(),
        }
        i += 1;
    }

    if let Some(window) = compare_window {
        std::env::set_var("SUB4_PP_REPLAY_CHUNK_COMPARE", window.to_string());
    }

    let widths = if canonical {
        vec![32usize, 64, 96, 128]
    } else {
        vec![width]
    };
    for width in widths {
        let ladder_budget = budget.unwrap_or_else(|| (96 * width).div_ceil(256).max(2));
        let config = Config {
            width,
            mode,
            variant,
            ladder_budget,
            random_batches: batches,
            exhaustive,
        };
        match point_add::small_width::run(config) {
            Ok(metrics) => println!("{}", metrics.json()),
            Err(error) => {
                eprintln!("error: {error}");
                std::process::exit(2);
            }
        }
    }
}
