# Final-Add Carry-to-Fold Handoff Implementation Plan

> **Execution mode:** inline sole-owner TDD under the committed resolution
> contract. Reduced-width success is discovery only; the exact-width gate is
> mandatory for ADMIT.

**Goal:** Either construct an exact-source final-carry handoff that saves at
least 1,500 net average executed Toffoli at Q1266 on 694/693, or prove the entire
permitted family impossible with checked information/cost/lifetime evidence for
both fused replay sites.

**Scope:** The experiment may add bounded files under
`src/point_add/memory/repro/` and, only after a construction survives its pure
miter, an env-gated exact-source diff limited to the final carry publication and
selector/fold/cleanup interface in `src/point_add/pingpong_div.rs` (plus a
focused static-census hook if strictly required). No other source changes.

**Tooling:** Python standard library (`unittest`, exhaustive Boolean enumeration,
ANF/GF(2) rank, deterministic JSON), Rust/Cargo locked offline build, and the
existing operation stream/condition-depth and active-qubit instrumentation.

---

## Task 1: Freeze source binding and baseline inventory

**Files:**

- Create: `src/point_add/memory/repro/final_carry_handoff_inventory.json`
- Create: `src/point_add/memory/repro/test_final_carry_handoff.py`
- Inspect only: `src/point_add/pingpong_div.rs`
- Inspect only: `src/point_add/arith/compare.rs`
- Inspect only: `src/point_add/mod.rs`

1. Write a failing binding test for the exact commit/tree, 694/693, widths
   54/53, flag/chunk compare 22, and exact function/source-line fingerprints.
2. Run only the focused test and record RED.
3. Add the deterministic inventory extractor/model containing 692 divide plus
   691 multiply cells, 21 depth-one comparator CCX per cell, and formulas for
   gross and net savings.
4. Run GREEN and hash the JSON.
5. Record per-site selector wires, fold-carry widths, last-chunk carry lifetime,
   and candidate host intervals. Count every simultaneous retained wire.

## Task 2: RED/GREEN phase-aware reduced miter

**Files:**

- Create: `src/point_add/memory/repro/final_carry_handoff.py`
- Modify: `src/point_add/memory/repro/test_final_carry_handoff.py`

1. Write RED tests that deliberately omit the divide parity-zero overflow
   dimension and deliberately omit a phase cleanup; require explicit witnesses.
2. Implement the exact baseline divide and multiply cell equations for widths
   5..9, maximum redundant values, all sign/parity/doubled/carry arms, every HMR
   bit, and forward plus inverse cleanup.
3. Preserve the corrected test orientation: the intentionally incomplete
   candidate must fail and the baseline identity must pass.
4. Emit deterministic collision tables, truth-table ranks, ANF degrees, and
   route status updates. Run the focused suite through GREEN.

## Task 3: Attempt R2 quotient publication and exact transfer

**Files:**

- Modify: `src/point_add/memory/repro/final_carry_handoff.py`
- Modify: `src/point_add/memory/repro/test_final_carry_handoff.py`

1. Enumerate the minimal selector/first-carry publication for divide and
   multiply separately.
2. Search for collisions with equal permitted visible state and unequal raw
   carry, required HMR phase, or inverse-cleanup state.
3. For every reduced collision class, construct a source-valid secp256k1
   embedding or reject the collision as non-transferable.
4. Kill R2 only with a concrete exact-transfer witness for each affected site;
   otherwise retain the missing rank in the interface and pass it to R1.

## Task 4: Attempt R1 retained-suffix/fold conjugation

**Files:**

- Modify: `src/point_add/memory/repro/final_carry_handoff.py`
- Modify: `src/point_add/memory/repro/test_final_carry_handoff.py`

1. Start at the economic minimum of three saved depth-one comparator gates per
   cell. Enumerate retained suffix ranks and candidate clean/dirty fold hosts.
2. Search reversible transformations from add-suffix state to fold-carry state
   and back for n=5..9. Charge every nonlinear gate; reject dirty-target
   assignments that only work from zero.
3. Miter forward value, every measurement-conditioned phase arm, and inverse
   cleanup. Require every temporary to return to zero.
4. Transfer the construction algebra to divide width 54 and multiply width 53
   with exact `f`, independently proving all sign/parity arms.
5. Kill R1 on a checked rank/synthesis counterexample, or proceed only if the
   exact checker is fully green and the static net-cost ceiling remains viable.

## Task 5: Close R3 nonlinear-cost and lifetime route

**Files:**

- Modify: `src/point_add/memory/repro/final_carry_handoff.py`
- Modify: `src/point_add/memory/repro/test_final_carry_handoff.py`
- Create: `src/point_add/memory/repro/final_carry_handoff_evidence.json`

1. Prove/check the multiplicative complexity of the no-retention 22-bit carry
   phase predicate under the permitted inputs and compare it to the existing 21
   depth-one CCX construction.
2. For retained rank `k`, compute comparator savings, dirty-host conversion
   cost, selector cost changes, condition depths, and peak overlap. Report gross
   and added nonlinear cost separately per site and in aggregate.
3. Predeclared economic rejection: any surviving uniform route whose total is
   less than 1,500 net average T is killed. Two saved depth-one CCX per cell are
   explicitly insufficient.
4. Emit a deterministic route registry and exact counterexample/lower-bound
   certificate. Test its schema, counts, and hash stability.

## Task 6: Exact Rust gate, only if a construction survives

**Files:**

- Modify only if admitted by Tasks 2–5: `src/point_add/pingpong_div.rs`
- Modify only if necessary: focused local static-census entry point

1. Add a failing exact-source Rust/self-check test for the candidate and record
   RED without running the broad dormant test suite.
2. Implement only the permitted carry publication and selector/fold/cleanup
   diff, env-gated for experiment isolation.
3. Run the focused exact 54/53 phase-aware forward/inverse checker.
4. Run `cargo build --locked --offline`.
5. Build the exact 694/693 operation stream without the full evaluator. Census
   condition-depth-weighted T, peak Q, peak owner, and active lifetimes; compare
   baseline/candidate and require Q<=1266 and net saving>=1500.
6. If any gate fails, revert the route to ALIVE/KILLED as the evidence dictates;
   do not label it ADMIT.

## Task 7: Independent REFUTE and terminal packet

**Files:**

- Modify: `src/point_add/memory/repro/final_carry_handoff_evidence.json`
- Create: `docs/superpowers/reports/2026-08-24-final-carry-handoff-report.md`

1. Remove generated `__pycache__` and verify the scoped allowlist.
2. Give the completed packet and every contract trap to a separate worker with
   the sole instruction to REFUTE. Resolve any sustained refutation.
3. Re-run exact focused tests and deterministic artifact generation; record
   commands, results, hashes, source/tree, gross/add/net cost, and Q/lifetimes.
4. Commit only the bounded evidence packet.
5. Return exactly `ADMIT_CARRY_HANDOFF_TO_FULL_EVAL` or
   `HARD_NACK_CARRY_HANDOFF_FAMILY`, with the cheapest next external gate. Do not
   claim full-evaluator validation, promotion, or submission.
