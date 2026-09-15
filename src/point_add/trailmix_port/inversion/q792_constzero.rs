//! Thread-local constant-zero rail for the four-hole mod-16 charts.
//!
//! The mod-16 (Q792) chart is defined over twelve rails whose fourth v-rail
//! `v3 = W2[255]` is one of the four rails the four-hole geometry omits. The two
//! production call sites cannot read that rail (it is not zero on the reachable
//! domain) and cannot allocate inside their own optimized region
//! (`shared_optimize::cancel_nct` asserts the region contains only X/CX/CCX), so
//! the zero rail is allocated at the top of the block pipeline and published here
//! for the chart call sites to consume.
//!
//! Contract: `with_zero_rail` allocates a fresh lane (|0> at allocation), runs
//! the closure, then zeroes and frees the lane. It must be entered OUTSIDE any
//! `cancel_nct` region, i.e. at the block/template level.

use std::cell::RefCell;
use crate::point_add::trailmix_port::circuit::{Circuit, QReg};

thread_local! {
    static ZERO_RAILS: RefCell<Vec<QReg>> = const { RefCell::new(Vec::new()) };
    static IN_STEP: std::cell::Cell<bool> = const { std::cell::Cell::new(false) };
}

/// True while a production step is emitting. The instrumented call sites check
/// this so that a direct `step()` call (as in the stage-check harnesses) keeps
/// its exact qubit high-water mark and does not try to consume a rail.
pub(super) fn in_step() -> bool {
    IN_STEP.with(|c| c.get())
}

/// Run `f` with the "inside a production step" flag set.
pub(super) fn with_step_flag<R>(f: impl FnOnce() -> R) -> R {
    IN_STEP.with(|c| c.set(true));
    let out = f();
    IN_STEP.with(|c| c.set(false));
    out
}

/// Current constant-zero rail, if one is funded.
pub(super) fn zero_rail() -> Option<QReg> {
    ZERO_RAILS.with(|z| z.borrow().last().map(|q| q.borrowed_alias()))
}

/// Run `f` with a funded constant-zero rail available to the chart call sites.
pub(super) fn with_zero_rail<R>(
    circ: &mut Circuit,
    f: impl FnOnce(&mut Circuit) -> R,
) -> R {
    let rail = circ.alloc_qreg("q792.v3.const0");
    ZERO_RAILS.with(|z| z.borrow_mut().push(rail.borrowed_alias()));
    let out = f(circ);
    ZERO_RAILS.with(|z| {
        z.borrow_mut().pop();
    });
    circ.zero_and_free(rail);
    out
}

/// Run `f` with a borrowed constant-zero rail that the caller already owns.
/// Used where allocation is not permitted (register-free regions, or callers
/// that assert the exact qubit high-water mark).
pub(super) fn with_borrowed_zero_rail<R>(
    rail: &QReg,
    f: impl FnOnce() -> R,
) -> R {
    ZERO_RAILS.with(|z| z.borrow_mut().push(rail.borrowed_alias()));
    let out = f();
    ZERO_RAILS.with(|z| {
        z.borrow_mut().pop();
    });
    out
}

/// Freeze a value for the constant-zero rail. In the four-hole geometry the
/// fourth omitted Work1 rail (`W2[255]`) is the rail the mod-16 chart's v3 input
/// is defined to carry, and it is structurally |0> across the whole traversal,
/// so that omitted physical lane's *logical* value is what the chart must see.
/// `freeze` returns a fresh |0> lane for callers that prefer to fund one
/// explicitly; it is a thin alias of `alloc_qreg` kept for readability.
pub(super) fn freeze_zero(circ: &mut Circuit, name: &str) -> QReg {
    circ.alloc_qreg(name)
}
