# Lane state: b523 Q1274 control predictor

## Current verdict

`BAKE_PASS`; `PROTECTED_OPT_OUT_PASS`; `HOLD_DENSITY`; `HOLD_MODEL`; `HOLD_PARITY`;
`HOLD_SCAN`; `HOLD_HUNT`; `HOLD_PROVIDER`; `HOLD_SUBMIT`.

The paired H64, density margins, and blinded disjoint32 were frozen before any
source/model edit or candidate-corpus outcome.  The two-line bake reproduces
the Q1274 target at 12,935,433 operations/SHA `61a57ce6...` and the explicit
Q1278/ladder248 opt-out reproduces protected b523 at 12,876,472 operations/SHA
`4cb1787b...`.  See `.lane/PREDECLARATION.md` and `.lane/BAKE.md`.

## Next bounded action

Commit and push the byte-exact bake.  Then run the precommitted paired H64
through unchanged full 9,024-shot evaluation for protected b523 and the Q1274
control, bind every operation stream, and apply the frozen density margins.
