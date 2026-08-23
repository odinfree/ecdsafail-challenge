# Lane state: b523 Q1274 control predictor

## Current verdict

`PREDECLARED`; `HOLD_BAKE`; `HOLD_DENSITY`; `HOLD_MODEL`; `HOLD_PARITY`;
`HOLD_SCAN`; `HOLD_HUNT`; `HOLD_PROVIDER`; `HOLD_SUBMIT`.

The paired H64, density margins, and blinded disjoint32 are frozen before any
source/model edit or candidate-corpus outcome.  See `.lane/PREDECLARATION.md`.

## Next bounded action

Commit and push this predeclaration.  Then change only the replay-peak and
square-ladder defaults, reproduce the exact Q1274 target, and prove the explicit
Q1278/ladder248 opt-out is byte-identical to protected b523.
