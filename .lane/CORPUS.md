# Predeclared corpora and decision rule

Frozen before any new build/profile, predictor census, or full simulation in
this lane on 2026-08-23 (Europe/Zurich).

## Fixtures

- F0: inherited nonce `251000962439`; receipt reproduction only, never a
  density estimate.
- F1: built-in product-square selftest, its unchanged deterministic 64 inputs.
- F2: built-in pingpong point-add selftest, its unchanged deterministic 64
  affine additions.
- F3: `PP_PROFILE_SEED=hard-fold-55`, 64 lanes, for focused value/phase/dirty
  sanity and phase-by-phase Q/T pricing.

## Density blocks

- H: nonces `444000000000..444000000063` inclusive (64 complete 9024-shot
  classical predictor draws). Always run all 64 for base and candidate.
- P: the first 16 nonces of H, `444000000000..444000000015` inclusive, through
  the unchanged complete 9024-shot simulator with early abort disabled. Always
  run all 16 for base and candidate and report classical, phase-batch, ancilla,
  and exact average-Toffoli totals.

The same numeric nonces bind to different SHA-derived corpora after an op-stream
change. Therefore comparisons are ensemble comparisons, not paired-shot
claims. No adaptive extension, survivor selection, or search follows from
these blocks.

## E-001 hypothesis and gate

Changing only replay fold `54 -> 55` will:

1. preserve Q1272 and keep rounded full T at or below 921139;
2. preserve exact F0 base and promoted-route reproduction under `=54`;
3. pass F1--F3 with classical/phase/ancilla all zero;
4. reduce `replay_div + replay_mul` classical density on H by at least 20%
   without a new result-channel population; and
5. not increase mean full-simulation phase-batch density on P.

If gates 1--3 fail, kill the source change. If gate 4 fails, replay-fold
widening is not the hard-channel lever. Gate 5 is secondary: a statistically
flat P result does not erase a classical win, but a clear phase regression
blocks composition. Any advance remains a density-improved architecture, not
a clean submission candidate.

## E-001 terminal result and E-001b gate

E-001 stopped before H/P because its measured peak was Q1273. E-001b is frozen
before measurement as `SUB4_PP_REPLAY_FOLD_WINDOW=55 SUB4_PP_PEAK=1271` on the
unchanged source. First run F3 only. If and only if F3 reports Q1272 or lower,
rounded-T headroom remains positive, and `0/0/0`, run the already-frozen H and P
blocks in full. No corpus or threshold changes.

E-001b stopped before H/P at Q1273. E-001c is now frozen before measurement as
`SUB4_PP_MUL_PLUS2F_ALIAS=1 SUB4_PP_REPLAY_FOLD_WINDOW=55` at the original
peak1272 plan. First run the exhaustive selector miter and F3. Only if the miter
passes and F3 is Q1272 or lower, `0/0/0`, and inside the T ceiling may H/P run.
The original H/P ranges and thresholds remain unchanged.
