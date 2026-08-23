# Predeclaration — replay chunk-carry ladder single-wire overturn

Written after reproduction of the parent artifact and peak census, before any
semantic source edit and before any armed (non-default) measurement of the
candidate. Lane: `research/fable-2c79-replay-ladder-overturn`.
Frozen parent / promoted source: `2c79d2f4ef1f6fdc6f75024ef4ae50c6506e2208`
(tree `d50e00b6ba06975de822e7184ca930d3542e255e`), Q1274 / rounded T916526 /
score 1,167,654,124 / full 9,024-shot `0/0/0` (live board reopened this
session: current best 1,167,654,124 @ 2c79d2f — the parent IS the frontier).

## Census correction (measured here, supersedes the inherited three-way claim)

`PP_PROFILE=1 PROFILE_ACTIVE_TIMELINE=1` on the default build, all phases:
peak_qubits=1274 = num_qubits (trusted Q = max referenced id + 1), peak binds
at ops_idx 2528381 in `pp_div_replay` (terminal batch replay), 64-lane
composition `classical_mismatch=0 phase=0x0 dirty_qubits=0`, and the per-phase
active maxima show a **FOUR-way tie**, not three:

```text
pp_div_replay            1274   <- binder (terminal batch ladder 62)
square_product_register  1274   <- binder (SQUARE_LADDER=244; peak = 1030+244)
pp_mul_replay            1274   <- binder (terminal batch ladder 63 + doubled_out)
pp_mul_walkback          1274   <- binder (interleaved replay ladders + split-walk ladders)
pp_div_walk / pp_div_walkback / pp_mul_walk   1057
next-highest others      <= 1026
```

The predecessor lane (`research/fable-2c79-retained-transducer@fb07d5e`)
reported only the six `pp_*` phases; `square_product_register` at exactly 1274
was omitted from its census. The dispatch's family clause "so no Q1274 tie
remains" therefore requires dropping **four** binders. Every one of the four is
a budget-filled carry-ladder allocation:

- `pp_*` binders derive from `plan.peak` (`SUB4_PP_PEAK`, default 1274,
  `pingpong_div.rs:1263`): batch replay chunk ladders via
  `pick_chunks → ladder_for_allowance → chunk_layout`, interleaved replay
  ladders per round, and the split-walk ladders via `walk_low_chunk`
  (`WALK_PEAK = plan.peak`).
- the square binder derives from `SQUARE_LADDER = 244`
  (`SUB4_SQUARE_LADDER`, `product_register.rs:28`) through the same
  `add_chunked_measured_budgeted` allocator.

Co-binder identity at the divide terminal batch (measured + code-exact):
tape 698 + coefficient 256 + numerator 256 + 2 loaned sign wires + chunk
carry ladder 62 = 1274, layout `chunk_layout(256, 62, final)` =
`[12,61,61,61,61]` (3 approximate boundary repairs + 1 exact leading repair),
max simultaneous ladder live = boundary_in + (w−1) owned Gidney carries +
boundary_out/final = 62. Multiply terminal batch: budget 63 (`cell_extra=1`
for `doubled_out`), layout `[8,62,62,62,62]`, 696+512+2+1+63 = 1274.

## One family, exactly

Remove **one simultaneously live carry/bridge wire** from every carry-ladder
allocation that binds Q1274 — the chunked replay cell at `pp_div_replay`,
`pp_mul_replay`, `pp_mul_walkback` (batch, interleaved, and split-walk
ladders), and the square's chunked wide adds — so that no instant of the op
stream references more than 1273 simultaneous qubits.

### Exact carry invariant

At every op-stream instant whose active width currently equals 1274, the
number of simultaneously live carry-chain wires (chunk Gidney carries +
boundary bridge carries + final carry-out + split-walk `c_lo`/`c_hi` +
split boundary) decreases by at least one, while:

1. every carry **value** remains bit-exact (boundary carries, split-walk
   boundary carry, and final carry-out are computed by the identical exact
   ripple recurrences over re-partitioned position ranges);
2. all data-channel arithmetic is unchanged — sums, folds, selectors, signs,
   and the ABI are bit-for-bit functions of the same inputs;
3. approximation stays confined to the phase channel through the existing
   measured-erasure repairs (`hmr` + `cmp_lt_phase_conditioned`); **no new
   classical-channel approximation of any carry is introduced**;
4. no sign tape shortening, no raw `(u,v)` materialization, and trusted
   Q = max referenced qubit id + 1 (LIFO allocator, `num_qubits` from
   `analyze_ops` is the authority, not the builder's active count).

### Preferred-order search (dispatch step 1–2), priced statically first

1. **Is a ladder endpoint carry reconstructible from already-live replay
   operands / selectors / a restored dirty tape or passenger wire?**
   Reconstructible in principle — the identity is already in the artifact:
   the boundary/final carry of chunk j equals `[sum_j < addend_j]` modulo the
   `addend_j = 2^w−1 ∧ cin` edge, which is exactly what the measured-erasure
   repairs evaluate. Priced realizations:
   - *exact in-place replacement*: a ≥w-bit comparator ripple at the binding
     instant carries its own ≥w−1-wide carry ladder — it cannot cost less
     width than the one wire it frees. No width win. KILL.
   - *deferred exact recompute* (run the last chunk carry-free, regenerate
     the carry after the ladder retires): a 256-bit exact chunked compare per
     replay round ≈ +256 emitted CCX/round × ~137 terminal rounds ≈ +18k–35k
     executed T ≫ +719 ceiling. KILL.
   - *truncated recompute feeding the fold*: moves the deliberately
     phase-only approximation into the classical data channel (the fold
     writes data); classical faults on the unchanged nonce; soundness
     failure, disqualifying regardless of economics. KILL.
   - *dirty-borrowed endpoint* (idle tape sign / loaned passenger as carry
     target): the wire then holds `t⊕c`; it cannot control the fold selector
     ANDs (`and_clean(overflow, …)`), and compensation doubles the fold
     (+~50–100 CCX/round) or demands a unitary restore (re-ripple ≈ +w
     CCX/round). Measured erasure (`hmr`) cannot be applied to a borrowed
     wire at all — measurement destroys the borrowed state — so the
     Gidney-measured ladder admits no wire-for-wire dirty substitution. KILL.
2. **Surviving realization — allocation contraction** (this is the family's
   implementable member): shrink every peak-filling ladder budget by exactly
   one: `SUB4_PP_PEAK=1273` and `SUB4_SQUARE_LADDER=243`. Both knobs exist in
   the frozen parent and default to the parent values, so the default stream
   is byte-identical by construction (opt-out identity is trivial). The
   armed layouts stay structurally identical at the binding instants:
   - divide terminal: `[12,61,61,61,61]` → `[16,60,60,60,60]` (same 3
     approximate + 1 exact repairs; exact leading compare 12→16 bits),
   - multiply terminal: `[8,62,62,62,62]` → `[12,61,61,61,61]` (same),
   - split-walk rounds: `low = width−ladder` grows by 1 (the split's
     boundary repair is exact by construction; +1 emitted CCX per split),
   - square wide adds: leading chunk shifts by ~1 bit, same chunk count,
   - interleaved fill-band rounds shift within the same repair count except
     rounds whose budget crosses 60→59, which pay one extra approximate
     20-bit repair each (a measured handful of rounds).
   Guard checks derived from the allocator algebra (verified against the
   schedule): `walk_low_chunk`'s split guards (`low·2 ≤ width`, `low+2 ≤
   width`) hold with ≥50-wire margin at peak−1 across the whole interleave;
   no `chunk_layout` None-fallback is reachable at any armed budget.

## Target binders

All four measured Q1274 binders together: `pp_div_replay`,
`square_product_register`, `pp_mul_replay`, `pp_mul_walkback`. A cut that
leaves any of them at 1274 fails the N-way-tie law and is disqualified.

## Optimistic Q/T bound (static, before any armed run)

- Q: 1273 exactly (every 1274-binding instant is budget-derived; nothing else
  measured above 1057 except tlm_coord phases at ≤1026).
- ΔT (executed, avg/shot), component sum:
  terminal batches ≈ +2 exec/round × 136 rounds ≈ +272;
  split-walk rounds ≈ +0.5 exec/round × ~440 split rounds ≈ +220;
  fill-band/cliff interleaved rounds ≈ +50–150;
  square ≈ +10–30.
  **Optimistic total ≈ +550 executed T** against the refreshed strict
  ceiling headroom of **+719** (Q1273 ceiling = rounded T ≤ 917,245 against
  live 1,167,654,124; parent 916,526). The bound survives with ~170 margin;
  the uncertainty band (±~300) straddles the ceiling, so the kill decision
  is delegated to the measured 64-lane profile delta before the single full
  diagnostic.

## Miters and tests (armed candidate, all cheap gates before the one full run)

- `pingpong_simulator_selfcheck` armed: Divide + Multiply component miters,
  64 lanes — ABI preserved, ancillas zero, phase zero (covers boundary carry
  0/1 states stochastically over the reachable corpus; the arithmetic is
  layout-independent by the exactness invariant, and no borrowed dirty state
  exists in the surviving realization — the transducer branch that would
  have required the arbitrary-dirty-state miter is statically killed above).
- `SUB4_PRODUCT_SQUARE_SELFTEST` armed: square component miter at ladder 243.
- `PP_PROFILE` armed full composition: 64-lane affine adds
  `classical_mismatch=0 phase=0x0 dirty_qubits=0`, peak_qubits=1273,
  num_qubits=1273, per-phase maxima all ≤ 1273, exec-T delta recorded.
- Opt-out byte identity: default build unchanged (no source edit; knobs
  default to parent values). `git diff` of `src/` against `2c79d2f` empty.
- At most **one** inherited-nonce unchanged full 9,024-shot diagnostic
  (`build_circuit` armed + `eval_circuit`), only after every cheap gate
  passes. A dirty result grants no hunt and no submission; it is recorded as
  HOLD with exact channel counts.

## Stop rules

1. Any armed measurement shows peak_qubits ≠ 1273 or num_qubits ≠ 1273, or
   any phase maximum > 1273 → KILL (a non-budget binder exists; name it).
2. Projected official rounded T > 917,245 from the measured profile delta at
   default R1/R2 → one bounded rebalance pass over (R1,R2) ∈ 336..344 ×
   624..632 at PEAK=1273 (64-lane profile only, no GPU, no hunt); still
   over → KILL with the exact measured floor.
3. Any component or composition miter failure (nonzero classical / phase /
   ancilla on 64 lanes) → KILL (structural soundness).
4. The full diagnostic is dirty → HOLD (candidate valid on Q and T but not
   submission-clean on the inherited nonce; no hunt authority in this lane).
5. Any realization requiring tape shortening, raw `(u,v)`, classical-channel
   carry approximation, or an unreferenced-but-retained high qubit id →
   outside the family, forbidden.

## Hard exclusions (dispatch)

No nonce hunt, provider/cloud compute, submission, public note, API-key
access, external communication, or edits outside this worktree. `ops.bin`,
`results.tsv` changes, `target`, caches, logs, helper binaries, generated
artifacts are never committed.
