# D3 Divide Width-2 Proof Miter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone exhaustive Boolean miter that proves or falsifies a lower-nonlinearity/no-retained-wire implementation for the promoted divide leading-boundary width-2 family.

**Architecture:** A single dependency-free Rust binary represents four-input Boolean functions as 16-bit truth tables. It derives ANFs by Möbius transform, exhausts the complete affine-plus-one-product family, checks the shipped two-product carry identity, and checks a direct post-sum HMR phase polynomial over both measurement outcomes. Source/trace bindings are reported as constants and independently verified with read-only shell hashes.

**Tech Stack:** Rust standard library, Cargo offline release build, Git and `shasum` for source/artifact binding.

## Global Constraints

- Bind the family to promoted commit `67524171baaf568dc3dc606f38515745f70804ff`, tree `8202910d176fa1f3332ff961e6f3f789ca6a7ac2`, and lane-B census artifact SHA-256 `becd6300974d990acb8c6f0cf617d7929c556f191db789dc5ff4c57adbac8adc`.
- Preserve all four local data bits and deliver the identical carry Boolean through the existing `Option<QubitId>` ABI.
- Cross-chunk fusion, prefix recomputation, and repeated on-demand synthesis are excluded.
- Create only the standalone red-team binary and this plan; do not edit or register a production module.
- Use only dedicated offline commands. Do not run ordinary `cargo test`, fetch, push, providers, evaluators, or submissions.

---

### Task 1: Add the exhaustive truth-table and ANF certificate

**Files:**

- Create: `src/bin/d3_width2_miter.rs`
- Verify unchanged: `src/point_add/pingpong_div.rs`
- Verify unchanged: `src/point_add/arith/compare.rs`

**Interfaces:**

- Consumes: four-bit indices ordered as `(a0, a1, x0, x1)` for the pre-add carry and `(a0, a1, s0, s1)` for the post-sum phase predicate.
- Produces: one JSON line with source binding, support mask, truth/ANF masks, degrees, exhaustive-search counts, RED witnesses, GREEN mismatch counts, ABI verdict, and total failures; exits nonzero on any mismatch.

- [x] **Step 1: Create a deliberate RED scaffold**

Create `src/bin/d3_width2_miter.rs` with a dedicated fail-closed entry point:

```rust
fn main() {
    eprintln!("D3_RED_MITER_NOT_IMPLEMENTED");
    std::process::exit(1);
}
```

- [x] **Step 2: Build and run the RED scaffold**

Run:

```sh
cargo build --release --offline --bin d3_width2_miter
./target/release/d3_width2_miter
```

Expected: build succeeds; the binary prints `D3_RED_MITER_NOT_IMPLEMENTED` and exits 1.

- [x] **Step 3: Implement truth tables, Möbius ANF, and exhaustive one-product search**

Replace the scaffold with a standalone implementation containing these exact core interfaces:

```rust
const PROMOTED_COMMIT: &str = "67524171baaf568dc3dc606f38515745f70804ff";
const PROMOTED_TREE: &str = "8202910d176fa1f3332ff961e6f3f789ca6a7ac2";
const CENSUS_COMMIT: &str = "f6eaee6c83ca254b78c3aff5e5c6202b7ead3287";
const CENSUS_SHA256: &str =
    "becd6300974d990acb8c6f0cf617d7929c556f191db789dc5ff4c57adbac8adc";
const SOURCE_SUPPORT_MASK: u16 = 0xffff;

fn truth_mask(mut predicate: impl FnMut(usize) -> bool) -> u16;
fn variable_mask(variable: usize) -> u16;
fn affine_mask(coefficients: usize) -> u16;
fn anf_mask(truth: u16) -> u16;
fn algebraic_degree(anf: u16) -> u32;
fn carry_reference(index: usize) -> bool;
fn carry_current_identity(index: usize) -> bool;
fn phase_reference(index: usize) -> bool;
fn phase_direct_identity(index: usize) -> bool;
```

Use the reference carry

```rust
let addend = index & 3;
let accumulator = (index >> 2) & 3;
addend + accumulator >= 4
```

and the current two-product identity

```rust
let a0 = index & 1 != 0;
let a1 = index & 2 != 0;
let x0 = index & 4 != 0;
let x1 = index & 8 != 0;
let p = a0 & x0;
p ^ ((a1 ^ p) & (x1 ^ p))
```

Generate all 32 affine masks. Exhaust all `32 * 32 * 32 = 32,768` masks of the form `a XOR (b AND c)`, record any exact match, and record the maximum agreement plus the first mismatch of the lexicographically first best candidate. Assert:

```rust
assert_eq!(carry_truth, 0xec80);
assert_eq!(carry_anf, 0x2480);
assert_eq!(algebraic_degree(carry_anf), 3);
assert_eq!(one_product_searches, 32_768);
assert!(one_product_match.is_none());
assert_eq!(current_identity_mismatches, 0);
```

The closest one-product representative must be `a1 AND x1`, agreeing on 14/16 rows and failing first at index 7, `(addend=3, accumulator=1)`.

- [x] **Step 4: Implement the post-sum HMR phase miter**

Index the phase truth table as `(a0, a1, s0, s1)` and use `sum < addend` as the reference. Implement the direct identity:

```rust
let linear_quadratic =
    a0 ^ a1 ^ (a0 & a1) ^ (a0 & s0) ^ (a0 & s1) ^ (a1 & s1);
let cubic = a0 & s0 & (a1 ^ s1);
linear_quadratic ^ cubic
```

Assert:

```rust
assert_eq!(phase_truth, 0x08ce);
assert_eq!(phase_anf, 0x26ae);
assert_eq!(algebraic_degree(phase_anf), 3);
assert_eq!(phase_identity_mismatches, 0);
assert_eq!(measurement_phase_mismatches, 0); // all 16 inputs, m in {0,1}
```

Report the phase implementation as Clifford `Z/CZ` terms plus one CCZ-class term `a0*s0*(a1 XOR s1)`, zero comparator scratch qubits, and one nonlinear phase gate. Explicitly report that the retained boundary count remains one and that the current comparator already uses one nonlinear gate.

- [x] **Step 5: Add fail-closed ABI and receipt output**

Set `abi_requires_qubit_id=true`, `cross_chunk_fusion=false`, `prefix_recomputation=false`, and verdict `HARD_NACK_EXISTING_ABI_WIDTH2`. Increment `failures` unless all exact masks, degrees, search counts, GREEN miters, support mask, and ABI exclusions match the specification. Print the first fixed-zero RED witness `(addend=3, accumulator=1, expected_carry=1)` and the closest-one-product RED witness at the same input.

- [x] **Step 6: Build and run the GREEN miter**

Run:

```sh
cargo build --release --offline --bin d3_width2_miter
./target/release/d3_width2_miter
```

Expected: one JSON record containing `carry_truth_mask="0xec80"`, `carry_anf_mask="0x2480"`, `carry_degree=3`, `one_product_searches=32768`, `one_product_match=false`, `current_identity_mismatches=0`, `phase_truth_mask="0x08ce"`, `phase_anf_mask="0x26ae"`, `phase_degree=3`, `measurement_phase_mismatches=0`, `verdict="HARD_NACK_EXISTING_ABI_WIDTH2"`, and `failures=0`; exit 0.

- [x] **Step 7: Verify source binding and edit scope**

Run:

```sh
git rev-parse HEAD^{tree}
git show 67524171baaf568dc3dc606f38515745f70804ff:src/point_add/pingpong_div.rs | shasum -a 256
shasum -a 256 /Users/odin/Documents/coding\ with\ codin/ecdsafail-675-reachable-census-codex/src/point_add/memory/repro/replay_window_census.py
shasum -a 256 src/point_add/pingpong_div.rs src/point_add/arith/compare.rs
git diff --check
git status --short
```

Expected promoted source stream hash: `953dd851629e4d15a4f56d5061e3c0d61ea83bebab8f7aca5243636d4f240c38`; expected census artifact hash: `becd6300974d990acb8c6f0cf617d7929c556f191db789dc5ff4c57adbac8adc`; only the plan and standalone binary may differ from the pre-D3 tree.

- [x] **Step 8: Commit the proof artifact and rerun from the committed tree**

```sh
git add src/bin/d3_width2_miter.rs research/small-width/2026-08-24-divide-width2-j2-d3-plan.md
git commit -m "research: prove divide width2 boundary lower bound"
cargo build --release --offline --bin d3_width2_miter
./target/release/d3_width2_miter
git status --short --branch
```

Expected: the post-commit miter exits 0 and the worktree is clean.
