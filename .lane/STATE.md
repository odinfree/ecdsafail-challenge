# Lane state: b523 Q1276 model qualification

## Current verdict

`CORRECTION_FROZEN`; `H64_COUNTS_PASS`; `HOLD_EXACT_MODEL`; `HOLD_PARITY`;
`HOLD_SCAN`; `HOLD_HUNT`; `HOLD_SUBMIT`.

The two-line hard-coded bake is byte-identical to the measured Q1276 candidate.
The exact upstream port initially underpredicted three fixed H64 rows, and the
source-bound audit localized all three to the coordinate shell's dropped
bit-53 carry.  The frozen general correction now matches all 64 known evaluator
counts, but full 64-row exact shot-set parity and blinded disjoint32 remain.

## Durable source

- branch: `research/b523-q1276-model-qualify`;
- predeclaration: `936a6e31a2c77abfd97ab00f8ec93bff173f90ef`;
- exact bake: `1adf7573101a3f8e9af2e7f7e2505faa9c6bea20`;
- candidate operations: `12,901,678`;
- candidate operations SHA-256:
  `d460c3968659b6bbbf5615268d73df210df55f9cd4cbca330de1ef960c6dd4c0`.

## Next bounded action

Commit and push the frozen correction in `.lane/COORD-SHELL-CORRECTION.md`.
Then regenerate complete trusted-evaluator shot sets for original H64 and
require 64/64 equality.  If that passes, reveal the precommitted disjoint32 and
require 32/32 exact set equality.  The model is not scan-safe before both gates.
