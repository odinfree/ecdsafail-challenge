# Lane state: b523 Q1274 control predictor

## Current verdict

`BAKE_PASS`; `PROTECTED_OPT_OUT_PASS`; `DENSITY_PASS`;
`MODEL_DIAGNOSIS_PASS_SQUARE_BIT56`; `MODEL_H64_PASS_64_OF_64`;
`HOLD_PARITY`; `HOLD_SCAN`; `HOLD_HUNT`; `HOLD_PROVIDER`; `HOLD_SUBMIT`.

The paired H64, density margins, and blinded disjoint32 were frozen before any
source/model edit or candidate-corpus outcome.  The two-line bake reproduces
the Q1274 target at 12,935,433 operations/SHA `61a57ce6...` and the explicit
Q1278/ladder248 opt-out reproduces protected b523 at 12,876,472 operations/SHA
`4cb1787b...`.  The paired full-shot H64 then passes both frozen density
margins: candidate/protected classical ratio `0.965388213`, phase ratio
`1.028301887`, and ancilla zero on every row.  See `.lane/PREDECLARATION.md`,
`.lane/BAKE.md`, and `.lane/PAIRED-H64-DENSITY.md`.  The generic coordinate
shell correction plus the single predeclared circuit-exact product-register
square correction now matches all 64/64 candidate H64 complete classical sets:
1,032/1,032 faults, with no evaluator-only or predictor-only shots.  Disjoint32
remains blinded.

## Next bounded action

Commit and push the H64-qualified corrected model.  Only afterward, open the
frozen disjoint32: predictor first, unchanged full evaluator second, requiring
32/32 complete-set equality plus the structural guards.
