# Lane state: b523 Q1274 control predictor

## Current verdict

`BAKE_PASS`; `PROTECTED_OPT_OUT_PASS`; `DENSITY_PASS`; `FAIL_MODEL_H64_2`;
`HOLD_PARITY`; `HOLD_SCAN`; `HOLD_HUNT`; `HOLD_PROVIDER`; `HOLD_SUBMIT`.

The paired H64, density margins, and blinded disjoint32 were frozen before any
source/model edit or candidate-corpus outcome.  The two-line bake reproduces
the Q1274 target at 12,935,433 operations/SHA `61a57ce6...` and the explicit
Q1278/ladder248 opt-out reproduces protected b523 at 12,876,472 operations/SHA
`4cb1787b...`.  The paired full-shot H64 then passes both frozen density
margins: candidate/protected classical ratio `0.965388213`, phase ratio
`1.028301887`, and ancilla zero on every row.  See `.lane/PREDECLARATION.md`,
`.lane/BAKE.md`, and `.lane/PAIRED-H64-DENSITY.md`.  The generic Q1276
coordinate-shell correction then matches 62/64 candidate H64 complete sets but
misses two evaluator-only shots (`008/6885`, `031/3691`) with no
predictor-only shots.  Disjoint32 remains blinded.

## Next bounded action

Commit and push `.lane/MISSING-CHANNEL-PREDECLARATION.md`, then run its bounded
first-divergence trace on the two revealed shots.  Permit at most one general
source-semantic correction and keep the frozen disjoint32 unopened until that
correction is committed.
