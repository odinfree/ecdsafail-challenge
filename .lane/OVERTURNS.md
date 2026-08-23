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
- Falsifier run (2026-08-23, exact — E6/E7): **KILLED, lower bound.** Three exact walls:
  1. *Zero release*: `walk_back_round` (pingpong_div.rs:1109) consumes each tape[r] as
     the control of the reverse signed add and uncomputes it against that round's
     boundary state, so NO replay-side representation frees a tape bit at either Q1278
     binder (r1 batch op 2,636,142 or terminal). Tape bits released = 0.
  2. *No compression*: exact sweep (E6, all 2^k patterns, k=1..14, both directions,
     both parities) — s ↦ M_seg is injective, so any register applying the segment
     action holds ≥ k qubits; entry width is exactly b(k)=k+1 signed bits (proved
     bound, tight), so a materialized matrix costs ≥ 3(k+1) qubits. The transition
     monoid is free: aggregation never compresses.
  3. *Application dominates* (E7): streamed application (each sign touched once) is
     circuit-identical to per-round replay — gain exactly 0. Materialized application
     is 4 quantum×quantum multiplies + inverse-application erasure (measured erasure
     barred by the phase-garbage gate) = 8(k+1) controlled 256-bit adds ≥ 2040(k+1) T
     vs a per-round cost < 900 T (one adder pass + O(window) fold, by circuit shape).
- Numerical verdict: best-possible case (representation at the injectivity floor k,
  zero T overhead) is Δscore ≥ +k·915,947; real materialized k=2 is ≥ +14M (+1.2%).
  ΔQ > 0 with 0 released ⇒ A2 never enters the 716.7 T/qubit tradeoff. **CLOSED.**
- Corollary: the coefficient register is tape-redundant mid-replay ((x,y) =
  num·(column of M_partial) since x₀=0), but exploiting the redundancy requires
  exactly the materialized aggregate application priced above. Same wall.

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
- **FALSIFIED as a global claim by the independent coordinated saddle (E8).** Peak-only
  cuts are net-negative and the plateau census (E3) correctly requires simultaneous
  movement in replay and square. The paired defaults do exactly that: peak1277 plus
  ladder247 measured Q1277/T916186.355, and peak1276 plus ladder246 measured
  Q1276/T916628.572. Both inherited nonces are dirty, but their counterfactual products
  beat Q1278; Q1276 is the stronger hunt candidate. This does not reopen the tape or
  decoder overturns A1–A4/A2.

## A6 — "A tape-free (data-independent-schedule) inversion could beat Q·T" (outside ping-pong)
- Claim: the 698-bit sign tape is a ping-pong artifact; an inversion with a classical
  schedule (Fermat x^(p−2), multiplication ladder) carries no tape and could win on Q.
- Falsifier run (2026-08-23, arithmetic on repo-measured costs — E7): **KILLED.**
  Dichotomy: a data-independent schedule cannot branch on data, so it must be a
  multiplication ladder; every add-based inversion (ping-pong, divstep/Bernstein–Yang,
  Kaliski) branches per step and carries the decision log (A1's forced-information
  argument applies to each).
  - Whole-circuit: one 256-bit modular squaring costs ~54k executed T in this codebase
    (WAYFINDER: square = 5.9% of T). Fermat needs ≥ ~270 mult/sq → ≥ 14.6M T; even at
    a generous Q=900 that is ≥ 13.1B score ≈ 11× the 1.17B target.
  - Hybrid margin (stop the walk early, finish multiplicatively): cutting one walk bit
    saves ~2.7 rounds ≈ 2.7 tape qubits (1,935 T-equivalent at 716.7) plus those
    rounds' walk/replay adds (~4 adder passes/round ≈ 5.4k T) ≈ 7.3k T-equivalent
    total, but costs ~2 mults ≈ 108k T per bit — dead by ≥14× at every stopping point.
- Consequence: the tape is not an artifact; it is the price of the add-only structure,
  and the add-only structure is ~10× cheaper than the tape-free alternative.

## Verdict
The tape cannot be removed, checkpointed, streamed, dirtied, classically recomputed,
or aggregated into transition matrices (A1–A4 + A2 closed with exact arguments), and
the tape-free escape loses ~10× on Toffoli (A6). The tape/decoder architecture space
reachable by this lane is exhausted. A5 is separately falsified by the coordinated
replay-cap plus square-ladder saddle, so this ledger must not be read as a global Q1278
lower bound. Conclude this lane and redirect qualification to the measured Q1276 pair.
