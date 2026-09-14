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
