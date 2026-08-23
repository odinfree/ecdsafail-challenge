# Predeclaration — direct Q1272 replay-ladder descent (second −1 rung)

Written after reproduction of the parent control and the sibling Q1273
configuration, before any armed Q1272 measurement and before any semantic
source edit. Lane: `research/fable-2c79-replay-ladder-q1272` (worktree
`fable-2c79-replay-ladder-q1272`), dispatch
`.lane/FABLE_Q1272_LADDER_DISPATCH.md` @ `6a0679d`.

## Frozen base and live board

- Frozen parent / promoted source: `2c79d2f4ef1f6fdc6f75024ef4ae50c6506e2208`
  (tree `d50e00b6ba06975de822e7184ca930d3542e255e`), Q1274 / official rounded
  T 916,526 / score 1,167,654,124 / full 9,024-shot `0/0/0`.
- `git diff 2c79d2f HEAD -- src/` is EMPTY: this lane's source tree is
  byte-identical to the promoted source; HEAD adds only `.lane/` documents.
- Live board reopened this session (`ecdsafail benchmark` + `submissions`):
  **current best 1,167,654,124 @ 2c79d2f — the parent IS the frontier.**
- Strict ceilings recomputed from the live score this session:
  - Q1273: rounded T ≤ 917,245 (floor((1,167,654,124−1)/1273)); sibling's
    number re-derived, unchanged.
  - **Q1272: rounded T ≤ 917,967** (floor((1,167,654,124−1)/1272) =
    917,967; 1272 × 917,967 = 1,167,654,024 < live; +1272 exceeds it).
    Headroom over the parent's official 916,526: **+1,441**.

## Reproductions completed before this declaration (gate 2)

Parent control, default build, this session, this machine:

- `PP_PROFILE peak_qubits=1274 peak_ops_idx=2528381 peak_phase=pp_div_replay
  num_qubits=1274 ops=12919977`; 64-lane composition
  `classical_mismatch=0 phase=0x0 dirty_qubits=0`; profile-lane executed
  total 916,424.62; emitted 957,346 CCX + 28 CCZ = 957,374; `ops.bin` md5
  `fdbc7f23a1ed45cca413531bed988100` — byte-identical to the recorded parent
  stream. Selfcheck lanes: `957374 emitted / 916510.469 executed Toffoli,
  1274 qubits`. Both match the sibling lane's control to the printed digit.
- Peak-owner census (default): four-way tie at exactly 1274 —
  `pp_div_replay` 263,451.39 exec, `square_product_register` 58,703.33,
  `pp_mul_replay` 23,982.41, `pp_mul_walkback` 307,827.27; next-highest
  phases 1057 (`pp_div_walk`/`pp_div_walkback`/`pp_mul_walk`); all `tlm_*`
  ≤ 1026. Reproduces the corrected FOUR-way census exactly.

Sibling Q1273 configuration (`SUB4_PP_PEAK=1273 SUB4_SQUARE_LADDER=243`),
re-run this session: `peak_qubits=1273 peak_ops_idx=2528391
peak_phase=pp_div_replay num_qubits=1273`, ops emitted 12,933,805, `ops.bin`
md5 `5ba8782cd13b79eda79752b9351bc166` — **byte-identical to the sibling's
armed stream**; profile-lane executed 917,056.48 (+631.86 over control);
emitted 958,485+28 = 958,513 (+1,139); composition `0 / 0x0 / 0`; all four
former binders at exactly 1273. The sibling's one-step receipts reproduce.

## One bounded family, exactly

Set **only** `SUB4_PP_PEAK=1272 SUB4_SQUARE_LADDER=242` on exact `2c79d2f`.
Divide/multiply rounds (698/696), R1/R2 (defaults 340/628 on this source),
width schedule, replay fold, arithmetic, and evaluator semantics unchanged.
No source edit: both knobs exist in the frozen parent (`pingpong_div.rs`
`plan()` reads `SUB4_PP_PEAK`, default 1274;
`trailmix_ludicrous/square/product_register.rs` reads `SUB4_SQUARE_LADDER`,
default 244), so the default stream stays byte-identical by construction.

Hypothesis: the same exact carry-layout repartition that paid one wire at
Q1273 removes **two** simultaneous ladder wires across all four co-binders,
reaches trusted Q1272 (builder `num_qubits` AND trusted evaluator = max
referenced id + 1), and prices within the +1,441 strict headroom.

### Exact carry invariant (inherited verbatim from the Q1273 family)

At every op-stream instant whose active width currently binds the peak, the
number of simultaneously live carry-chain wires decreases by two relative to
the parent (one relative to the sibling), while:

1. every carry **value** stays bit-exact (identical exact ripple recurrences
   over re-partitioned position ranges);
2. all data-channel arithmetic is unchanged — sums, folds, selectors, signs,
   ABI bit-for-bit functions of the same inputs;
3. approximation stays confined to the phase channel through the existing
   measured-erasure repairs (`hmr` + `cmp_lt_phase_conditioned`); no new
   classical-channel approximation of any carry;
4. no sign-tape shortening, no raw `(u,v)` materialization; trusted Q = max
   referenced qubit id + 1 (`analyze_ops` is the authority).

### Static layout derivation (allocator algebra replicated, no armed run)

`chunk_layout(256, target, final)` with the 20-bit exact-lead compare window
(`replay_chunk_compare()=20`), replicated externally and cross-checked
against the measured 1274/1273 layouts before deriving 1272:

| binder instant | budget | layout | repairs |
|---|---|---|---|
| div terminal @1274 (measured) | 62 | `[12,61,61,61,61]` | 1 exact lead + 3 approx |
| div terminal @1273 (measured) | 61 | `[16,60,60,60,60]` | same |
| **div terminal @1272 (derived)** | 60 | `[20,59,59,59,59]` | same — lead hits the 20-bit window EXACTLY, repair stays exact |
| div terminal @1271 (derived) | 59 | `[52,51,51,51,51]` equal split | **CLIFF**: exact-lead form unreachable, 4 approx boundaries + no exact lead |
| mul terminal @1274 (measured) | 63 | `[8,62,62,62,62]` | 1 exact lead + 3 approx |
| **mul terminal @1272 (derived)** | 61 | `[16,60,60,60,60]` | same |

Q1272 is therefore the **last rung of this family**: at 1271 the divide
terminal loses the exact-lead layout entirely (the lead cap is the compare
window, already saturated at 20), flipping 3 approximate repairs to 4 plus
loss of the exact lead — a different (worse-λ) structure, out of family.
Expected four-way cut: all four binders move 1274 → exactly 1272 together;
co-binder identities become divide `698+256+256+2+60=1272`, multiply
`696+512+2+1+61=1272`, square `1030+242=1272`.

Walk-split guards: `value_width` is peak-independent and `low = width −
ladder` grows by exactly 1 per peak step, so the sibling's verified ≥50-wire
`low·2 ≤ width` margin at peak 1273 implies ≥48 at 1272 — no guard can flip;
newly split rounds (ladder crossing width−1) cost `low` emitted CCX each and
are captured by the measured T gates. `chunk_layout` None-fallback
(12-chunk equal split) is unreachable at both terminal budgets by the
derivation above; if any interleaved round hit it, the phase-profile census
would show an anomalous exec/λ jump — covered by stop rules.

## Optimistic Q/T bound (static, before any armed run)

- Q: 1272 exactly, both trust paths (all binding instants are budget-derived;
  nothing else measured above 1057).
- ΔT (executed, avg/shot) over the PARENT: the measured first step is
  +631.86 (profile lanes) / +677.89 (selfcheck lanes). The second step has
  the same component structure (terminal lead compare +4 bits/round,
  interleaved fill-band budget crossings 60→59, +1-bit split-walk lows,
  square leading-chunk shift) with mildly more fill-band crossings.
  Dispatch's inherited bracket: **+1,264 … +1,356 total against +1,441**
  (margin +85…+177). This lane treats the bracket as the optimistic bound
  and delegates the kill decision to the two paired 64-lane measurements.
- Projected official rounded T if the bracket holds: 917,790…917,882
  ≤ 917,967. Projected score 1272 × (917,790…917,882) =
  1,167,428,880…1,167,545,904 = **−108,220…−225,244** under the live best.

## Distinctness declaration

This is NOT the active Q1272 selector pilot (circuit source `14608572`,
operation SHA `678c149f…22f0`, 696/696 traversal, fused-fold selector): this
lane's artifact is the direct replay-ladder descent on source `2c79d2f`
(698/696 traversal, no selector rework). A surviving result reports its own
source/ops/checkpoint identity and reuses nothing from that pilot's model or
fault-density claims.

## Tests (armed candidate; every cheap gate before the one full run)

1. Builder census: `PP_PROFILE=1 PROFILE_ACTIVE_TIMELINE=1` armed —
   peak_qubits = num_qubits = 1272, all four former binders exactly 1272,
   nothing else > 1057, binding instant recorded (TRACE_PEAK-equivalent:
   peak_ops_idx + peak_phase).
2. Trusted Q: `eval_circuit` on the armed `ops.bin` must print qubits 1272
   (max referenced id + 1). (Its full 9,024-shot run doubles as gate 8 —
   the Q readout is checked when the run starts, the diagnostic when it
   ends.)
3. 64-lane composition (profile lanes): `classical_mismatch=0 phase=0x0
   dirty_qubits=0`.
4. Composition selfcheck (`SUB4_PINGPONG_POINT_ADD_SELFTEST=1` armed): 64
   affine adds correct, offsets preserved, phase 0, all ancillas clean,
   1272 qubits; asserts are fatal — a pass is the receipt.
5. Square component miter (`SUB4_PRODUCT_SQUARE_SELFTEST=1` armed): PASS.
6. Divide+Multiply component miters (`SUB4_PINGPONG_POINT_ADD_SELFTEST`
   covers the composition; the per-direction `pingpong_simulator_selfcheck`
   battery is included if runnable in isolation).
7. Two paired deterministic 64-lane T measurements: profile lanes
   (916,424.62 control) and selfcheck lanes (916,510.469 control), armed
   minus control on identical seeds; projected official rounded T =
   916,525.546 + max(bracket of the two deltas), gate: ≤ 917,967.
8. If and only if 1–7 pass: **one** unchanged inherited-nonce full
   9,024-shot diagnostic (`build_circuit` armed, default tail nonce
   100000045835813 untouched, then `eval_circuit`). Record exact
   classical / phase / ancilla and exact average executed T. A dirty draw
   is structural evidence only — never a candidate or a submission.
9. Opt-out byte identity: default build md5 must remain
   `fdbc7f23a1ed45cca413531bed988100` (no source edit is planned; if any
   semantic source edit becomes necessary it requires a NEW predeclaration,
   default-off gating, and this file's supersession).

## Stop rules

1. Any armed measurement shows peak_qubits ≠ 1272 or num_qubits ≠ 1272, or
   any phase maximum in (1272, 1274] not explained as a former binder at
   exactly 1272, or trusted-eval qubits ≠ 1272 → **KILL** (name the binder).
2. Projected official rounded T > 917,967 from the paired measured deltas at
   default R1/R2 → exactly **one** predeclared local rebalance pass over
   (R1,R2) ∈ 336..344 × 624..632 at PEAK=1272/LADDER=242 (64-lane profile
   measurements only; no GPU, no hunt, no other knob), and ONLY if the armed
   phase profile names the specific paid cliff (which phase absorbed the
   overrun). Still over → **KILL** with the measured floor.
3. Any component or composition miter failure (nonzero classical / phase /
   ancilla in any focused gate) → **KILL** (structural soundness).
4. The one full diagnostic is dirty → **HOLD-HUNT** (candidate valid on Q/T,
   not submission-clean on the inherited nonce; no hunt authority here;
   exact channel counts recorded as structural evidence).
5. Any realization requiring a semantic source edit, tape shortening, raw
   `(u,v)`, classical-channel carry approximation, or a retained
   unreferenced high id → outside the family, forbidden without a new
   predeclaration.
6. Never more than one full 9,024-shot run; never more than the single
   rebalance pass of rule 2.

## Hard exclusions (dispatch, verbatim scope)

No provider or cloud compute, no nonce hunt, no range declaration, no
submission, no public note, no API-key access, no external message. No edits
to other worktrees. Never committed: `ops.bin`, `results.tsv` changes,
score files, binaries, `target/`, logs, caches, temporary evaluators,
generated artifacts.

## Predictor / qualification statement (gate 6, to be completed at verdict)

If the family survives, the terminal account must state the smallest exact
classical-plus-phase predictor port/qualification route for the Q1272 stream
and whether the existing Q1273 wrapped model adapts without changing its
semantic recurrence — from measured structure, not labels.

Model: Claude Fable 5 (`claude-fable-5`), autonomous lane, high effort.
