# Lane state: b523 Q1276 model qualification

## Current verdict

`EXACT_CPU_MODEL_PASS`; `HOLD_LINUX_CUDA_PARITY`; `HOLD_SCAN`; `HOLD_HUNT`;
`HOLD_PROVIDER`; `HOLD_SUBMIT`.

The two-line hard-coded bake is byte-identical to the measured Q1276 candidate.
The exact upstream port initially underpredicted three fixed H64 rows, and the
source-bound audit localized all three to the coordinate shell's dropped
bit-53 carry.  The frozen general correction now matches the trusted
evaluator's complete classical mismatch-shot sets on the original H64 and the
precommitted blinded disjoint32: 96/96 fixtures, 1,571/1,571 shots, with no
evaluator-only or predictor-only shots.

## Durable source

- branch: `research/b523-q1276-model-qualify`;
- predeclaration: `936a6e31a2c77abfd97ab00f8ec93bff173f90ef`;
- exact bake: `1adf7573101a3f8e9af2e7f7e2505faa9c6bea20`;
- candidate operations: `12,901,678`;
- candidate operations SHA-256:
  `d460c3968659b6bbbf5615268d73df210df55f9cd4cbca330de1ef960c6dd4c0`.

## Exact qualification

- original H64: 64/64 exact sets, classical/phase/ancilla `1048/883/0`;
- blinded disjoint32: 32/32 exact sets, classical/phase/ancilla `523/444/0`;
- compact digest ledger:
  `.lane/model-exact-set-qualification.tsv`;
- full receipt and executable hashes:
  `.lane/EXACT-MODEL-QUALIFICATION.md`.

## Next bounded action

Port the generic coordinate-shell correction to the source-bound Linux/CUDA
model and freeze a no-scan parity packet.  Require CPU = CUDA comb8 = CUDA
comb16 on the fixed fixtures and preserve wrong-count and same-count/wrong-SHA
rejection.  No range, provider, hunt, or submission is authorized.
