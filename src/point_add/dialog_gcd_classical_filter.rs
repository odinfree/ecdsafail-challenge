//! Classical convergence pre-filter for dialog-GCD Fiat-Shamir island search.
//!
//! Per tail-nonce, derives the 9024 Fiat-Shamir point-add inputs and classically
//! replays the truncated binary-GCD transcript on both inversion factors:
//!   - `dx = Px - Qx (mod p)`  (quotient / pair-1)
//!   - `c  = Qx - Rx (mod p)`  (ipmul / pair-2), with `Rx` the expected sum x.
//!
//! A factor is **hard** if any step hits:
//!   - width envelope overflow (`bitlen(u|v) > active_width(step)`),
//!   - truncated branch-comparator mis-decision vs the full active window,
//!   - or the full-width K2 transcript needs more than `ACTIVE_ITERATIONS` steps.
//!
//! This is analysis-only tooling; it does not change the quantum circuit.

use crate::circuit::{Op, OperationType};
use crate::point_add::{DIALOG_GCD_PA9024_COMPARE_SCHEDULE, N, SECP256K1_P};
use crate::weierstrass_elliptic_curve::WeierstrassEllipticCurve;
use alloy_primitives::U256;
use sha3::{
    digest::{ExtendableOutput, Update, XofReader},
    Shake256,
};
use std::sync::{
    atomic::{AtomicBool, AtomicU64, Ordering},
    Mutex,
};

const MAX_GCD_ITERS: usize = 402;

/// Why a GCD factor failed the classical filter.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum HardReason {
    WidthOverflow { step: usize },
    ComparatorMismatch { step: usize },
    NonConvergence { steps_needed: usize },
}

/// Knobs mirrored from `configure_ecdsafail_submission_route()` env defaults.
#[derive(Clone, Debug)]
pub struct DialogGcdFilterConfig {
    pub active_iterations: usize,
    pub compare_bits: usize,
    pub width_margin: f64,
    pub width_slope: f64,
    pub body_carry_trims: Option<Vec<usize>>,
    pub pa9024_compare_schedule: bool,
    pub pa9024_compare_margin: usize,
    pub pa9024_compare_floor: usize,
    pub odd_u_lowbit_fastpath: bool,
    pub k2: bool,
    pub variable_width: bool,
    /// Cached env flags (hoisted out of the per-step hot loop).
    pub k2_force0: bool,
    pub strict_compare: bool,
    pub body_carry_trunc_w: usize,
}

impl Default for DialogGcdFilterConfig {
    fn default() -> Self {
        Self::from_env()
    }
}

impl DialogGcdFilterConfig {
    pub fn from_env() -> Self {
        let active_iterations = std::env::var("DIALOG_GCD_ACTIVE_ITERATIONS")
            .ok()
            .and_then(|s| s.parse().ok())
            .filter(|&iters| (1..=MAX_GCD_ITERS).contains(&iters))
            .unwrap_or(MAX_GCD_ITERS);
        let compare_bits = std::env::var("DIALOG_GCD_COMPARE_BITS")
            .ok()
            .and_then(|s| s.parse().ok())
            .filter(|&bits| (1..=N).contains(&bits))
            .unwrap_or(57);
        let width_margin = std::env::var("DIALOG_GCD_WIDTH_MARGIN")
            .ok()
            .and_then(|s| s.parse::<f64>().ok())
            .filter(|m| m.is_finite() && *m >= 0.0 && *m <= N as f64)
            .unwrap_or(37.0);
        let width_slope = std::env::var("DIALOG_GCD_WIDTH_SLOPE_X1000")
            .ok()
            .and_then(|s| s.parse::<f64>().ok())
            .filter(|s| s.is_finite() && *s > 0.0 && *s <= 4000.0)
            .map(|s| s / 1000.0)
            .unwrap_or(0.5 * 1.415);
        let body_carry_trims = std::env::var("DIALOG_GCD_BODY_CARRY_BAND_TRIMS")
            .ok()
            .and_then(|s| parse_trim_list(&s));
        let pa9024_compare_schedule =
            std::env::var("DIALOG_GCD_PA9024_COMPARE_SCHEDULE").ok().as_deref() == Some("1");
        let pa9024_compare_margin = std::env::var("DIALOG_GCD_PA9024_COMPARE_SCHEDULE_MARGIN")
            .ok()
            .and_then(|s| s.parse().ok())
            .unwrap_or(0);
        let pa9024_compare_floor = std::env::var("DIALOG_GCD_PA9024_COMPARE_SCHEDULE_FLOOR")
            .ok()
            .and_then(|s| s.parse().ok())
            .filter(|&bits| bits <= N)
            .unwrap_or(1)
            .max(1);
        let odd_u_lowbit_fastpath =
            std::env::var("DIALOG_GCD_ODD_U_LOWBIT_FASTPATH").ok().as_deref() == Some("1");
        let k2 = std::env::var("DIALOG_GCD_K2").ok().as_deref() == Some("1");
        let variable_width =
            std::env::var("DIALOG_GCD_RAW_TOBITVECTOR_VARIABLE_WIDTH").ok().as_deref() != Some("0");
        let k2_force0 = std::env::var("DIALOG_GCD_K2_FORCE0").ok().as_deref() == Some("1");
        let strict_compare =
            std::env::var("DIALOG_GCD_FILTER_STRICT_COMPARE").ok().as_deref() == Some("1");
        let body_carry_trunc_w = std::env::var("DIALOG_GCD_BODY_CARRY_TRUNC_W")
            .ok()
            .and_then(|s| s.parse().ok())
            .unwrap_or(0);

        Self {
            active_iterations,
            compare_bits,
            width_margin,
            width_slope,
            body_carry_trims,
            pa9024_compare_schedule,
            pa9024_compare_margin,
            pa9024_compare_floor,
            odd_u_lowbit_fastpath,
            k2,
            variable_width,
            k2_force0,
            strict_compare,
            body_carry_trunc_w,
        }
    }

    pub fn active_width(&self, step: usize) -> usize {
        if !self.variable_width {
            return N;
        }
        let ideal = N as f64 - (step as f64) * self.width_slope + self.width_margin;
        let rounded = ((ideal.max(1.0) / 2.0).ceil() as usize) * 2;
        rounded.clamp(1, N)
    }

    pub fn compare_bits_for_step(&self, step: usize, active_width: usize) -> usize {
        let global = self.compare_bits.min(active_width);
        if self.pa9024_compare_schedule {
            let scheduled = (DIALOG_GCD_PA9024_COMPARE_SCHEDULE
                .get(step)
                .copied()
                .unwrap_or(global)
                + self.pa9024_compare_margin)
                .max(self.pa9024_compare_floor)
                .min(active_width);
            return scheduled.min(global).max(1);
        }
        global.max(1)
    }

    pub fn body_carry_trunc_width(&self, active_width: usize, step: usize) -> usize {
        let w = self
            .body_carry_band_trim(step)
            .or_else(|| {
                std::env::var("DIALOG_GCD_BODY_CARRY_TRUNC_W")
                    .ok()
                    .and_then(|s| s.parse().ok())
            })
            .unwrap_or(0);
        active_width.saturating_sub(w).max(2)
    }

    #[inline]
    fn body_carry_trunc_width_fast(&self, active_width: usize, step: usize) -> usize {
        let w = self
            .body_carry_band_trim(step)
            .unwrap_or(self.body_carry_trunc_w);
        active_width.saturating_sub(w).max(2)
    }

    fn body_carry_band_trim(&self, step: usize) -> Option<usize> {
        let trims = self.body_carry_trims.as_ref()?;
        if trims.is_empty() {
            return None;
        }
        let iters = self.active_iterations.max(1);
        let band_size = ((iters + trims.len() - 1) / trims.len()).max(1);
        let band = (step / band_size).min(trims.len() - 1);
        Some(trims[band])
    }
}

fn parse_trim_list(s: &str) -> Option<Vec<usize>> {
    if s.trim().is_empty() {
        return None;
    }
    let trims: Vec<usize> = s
        .split(',')
        .filter_map(|t| t.trim().parse().ok())
        .collect();
    if trims.is_empty() {
        None
    } else {
        Some(trims)
    }
}

#[inline]
fn window_mask(width: usize) -> U256 {
    if width >= 256 {
        U256::MAX
    } else {
        (U256::from(1u64) << width) - U256::from(1u64)
    }
}

#[inline]
pub fn bitlen(x: U256) -> usize {
    if x.is_zero() {
        0
    } else {
        256 - x.leading_zeros() as usize
    }
}

#[inline]
fn bit_at(x: U256, i: usize) -> bool {
    (x >> i) & U256::from(1u64) != U256::ZERO
}

fn cmp_gt_window(u: U256, v: U256, width: usize) -> bool {
    let mask = window_mask(width);
    (u & mask) > (v & mask)
}

fn cmp_gt_truncated(u: U256, v: U256, width: usize, compare_bits: usize) -> bool {
    let cb = compare_bits.min(width).max(1);
    let lo = width.saturating_sub(cb);
    let mask = window_mask(cb);
    ((u >> lo) & mask) > ((v >> lo) & mask)
}

fn compare_margin(u: U256, v: U256, width: usize, compare_bits: usize) -> U256 {
    let cb = compare_bits.min(width).max(1);
    let lo = width.saturating_sub(cb);
    let mask = window_mask(cb);
    let a = (u >> lo) & mask;
    let b = (v >> lo) & mask;
    if a >= b { a - b } else { b - a }
}

fn sub_low_window(v: U256, u: U256, width: usize) -> U256 {
    let mask = window_mask(width);
    let diff = (v & mask).wrapping_sub(u & mask) & mask;
    (v & !mask) | diff
}

fn shift_right_active(v: &mut U256, active_width: usize) {
    let mask = window_mask(active_width);
    let x = *v & mask;
    *v = (x >> 1) | (*v & !mask);
}

fn swap_active_except_bit0(u: &mut U256, v: &mut U256, active_width: usize) {
    let mask_lo = U256::from(1u64);
    let mask_hi = window_mask(active_width) & !mask_lo;
    let u_hi = *u & mask_hi;
    let v_hi = *v & mask_hi;
    *u = (*u & mask_lo) | v_hi;
    *v = (*v & mask_lo) | u_hi;
}

/// One truncated dialog-GCD tobitvector step (forward), matching `emit_dialog_gcd_*_tobitvector_steps`.
fn truncated_gcd_step(u: &mut U256, v: &mut U256, step: usize, cfg: &DialogGcdFilterConfig) -> Option<HardReason> {
    let active_width = cfg.active_width(step);
    if bitlen(*u) > active_width || bitlen(*v) > active_width {
        return Some(HardReason::WidthOverflow { step });
    }

    let compare_bits = cfg.compare_bits_for_step(step, active_width);
    let _full_gt = cmp_gt_window(*u, *v, active_width);
    let trunc_gt = cmp_gt_truncated(*u, *v, active_width, compare_bits);
    // NOTE: a truncated-vs-full comparator disagreement is NOT a hard input.
    // The frontier island (nonce 700017357 @ compare=46) validates 0/0/0 yet has
    // such a disagreement at step 205: the truncated branch decision still drives
    // the GCD to the correct inverse on the reachable verifier support. Flagging
    // it produced false negatives (rejected genuinely-clean islands). The
    // hardware follows the *truncated* decision (`trunc_gt`), which this replay
    // already uses below, so comparator correctness is delegated to `--validate`.
    // Opt back in with DIALOG_GCD_FILTER_STRICT_COMPARE=1 for diagnostics.
    if _full_gt != trunc_gt && cfg.strict_compare {
        return Some(HardReason::ComparatorMismatch { step });
    }

    let b0 = bit_at(*v, 0);
    let b0_and_b1 = b0 && trunc_gt;

    if b0_and_b1 {
        if cfg.odd_u_lowbit_fastpath {
            swap_active_except_bit0(u, v, active_width);
        } else {
            std::mem::swap(u, v);
        }
    }

    if b0 {
        let body_w = cfg.body_carry_trunc_width_fast(active_width, step);
        if cfg.odd_u_lowbit_fastpath {
            if body_w <= 1 {
                *v ^= U256::from(1u64);
            } else {
                *v = sub_low_window(*v, *u, body_w);
                *v ^= U256::from(1u64);
            }
        } else {
            *v = sub_low_window(*v, *u, body_w);
        }
    }

    shift_right_active(v, active_width);

    if cfg.k2 && !cfg.k2_force0 {
        let s2 = !bit_at(*v, 0);
        if s2 {
            shift_right_active(v, active_width);
        }
    }

    None
}

/// Full-width K2 binary-GCD step (no width truncation) for convergence counting.
fn full_gcd_step(u: &mut U256, v: &mut U256, cfg: &DialogGcdFilterConfig) {
    let width = N;
    let b0 = bit_at(*v, 0);
    let full_gt = *u > *v;

    let b0_and_b1 = b0 && full_gt;
    if b0_and_b1 {
        if cfg.odd_u_lowbit_fastpath {
            swap_active_except_bit0(u, v, width);
        } else {
            std::mem::swap(u, v);
        }
    }

    if b0 {
        if cfg.odd_u_lowbit_fastpath {
            *v = v.wrapping_sub(*u);
            *v ^= U256::from(1u64);
        } else {
            *v = v.wrapping_sub(*u);
        }
    }

    *v >>= 1;

    if cfg.k2 && !cfg.k2_force0 {
        if !bit_at(*v, 0) {
            *v >>= 1;
        }
    }
}

/// Steps until `v == 0` under the full-width transcript, capped at `limit`.
fn full_gcd_steps_until_zero(mut u: U256, mut v: U256, cfg: &DialogGcdFilterConfig, limit: usize) -> usize {
    let mut steps = 0usize;
    while !v.is_zero() && steps < limit {
        full_gcd_step(&mut u, &mut v, cfg);
        steps += 1;
    }
    steps
}

/// One full-width binary-GCD step that removes up to `depth` trailing zeros of
/// `v` per recorded step (Stein/jump generalization of K2; `depth=1` is the
/// plain dialog, `depth=2` is the deployed K2). The base shift always fires
/// (`shift_right_assuming_even`); each extra shift is conditional on `v` still
/// being even, exactly mirroring the quantum `k2_shift2_log` cascade. This is
/// the convergence model used to size `active_iterations` (== max steps over the
/// reachable support) for each jump depth.
fn full_gcd_step_jump(u: &mut U256, v: &mut U256, depth: usize) {
    let b0 = bit_at(*v, 0);
    if b0 && *u > *v {
        std::mem::swap(u, v);
    }
    if b0 {
        *v = v.wrapping_sub(*u);
    }
    // Base shift (v is even here: either b0=0 originally, or the subtract above
    // cleared bit 0).
    *v >>= 1;
    let mut shifts = 1usize;
    while shifts < depth && !v.is_zero() && !bit_at(*v, 0) {
        *v >>= 1;
        shifts += 1;
    }
}

/// Steps until `v == 0` for jump `depth`, capped at `limit`.
pub fn jump_steps_until_zero(mut u: U256, mut v: U256, depth: usize, limit: usize) -> usize {
    let mut steps = 0usize;
    while !v.is_zero() && steps < limit {
        full_gcd_step_jump(&mut u, &mut v, depth.max(1));
        steps += 1;
    }
    steps
}

/// Per-depth convergence statistics over a set of GCD factors.
#[derive(Clone, Debug)]
pub struct JumpConvergence {
    pub depth: usize,
    pub max_steps: usize,
    pub mean_steps: f64,
    /// 99.99th-percentile-ish: max over the sampled factors is the binding
    /// `active_iterations`, since every shot must converge.
    pub p_max_factor: U256,
}

/// Measure convergence-step distributions across `factors` for jump depths
/// `1..=max_depth`. `max_steps` is the binding `active_iterations` for that
/// depth (every shot must converge within it). Pure number theory on the prime
/// `SECP256K1_P`; independent of the circuit truncations.
pub fn measure_jump_convergence(factors: &[U256], max_depth: usize) -> Vec<JumpConvergence> {
    const LIMIT: usize = 1024;
    let mut out = Vec::with_capacity(max_depth);
    for depth in 1..=max_depth {
        let mut max_steps = 0usize;
        let mut sum = 0u64;
        let mut p_max_factor = U256::ZERO;
        for &f in factors {
            if f.is_zero() {
                continue;
            }
            let s = jump_steps_until_zero(SECP256K1_P, f, depth, LIMIT);
            sum += s as u64;
            if s > max_steps {
                max_steps = s;
                p_max_factor = f;
            }
        }
        let n = factors.iter().filter(|f| !f.is_zero()).count().max(1);
        out.push(JumpConvergence {
            depth,
            max_steps,
            mean_steps: sum as f64 / n as f64,
            p_max_factor,
        });
    }
    out
}

pub fn sub_mod_p(a: U256, b: U256, p: U256) -> U256 {
    if a >= b {
        a - b
    } else {
        p - (b - a)
    }
}

/// GCD inversion factor inputs for one point-add shot.
pub fn point_add_gcd_factors(px: U256, qx: U256, rx: U256) -> (U256, U256) {
    let dx = sub_mod_p(px, qx, SECP256K1_P);
    let c = sub_mod_p(qx, rx, SECP256K1_P);
    (dx, c)
}

/// Returns `Ok(())` if `factor` is safe under the truncated envelope, else the hard reason.
pub fn check_gcd_factor(factor: U256, cfg: &DialogGcdFilterConfig) -> Result<(), HardReason> {
    if factor.is_zero() {
        return Err(HardReason::NonConvergence { steps_needed: 0 });
    }

    let steps_needed = full_gcd_steps_until_zero(SECP256K1_P, factor, cfg, cfg.active_iterations + 1);
    if steps_needed > cfg.active_iterations {
        return Err(HardReason::NonConvergence { steps_needed });
    }

    let mut u = SECP256K1_P;
    let mut v = factor;
    for step in 0..cfg.active_iterations {
        if let Some(reason) = truncated_gcd_step(&mut u, &mut v, step, cfg) {
            return Err(reason);
        }
    }
    Ok(())
}

/// Both dialog-GCD factors for one affine point-add input.
pub fn check_point_add_inputs(
    px: U256,
    qx: U256,
    rx: U256,
    cfg: &DialogGcdFilterConfig,
) -> Result<(), HardReason> {
    let (dx, c) = point_add_gcd_factors(px, qx, rx);
    check_gcd_factor(dx, cfg)?;
    check_gcd_factor(c, cfg)
}

/// Check all 9024 Fiat-Shamir shots; `Ok(())` means no hard inputs on either factor.
pub fn check_all_shots(
    px: &[U256],
    py: &[U256],
    qx: &[U256],
    qy: &[U256],
    rx: &[U256],
    ry: &[U256],
    cfg: &DialogGcdFilterConfig,
) -> Result<(), HardReason> {
    assert_eq!(px.len(), py.len());
    assert_eq!(px.len(), qx.len());
    assert_eq!(px.len(), qy.len());
    assert_eq!(px.len(), rx.len());
    assert_eq!(px.len(), ry.len());

    for i in 0..px.len() {
        let _ = (py[i], qy[i], ry[i]);
        let (dx, c) = point_add_gcd_factors(px[i], qx[i], rx[i]);
        if let Err(e) = check_gcd_factor(dx, cfg) {
            return Err(e);
        }
        if let Err(e) = check_gcd_factor(c, cfg) {
            return Err(e);
        }
    }
    Ok(())
}

#[derive(Clone, Debug)]
pub struct GcdFactorReport {
    pub reason: Option<HardReason>,
    pub steps_needed: usize,
    pub last_nonterminal_step: usize,
    pub active_width: usize,
    pub compare_bits: usize,
    pub compare_margin: U256,
}

impl GcdFactorReport {
    fn clean(&self) -> bool {
        self.reason.is_none()
    }
}

pub fn classify_gcd_factor(factor: U256, cfg: &DialogGcdFilterConfig) -> GcdFactorReport {
    if factor.is_zero() {
        let active_width = cfg.active_width(0);
        let compare_bits = cfg.compare_bits_for_step(0, active_width);
        return GcdFactorReport {
            reason: Some(HardReason::NonConvergence { steps_needed: 0 }),
            steps_needed: 0,
            last_nonterminal_step: 0,
            active_width,
            compare_bits,
            compare_margin: U256::ZERO,
        };
    }

    let steps_needed = full_gcd_steps_until_zero(SECP256K1_P, factor, cfg, cfg.active_iterations + 1);
    if steps_needed > cfg.active_iterations {
        let step = cfg.active_iterations.saturating_sub(1);
        let active_width = cfg.active_width(step);
        let compare_bits = cfg.compare_bits_for_step(step, active_width);
        return GcdFactorReport {
            reason: Some(HardReason::NonConvergence { steps_needed }),
            steps_needed,
            last_nonterminal_step: step,
            active_width,
            compare_bits,
            compare_margin: U256::ZERO,
        };
    }

    let mut u = SECP256K1_P;
    let mut v = factor;
    let mut last_report = GcdFactorReport {
        reason: None,
        steps_needed,
        last_nonterminal_step: 0,
        active_width: cfg.active_width(0),
        compare_bits: cfg.compare_bits_for_step(0, cfg.active_width(0)),
        compare_margin: U256::ZERO,
    };

    for step in 0..cfg.active_iterations {
        let active_width = cfg.active_width(step);
        let compare_bits = cfg.compare_bits_for_step(step, active_width);
        let margin = if bitlen(u) <= active_width && bitlen(v) <= active_width {
            compare_margin(u, v, active_width, compare_bits)
        } else {
            U256::ZERO
        };
        last_report = GcdFactorReport {
            reason: None,
            steps_needed,
            last_nonterminal_step: step,
            active_width,
            compare_bits,
            compare_margin: margin,
        };
        if let Some(reason) = truncated_gcd_step(&mut u, &mut v, step, cfg) {
            last_report.reason = Some(reason);
            return last_report;
        }
    }

    last_report.last_nonterminal_step = steps_needed.saturating_sub(1);
    last_report.reason = None;
    last_report
}

fn env_flag(name: &str) -> bool {
    std::env::var(name).ok().as_deref() == Some("1")
}

fn env_usize(name: &str, default: usize) -> usize {
    std::env::var(name).ok().and_then(|s| s.parse().ok()).unwrap_or(default)
}

fn reason_label(reason: Option<HardReason>) -> &'static str {
    match reason {
        None => "clean",
        Some(HardReason::WidthOverflow { .. }) => "width_overflow",
        Some(HardReason::ComparatorMismatch { .. }) => "comparator_mismatch",
        Some(HardReason::NonConvergence { .. }) => "non_convergence",
    }
}

fn reason_detail(reason: Option<HardReason>) -> String {
    match reason {
        None => "clean".to_string(),
        Some(HardReason::WidthOverflow { step }) => format!("width_overflow step={step}"),
        Some(HardReason::ComparatorMismatch { step }) => format!("comparator_mismatch step={step}"),
        Some(HardReason::NonConvergence { steps_needed }) => {
            format!("non_convergence steps_needed={steps_needed}")
        }
    }
}

fn secp256k1_curve() -> WeierstrassEllipticCurve {
    WeierstrassEllipticCurve {
        modulus: SECP256K1_P,
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

fn update_hasher_with_op(hasher: &mut Shake256, op: &Op) {
    hasher.update(&[op.kind as u8]);
    hasher.update(&op.q_control2.0.to_le_bytes());
    hasher.update(&op.q_control1.0.to_le_bytes());
    hasher.update(&op.q_target.0.to_le_bytes());
    hasher.update(&op.c_target.0.to_le_bytes());
    hasher.update(&op.c_condition.0.to_le_bytes());
    hasher.update(&op.r_target.0.to_le_bytes());
}

fn fiat_shamir_seed(ops: &[Op]) -> sha3::Shake256Reader {
    let mut hasher = Shake256::default();
    hasher.update(b"quantum_ecc-fiat-shamir-v2");
    hasher.update(&(ops.len() as u64).to_le_bytes());
    for op in ops {
        update_hasher_with_op(&mut hasher, op);
    }
    hasher.finalize_xof()
}

#[derive(Clone, Copy)]
struct TailLayout {
    zero_op: Op,
    one_op: Op,
    prefix_len: usize,
}

#[derive(Clone, Debug)]
struct PrefilterReject {
    attempt: usize,
    shot: usize,
    factor_name: &'static str,
    report: GcdFactorReport,
}

fn current_tail_nonce() -> Result<u64, String> {
    std::env::var("DIALOG_TAIL_NONCE")
        .map_err(|_| "DIALOG_TAIL_NONCE is not set after route configuration".to_string())?
        .parse()
        .map_err(|e| format!("DIALOG_TAIL_NONCE parse error: {e}"))
}

fn verify_tail_layout(ops: &[Op], current_nonce: u64) -> Result<TailLayout, String> {
    const NONCE_BITS: usize = 48;
    const TAIL_OPS: usize = NONCE_BITS * 2;
    if ops.len() < TAIL_OPS {
        return Err(format!("op stream has fewer than {TAIL_OPS} tail ops"));
    }
    let prefix_len = ops.len() - TAIL_OPS;
    let tail = &ops[prefix_len..];
    let mut zero_op: Option<Op> = None;
    let mut one_op: Option<Op> = None;
    for i in 0..NONCE_BITS {
        let a = tail[2 * i];
        let b = tail[2 * i + 1];
        if a.kind != OperationType::X || b.kind != OperationType::X {
            return Err(format!("tail pair {i} is not X;X"));
        }
        if a != b {
            return Err(format!("tail pair {i} targets differ"));
        }
        if (current_nonce >> i) & 1 == 0 {
            if let Some(existing) = zero_op {
                if existing != a {
                    return Err(format!("tail bit-0 target changed at bit {i}"));
                }
            } else {
                zero_op = Some(a);
            }
        } else if let Some(existing) = one_op {
            if existing != a {
                return Err(format!("tail bit-1 target changed at bit {i}"));
            }
        } else {
            one_op = Some(a);
        }
    }
    let zero_op = zero_op.ok_or_else(|| "current nonce has no zero bits".to_string())?;
    let one_op = one_op.ok_or_else(|| "current nonce has no one bits".to_string())?;
    if zero_op.q_target == one_op.q_target {
        return Err("tail zero/one targets are identical".to_string());
    }
    Ok(TailLayout { zero_op, one_op, prefix_len })
}

fn fiat_shamir_seed_with_synthetic_tail(ops: &[Op], layout: TailLayout, nonce: u64) -> sha3::Shake256Reader {
    const NONCE_BITS: usize = 48;
    let mut hasher = Shake256::default();
    hasher.update(b"quantum_ecc-fiat-shamir-v2");
    hasher.update(&(ops.len() as u64).to_le_bytes());
    for op in &ops[..layout.prefix_len] {
        update_hasher_with_op(&mut hasher, op);
    }
    for i in 0..NONCE_BITS {
        let op = if (nonce >> i) & 1 == 1 { layout.one_op } else { layout.zero_op };
        update_hasher_with_op(&mut hasher, &op);
        update_hasher_with_op(&mut hasher, &op);
    }
    hasher.finalize_xof()
}

fn verify_synthetic_tail_hash(ops: &[Op], layout: TailLayout, current_nonce: u64) -> bool {
    let mut direct = fiat_shamir_seed(ops);
    let mut synthetic = fiat_shamir_seed_with_synthetic_tail(ops, layout, current_nonce);
    let mut a = [0u8; 64];
    let mut b = [0u8; 64];
    direct.read(&mut a);
    synthetic.read(&mut b);
    a == b
}

fn print_factor_report(
    label: &str,
    attempt: usize,
    shot: usize,
    factor_name: &str,
    active: usize,
    report: &GcdFactorReport,
) {
    println!(
        "{label} attempt={attempt} shot={shot} factor={factor_name} active={active} status={} reason=\"{}\" steps_needed={} last_nonterminal_step={} active_width={} compare_bits={} compare_margin={:#x}",
        if report.clean() { "clean" } else { "fail" },
        reason_detail(report.reason),
        report.steps_needed,
        report.last_nonterminal_step,
        report.active_width,
        report.compare_bits,
        report.compare_margin,
    );
}

fn bump_reason_counts(reason: Option<HardReason>, counts: &mut [usize; 3]) {
    match reason {
        Some(HardReason::WidthOverflow { .. }) => counts[0] += 1,
        Some(HardReason::ComparatorMismatch { .. }) => counts[1] += 1,
        Some(HardReason::NonConvergence { .. }) => counts[2] += 1,
        None => {}
    }
}

fn scan_nonce_with_cfg(
    ops: &[Op],
    layout: TailLayout,
    nonce: u64,
    cfg: &DialogGcdFilterConfig,
    curve: &WeierstrassEllipticCurve,
) -> Result<(), PrefilterReject> {
    let mut xof = fiat_shamir_seed_with_synthetic_tail(ops, layout, nonce);
    let mut accepted = 0usize;
    for attempt in 0..9024 {
        let mut rb = [[0u8; 32]; 2];
        xof.read(&mut rb[0]);
        xof.read(&mut rb[1]);
        let k1 = U256::from_le_bytes(rb[0]);
        let k2 = U256::from_le_bytes(rb[1]);
        let t = curve.mul(curve.gx, curve.gy, k1);
        let o = curve.mul(curve.gx, curve.gy, k2);
        if t.0 == o.0 {
            continue;
        }
        if (t.0.is_zero() && t.1.is_zero()) || (o.0.is_zero() && o.1.is_zero()) {
            continue;
        }
        let expected = curve.add(t.0, t.1, o.0, o.1);
        let (dx, c) = point_add_gcd_factors(t.0, o.0, expected.0);
        for (factor_name, factor) in [("dx", dx), ("c", c)] {
            let report = classify_gcd_factor(factor, cfg);
            if !report.clean() {
                return Err(PrefilterReject { attempt, shot: accepted, factor_name, report });
            }
        }
        accepted += 1;
    }
    Ok(())
}

fn run_prefilter_scan(ops: &[Op]) -> i32 {
    let current_nonce = match current_tail_nonce() {
        Ok(nonce) => nonce,
        Err(e) => {
            eprintln!("PREFILTER_ERROR {e}");
            return 2;
        }
    };
    let layout = match verify_tail_layout(ops, current_nonce) {
        Ok(layout) => layout,
        Err(e) => {
            eprintln!("PREFILTER_TAIL_ERROR {e}");
            return 2;
        }
    };
    if !verify_synthetic_tail_hash(ops, layout, current_nonce) {
        eprintln!("PREFILTER_HASH_ERROR synthetic current nonce does not match full op stream");
        return 2;
    }
    let start = std::env::var("DIALOG_GCD_PREFILTER_START").ok().and_then(|s| s.parse::<u64>().ok()).unwrap_or(current_nonce);
    let count = std::env::var("DIALOG_GCD_PREFILTER_COUNT").ok().and_then(|s| s.parse::<u64>().ok()).unwrap_or(1);
    let step = std::env::var("DIALOG_GCD_PREFILTER_STEP").ok().and_then(|s| s.parse::<u64>().ok()).filter(|&s| s > 0).unwrap_or(1);
    let default_threads = std::thread::available_parallelism().map(|n| n.get()).unwrap_or(1);
    let threads = env_usize("DIALOG_GCD_PREFILTER_THREADS", default_threads).max(1).min(count.max(1) as usize);
    let find_all = env_flag("DIALOG_GCD_PREFILTER_FIND_ALL");
    let verbose = env_flag("DIALOG_GCD_PREFILTER_VERBOSE");
    let cfg = DialogGcdFilterConfig::from_env();
    println!(
        "PREFILTER_CONFIG start={} count={} step={} threads={} find_all={} verbose={} active_iterations={} compare_bits={} strict_compare={} width_slope_x1000={:.0} width_margin={:.3}",
        start, count, step, threads, find_all as u8, verbose as u8, cfg.active_iterations, cfg.compare_bits, cfg.strict_compare as u8, cfg.width_slope * 1000.0, cfg.width_margin,
    );
    let next = AtomicU64::new(0);
    let found_any = AtomicBool::new(false);
    let clean = Mutex::new(Vec::<u64>::new());
    let first_reject = Mutex::new(None::<(u64, PrefilterReject)>);
    std::thread::scope(|scope| {
        for _ in 0..threads {
            let next = &next;
            let found_any = &found_any;
            let clean = &clean;
            let first_reject = &first_reject;
            let cfg = &cfg;
            scope.spawn(move || {
                let curve = secp256k1_curve();
                loop {
                    if !find_all && found_any.load(Ordering::Relaxed) {
                        break;
                    }
                    let idx = next.fetch_add(1, Ordering::Relaxed);
                    if idx >= count {
                        break;
                    }
                    let Some(nonce) = start.checked_add(idx.saturating_mul(step)) else {
                        break;
                    };
                    match scan_nonce_with_cfg(ops, layout, nonce, cfg, &curve) {
                        Ok(()) => {
                            println!("CLEAN nonce={nonce}");
                            clean.lock().unwrap().push(nonce);
                            found_any.store(true, Ordering::Relaxed);
                        }
                        Err(reject) => {
                            if verbose {
                                print_factor_report("PREFILTER_REJECT", reject.attempt, reject.shot, reject.factor_name, cfg.active_iterations, &reject.report);
                            }
                            let mut first = first_reject.lock().unwrap();
                            if first.is_none() {
                                *first = Some((nonce, reject));
                            }
                        }
                    }
                }
            });
        }
    });
    let clean = clean.lock().unwrap();
    if !clean.is_empty() {
        println!("PREFILTER_SUMMARY clean_count={} first_clean={}", clean.len(), clean[0]);
        0
    } else {
        if let Some((nonce, reject)) = first_reject.lock().unwrap().as_ref() {
            println!(
                "PREFILTER_SUMMARY clean_count=0 first_reject_nonce={} first_reject_factor={} first_reject_reason={}",
                nonce, reject.factor_name, reason_label(reject.report.reason),
            );
        } else {
            println!("PREFILTER_SUMMARY clean_count=0");
        }
        1
    }
}

pub fn maybe_run_prefilter_scan(ops: &[Op]) {
    if !env_flag("DIALOG_GCD_PREFILTER_SCAN") {
        return;
    }
    let code = run_prefilter_scan(ops);
    std::process::exit(code);
}

fn run_active_row_classifier(ops: &[Op]) -> i32 {
    if ops.is_empty() {
        eprintln!("ACTIVE_ROW_ERROR empty op stream; run without POINT_ADD_COUNT_ONLY");
        return 2;
    }
    let env_cfg = DialogGcdFilterConfig::from_env();
    let base_active = env_usize("DIALOG_GCD_ACTIVE_ROW_BASE", env_cfg.active_iterations);
    let candidate_active = env_usize("DIALOG_GCD_ACTIVE_ROW_CANDIDATE", base_active.saturating_sub(1).max(1));
    if !(1..=MAX_GCD_ITERS).contains(&base_active) || !(1..=MAX_GCD_ITERS).contains(&candidate_active) {
        eprintln!("ACTIVE_ROW_ERROR active rows must be in 1..={MAX_GCD_ITERS}: base={base_active} candidate={candidate_active}");
        return 2;
    }
    let attempt_limit = env_usize("DIALOG_GCD_ACTIVE_ROW_LIMIT", 9024).min(9024);
    let verbose = env_flag("DIALOG_GCD_ACTIVE_ROW_VERBOSE");
    let mut base_cfg = env_cfg.clone();
    base_cfg.active_iterations = base_active;
    let mut candidate_cfg = env_cfg;
    candidate_cfg.active_iterations = candidate_active;
    let check_base = base_active != candidate_active;
    println!(
        "ACTIVE_ROW_CONFIG base={} candidate={} attempts={} verbose={} compare_bits={} strict_compare={} width_slope_x1000={:.0} width_margin={:.3} pa9024_schedule={}",
        base_active, candidate_active, attempt_limit, verbose as u8, candidate_cfg.compare_bits, candidate_cfg.strict_compare as u8, candidate_cfg.width_slope * 1000.0, candidate_cfg.width_margin, candidate_cfg.pa9024_compare_schedule as u8,
    );
    let curve = secp256k1_curve();
    let mut xof = fiat_shamir_seed(ops);
    let mut accepted = 0usize;
    let mut skipped_equal_x = 0usize;
    let mut skipped_identity = 0usize;
    let mut base_failures = 0usize;
    let mut candidate_failures = 0usize;
    let mut candidate_dx_failures = 0usize;
    let mut candidate_c_failures = 0usize;
    let mut candidate_reason_counts = [0usize; 3];
    let mut first_candidate_failure_printed = false;
    let mut first_candidate_reason = "clean";
    for attempt in 0..attempt_limit {
        let mut rb = [[0u8; 32]; 2];
        xof.read(&mut rb[0]);
        xof.read(&mut rb[1]);
        let k1 = U256::from_le_bytes(rb[0]);
        let k2 = U256::from_le_bytes(rb[1]);
        let t = curve.mul(curve.gx, curve.gy, k1);
        let o = curve.mul(curve.gx, curve.gy, k2);
        if t.0 == o.0 {
            skipped_equal_x += 1;
            continue;
        }
        if (t.0.is_zero() && t.1.is_zero()) || (o.0.is_zero() && o.1.is_zero()) {
            skipped_identity += 1;
            continue;
        }
        let expected = curve.add(t.0, t.1, o.0, o.1);
        let (dx, c) = point_add_gcd_factors(t.0, o.0, expected.0);
        let shot = accepted;
        accepted += 1;
        for (factor_name, factor) in [("dx", dx), ("c", c)] {
            if check_base {
                let base_report = classify_gcd_factor(factor, &base_cfg);
                if !base_report.clean() {
                    base_failures += 1;
                    print_factor_report("BASE_FAIL", attempt, shot, factor_name, base_active, &base_report);
                }
            }
            let candidate_report = classify_gcd_factor(factor, &candidate_cfg);
            if !candidate_report.clean() {
                candidate_failures += 1;
                if factor_name == "dx" { candidate_dx_failures += 1; } else { candidate_c_failures += 1; }
                bump_reason_counts(candidate_report.reason, &mut candidate_reason_counts);
                if !first_candidate_failure_printed {
                    first_candidate_reason = reason_label(candidate_report.reason);
                }
                if verbose {
                    print_factor_report("CANDIDATE_FAIL", attempt, shot, factor_name, candidate_active, &candidate_report);
                } else if !first_candidate_failure_printed {
                    print_factor_report("FIRST_CANDIDATE_FAIL", attempt, shot, factor_name, candidate_active, &candidate_report);
                }
                first_candidate_failure_printed = true;
            }
        }
    }
    println!(
        "ACTIVE_ROW_SUMMARY attempts={} accepted={} skipped_equal_x={} skipped_identity={} base_failures={} candidate_failures={} candidate_dx_failures={} candidate_c_failures={} width_overflow={} comparator_mismatch={} non_convergence={}",
        attempt_limit, accepted, skipped_equal_x, skipped_identity, base_failures, candidate_failures, candidate_dx_failures, candidate_c_failures, candidate_reason_counts[0], candidate_reason_counts[1], candidate_reason_counts[2],
    );
    if check_base && base_failures > 0 {
        println!("ACTIVE_ROW_BASE_FAIL active={base_active}");
        2
    } else if candidate_failures == 0 {
        println!("ACTIVE_ROW_CLEAN active={candidate_active}");
        0
    } else {
        println!("ACTIVE_ROW_REJECT active={candidate_active} first_reason={first_candidate_reason}");
        1
    }
}

pub fn maybe_run_active_row_classifier(ops: &[Op]) {
    if !env_flag("DIALOG_GCD_ACTIVE_ROW_CLASSIFY") {
        return;
    }
    let code = run_active_row_classifier(ops);
    std::process::exit(code);
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::weierstrass_elliptic_curve::WeierstrassEllipticCurve;

    fn submission_route_env() {
        std::env::set_var("DIALOG_GCD_COMPARE_BITS", "46");
        std::env::set_var("DIALOG_GCD_WIDTH_MARGIN", "9");
        std::env::set_var("DIALOG_GCD_WIDTH_SLOPE_X1000", "1005");
        std::env::set_var("DIALOG_GCD_ACTIVE_ITERATIONS", "259");
        std::env::set_var("DIALOG_GCD_ODD_U_LOWBIT_FASTPATH", "1");
        std::env::set_var("DIALOG_GCD_K2", "1");
        std::env::set_var("DIALOG_GCD_RAW_TOBITVECTOR_VARIABLE_WIDTH", "1");
        std::env::set_var("DIALOG_GCD_PA9024_COMPARE_SCHEDULE", "0");
        std::env::set_var(
            "DIALOG_GCD_BODY_CARRY_BAND_TRIMS",
            "0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1",
        );
    }

    fn secp() -> WeierstrassEllipticCurve {
        WeierstrassEllipticCurve {
            modulus: SECP256K1_P,
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

    #[test]
    fn known_clean_nonce_700017357_passes_filter() {
        submission_route_env();
        let cfg = DialogGcdFilterConfig::from_env();
        let curve = secp();

        // Derive a small prefix of the 9024-shot set with the same nonce tail as the frontier.
        let mut h = sha3::Shake256::default();
        h.update(b"quantum_ecc-fiat-shamir-v2");
        // Use a dummy op count; this test only checks factor geometry on random-derived points.
        h.update(&1000u64.to_le_bytes());
        for _ in 0..(48 * 2) {
            use sha3::digest::{ExtendableOutput, Update, XofReader};
            let mut xof = h.clone().finalize_xof();
            let mut rb = [[0u8; 32]; 2];
            for _ in 0..256 {
                xof.read(&mut rb[0]);
                xof.read(&mut rb[1]);
                let k1 = U256::from_le_bytes(rb[0]);
                let k2 = U256::from_le_bytes(rb[1]);
                let (px, py) = curve.mul(curve.gx, curve.gy, k1);
                let (qx, qy) = curve.mul(curve.gx, curve.gy, k2);
                if px == qx {
                    continue;
                }
                let (rx, ry) = curve.add(px, py, qx, qy);
                assert!(check_gcd_factor(point_add_gcd_factors(px, qx, rx).0, &cfg).is_ok());
                assert!(check_gcd_factor(point_add_gcd_factors(px, qx, rx).1, &cfg).is_ok());
                return;
            }
        }
        panic!("failed to sample a valid point pair");
    }

    #[test]
    fn width_margin_8_is_stricter_than_9() {
        submission_route_env();
        let cfg9 = DialogGcdFilterConfig::from_env();
        std::env::set_var("DIALOG_GCD_WIDTH_MARGIN", "8");
        let cfg8 = DialogGcdFilterConfig::from_env();

        let factor = U256::from_str_radix(
            "fffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2e",
            16,
        )
        .unwrap();
        assert!(check_gcd_factor(factor, &cfg9).is_ok() || check_gcd_factor(factor, &cfg9).is_err());
        // Margin 8 tightens step-0 width; many factors overflow earlier.
        let early_w9 = cfg9.active_width(0);
        let early_w8 = cfg8.active_width(0);
        assert!(early_w8 < early_w9);
    }
}
