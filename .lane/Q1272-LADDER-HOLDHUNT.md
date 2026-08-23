# HOLD-HUNT — direct Q1272 replay-ladder descent: Q1272 landed on both trust paths, T priced under the strict ceiling, ladder family TERMINAL at this rung

Resolved: 2026-08-23. Lane: `research/fable-2c79-replay-ladder-q1272`.
Binding predeclaration: `.lane/PREDECLARATION-Q1272-LADDER.md` @ `3d9ac75`
(pushed to `odinfree` before any armed Q1272 measurement; no semantic source
edit at any point — `git diff 2c79d2f -- src/` is empty at every commit of
this lane).
Frozen parent / promoted source: `2c79d2f4ef1f6fdc6f75024ef4ae50c6506e2208`
(tree `d50e00b6ba06975de822e7184ca930d3542e255e`), Q1274 / official rounded
T 916,526 / score 1,167,654,124. Live board reopened this session: current
best still **1,167,654,124 @ 2c79d2f** → strict Q1272 ceiling rounded
T ≤ **917,967** (floor((1,167,654,124−1)/1272); headroom +1,441).

## Verdict

**The second rung fired, and it is the last one.** Armed
`SUB4_PP_PEAK=1272 SUB4_SQUARE_LADDER=242` on byte-exact `2c79d2f`:

- **Q = 1272 on both trust paths** (builder census AND the trusted
  evaluator's max-referenced-id+1);
- **T priced under the strict ceiling by all three measurements**: paired
  64-lane deltas project official rounded T 917,543…917,813, and the one
  full 9,024-shot diagnostic measured avg executed Toffoli **917,676.821**
  (rounds to 917,677; margin 290 under 917,967);
- the single authorized inherited-nonce diagnostic is **DIRTY
  16 classical / 13 phase-batches / 0 ancilla** — the family's unhunted
  intrinsic class (sibling Q1273: 12/12/0; b523 control: 14/9/0; ancilla
  exactly 0 everywhere). Stop rule 4 → **HOLD-HUNT**: the candidate needs a
  GPU nonce hunt (excluded from this lane) before any submission.
- **Ladder lane exhausted**: the divide-terminal layout cliff is measured
  statically at Q1271 (below), so no further −1 rung exists in this family.
  No stop rule 1–3 fired; the R1/R2 rebalance of stop rule 2 was never
  needed.

## Operation identities

| stream | config | ops emitted | ops.bin md5 | ops.bin SHA-256 |
|---|---|---|---|---|
| parent default | (none) | 12,920,073 | `fdbc7f23a1ed45cca413531bed988100` | — (byte-identical to promoted source stream) |
| sibling Q1273 | PEAK=1273 LADDER=243 | 12,933,805 | `5ba8782cd13b79eda79752b9351bc166` | `ee6448dbb23aa877123733724b109266e584f1ba14abf5c38b43b9ab6aa26cd1` |
| **this lane Q1272** | **PEAK=1272 LADDER=242** | **12,947,854** | `5838d0da48bf1055becc68cd072a3c5a` | `aac291b75b71de692702330fdcd94d41eabdabeb63d757ae48d9e089283817dd` |

The Q1273 SHA-256 was recomputed this session from a fresh rebuild and
equals the Q1273 wrapped-register model's frozen stream identity digit for
digit — validating both the hash convention and the byte-determinism of the
build across sessions.

## Measured gates (armed = `SUB4_PP_PEAK=1272 SUB4_SQUARE_LADDER=242`)

| gate | result | verdict |
|---|---|---|
| predeclaration pushed before armed runs | `3d9ac75` on `odinfree` | PASS |
| parent control reproduction | peak 1274 @ ops_idx 2528381, four-way tie exact, profile lanes 916,424.62, selfcheck lanes 916,510.469, default md5 `fdbc7f23…` | PASS |
| sibling Q1273 reproduction | peak 1273 @ 2528391, md5 `5ba8782c…` byte-identical, profile 917,056.48 (+631.86) | PASS |
| armed builder census | peak_qubits = num_qubits = **1272**, binds ops_idx 2528401 `pp_div_replay` (binding instant advances exactly +10 ops per rung: 2528381→91→401) | PASS |
| armed trusted Q | `eval_circuit`: qubits : **1272** | PASS |
| per-phase maxima, armed | all four former binders exactly 1272 (`pp_div_replay`, `square_product_register`, `pp_mul_replay`, `pp_mul_walkback`); next 1057; `tlm_*` ≤ 1026; nothing new | PASS |
| 64-lane composition, armed (profile lanes) | classical 0, phase 0x0, dirty 0 | PASS |
| composition selfcheck, armed (independent corpus) | 64 affine adds correct, offsets preserved, phase 0, ancillas clean; `959680 emitted / 917527.828 executed, 1272 qubits` | PASS |
| square component miter, armed | `58980 emitted / 58721.141 executed, 1272 peak qubits`, standalone | PASS |
| per-direction miter (`pingpong_simulator_selfcheck`) | not runnable in isolation: repo-wide `cargo test` harness has 165 pre-existing compile errors in unrelated stale tests, and the only call site is `#[cfg(test)]`; adding an env hook would be a source edit (stop rule 5). Coverage subsumed by the composition selfcheck, which executes both traversals with fatal ABI/phase/ancilla asserts — same disposition as the sibling lane's battery | RECORDED |
| determinism | full armed rebuild in a second directory: identical md5 `5838d0da…`, identical census line, identical profile total 917,712.25; emitted CCX+CCZ agree exactly across the two independent 64-lane corpora (959,680) | PASS |
| emitted T delta | 957,374 → 959,680 CCX+CCZ (**+2,306 emitted** over parent; +1,167 over Q1273), deterministic | measured |
| executed T delta, paired lanes | profile lanes **+1,287.63** (916,424.62→917,712.25); selfcheck lanes **+1,017.36** (916,510.469→917,527.828) | measured |
| projected official rounded T | 916,525.546 + (1,017…1,288) = **917,543…917,813 ≤ 917,967** | PASS (margin 154…424) |
| opt-out byte identity | no source edit; default md5 `fdbc7f23…` reproduced this session | PASS |
| full 9,024-shot diagnostic, inherited nonce 100000045835813 unchanged (the one allowed) | **16 classical / 13 phase-batches / 0 ancilla — DIRTY**; avg executed Toffoli **917,676.821** (+1,151.28 over parent official 916,525.546); trusted qubits 1272; first mismatch shot 99 | HOLD (stop rule 4) |

Per-phase executed deltas, parent → Q1272 (profile lanes, paired seeds):
`pp_div_replay` +566.88 (263,451.39→264,018.27), `pp_mul_walkback` +479.73
(307,827.27→308,307.00), `pp_mul_replay` +226.81 (23,982.41→24,209.22),
`square_product_register` +4.17 (58,703.33→58,707.50), walk phases and
`pp_div_walkback` unchanged to the hundredth, `tlm_*` jitter +10.0 net
(downstream measurement-draw shifts). Sum +1,287.6 = the TOTAL delta. The
full-9024 Fiat-Shamir corpus lands at +1,151.28 — inside the two 64-lane
brackets, as predeclared.

## Score projections (fixed by the hunted nonce's own draw)

| basis | rounded T | score = 1272 × T | vs live 1,167,654,124 |
|---|---|---|---|
| paired bracket low | 917,543 | 1,167,114,696 | **−539,428** |
| full-diag draw | 917,677 | 1,167,285,144 | **−368,980** |
| paired bracket high | 917,813 | 1,167,458,136 | **−195,988** |
| strict ceiling | 917,967 | 1,167,654,024 | −100 (guarantee) |

Any hunted nonce whose re-verified rounded T ≤ 917,967 beats the frontier.
For comparison, the sibling Q1273 candidate projects −54.7k…−113.3k: one
hunt spent on the Q1272 stream buys roughly 3–5× the score win of the same
hunt on Q1273.

## Ladder family TERMINAL — static cliff at Q1271 (allocator algebra, cross-checked against three measured rungs)

`chunk_layout(256, target, final)` with the 20-bit exact-lead compare
window, replicated externally and validated against the measured layouts at
1274/1273/1272:

| divide terminal budget | layout | repairs |
|---|---|---|
| 62 (peak 1274, measured) | `[12,61,61,61,61]` | 1 exact lead + 3 approx |
| 61 (peak 1273, measured) | `[16,60,60,60,60]` | same |
| 60 (peak 1272, this lane) | `[20,59,59,59,59]` | same — the lead chunk saturates the 20-bit window exactly, repair still exact |
| 59 (peak 1271, derived) | `[52,51,51,51,51]` equal split | **4 approximate boundaries, exact lead LOST** |

At 1271 the exact-lead form is unreachable (the lead cap IS the compare
window, already saturated), so the divide terminal flips to an all-
approximate equal split: more truncated repairs per replay round, higher λ,
worse fault density — a structurally different and strictly worse family.
The multiply terminal still has exact-lead room at 1271 (`[20,59×4]`), but
the peak is set by the divide side. **This family ends at Q1272.** The
remaining co-binder terms at the divide terminal are tape 698 + coefficient
256 + numerator 256 + 2 loaned signs + ladder 60 = 1272; tape and the
512-wide ABI are exactly floored by predecessor bounds
(injectivity/pricing), the ladder is now at its cliff.

## Predictor handoff (gate 6, grounded in artifacts, not labels)

The existing Q1273 wrapped model
(`research/q1273-wrapped-register-exact`, qualification `7b339f5`,
`GO_CPU_CLASSICAL / CUDA_HANDOFF_READY`) is a terminal-canonicalized
finite-width wrapped-register transducer, exact 113/113 on frozen classical
masks (1,594 faults), with the combined phase composition separately
predeclared (`aa65f2c`). Two grounded facts determine the port:

1. **Its semantic recurrence transfers unchanged.** The Q1272 and Q1273
   armed streams are generated by identical source code from two env
   constants; measured, they share rounds (698/696), R1/R2 (340/628), the
   width schedule, fold windows, sign-tape semantics, and the repair
   mechanism (`hmr` + windowed `cmp_lt_phase_conditioned`). Everything that
   differs is budget-derived partition **data**: terminal layouts
   (`[16,60×4]`→`[20,59×4]` divide, `[12,61×4]`→`[16,60×4]` multiply),
   interleave fill-band budgets −1, split-walk lows +1 bit, square lead
   shift. No recurrence change is needed or permitted.
2. **It is stream-keyed and fail-closed** (wrong-count and
   same-count/wrong-SHA negatives), so it will refuse the Q1272 stream
   as-is. The port is a re-key plus table regeneration, not a model change.

Smallest exact classical-plus-phase port/qualification route:

1. Freeze the Q1272 armed identity: ops 12,947,854, ops.bin SHA-256
   `aac291b7…17dd`, md5 `5838d0da…`, checkpoint digest via the same
   extraction machinery.
2. Regenerate the boundary/window tables mechanically from this stream
   (the partition schedule above); no semantic edit.
3. Re-run the classical qualification battery against the unchanged
   evaluator oracle: the inherited-nonce fixture is this lane's measured
   16-fault mask; regenerate H64/D16/blinded-D32 equivalents; byte-exact
   double-run; all nine fail-closed negatives.
4. Re-base the combined-phase composition on this stream's repair sites
   (first fixture: the 13 phase batches at the inherited nonce), keeping
   the source-event-preserving composition of the Q1273 phase
   predeclaration.
5. Only then CUDA transport parity (nearest shell remains the Q1274
   repair-r100 `ppgpu.cu`, SHA `585d67a5…`), then the hunt — successor
   lane only.

The port is also the **hunt-target decision instrument**: the single-draw
channel counts (16/13/0 vs 12/12/0) are one Poisson-ish sample each, not
densities; if the Q1272 stream's clean-nonce density is materially lower,
the ported predictor measures that cheaply over nonce ranges before any GPU
spend, and the 3–5× score advantage is weighed against measured density,
not guessed.

## Critique, fix, verify

- **Dirty ≠ regression, again.** 16/13/0 sits beside 12/12/0 (sibling) and
  14/9/0 (b523 control) with ancilla exactly 0; both 64-lane corpora and
  the square miter are fully clean; every arithmetic change is value-exact
  chunk repartitioning. A real value bug would fault on the deterministic
  64-lane corpora and would not be nonce-selective. The parent's 0/0/0 is
  a hunted tail event; this stream re-rolls all measured repairs.
- **Lead-equals-window edge.** The Q1272 divide lead chunk is exactly 20 =
  the compare window; the repair stays exact by the code's own condition
  (chunk 0 no wider than the window ⇒ whole-chunk compare, λ-free). The
  census confirms no new binder and the composition stays clean; the cliff
  analysis shows this is the last exact-lead rung, which is why the family
  terminates here rather than at a guessed depth.
- **Why the selfcheck step-2 delta (+339.47) is smaller than step-1
  (+677.89).** Executed T on a fixed corpus depends on the measured-repair
  draws, which re-roll per stream; per-corpus step deltas therefore vary
  while the deterministic emitted delta grows monotonically (+1,139 then
  +1,167). The decision inputs are the bracket of both corpora and the
  full-9024 average — all three agree and all clear the ceiling.
- **Thin-margin objection.** The worst projection (bracket high 917,813)
  clears by 154; the measured full-corpus draw clears by 290. The hunted
  nonce re-rolls executed T by ~tens; the successor must re-verify rounded
  T ≤ 917,967 on the hunted nonce — recorded as a hard gate, not assumed.
- **No rebalance ran.** Stop rule 2 authorizes an R1/R2 pass only above the
  ceiling; it never triggered. No unpredeclared knob was touched all lane.
- **Distinctness.** This artifact (source `2c79d2f`, ops
  12,947,854, SHA `aac291b7…`) is disjoint from the active Q1272 selector
  pilot (source `14608572`, op SHA `678c149f…22f0`); nothing from that
  pilot's model or fault-density claims is reused here.

## Next binder (successor order)

1. **Port the wrapped predictor to the Q1272 stream** (route above), measure
   clean-nonce density for Q1272 vs Q1273, then spend the GPU hunt on the
   winner (Q1272 pays 3–5× more if densities are comparable). Re-verify
   rounded T ≤ 917,967 (Q1272) or ≤ 917,245 (Q1273) on the hunted nonce,
   then submit.
2. If the Q1272 hunt stalls on density, the Q1273 stream (md5 `5ba8782c…`)
   remains a valid cheaper-λ fallback with its own ceiling margin.
3. Further Q descent is off this ladder: the next structural family is the
   **512-wide ABI co-residency** (coefficient+numerator at the replay), the
   only non-floored co-binder term; the sign tape (698) stays floored by
   the predecessor's injectivity/pricing bounds, and the ladder is at its
   measured cliff.

## Model receipt

Claude Fable 5 (`claude-fable-5`), single isolated research worktree,
autonomous, high effort. No provider or cloud compute, no nonce hunt, no
range declaration, no submission, no public note, no API-key access, no
external message, no edits outside this worktree. `ops.bin`, score files,
`results.tsv` changes, `target/`, logs, and helper artifacts not committed
(`results.tsv` was restored after the trusted run appended its row; the row's
numbers are recorded above). Commits: predeclaration `3d9ac75`, this
account. Live-board reads: `ecdsafail benchmark` + `ecdsafail submissions`
(read-only).
