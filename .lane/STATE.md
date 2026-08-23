# Lane state: b523 Q1276 model qualification

## Current verdict

`FAIL_MODEL`; `HOLD_PARITY`; `HOLD_SCAN`; `HOLD_HUNT`; `HOLD_SUBMIT`.

The two-line hard-coded bake is byte-identical to the measured Q1276 candidate,
but the exact upstream classical-model port underpredicts three of 64 frozen
full-evaluator rows by one.  See `.lane/MODEL-QUALIFICATION.md` and
`.lane/model-calibration-h64.tsv`.

## Durable source

- branch: `research/b523-q1276-model-qualify`;
- predeclaration: `936a6e31a2c77abfd97ab00f8ec93bff173f90ef`;
- exact bake: `1adf7573101a3f8e9af2e7f7e2505faa9c6bea20`;
- candidate operations: `12,901,678`;
- candidate operations SHA-256:
  `d460c3968659b6bbbf5615268d73df210df55f9cd4cbca330de1ef960c6dd4c0`.

## Next bounded action

Commit and push this terminal receipt.  Only then open a separately
predeclared structural missing-channel audit.  Approximate predictor output is
canary-only; it is not scan-safe.

