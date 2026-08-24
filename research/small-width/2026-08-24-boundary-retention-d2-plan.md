# D2 Zero-Predecessor Falsifier Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add one red-team-only exhaustive probe that demonstrates the phase dependency on a retained predecessor carry while preserving the value path and clean ancillas.

**Architecture:** Keep the production adder untouched. Extend the existing dedicated red-team module with a minimal copy of the chunk value path plus two cleanup modes: the existing exact reverse-retention control and a falsifier that retains every boundary but substitutes a clean zero only when repairing a non-first boundary's phase. Search widths and budgets in ascending order and stop at the first geometry with at least three chunks that yields a phase-only witness under the falsifier while the exact control remains clean.

**Tech Stack:** Rust, the existing circuit builder and 64-shot simulator, SHAKE256 deterministic seeds, Cargo offline release builds.

## Global Constraints

- Modify only the red-team probe and this research plan; do not edit production primitives.
- Use the dedicated `small_width_redteam` binary; ordinary `cargo test` is excluded because of known stale-symbol failures.
- Stay local: no fetch, push, provider, evaluator, or submission actions.
- The verdict is limited to reverse retention and early erase without prefix recomputation; do not generalize to checkpoint or prefix-recomputation schedules.

---

### Task 1: Implement and verify the zero-predecessor falsifier

**Files:**

- Modify: `src/point_add/small_width_redteam.rs`
- Verify unchanged: `src/point_add/pingpong_div.rs`
- Verify unchanged: `src/point_add/small_width.rs`

- [ ] Add a dynamic-width red-team circuit builder that reproduces the current exact reverse-retention cleanup and offers a zero-predecessor phase-repair mode without changing the forward value path.
- [ ] Add an exhaustive, live-shot-masked simulator sweep that checks addend preservation, modular addition, phase, and every non-external qubit.
- [ ] Search `(width, budget)` lexicographically for the smallest layout with at least three chunks and print the exact control plus the first zero-predecessor phase-only witness.
- [ ] Fail closed unless the exact control has zero value, phase, and ancilla errors and the falsifier has zero value and ancilla errors but at least one phase witness.
- [ ] Build with `cargo build --release --offline --bin small_width_redteam` and run `./target/release/small_width_redteam`; capture the smallest witness and baseline control.
- [ ] Re-run the width-256 standalone approximate/exact probes and point-add proxies, then verify production file hashes, expected diff scope, and a clean committed tree.
