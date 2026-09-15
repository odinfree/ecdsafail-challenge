# PRO status (resumable) — updated 19:16Z

DEADLINE 2026-09-15T02:55:43Z (immutable, START 18:55:43Z). Model deepseek-v4-pro,
effort max, session 01a0a139-9e50-75a1-987c-24314aabc050. Resumed context verified
via `ps`: `deepseek resume ... --model deepseek-v4-pro -c model_provider="deepseek"
-c model_reasoning_effort="max" --dangerously-bypass-approvals-and-sandbox`.

## Bound parent
Official 88dc9f4 (welttowelt) Q793 / T682,564,189, ops 1,243,369,959.
Worktree: /Users/odin/DeepSeek/pareto-head-to-head-20260914/worktrees/pro-bench
@38c7fe6b (reset 88dc9f4 onto harness 9700396), branch codex/pro-20260914.
Isolated CARGO_TARGET_DIR: /Users/odin/DeepSeek/pareto-head-to-head-20260914/target-pro.
Baseline release build done (exit 0).

## Live frontier (computed 18:56Z from 1227 public rows)
Q<=791 unclaimed. Low-Q envelope: Q792/T893,988,754 (bulengerk cf39122),
Q793/T682,564,189 (welttowelt 88dc9f4), Q794/T415,821,960, Q795/T300,862,444,
Q807/T276,427,457, Q822/T250,088,365. Last official submission 9/14 01:45Z.
Hard evaluator cap: MAX_OPS=4e9 (load-time), NUM_TESTS=9024.

## Route pro-q792-peak (claimed -> implementing)
Peak anatomy (derived, to be confirmed by census):
  793 = 539 core (work1 256 phys + work2 259 + rank5 state 21 + p1/p2/iter 3)
        + 23 ty/lambda-borrowed helpers + 231 passenger residual (256 - 25 lent).
Falsifier: whole-count TRACE_PEAK_NAMES=1 census confirms peak=793 and names owners.

Hypotheses, in order of first probe:
- H3a (+2 helper loan): lend passenger[25..27] as dirty helpers (23 -> 25).
  Peak 793 -> 791 if it holds. Edit sites: q793_step_r03.rs assert 23->25,
  q793_lifecycle_r03.rs template/loan_bracket_ops 23->25 & 565->567,
  remap first+23->first+25 & 562->564, q793_mbu.rs template 23->25 & 565->567,
  mod.rs peak assert gated (791 when flag on). MCX dirty ladders get >= 2 more
  dirty wires -> structural T should not rise (may fall).
- H1 (4th omitted rail / modulo16 chart): work1 256 -> 255 physical. Requires
  exact mod16 cycle synthesis (mod8 chart is 9 wires / 178 T); larger lift.
- H2 (work2 pad): the 2 pads are released during outer multiplication already;
  check whether one pad can be omitted at the step peak.

## Gate chain (LOWQ_Q793_NATIVE_MODE)
whole-count (TRACE_PEAK_NAMES=1) -> whole-stream (64-shot 0/0/0) -> whole-9024
(compact, ~50 min RAM-exclusive). t-census is per-template T (FLASH owns A24
pruning; do not duplicate). Any Q<=792 candidate additionally needs total ops
< 4e9 and official 9024 metrics nondominated vs live frontier.

## Next exact commands (after heavy lock acquired)
```
cd /Users/odin/DeepSeek/pareto-head-to-head-20260914/worktrees/pro-bench
BIN=/Users/odin/DeepSeek/pareto-head-to-head-20260914/target-pro/release/build_circuit
LOWQ_Q793_NATIVE_MODE=whole-count TRACE_PEAK_NAMES=1 "$BIN" 2>&1 | tee /tmp/pro-q793-census-off.log
```
Then the H3a edit (default-OFF flag Q793_HELPERS_25) and the same census with
Q793_HELPERS_25=1 expecting peak=791.

## Coordination state
My heavy lock released (build done 19:04Z). Queue #1 done. FLASH legacy `build`
lock (pid=session17681) still held at 19:16Z; FLASH live and reconciling.
FLASH owns queue #2 (its baseline build). I wait for queue order; do not jump.
Next heavy job for me: queue #3 = OFF census + H3a census (one heavy acquisition,
release after each job per rules).

## ROOT HANDOFF — Q792 leak localized (2026-09-15T10:30Z)

Count pass `LOWQ_Q792_EEA=1 LOWQ_Q793_NATIVE_MODE=whole-count` deterministically
panics at the template self-check with:

```
Q792_HOLE_TOUCH block=124 j=0 hole=255 idx=170128 kind=CX q1=NO_QUBIT q2=279 t=275
omitted low residual rail still emitted
```

Decoding the template's register allocation (rank 0..5, a 5..11, c 11..17,
sm 17..21, p1 21, p2 22, iter 23, w1 24..283, w2 283..542) makes the leaking
gate `CX(w2[19], w1[255])` — a copy INTO the newly omitted rail, inside block
124 / j 0, at template offset 170128.

Cheapest fix: guard that single emission with `!four_hole()` (same pattern as
`metadata_remainder5_phased.rs`'s `if four_hole() && i == 255 { continue; }`), or
retarget it to the port the four-hole mapping already chose for A=254
(`w2[257]`, see `q794_handoffs.rs`). Then: whole-count must print
`peak_qubits=792`, refreeze `codex10h_resources()` + the peak assert, whole-stream
must be 0/0/0, then submit.

Full analysis: `../../lanes/laneRoot/Q792-BLOCKER-ANALYSIS.md` and
`../../lanes/laneRoot/Q792-NEXT-STEP.md`. Also: A24 is already OFFICIAL —
submission `2dc9b2b`, Q793 / T671,563,551, the new nondominated Q793 frontier row.

## ROOT NOTE — Q792 whole-stream defect (2026-09-15T11:20Z)

`whole-count` now passes: **peak=792, ops=1,369,818,684, structural_T=820,699,472**.
But the 64-shot `whole-stream` pass panics in the simulator:

```
thread 'main' panicked at src/sim.rs:48: index out of bounds: the len is 1024
but the index is 4294967295
```

Index `u32::MAX` is `NO_QUBIT`, so an emitted op still carries a sentinel as its
`q_target` (sim.rs:48 reads `self.qubit(op.q_target)`). This is a remap/emit
defect, not a hole-geometry one: the template self-check validates the pre-remap
stream (where sentinels are legal placeholders), but the remapped/passed-on op
must have all three qubit fields resolved. Find the op whose `.q_target` is
`NO_QUBIT` in the emitted stream — likely an entry built by direct `Op`
construction (not via `circ.x/cx/ccx`) or a captured-and-replayed `Vec<Op>` that
kept a placeholder — and resolve or drop it.

Also note for the eventual submission: the whole-artifact exact CCX cancellation
sweep in `mod.rs` (`cancel_adjacent_ccx_in_memory` + `cancel_commuting_ccx_in_memory`)
was being skipped by a guard; it is now enabled in the root tree and was measured
to remove **62,152,364 CCX** from the A24 artifact (window 64). The committed
submission with it is `7351d318`. Once the Q792 port is its own tree, it should
carry the same sweep for the same reason — it will cut ~9% of Toffoli there too,
and the drift armour in `trailmix_port/mod.rs:4412` now accepts a bound when
`Q793_CANCEL_SWEEP_APPLIED=1` is set by `build()`.
