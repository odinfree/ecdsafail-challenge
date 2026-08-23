# KILL — in-place algebraic retained-word sign transducer, before implementation

Resolved: 2026-08-23. Lane: `research/fable-2c79-retained-transducer`.
Binding predeclaration: `.lane/PREDECLARATION-RETAINED-TRANSDUCER.md`, commit
`9567fe0476f905377c9bd4f02f00b92f89c8e1b7` (pushed to `odinfree` before this
bound existed and before any semantic source edit).
Frozen parent / promoted source: `2c79d2f4ef1f6fdc6f75024ef4ae50c6506e2208`
(tree `d50e00b6ba06975de822e7184ca930d3542e255e`), Q1274 / rounded T916526 /
score 1,167,654,124 / full 9,024-shot `0/0/0`.

## Verdict

**Terminal KILL at the static feasibility gate. No implementation opened.** The
retained-word transducer family cannot supply the divstep sign to the coefficient
replay under Q1273 without either (a) materializing a live full-width walk state
beside the ABI, which floors at **Q1284** > Q1273, or (b) extracting the sign
from a compact denominator-keyed code, whose closed form has already been
measured to explode (ANF terms 2,2,5,…,16433 through sign 14; no sign source past
round 7). The reverse (walk-back) sign is provably **not** recoverable from local
low bits, closing the "interleave, discard, regenerate" escape that would have
avoided both. The peak is a **three-way** tie, so even a perfect divide-side
transducer leaves Q1274 standing.

No model source edit, build of a candidate, nonce, provider, hunt, submission,
public note, or external call was made. Only the predeclaration and this account
were committed. `ops.bin` (a generated artifact from the diagnostics) is not
committed.

## Measured peak (this worktree, source 2c79d2f)

`TRACE_EACH_PEAK=1`: Q1274 first binds in `pp_div_replay` at ops_idx 2528381.
`PP_PROFILE=1 PROFILE_ACTIVE_TIMELINE=1` per-phase active-qubit maxima:

```text
pp_div_walk        1057
pp_div_replay      1274   <- binder
pp_div_walkback    1057
pp_mul_walk        1057
pp_mul_replay      1274   <- binder
pp_mul_walkback    1274   <- binder
```

The peak is a **three-way tie** across the divide replay and both multiply
replay phases (matching the historical three-way tie in
`memory/09-pingpong-interleaved.md`). `peak_phase` reports only `pp_div_replay`
because it updates on strict `>`; the profiler's per-phase column is the
authority. **A cut must drop all three tied binders (or be provably sole-binder)
to move global Q** — the N-way-tie law. Divide and multiply carry independent
sign tapes (698 and 696 wide), so a divide-only transducer changes nothing.

Co-binder decomposition at the divide replay (budget identity
`allowance = peak − (tape_len + 2N + 2·walk_width)`, N=256):

```text
tape (one sign qubit per round)   698   <- the transducer's target, 55% of Q
coefficient (ABI)                 256
numerator   (ABI)                 256
loaned u,v sign wires               2
chunk carry ladder                 62
total                            1274
```

## Score ceilings (recomputed from live 1,167,654,124)

```text
Q1273 strict rounded T ceiling = floor((1,167,654,124 − 1)/1273) = 917245
Q1272 strict rounded T ceiling = 917967
```

## Why the tape is 698 wide (the constraint the transducer must beat)

The sign `sigma_r = target[1] ⊕ source[1]` is produced by the forward walk on
`(u,v)` (`value_walk`, `pingpong_div.rs:1296-1300`), but the coefficient replay
runs on a *different* register pair `(coefficient, numerator)`
(`replay_halving_round` → `signed_mod_add_pm_halve_fused`, `:1720`). The sign is
the **only** bridge between the two, and it must survive from walk-time to
replay-time. At the terminal batch replay the forward replay has committed signs
`0..628` and is consuming `629..697`, while `value_walk_back` (later) will
consume all `697..0` in reverse. Forward-replay consumes increasing, walk-back
decreasing, from opposite ends — so no sign is free before the very end and all
698 are co-resident. That co-residence is the 698-wide tape and 55% of Q.

## Feasibility bound

Three exhaustive supply mechanisms, each with an exact inequality.

### Bound 1 — counting (new, derived here)

The walk is reversible and terminates at a canonical O(1)-bit state (`±1, ±1`,
`pingpong_div.rs:167-169`), so the map `sign_sequence → denominator` is
injective: the 698-bit sequence carries exactly the denominator's ≤256 bits. Any
code `C` that determines all signs therefore has `|C| ≥ 256`. This rules out
every narrow rolling code (`|C| < 256`) regardless of extraction cost — a
sub-256-bit code cannot even represent the sign sequence it must emit.

### Bound 2 — geometry (new, derived here)

A code that regenerates `sigma_r` from a **live** walk state must, at the widest
walk round (`value_width = 258` at r=8, `pingpong_div.rs` schedule), hold that
state co-resident with the ABI:

```text
2 · 258  (u,v live)        516
coefficient + numerator    512
retained code |C|          256
                          ----
peak lower bound          1284   (before one ladder wire or one extraction scratch)
1284 − 1273 = 11 over the Q1273 target
```

Independent cross-check with the sign-checkpoint lane, from the other direction:
768 ABI (denominator + coefficient + numerator) + 516 live `(u,v)` = **1284**,
the same floor its `KILL-SIGN-CHECKPOINT-BOUND-B523` reached for the first
missing sign at round 8. Two independent decompositions agree. This is the
"never materialize raw `(u,v)`" charter clause failing quantitatively: honoring
it forbids Bound-2 supply; violating it costs Q1284.

### Bound 3 — extraction without a live walk state (borrowed evidence)

The one surviving shape is a code `|C| ≈ 256` (the retained denominator word)
from which `sigma_r` extracts with **no** live walk state. This is killed not
here but by the adjacent lane's **measured** ANF density of `sigma_r` as a
function of the denominator: 2, 2, 5, 11, 25, 57, 115, 244, 481, 1001, 2013,
4041, 8177, 16433 terms through sign 14 (`ROUND3-RETAINED-WORD-BDF4845.md`,
`KILL-RETAINED-SPLICE-CANONICAL-B523.md`), super-exponential; the retained-word
oracle supplies signs only through round 7 (6/696 divide, 0/694 multiply). I
state plainly that this is borrowed measurement, not re-derived here — and it is
exactly what fixes the reopen condition below.

### The escape that would bypass Bounds 2 and 3 — closed here (new)

If the forward replay could extract `sigma_r`, use it, and **discard** it, while
walk-back **regenerated** `sigma_r` locally, no tape and no live wide state would
be needed. It cannot: on reverse, `sigma_r` is not a function of the post-state's
low bits. With `source` unchanged and `H` the halved sum recovered after undoing
the shift, `pre_target = 2H − (−1)^{sigma}·source`, and the forward consistency
`sigma = pre_target[1] ⊕ source[1]` evaluates to:

```text
sigma = 0 branch:  requires H0 = 1
sigma = 1 branch:  requires H0 = 1
```

Both branches require only `H0 = 1`, which always holds (the halved value is odd
by invariant). The low-bit condition is **vacuous** — it does not discriminate
the sign. The true reverse discriminator is the divstep branch (the magnitude/δ
comparison), a global high-bit property of the full-width state, which is why
`walk_back_round` (`pingpong_div.rs:1165`) is *passed* the tape sign rather than
recomputing it, and why the ANF (Bound 3) is dense. An envelope-keyed reverse
extractor keyed on the width schedule's reachability envelope would be
**approximate** — the schedule admits width violations at ≈1.5λ per 9,024-shot
draw — so it fails the classical correctness channel on some shots; that is a
soundness failure, not a T cost, and it is disqualifying regardless of economics.

### Why full interleaving is not a 186-qubit win (closing my own question)

Interleaving the whole replay while *keeping* signs on the tape is width-negative
at the tail: at r=697, `tape_len ≈ 697`, so peak ≈ 697 + 512 + 2·8 + ladder ≈
1287 > 1274. That is precisely why the shipped schedule batches the tail and
loans `(u,v)` down to two wires; R1=340 / R2=628 is the tuned optimum of the
`tape_len` vs `2·walk_width` trade. Interleaving while *discarding* signs is the
escape above, closed by the reverse-σ algebra.

## Gate ledger

| gate | result | verdict |
|---|---|---|
| frozen source / predeclaration pushed before bound | parent `2c79d2f`, tree `d50e00b`; predecl `9567fe0` on `odinfree` | PASS |
| peak binder identification | three-way tie 1274: pp_div_replay, pp_mul_replay, pp_mul_walkback | measured |
| Bound 1 counting `|C| ≥ 256` | narrow rolling codes cannot represent the sequence | KILL for `|C|<256` |
| Bound 2 geometry (live walk state) | Q ≥ 1284 > 1273; cross-checks sign-checkpoint lane | **KILL** |
| Bound 3 extraction (denominator-keyed) | measured ANF density explodes; no sign source past round 7 | **KILL (borrowed)** |
| reverse-σ local recovery | low-bit consistency vacuous (both branches need H0=1) | escape CLOSED |
| implementation / miters | static gate fails under optimistic assumptions | NOT OPENED |
| protected default / full-9024 | no candidate exists; step-7 diagnostic not authorized | inherited control only |

## Critique, fix, verify

- **Circular-tie objection.** The multiply ladder was *not* assumed equal to
  1274; it was measured. `PP_PROFILE=1 PROFILE_ACTIVE_TIMELINE=1` reports 1274 at
  three phases directly. The doc's "must drop all three" clause rests on the
  measurement, not the budget identity.
- **Bound-2 optimism objection.** 1284 grants away the ladder wire and the
  extraction scratch and counts only the widest single round; it is a floor, and
  it still exceeds Q1273 by 11. The multiply side would add its own.
- **Bijective-recoding objection to Bound 3.** A code could in principle make
  `sigma_r` cheap if it were the live `(u,v)` itself — but that is not a
  compression (it is 2·`value_width` wide) and lands in Bound 2. Any code below
  full width that stays closed under the in-place round update must drop high
  bits, which the reverse-σ result and the ANF density both show are essential.
- **Changed-premise objection.** The only unfired premise is a *different sign
  extractor* — one that produces the reverse sign exactly from a sub-full-width
  in-place code without a magnitude comparison. No such extractor is known; the
  reopen gate is a proof that `sigma_r` has a bounded-width exact reverse
  discriminator, before any code is written.

`git diff 9567fe0 -- src/` is empty; the frozen source is unchanged.

## Next binder (not opened)

The peak is a three-way sign-tape tie at Q1274. Every structural route through
the *sign* now has an exact floor at or above Q1284, or a measured
soundness/ANF failure. The reopen condition is narrow and provable-first: an
exact, bounded-width, in-place reverse discriminator for `sigma_r` that needs
neither a live full-width `(u,v)` nor a denominator-keyed ANF — with its own
predeclaration and static price against the Q1273 ceiling (917245) before any
code, and applied to the divide AND both multiply binders together. Absent that,
the productive direction is off the sign axis entirely: the 512 ABI
(coefficient + numerator) and the ~62 replay ladder are the only other terms in
the 1274 co-binder set, and the ladder is the sole one with any measured slack.

## Model receipt

Claude Fable 5 (`claude-fable-5`), single-lane research worktree. No shell beyond
this worktree, no network, no provider, hunt, submission, or publication
authority. Commits: predeclaration `9567fe0`, this account. Spend recorded by the
harness.
