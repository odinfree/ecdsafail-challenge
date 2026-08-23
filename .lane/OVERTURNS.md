# Overturn ledger — tape/decoder lane (bdf4845)

Family: ping-pong signed-walk division/multiplication with per-round sign tape
(`pingpong_div.rs`), interleaved coefficient replay, Plan{r1=356, r2=625, peak=1278}.

Exchange rate at operating point (Q=1278, T=915,947.392): **1 qubit ≡ 716.7 avg Toffoli**.
Any overturn must clear this bar net of its own Toffoli cost.

## A1 — "One resident sign qubit per not-yet-walked-back round is required"
- Wall: tape term at every binder (356 at the r1 batch, 698 at the terminal batch).
- Overturning observation would be: a walk-back that runs without the stored sign.
- Falsifier run (2026-08-23, algebraic, exact — E4 in EXPERIMENTS.md): **KILLED, forced.**
  The round map (u,v) → (u, v′=(v∓u)>>1, sign) has both pre-images 2v′+u and 2v′−u
  odd (2v′ even, u odd), so the branch bit is not a function of the post state; the
  terminal state (±1,±1) carries ~2 bits, so ~254 bits of denominator entropy must
  reside in the tape at replay end. Measurement escapes are closed: computational-basis
  measurement of data-dependent signs decoheres live-shot batches (eval's phase-garbage
  gate); X-basis erasure (Gidney style) destroys the value walk-back needs as a control.
- Consequence: family floor ≈ tape(698) + 2N(512) + terminal signs(2) + ladder_min ≈ 1215–1230.

## A2 — "Replay must consume the tape as per-round quantum controls"
- Wall: replay pins tape + coefficient + numerator (512) simultaneously at every binder.
- Overturn candidate: segment-aggregate replay — apply a whole segment's effect on the
  coefficient pair via its 2×2 transition matrix instead of per-round signs.
- Status: OPEN, unpriced. Matrix entries for a k-round segment are data-dependent and
  ~k bits wide, so naive materialization rebuys the tape width. Needs a redundant/
  streamed-representation design before a falsifier exists. This is the only surviving
  in-family structural direction.

## A3 — "The r1 batch replay must pause the walk holding u,v (2×139=278 wires)"
- KILLED by arithmetic: walk and replay act on disjoint registers, so any interleaving
  is legal; d(tape + 2·width)/d(round) ≈ +0.29 > 0, so the lockstep/batch placement the
  incumbent already uses is footprint-minimal. Nothing to run.

## A4 — "The chunk ladder must be clean ancillas" (dirty-borrow from idle signs)
- At every binder there are ≥130 idle already-replayed sign wires (626 at terminal)
  that could serve as dirty carries, freeing the clean ladder (peak −66 potential).
- KILLED by exchange rate: dirty carries lose the measured-uncompute discount
  (≥1 extra Toffoli per carry per add); ≈2 traversals × ~700 replay adds ≈ 1,400–2,800
  extra T per qubit freed vs break-even 716.7 → net-negative ≈2–4×.

## A5 — "Peak 1278 is the score-optimal operating point of this family"
- Supported: prior lane measurement (PEAK=1277 net-negative); plateau census (E3) shows
  all three binder families (pp_div_replay, pp_mul_walkback, square_product_register)
  are budget-followers whose ladders spend allowance up to 1278 to buy Toffoli. A Q cut
  requires shedding ALL THREE simultaneously; the square co-binder is the closed-lane
  territory (Q1275 packet), leaving A2 as the only in-lane opening.

## Verdict
The tape cannot be removed, checkpointed, streamed, dirtied, or classically recomputed
within the current replay primitive — closed with exact arguments, not samples. The
burn must move one level up: replace the sign-consuming replay (A2) or leave the
ping-pong family. Q1278 stands as the family's score optimum.
