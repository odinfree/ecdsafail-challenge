# Lane state: b523 Q1274 control predictor

## Current verdict

`BAKE_PASS`; `PROTECTED_OPT_OUT_PASS`; `DENSITY_PASS`; `GO_CPU_MODEL`;
`HOLD_PARITY`; `HOLD_SCAN`; `HOLD_HUNT`; `HOLD_PROVIDER`; `HOLD_SUBMIT`.

The paired H64, density margins, and blinded disjoint32 were frozen before any
source/model edit or candidate-corpus outcome.  The two-line bake reproduces
the Q1274 target at 12,935,433 operations/SHA `61a57ce6...` and the explicit
Q1278/ladder248 opt-out reproduces protected b523 at 12,876,472 operations/SHA
`4cb1787b...`.  The paired full-shot H64 then passes both frozen density
margins: candidate/protected classical ratio `0.965388213`, phase ratio
`1.028301887`, and ancilla zero on every row.  See `.lane/PREDECLARATION.md`,
`.lane/BAKE.md`, and `.lane/PAIRED-H64-DENSITY.md`.

## Next bounded action

Commit and push the paired-density verdict.  Then port the current-source
classical model plus the already-qualified generic low53/high203 coordinate
shell.  Require candidate H64 complete-set equality, commit before revealing
the frozen disjoint32, and hold all parity/search work until exact CPU
qualification closes.
