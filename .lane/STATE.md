# Lane state: b523 Q1274 control predictor

## Current verdict

`BAKE_PASS`; `PROTECTED_OPT_OUT_PASS`; `DENSITY_PASS`;
`MODEL_DIAGNOSIS_PASS_SQUARE_BIT56`; `MODEL_H64_PASS_64_OF_64`;
`MODEL_D32_PASS_32_OF_32`; `CPU_MODEL_EXACT_96_OF_96`; `GO_PARITY_PACKET`;
`HOLD_PHASE_SCREEN`; `HOLD_SCAN`; `HOLD_HUNT`; `HOLD_PROVIDER`; `HOLD_SUBMIT`.

The paired H64, density margins, and blinded disjoint32 were frozen before any
source/model edit or candidate-corpus outcome.  The two-line bake reproduces
the Q1274 target at 12,935,433 operations/SHA `61a57ce6...` and the explicit
Q1278/ladder248 opt-out reproduces protected b523 at 12,876,472 operations/SHA
`4cb1787b...`.  The paired full-shot H64 then passes both frozen density
margins: candidate/protected classical ratio `0.965388213`, phase ratio
`1.028301887`, and ancilla zero on every row.  See `.lane/PREDECLARATION.md`,
`.lane/BAKE.md`, and `.lane/PAIRED-H64-DENSITY.md`.  The generic coordinate
shell correction plus the single predeclared circuit-exact product-register
square correction matches all 64/64 candidate H64 complete classical sets:
1,032/1,032 faults, with no evaluator-only or predictor-only shots.  After the
model source was committed and pushed, the blinded disjoint32 also closed at
32/32 complete sets and 517/517 faults.  The exact CPU model is therefore
qualified across 96/96 nonces and 1,549/1,549 classical mismatch shots.

## Next bounded action

Commit and push the disjoint32 evidence and 32-fixture parity packet.  Hand the
exact source/model/fixture hashes to the isolated Linux/CUDA lane.  Do not run
a range, phase-based rejection, provider action, hunt, or submission.
