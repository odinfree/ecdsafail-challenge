# B1=24 source-bound predictor promotion

Predeclared before the semantic source edit.

- Base: promoted `b523ecf`, Q1278/T914789.886, full `0/0/0` at its own tail
  nonce.
- Frozen edit: change only `value_width` `BREAK_1` from 30 to 24.
- Expected identity from the completed environment-knob sweep: 12,822,408
  operations, SHA-256
  `af28dbc49471651c3e856c62c1fd97cb429469cde4b66fe7fe082a0d23fe1ad7`,
  Q1278/T911310.414 at the inherited diagnostic nonce, full `17/13/0`.
- Live anchor: `b523ecf`, score `1,169,101,620`. The projected B1=24 product is
  `1,164,654,180`, a margin of 4,447,440 before nonce selection.

The hard-coded source must reproduce the expected identity exactly. The
classical and phase predictor must be bound to that complete operation stream
and cross-checked against unchanged evaluator masks before any scan. A bounded
canary may be declared only after local CPU and Linux/CUDA parity. Every
survivor still requires the unchanged full 9,024-shot evaluator; only
classical/phase/ancilla `0/0/0` can advance.

## Frozen first cross-check

Before running any additional evaluator, cross-check the exact classical count
on nonces `81327465284`, `81327465285`, `81327465286`, and `81327465287`.
These four consecutive values were fixed before seeing any result beyond the
already-known promoted diagnostic nonce `81327465284`. All complete 9,024-shot
classical failure counts must equal the CPU model exactly; any disagreement
fails the model closed.
