# Exact Prefix Boundary Erase Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Measure an opt-in exact full-prefix phase repair while preserving the promoted ping-pong chunk schedule and its at-most-two live boundary wires.

**Architecture:** Add one pure comparator-range selector and use it in the existing `add_chunked_measured_with` erase closure. The strict environment gate selects a global prefix beginning at bit zero; the absent/default case selects the same local replay slice as source commit `67524171`.

**Tech Stack:** Rust 2021, Cargo offline mode, the repository circuit builder and 64-lane `PP_PROFILE` simulator, SHA-256 byte comparison.

## Global Constraints

- Work only in `/Users/odin/Documents/coding with codin/ecdsafail-exact-boundary-recompute-codex` on `research/codex-exact-boundary-recompute-20260824`.
- Preserve source binding `67524171baaf568dc3dc606f38515745f70804ff` / tree `8202910d176fa1f3332ff961e6f3f789ca6a7ac2` as the experiment base.
- Enable the experiment only for `SUB4_PP_EXACT_PREFIX_BOUNDARY_ERASE=1`.
- Do not change chunk allocation, chunk order, erase timing, or boundary lifetime.
- Use local CPU and Cargo `--offline`; do not fetch, push, launch providers, or submit.
- `ADMIT` requires exact 64-lane correctness, `Q < 1267`, and projected `Q*T` below the exact-675 baseline. Any failed conjunct is `HARD_NACK`.

---

### Task 1: Bind and capture the unmodified baseline

**Files:**
- Read: `src/point_add/pingpong_div.rs`
- Generate, ignored: `ops.bin`
- Copy, temporary: `/tmp/ecdsafail-c2-67524171-baseline.ops.bin`

**Interfaces:**
- Consumes: exact source commit and the existing `build_circuit` binary.
- Produces: baseline byte artifact, SHA-256, file size, peak qubits, executed Toffoli, and correctness counters.

- [ ] **Step 1: Verify source and branch binding**

Run:

```bash
git rev-parse HEAD
git rev-parse HEAD^{tree}
git branch --show-current
git status --short --branch
```

Expected: HEAD begins with the committed design on top of `67524171`; `git merge-base HEAD 67524171` is exactly `67524171`, the branch is `research/codex-exact-boundary-recompute-20260824`, and the tree is clean.

- [ ] **Step 2: Compile the unmodified circuit builder offline**

Run:

```bash
cargo build --offline --release --bin build_circuit
```

Expected: exit 0 and a release `build_circuit` binary.

- [ ] **Step 3: Capture the default byte artifact**

Run:

```bash
env -u SUB4_PP_EXACT_PREFIX_BOUNDARY_ERASE -u PP_PROFILE ./target/release/build_circuit
shasum -a 256 ops.bin
stat -f '%z' ops.bin
cp ops.bin /tmp/ecdsafail-c2-67524171-baseline.ops.bin
```

Expected: `build_circuit OK`, a non-empty SHA-256, a positive byte size, and an exact temporary copy.

- [ ] **Step 4: Profile the default 64 lanes**

Run:

```bash
env -u SUB4_PP_EXACT_PREFIX_BOUNDARY_ERASE PP_PROFILE=1 PP_PROFILE_SEED=0 ./target/release/build_circuit 2>&1 | tee /tmp/ecdsafail-c2-67524171-baseline-profile.log
```

Expected: `PP_PROFILE lanes=64 classical_mismatch=0 phase=0x0 dirty_qubits=0`; record `peak_qubits` and `TOTAL exec_tof` as the exact-675 baseline economics.

### Task 2: Add the exact-prefix range selection with TDD

**Files:**
- Modify and test: `src/point_add/pingpong_div.rs:2048-2140`

**Interfaces:**
- Consumes: `boundary_erase_compare_start(exact_prefix, lo, hi, compare)` and the strict environment value.
- Produces: an unchanged local range by default and start index zero when exact mode is enabled.

- [ ] **Step 1: Write the failing range and counterexample test**

Append beside the existing tests in `src/point_add/pingpong_div.rs`:

```rust
#[cfg(test)]
#[test]
fn exact_prefix_boundary_erase_includes_global_zero_carry() {
    let (lo, hi, compare) = (4usize, 8usize, 4usize);
    assert_eq!(boundary_erase_compare_start(false, lo, hi, compare), 4);
    assert_eq!(boundary_erase_compare_start(true, lo, hi, compare), 0);

    let original_acc = 0xffusize;
    let addend = 0x01usize;
    let sum = original_acc.wrapping_add(addend) & ((1usize << hi) - 1);
    let local_carry = (sum >> lo) < (addend >> lo);
    let global_zero_carry = sum < addend;
    assert!(!local_carry);
    assert!(global_zero_carry);
}
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```bash
cargo test --offline --bin build_circuit exact_prefix_boundary_erase_includes_global_zero_carry -- --exact --nocapture
```

Expected: compilation fails with `cannot find function boundary_erase_compare_start`.

- [ ] **Step 3: Implement the minimal range selector and env-gated closure**

Add immediately after `chunk_bounds`:

```rust
fn boundary_erase_compare_start(
    exact_prefix: bool,
    lo: usize,
    hi: usize,
    compare: usize,
) -> usize {
    if exact_prefix {
        0
    } else {
        hi - compare.min(hi - lo)
    }
}
```

In `add_chunked_measured_with`, read the strict gate once and replace only the comparator slice calculation:

```rust
    let exact_prefix_erase = std::env::var("SUB4_PP_EXACT_PREFIX_BOUNDARY_ERASE")
        .is_ok_and(|value| value == "1");
    let erase = |b: &mut B, carry: QubitId, lo: usize, hi: usize| {
        let compare_start = boundary_erase_compare_start(
            exact_prefix_erase,
            lo,
            hi,
            replay_chunk_compare(),
        );
        let phase = b.alloc_bit();
        b.hmr(carry, phase);
        cmp_lt_phase_conditioned(b, &acc[compare_start..hi], &addend[compare_start..hi], phase);
        b.free(carry);
    };
```

- [ ] **Step 4: Run the focused test and verify GREEN**

Run:

```bash
cargo test --offline --bin build_circuit exact_prefix_boundary_erase_includes_global_zero_carry -- --exact --nocapture
cargo fmt --check
git diff --check
```

Expected: one test passes; formatting and whitespace checks exit 0.

### Task 3: Verify byte identity, exactness, and economics

**Files:**
- Generate, ignored: `ops.bin`
- Read: `/tmp/ecdsafail-c2-67524171-baseline.ops.bin`
- Generate, temporary: `/tmp/ecdsafail-c2-exact-prefix-profile.log`

**Interfaces:**
- Consumes: the env-gated implementation and the saved baseline artifact/profile.
- Produces: exact default byte comparison and experiment correctness/Q/T/score deltas.

- [ ] **Step 1: Recompile offline and prove default byte identity**

Run:

```bash
cargo build --offline --release --bin build_circuit
env -u SUB4_PP_EXACT_PREFIX_BOUNDARY_ERASE -u PP_PROFILE ./target/release/build_circuit
shasum -a 256 ops.bin /tmp/ecdsafail-c2-67524171-baseline.ops.bin
cmp -s ops.bin /tmp/ecdsafail-c2-67524171-baseline.ops.bin
```

Expected: both SHA-256 values match and `cmp` exits 0.

- [ ] **Step 2: Profile the enabled exact repair on 64 lanes**

Run:

```bash
SUB4_PP_EXACT_PREFIX_BOUNDARY_ERASE=1 PP_PROFILE=1 PP_PROFILE_SEED=0 ./target/release/build_circuit 2>&1 | tee /tmp/ecdsafail-c2-exact-prefix-profile.log
```

Expected correctness gate: `PP_PROFILE lanes=64 classical_mismatch=0 phase=0x0 dirty_qubits=0`. Record `peak_qubits` and `TOTAL exec_tof`; a nonzero correctness counter is immediately `HARD_NACK`.

- [ ] **Step 3: Compute the projected score and deltas**

For each profile, compute:

```text
projected_score = peak_qubits * TOTAL_exec_tof
delta_Q = exact_Q - baseline_Q
delta_T = exact_T - baseline_T
delta_score = exact_projected_score - baseline_projected_score
```

Expected decision: `ADMIT` only if exact correctness is green, `exact_Q < 1267`, and `delta_score < 0`; otherwise `HARD_NACK` naming every failed conjunct.

- [ ] **Step 4: Commit the bounded source/test change**

Run:

```bash
git add src/point_add/pingpong_div.rs
git commit -m "experiment: recompute boundary phase from exact prefix"
git status --short --branch
```

Expected: one local commit and a clean branch. Do not push or submit.
